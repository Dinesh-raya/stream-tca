# TCA v2.0 Streamlit Implementation

This is a Python Streamlit implementation of the Terminal Communication Array v2.0 chat application.

## Features

- Terminal-style interface with green-on-black theme
- User authentication with password hashing
- Room-based chat system
- Real-time messaging (simulated with periodic refresh)
- Admin panel for user and room management
- MongoDB integration for persistent storage

## Prerequisites

- Python 3.8+
- MongoDB database (local or Atlas)

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update `MONGODB_URI` with your MongoDB connection string

4. Run the application:
   ```
   streamlit run app.py
   ```

## Deployment

This application is designed for cloud deployment on platforms that support Streamlit applications:

- Streamlit Community Cloud
- Heroku
- Google Cloud Run
- AWS Elastic Beanstalk

For MongoDB, you can use:
- MongoDB Atlas (free tier available)
- Self-hosted MongoDB instance

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
- `database.py`: MongoDB database operations
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: Streamlit configuration
- `.env`: Environment variables (not included in repo)

## License

This project is licensed under the MIT License.