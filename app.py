import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from database import db_manager

# Load environment variables
load_dotenv()

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
    
if 'current_room' not in st.session_state:
    st.session_state.current_room = None
    
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'rooms' not in st.session_state:
    st.session_state.rooms = []

def login_page():
    """Display the login page."""
    st.title("Terminal Communication Array v2.0")
    st.subheader("Secure Terminal Login")
    
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
    
    # Info about demo credentials
    st.info("""
    Demo Accounts:
    - admin / admin123 (Administrator)
    - user1 / password1 (User)
    - user2 / password2 (User)
    """)

def logout():
    """Handle user logout."""
    st.session_state.logged_in = False
    st.session_state.user_data = None
    st.session_state.current_room = None
    st.session_state.messages = []
    st.session_state.rooms = []
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

def load_room_messages(room_name: str):
    """Load messages for the current room."""
    # In a real implementation, you would fetch from database
    # For now, we'll keep messages in session state
    pass

def terminal_interface():
    """Display the main terminal interface."""
    # Header with logout button
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title(f"TCA v2.0 - User: {st.session_state.user_data['username']}")
        if st.session_state.user_data.get('role') == 'admin':
            st.caption("🛡️ Administrator Mode")
    with col2:
        if st.button("Logout"):
            logout()
    
    # Room selection
    st.subheader("Select Room")
    
    if not st.session_state.rooms:
        st.warning("You don't have access to any rooms.")
        if st.session_state.user_data.get('role') == 'admin':
            st.info("As an administrator, you can create rooms in the admin panel.")
        return
    
    # Select room
    selected_room = st.selectbox(
        "Available Rooms", 
        st.session_state.rooms, 
        index=0 if st.session_state.current_room is None else st.session_state.rooms.index(st.session_state.current_room)
    )
    
    if selected_room != st.session_state.current_room:
        st.session_state.current_room = selected_room
        st.session_state.messages = []  # Clear messages when switching rooms
        load_room_messages(selected_room)
        st.experimental_rerun()
    
    # Display messages
    st.subheader(f"Room: {st.session_state.current_room}")
    
    # Message container with scrollable area
    message_container = st.container()
    
    with message_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                st.text(f"[{message['timestamp']}] {message['username']}: {message['content']}")
        else:
            st.info("No messages yet. Be the first to send a message!")
    
    # Input area
    st.subheader("Send Message")
    with st.form(key="message_form", clear_on_submit=True):
        message_input = st.text_input("Message", max_chars=500)
        submit_button = st.form_submit_button("Send")
        
        if submit_button and message_input.strip():
            if st.session_state.current_room and st.session_state.user_data:
                send_message(
                    st.session_state.current_room, 
                    st.session_state.user_data['username'], 
                    message_input.strip()
                )
                st.experimental_rerun()
    
    # Auto-refresh option
    st.checkbox("Auto-refresh messages", value=False, key="auto_refresh")
    if st.session_state.auto_refresh:
        st.experimental_rerun()

def admin_panel():
    """Display admin panel for user and room management."""
    st.title("Admin Panel")
    
    # User management tab
    user_tab, room_tab = st.tabs(["User Management", "Room Management"])
    
    with user_tab:
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
    
    with room_tab:
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
        # Show admin panel for admin users
        if st.session_state.user_data.get('role') == 'admin':
            admin_tab, chat_tab = st.tabs(["Admin Panel", "Terminal Chat"])
            with admin_tab:
                admin_panel()
            with chat_tab:
                terminal_interface()
        else:
            terminal_interface()

if __name__ == "__main__":
    main()