# TCA v2.0 Streamlit Implementation

This is a Python Streamlit implementation of the Terminal Communication Array v2.0 chat application.

## Features

- Terminal-style interface with green-on-black theme
- User authentication with password hashing
- Room-based chat system
- Direct messaging between users
- Real-time messaging (simulated with periodic refresh)
- Admin panel for user and room management
- Supabase PostgreSQL integration for persistent storage
- Security key validation for administrative commands
- Discord-like command interface with contextual suggestions
- Clean separation between commands and regular chat messages
- Automatic message cleanup (3-day retention policy)
- Admin-only deletion permissions
- Bulk user creation capabilities

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
     
     -- Direct messages table
     CREATE TABLE direct_messages (
       id SERIAL PRIMARY KEY,
       sender VARCHAR(50) NOT NULL,
       recipient VARCHAR(50) NOT NULL,
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

### Discord-like Command Interface

The application features a Discord-like command interface where users can interact using slash commands. The interface provides contextual command suggestions based on the user's current state.

#### Contextual Command States:

1. **Lobby/Main Context** (when not in any room or DM):
   - `/dm <username>` - Start a direct message with a user
   - `/join <room>` - Join a chat room
   - `/listrooms` - List available rooms
   - `/help` - Show help information
   - `/logout` - Log out of the application

2. **In Room or DM Context**:
   - Type messages directly to chat in the current room/DM
   - `/quit` - Leave the current room or DM
   - `/help` - Show help information
   - `/logout` - Log out of the application

3. **Administrative Commands** (available to admin users in any context):
   - `/adduser <username> <password> <securitykey>` - Create a new user
   - `/createroom <roomname> <securitykey>` - Create a new room
   - `/deleteroom <roomname> <securitykey>` - Delete a room
   - `/deletemessage <message_id> <securitykey>` - Delete a specific message
   - `/cleanup <securitykey>` - Run manual cleanup of old messages
   - `/giveaccess <user1,user2,...> <roomname> <securitykey>` - Grant room access

### Terminal Commands

All commands start with '/'. Available commands:

```
/help                                          - Show this help
/login <username>                              - Login
/listrooms                                     - List available rooms
/join <room>                                   - Join a room
/users                                         - List users in current room
/dm <username>                                 - Start direct message
/exit                                          - Exit DM or leave room
/logout                                        - Logout
/adduser <username> <password> <securitykey>   - (Admin) Create new user
/changepass <oldpass> <newpass> <securitykey>  - Change your password
/createroom <roomname> <securitykey>           - (Admin) Create new room
/deleteroom <roomname> <securitykey>           - (Admin) Delete a room
/deletemessage <message_id> <securitykey>      - (Admin) Delete a message
/cleanup <securitykey>                         - (Admin) Cleanup old messages
/giveaccess <user1,user2,...> <roomname> <securitykey> - (Admin) Grant room access to users
/quit                                          - Quit the app
```

### Chatting

When in a room or direct message context, any text input that doesn't start with '/' will be treated as a chat message and sent to the current conversation.

### Administrative Operations

Administrative commands require a security key. The default key is `TCA_ADMIN_KEY_2023`. In a production environment, this should be changed and stored securely.

1. Login with admin credentials:
   - admin / admin123 (Administrator)

2. Use administrative commands with the security key:
   - `/adduser newuser newpassword TCA_ADMIN_KEY_2023`
   - `/createroom newroom TCA_ADMIN_KEY_2023`
   - `/deleteroom oldroom TCA_ADMIN_KEY_2023`
   - `/deletemessage 123 TCA_ADMIN_KEY_2023`
   - `/cleanup TCA_ADMIN_KEY_2023`
   - `/giveaccess user1,user2 newroom TCA_ADMIN_KEY_2023`

### Database Management Features

#### Automatic Message Cleanup
- Messages are automatically retained for only 3 days
- Data retention policy removes messages older than 72 hours
- Cleanup process runs automatically without manual intervention
- Admins can trigger manual cleanup with `/cleanup` command

#### Admin-Only Deletion Permissions
- Room deletion functionality restricted to admin users only
- Admins can delete individual messages within any room
- Proper authorization checks prevent non-admin users from performing deletion operations

#### Bulk User Creation
- Admin users can create multiple user accounts simultaneously
- Batch user creation through admin panel interface
- Support for creating users with specified usernames and passwords
- Results feedback for successful and failed creations

## Architecture

- `app.py`: Main Streamlit application
- `database.py`: Supabase database operations
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: Streamlit configuration
- `secrets.toml`: Streamlit secrets (not included in repo)

## License

This project is licensed under the MIT License.