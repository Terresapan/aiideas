# :bulb: AI Ideas Explorer

An AI-powered platform to search and explore new AI ideas.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aiideas.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Set up environment variables

   The application requires several environment variables to be set up. You can set them up in a `.streamlit/secrets.toml` file. Here are the required variables:

   ```
   [general]
   OPENAI_API_KEY = "your_openai_api_key"
   GROQ_API_KEY = "your_groq_api_key"

   [LANGCHAIN_API_KEY]
   API_KEY = "your_langchain_api_key"
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Repository Structure

- `README.md`: This file. Provides an overview of the project, setup instructions, and repository structure.
- `LICENSE`: Contains the license information for the project.
- `requirements.txt`: Lists the Python packages required to run the application.
- `streamlit_app.py`: The main Streamlit application file. Contains the code for the AI Ideas Explorer.
- `.gitignore`: Specifies files and directories that should be ignored by git.
- `.devcontainer/devcontainer.json`: Configuration file for development container.
- `.github/CODEOWNERS`: Defines the code owners for the repository.
