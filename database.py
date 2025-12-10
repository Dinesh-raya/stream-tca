import streamlit as st
import bcrypt
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client

class DatabaseManager:
    """Manages database connections and operations for the TCA application using Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase: Client = None
        self.connect()
    
    def connect(self):
        """Connect to Supabase database using Streamlit secrets."""
        try:
            # Use Streamlit secrets instead of environment variables
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            if url and key:
                self.supabase = create_client(url, key)
            else:
                print("Supabase credentials not found in Streamlit secrets")
        except Exception as e:
            print(f"Supabase connection error: {e}")
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user in the database."""
        try:
            # Check if user already exists
            existing_user = self.supabase.table("users").select("*").eq("username", username).execute()
            if existing_user.data:
                return False  # User already exists
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_data = {
                "username": username,
                "password": hashed_password.decode('utf-8'),
                "role": role,
                "created_at": datetime.utcnow().isoformat()
            }
            self.supabase.table("users").insert(user_data).execute()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return user data if successful."""
        try:
            response = self.supabase.table("users").select("*").eq("username", username).execute()
            if response.data:
                user = response.data[0]
                if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                    # Return user data without password
                    user_data = user.copy()
                    del user_data["password"]
                    return user_data
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_rooms(self, username: str) -> List[str]:
        """Get list of rooms the user has access to."""
        try:
            # Get all rooms where user is in allowed_users or room is public
            response = self.supabase.table("rooms").select("name, allowed_users, is_public").execute()
            user_rooms = []
            
            for room in response.data:
                if room.get("is_public", False) or username in room.get("allowed_users", []):
                    user_rooms.append(room["name"])
                    
            return user_rooms
        except Exception as e:
            print(f"Error fetching user rooms: {e}")
            return []
    
    def get_room_messages(self, room_name: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a room."""
        try:
            response = (self.supabase.table("messages")
                       .select("*")
                       .eq("room", room_name)
                       .order("timestamp", desc=True)
                       .limit(limit)
                       .execute())
            return response.data
        except Exception as e:
            print(f"Error fetching room messages: {e}")
            return []
    
    def save_message(self, room: str, username: str, content: str) -> bool:
        """Save a message to the database."""
        try:
            message_data = {
                "room": room,
                "username": username,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.supabase.table("messages").insert(message_data).execute()
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def create_room(self, room_name: str, allowed_users: List[str] = None, is_public: bool = False) -> bool:
        """Create a new room."""
        try:
            # Check if room already exists
            existing_room = self.supabase.table("rooms").select("*").eq("name", room_name).execute()
            if existing_room.data:
                return False  # Room already exists
                
            room_data = {
                "name": room_name,
                "allowed_users": allowed_users or [],
                "is_public": is_public,
                "created_at": datetime.utcnow().isoformat()
            }
            self.supabase.table("rooms").insert(room_data).execute()
            return True
        except Exception as e:
            print(f"Error creating room: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()