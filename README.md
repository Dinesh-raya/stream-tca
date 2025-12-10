# TCA v2.0 Streamlit Implementation

This is a Python Streamlit implementation of the Terminal Communication Array v2.0 chat application.

## Features

- Terminal-style interface with green-on-black theme
- User authentication with password hashing
- Room-based chat system
- Real-time messaging (simulated with periodic refresh)
- Admin panel for user and room management
- Supabase PostgreSQL integration for persistent storage

## Prerequisites

- Python 3.8+
- Supabase account (free tier available)

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up Supabase tables:
   - Create a Supabase project at https://supabase.com/
   - Create the following tables in the Supabase SQL editor:
     ```sql
     -- Users table
     CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       username VARCHAR(50) UNIQUE NOT NULL,
       password TEXT NOT NULL,
       role VARCHAR(20) DEFAULT 'user',
       created_at TIMESTAMP DEFAULT NOW()
     );
     
     -- Rooms table
     CREATE TABLE rooms (
       id SERIAL PRIMARY KEY,
       name VARCHAR(50) UNIQUE NOT NULL,
       allowed_users TEXT[] DEFAULT '{}',
       is_public BOOLEAN DEFAULT FALSE,
       created_at TIMESTAMP DEFAULT NOW()
     );
     
     -- Messages table
     CREATE TABLE messages (
       id SERIAL PRIMARY KEY,
       room VARCHAR(50) NOT NULL,
       username VARCHAR(50) NOT NULL,
       content TEXT NOT NULL,
       timestamp TIMESTAMP DEFAULT NOW()
     );
     ```

4. Configure Streamlit secrets:
   - Create a `secrets.toml` file in your Streamlit deployment environment
   - Add your Supabase credentials:
     ```toml
     SUPABASE_URL = "your_supabase_project_url"
     SUPABASE_KEY = "your_supabase_anon_key"
     ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## Deployment

This application is designed for cloud deployment on platforms that support Streamlit applications:

- Streamlit Community Cloud
- Heroku
- Google Cloud Run
- AWS Elastic Beanstalk

For the database, you can use:
- Supabase (free tier available with PostgreSQL)

## Usage

1. Login with one of the default accounts:
   - admin / admin123 (Administrator)
   - user1 / password1 (User)
   - user2 / password2 (User)

2. Select a room from the dropdown
3. Send messages using the input field
4. Administrators can create new users and rooms via the Admin Panel

## Commands

Unlike the original TCA, this version uses a graphical interface rather than text commands. However, future versions may implement command parsing.

## Architecture

- `app.py`: Main Streamlit application
- `database.py`: Supabase database operations
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: Streamlit configuration
- `secrets.toml`: Streamlit secrets (not included in repo)

## License

This project is licensed under the MIT License.