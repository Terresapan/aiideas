import streamlit as st
from streamlit_gsheets import GSheetsConnection
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langsmith import traceable
import os

# Set API keys
os.environ["OPENAI_API_KEY"] = st.secrets["general"]["OPENAI_API_KEY"]
os.environ["GROQ_API_KEY"] = st.secrets["general"]["GROQ_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]["API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "AI Ideas Explorer"

st.set_page_config(page_title="AI Ideas Explorer", page_icon="💡")

# Initialize embeddings
@st.cache_resource
@traceable(type="embeddings")
def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")

# Load data from Google Sheets
@st.cache_data(ttl=600)
@traceable(type="data")
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Ideas", ttl="10m", usecols=[0, 1, 2], nrows=210)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Create vector store
@st.cache_resource
@traceable(type="vector_store")
def create_vector_store(_embeddings, df):
    if df is None or df.empty:
        st.error("DataFrame is None or empty")
        return None
    
    try:
        df.columns = ['Idea', 'Category', 'How']
        text_data = [
            f"Idea: {idea}; Category: {category}; How: {how}"
            for idea, category, how in zip(df['Idea'], df['Category'], df['How'])
        ]
        
        metadatas = df.to_dict('records')
        
        vector_store = FAISS.from_texts(
            texts=text_data, 
            embedding=_embeddings,
            metadatas=metadatas
        )
        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None

# Main Streamlit app
def main():
    st.title("🌟 AI Ideas Explorer")
    st.markdown("### Explore and discover AI related new ideas")
    
    # Get embeddings
    embeddings = get_embeddings()
    
    # Load data
    df = load_data()
    if df is None or df.empty:
        st.error("Could not load data or data is empty")
        return
    
    # Create vector store
    vector_store = create_vector_store(embeddings, df)
    if vector_store is None:
        st.error("Could not create vector store")
        return
    
    # Initialize session state for query
    if "user_query" not in st.session_state:
        st.session_state["user_query"] = ""

    # User query input
    user_query = st.text_input("🔍 Ask a question about ideas:", 
                               placeholder="Type your question here...",
                               key="user_query")

    # Button to trigger search
    button_clicked = st.button("Explore Ideas")

    # Process query only if Enter is pressed or button is clicked
    if st.session_state["user_query"] and (st.session_state.get("process_query") or button_clicked):
        st.session_state["process_query"] = False  # Reset the flag
        try:
            # Search in vector store
            results = vector_store.similarity_search(user_query, k=5)
                
            # Initialize LLM
            llm = ChatGroq(
                model="llama-3.3-70b-versatile", 
                temperature=0,
                api_key=st.secrets["general"]["GROQ_API_KEY"]
            )
            
            if results:
                result_texts = "\n".join([
                    f"Idea: {result.metadata.get('Idea', 'N/A')}, "
                    f"How: {result.metadata.get('How', 'N/A')}, "
                    f"Category: {result.metadata.get('Category', 'N/A')}" 
                    for result in results
                ])
                
                prompt = f"I found the following ideas based on your query '{user_query}':\n{result_texts}\nCan you summarize or provide insight on these ideas?"
                
                response = llm.invoke(prompt)
                st.write(response.content)
            else:
                st.write("No relevant results found.")

            for result in results:
                st.write("Result Metadata:", result.metadata)
        
        except Exception as e:
            st.error(f"Error processing query: {e}")
    
    # Set flag to process query when Enter is pressed
    if user_query and not button_clicked:
        st.session_state["process_query"] = True

if __name__ == "__main__":
    main()

