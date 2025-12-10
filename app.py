import streamlit as st
from datetime import datetime
import os
from database import db_manager

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
    
if 'current_room' not in st.session_state:
    st.session_state.current_room = None
    
if 'direct_message_target' not in st.session_state:
    st.session_state.direct_message_target = None
    
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'rooms' not in st.session_state:
    st.session_state.rooms = []
    
if 'command_history' not in st.session_state:
    st.session_state.command_history = []
    
if 'show_reset_password' not in st.session_state:
    st.session_state.show_reset_password = False

def login_page():
    """Display the login page."""
    st.title("Terminal Communication Array v2.0")
    st.subheader("Secure Terminal Login")
    
    # Toggle for password reset
    if st.button("Forgot Password?"):
        st.session_state.show_reset_password = not st.session_state.show_reset_password
    
    if st.session_state.show_reset_password:
        st.subheader("Reset Password")
        reset_username = st.text_input("Username for Password Reset")
        reset_old_password = st.text_input("Old Password", type="password", key="reset_old_password")
        reset_new_password = st.text_input("New Password", type="password", key="reset_new_password")
        
        if st.button("Reset Password"):
            if reset_username and reset_old_password and reset_new_password:
                if db_manager.reset_user_password_unauthenticated(reset_username, reset_old_password, reset_new_password):
                    st.success("Password reset successfully! You can now login with your new password.")
                    st.session_state.show_reset_password = False
                else:
                    st.error("Failed to reset password. Please check your credentials.")
            else:
                st.error("Please fill in all fields.")
        
        if st.button("Back to Login"):
            st.session_state.show_reset_password = False
            st.experimental_rerun()
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            user_data = db_manager.authenticate_user(username, password)
            if user_data:
                st.session_state.logged_in = True
                st.session_state.user_data = user_data
                st.session_state.rooms = db_manager.get_user_rooms(username)
                st.success(f"Welcome, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
        
        # Password change section for authenticated users
        if st.session_state.logged_in:
            st.subheader("Change Password")
            change_new_password = st.text_input("New Password", type="password", key="change_new_password")
            
            if st.button("Change Password"):
                if change_new_password:
                    if db_manager.change_user_password_authenticated(st.session_state.user_data['username'], change_new_password):
                        st.success("Password changed successfully!")
                    else:
                        st.error("Failed to change password.")
                else:
                    st.error("Please enter a new password.")

def logout():
    """Handle user logout."""
    st.session_state.logged_in = False
    st.session_state.user_data = None
    st.session_state.current_room = None
    st.session_state.direct_message_target = None
    st.session_state.messages = []
    st.session_state.rooms = []
    st.session_state.show_reset_password = False
    st.success("You have been logged out successfully.")
    st.experimental_rerun()

def send_message(room: str, username: str, content: str):
    """Send a message to a room."""
    if db_manager.save_message(room, username, content):
        # Add to session state for immediate display
        new_message = {
            "username": username,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(new_message)
        return True
    return False

def send_direct_message(sender: str, recipient: str, content: str):
    """Send a direct message."""
    if db_manager.save_direct_message(sender, recipient, content):
        # Add to session state for immediate display
        new_message = {
            "username": sender,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(new_message)
        return True
    return False

def load_room_messages(room_name: str):
    """Load messages for the current room."""
    # In a real implementation, you would fetch from database
    # For now, we'll keep messages in session state
    pass

def show_help():
    """Display help information."""
    help_text = """TCA v2.0 Terminal Commands:
========================
/help                                          - Show this help
/login <username>                              - Login
/listrooms                                     - List available rooms
/join <room>                                   - Join a room
/users                                         - List users in current room
/dm <username>                                 - Start direct message
/exit                                          - Exit DM or leave room
/logout                                        - Logout
/changepass <newpass>                          - Change your password (authenticated users)
/resetpass <username> <oldpass> <newpass>      - Reset password (unauthenticated users)
/adduser <username> <password> <securitykey>   - (Admin) Create new user
/createroom <roomname> <securitykey>           - (Admin) Create new room
/deleteroom <roomname> <securitykey>           - (Admin) Delete a room
/deletemessage <message_id> <securitykey>      - (Admin) Delete a message
/cleanup <securitykey>                         - (Admin) Cleanup old messages
/giveaccess <user1,user2,...> <roomname> <securitykey> - (Admin) Grant room access to users
/quit                                          - Quit the app

Additional Information:
- All commands start with '/'
- Administrative commands require a security key
- Direct messages are private between two users
- Rooms can be public or private (access controlled)
"""
    st.text(help_text)

def list_rooms():
    """List available rooms."""
    rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
    if rooms:
        st.text("Available rooms:")
        for room in rooms:
            st.text(f"  - {room}")
    else:
        st.text("No rooms available.")

def join_room(room_name):
    """Join a room."""
    rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
    if room_name in rooms:
        st.session_state.current_room = room_name
        st.session_state.direct_message_target = None
        st.session_state.messages = []  # Clear messages when switching rooms
        st.text(f"Joined room: {room_name}")
    else:
        st.text(f"Error: Room '{room_name}' not found or access denied.")

def list_users():
    """List users in current room."""
    st.text("Users in current context:")
    st.text(f"  - {st.session_state.user_data['username']} (you)")

def start_dm(target_user):
    """Start direct messaging with a user."""
    st.session_state.direct_message_target = target_user
    st.session_state.current_room = None
    st.session_state.messages = []
    st.text(f"Started direct message with: {target_user}")

def exit_room_or_dm():
    """Exit current room or DM."""
    if st.session_state.direct_message_target:
        st.text(f"Exited direct message with: {st.session_state.direct_message_target}")
        st.session_state.direct_message_target = None
    elif st.session_state.current_room:
        st.text(f"Left room: {st.session_state.current_room}")
        st.session_state.current_room = None
        st.session_state.messages = []
    else:
        st.text("Not in any room or direct message.")

def validate_security_key(security_key):
    """Validate the security key for admin operations."""
    # Use Streamlit secrets instead of hardcoded value
    try:
        admin_security_key = st.secrets["ADMIN_SECURITY_KEY"]
        return security_key == admin_security_key
    except KeyError:
        # Fallback to default if not configured (for development)
        return security_key == "TCA_ADMIN_KEY_2023"

def change_password(new_pass):
    """Change user password for authenticated users."""
    if db_manager.change_user_password_authenticated(st.session_state.user_data['username'], new_pass):
        st.text("Password changed successfully.")
    else:
        st.text("Error: Failed to change password.")

def reset_password(username, old_pass, new_pass):
    """Reset user password for unauthenticated users."""
    if db_manager.reset_user_password_unauthenticated(username, old_pass, new_pass):
        st.text(f"Password for user '{username}' reset successfully.")
    else:
        st.text(f"Error: Failed to reset password for user '{username}'. Please check credentials.")

def add_user(username, password, security_key):
    """Add a new user (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    if db_manager.create_user(username, password, "user"):
        st.text(f"User '{username}' created successfully.")
    else:
        st.text(f"Error: Failed to create user '{username}'. Username may already exist.")

def add_multiple_users(users_data, security_key):
    """Add multiple users (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    results = db_manager.create_multiple_users(users_data, "user")
    st.text("Batch user creation results:")
    for username, success in results.items():
        if success:
            st.text(f"  ✓ User '{username}' created successfully.")
        else:
            st.text(f"  ✗ Failed to create user '{username}'. Username may already exist.")

def create_room(room_name, security_key):
    """Create a new room (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    if db_manager.create_room(room_name, [st.session_state.user_data['username']], False):
        st.text(f"Room '{room_name}' created successfully.")
        # Refresh rooms list
        st.session_state.rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
    else:
        st.text(f"Error: Failed to create room '{room_name}'. Room may already exist.")

def delete_room(room_name, security_key):
    """Delete a room (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    if db_manager.delete_room(room_name):
        st.text(f"Room '{room_name}' deleted successfully.")
        # Refresh rooms list
        st.session_state.rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
    else:
        st.text(f"Error: Failed to delete room '{room_name}'.")

def delete_message(message_id, security_key):
    """Delete a message (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    if db_manager.delete_message(int(message_id)):
        st.text(f"Message #{message_id} deleted successfully.")
    else:
        st.text(f"Error: Failed to delete message #{message_id}.")

def cleanup_old_messages(security_key):
    """Cleanup old messages (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    deleted_count = db_manager.cleanup_old_messages()
    st.text(f"Cleanup completed. {deleted_count} old messages deleted.")

def give_access(users_str, room_name, security_key):
    """Give access to users for a room (admin only)."""
    if not validate_security_key(security_key):
        st.text("Error: Invalid security key.")
        return
        
    users = users_str.split(',')
    if db_manager.grant_room_access(room_name, users):
        st.text(f"Access granted to {users_str} for room {room_name}.")
    else:
        st.text(f"Error: Failed to grant access to {users_str} for room {room_name}.")

def send_regular_message(message):
    """Send a regular message."""
    if st.session_state.current_room:
        send_message(
            st.session_state.current_room, 
            st.session_state.user_data['username'], 
            message
        )
    elif st.session_state.direct_message_target:
        send_direct_message(
            st.session_state.user_data['username'],
            st.session_state.direct_message_target,
            message
        )
    else:
        st.text("Error: Not in a room or direct message. Use /join <room> or /dm <user> first.")

def get_contextual_commands():
    """Get contextual command suggestions based on current state."""
    commands = []
    
    if not st.session_state.current_room and not st.session_state.direct_message_target:
        # In lobby/main context
        commands.extend([
            ("/dm <username>", "Start a direct message with a user"),
            ("/join <room>", "Join a chat room"),
            ("/listrooms", "List available rooms"),
            ("/help", "Show help information"),
            ("/logout", "Log out of the application")
        ])
    else:
        # In room or DM context
        commands.extend([
            ("/quit", "Leave the current room or DM"),
            ("/help", "Show help information"),
            ("/logout", "Log out of the application")
        ])
        
        # Add admin commands if user is admin
        if st.session_state.user_data.get('role') == 'admin':
            commands.extend([
                ("/adduser <username> <password> <securitykey>", "Create a new user"),
                ("/createroom <roomname> <securitykey>", "Create a new room"),
                ("/deleteroom <roomname> <securitykey>", "Delete a room"),
                ("/deletemessage <message_id> <securitykey>", "Delete a message"),
                ("/cleanup <securitykey>", "Cleanup old messages"),
                ("/giveaccess <user1,user2,...> <roomname> <securitykey>", "Grant room access")
            ])
        else:
            # Add user command for changing password
            commands.extend([
                ("/changepass <newpass>", "Change your password")
            ])
    
    return commands

def show_command_suggestions():
    """Display contextual command suggestions."""
    commands = get_contextual_commands()
    if commands:
        st.text("\nAvailable commands in current context:")
        for cmd, desc in commands:
            st.text(f"  {cmd:<50} - {desc}")

def process_command(command_str):
    """Process terminal commands."""
    st.session_state.command_history.append(command_str)
    
    # Check if it's a command (starts with /) or regular message
    if command_str.startswith('/'):
        # Parse command
        parts = command_str.split()
        if not parts:
            return
            
        command = parts[0].lower()
        
        # Process different commands
        if command == "/help":
            show_help()
            show_command_suggestions()
        elif command == "/listrooms":
            list_rooms()
        elif command == "/join" and len(parts) > 1:
            join_room(parts[1])
        elif command == "/users":
            list_users()
        elif command == "/dm" and len(parts) > 1:
            start_dm(parts[1])
        elif command == "/exit":
            exit_room_or_dm()
        elif command == "/logout":
            logout()
        elif command == "/quit":
            st.text("Goodbye! Thanks for using TCA v2.0.")
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.current_room = None
            st.session_state.direct_message_target = None
            st.session_state.messages = []
            st.session_state.rooms = []
            st.experimental_rerun()
        elif command == "/changepass" and len(parts) > 1:
            change_password(parts[1])
        elif command == "/resetpass" and len(parts) > 3:
            reset_password(parts[1], parts[2], parts[3])
        elif command == "/adduser" and len(parts) > 3 and st.session_state.user_data.get('role') == 'admin':
            add_user(parts[1], parts[2], parts[3])
        elif command == "/addmultipleusers" and len(parts) > 2 and st.session_state.user_data.get('role') == 'admin':
            # Parse users data from command (format: username1:password1,username2:password2,...)
            users_str = parts[1]
            security_key = parts[2]
            users_list = users_str.split(',')
            users_data = []
            for user_pair in users_list:
                if ':' in user_pair:
                    username, password = user_pair.split(':', 1)
                    users_data.append({"username": username, "password": password})
            add_multiple_users(users_data, security_key)
        elif command == "/createroom" and len(parts) > 2 and st.session_state.user_data.get('role') == 'admin':
            create_room(parts[1], parts[2])
        elif command == "/deleteroom" and len(parts) > 2 and st.session_state.user_data.get('role') == 'admin':
            delete_room(parts[1], parts[2])
        elif command == "/deletemessage" and len(parts) > 2 and st.session_state.user_data.get('role') == 'admin':
            delete_message(parts[1], parts[2])
        elif command == "/cleanup" and len(parts) > 1 and st.session_state.user_data.get('role') == 'admin':
            cleanup_old_messages(parts[1])
        elif command == "/giveaccess" and len(parts) > 3 and st.session_state.user_data.get('role') == 'admin':
            # Parse users list (comma separated)
            give_access(parts[1], parts[2], parts[3])
        else:
            st.text(f"Unknown command: {command}. Type /help for available commands.")
    else:
        # Treat as regular message if not a recognized command
        send_regular_message(command_str)

def admin_panel():
    """Display simplified admin panel for user and room management."""
    st.title("Admin Panel")
    
    # User management section
    st.header("User Management")
    
    st.subheader("Create New User")
    with st.form(key="create_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        user_role = st.selectbox("Role", ["user", "admin"])
        create_user_button = st.form_submit_button("Create User")
        
        if create_user_button and new_username and new_password:
            if db_manager.create_user(new_username, new_password, user_role):
                st.success(f"User {new_username} created successfully!")
            else:
                st.error("Failed to create user. Username may already exist.")
    
    st.subheader("Batch User Creation")
    st.caption("Enter users in format: username1:password1,username2:password2,...")
    with st.form(key="batch_create_user_form"):
        batch_users = st.text_area("Users (comma separated)", height=100)
        batch_create_button = st.form_submit_button("Create Users")
        
        if batch_create_button and batch_users:
            users_list = batch_users.split(',')
            users_data = []
            for user_pair in users_list:
                if ':' in user_pair:
                    username, password = user_pair.split(':', 1)
                    users_data.append({"username": username.strip(), "password": password.strip()})
            
            if users_data:
                results = db_manager.create_multiple_users(users_data, "user")
                st.write("Batch user creation results:")
                for username, success in results.items():
                    if success:
                        st.success(f"✓ User '{username}' created successfully.")
                    else:
                        st.error(f"✗ Failed to create user '{username}'. Username may already exist.")
            else:
                st.error("Invalid format. Please use username:password pairs separated by commas.")
    
    # Room management section
    st.header("Room Management")
    
    st.subheader("Create New Room")
    with st.form(key="create_room_form"):
        room_name = st.text_input("Room Name")
        is_public = st.checkbox("Public Room (accessible to all users)")
        create_room_button = st.form_submit_button("Create Room")
        
        if create_room_button and room_name:
            allowed_users = [st.session_state.user_data['username']] if not is_public else []
            if db_manager.create_room(room_name, allowed_users, is_public):
                st.success(f"Room {room_name} created successfully!")
                # Refresh rooms list
                st.session_state.rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
            else:
                st.error("Failed to create room. Room name may already exist.")
    
    st.subheader("Delete Room")
    with st.form(key="delete_room_form"):
        room_to_delete = st.selectbox("Select Room to Delete", st.session_state.rooms)
        confirm_delete = st.checkbox("Confirm deletion (this will also delete all messages in the room)")
        delete_room_button = st.form_submit_button("Delete Room")
        
        if delete_room_button and room_to_delete and confirm_delete:
            if db_manager.delete_room(room_to_delete):
                st.success(f"Room {room_to_delete} deleted successfully!")
                # Refresh rooms list
                st.session_state.rooms = db_manager.get_user_rooms(st.session_state.user_data['username'])
            else:
                st.error(f"Failed to delete room {room_to_delete}.")
    
    # Database management section
    st.header("Database Management")
    
    st.info("Automatic message cleanup runs daily to remove messages older than 3 days.")
    
    if st.button("Run Manual Cleanup Now"):
        deleted_count = db_manager.cleanup_old_messages()
        st.success(f"Manual cleanup completed. {deleted_count} old messages deleted.")

def terminal_interface():
    """Display the main terminal interface."""
    # Header
    st.title(f"TCA v2.0 - User: {st.session_state.user_data['username']}")
    if st.session_state.user_data.get('role') == 'admin':
        st.caption("🛡️ Administrator Mode")
    
    # Display current context
    if st.session_state.current_room:
        st.caption(f"📍 Room: {st.session_state.current_room}")
    elif st.session_state.direct_message_target:
        st.caption(f"👤 Direct Message: {st.session_state.direct_message_target}")
    else:
        st.caption("💬 Lobby - Not in any room or DM")
    
    # Display messages in terminal format
    message_container = st.container()
    
    with message_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                st.text(f"[{message['timestamp']}] {message['username']}: {message['content']}")
        else:
            st.text("System: Welcome to TCA v2.0!")
            st.text("Type /help for available commands or start chatting!")
    
    # Show contextual command suggestions
    show_command_suggestions()
    
    # Command input
    with st.form(key="command_form", clear_on_submit=True):
        command_input = st.text_input("Enter command or message:", key="command_input")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and command_input.strip():
            process_command(command_input.strip())

def main():
    """Main application function."""
    st.set_page_config(
        page_title="TCA v2.0",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom CSS to make it look more terminal-like
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: #00ff00;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        .stTextInput > div > div > input {
            font-family: monospace;
            background-color: #2d2d2d;
            color: #00ff00;
        }
        .stTextArea > div > div > textarea {
            font-family: monospace;
            background-color: #2d2d2d;
            color: #00ff00;
        }
        .stSelectbox > div > div {
            font-family: monospace;
            background-color: #2d2d2d;
            color: #00ff00;
        }
        .stButton > button {
            font-family: monospace;
            background-color: #2d2d2d;
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        .stTabs > div > div {
            font-family: monospace;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00ff00;
        }
        .stAlert {
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Show admin panel for admin users only
        if st.session_state.user_data.get('role') == 'admin':
            # Single page with all admin functions
            admin_panel()
            st.markdown("---")
        
        # Always show terminal interface
        terminal_interface()

if __name__ == "__main__":
    main()