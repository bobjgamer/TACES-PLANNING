# Private Family Tax-Planning System

A private Streamlit application for family tax planning, specifically tailored for Saskatchewan residents.

## Setup Instructions

### Local Development

1.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    Create a `.env` file in the root directory (do not commit this file) with your database connection if you use PostgreSQL:
    ```
    DATABASE_URL=postgresql://user:password@localhost/dbname
    ```
    *Note: If `DATABASE_URL` is not set, the app will default to a local SQLite database (`tax_plan.db`).*

3.  **Authentication Config:**
    Create a `secrets.toml` inside a `.streamlit` folder (`.streamlit/secrets.toml`) for authentication. You can generate a hashed password using `streamlit-authenticator`:
    ```toml
    [credentials.usernames.admin]
    email = "admin@example.com"
    name = "Admin"
    password = "your_hashed_password" # Use stauth.Hasher to generate this
    ```
    *If no secrets are found, the app uses a default local login for testing purposes (username: `admin`, password: `password`). Be sure to configure secrets before deploying.*

4.  **Run the Application:**
    ```bash
    streamlit run app.py
    ```

### Streamlit Cloud Deployment

1.  Push this code to a private GitHub repository.
2.  Connect the repository to Streamlit Cloud.
3.  In the Streamlit Cloud dashboard, go to App Settings > Secrets.
4.  Paste the contents of your `.streamlit/secrets.toml` into the secrets box.
5.  If using Supabase (PostgreSQL), add `DATABASE_URL="postgresql://..."` to the secrets.
