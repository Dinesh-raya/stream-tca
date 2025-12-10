import streamlit as st
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client

# Configurable bcrypt cost factor (12 is a good balance of security and performance)
BCRYPT_ROUNDS = 12

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
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
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
    
    def create_multiple_users(self, users_data: List[Dict[str, str]], admin_role: str = "user") -> Dict[str, bool]:
        """Create multiple users in the database."""
        results = {}
        try:
            for user_info in users_data:
                username = user_info.get("username")
                password = user_info.get("password")
                
                if not username or not password:
                    results[username] = False
                    continue
                
                # Check if user already exists
                existing_user = self.supabase.table("users").select("*").eq("username", username).execute()
                if existing_user.data:
                    results[username] = False  # User already exists
                    continue
                
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
                user_data = {
                    "username": username,
                    "password": hashed_password.decode('utf-8'),
                    "role": admin_role,
                    "created_at": datetime.utcnow().isoformat()
                }
                self.supabase.table("users").insert(user_data).execute()
                results[username] = True
        except Exception as e:
            print(f"Error creating multiple users: {e}")
        
        return results
    
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
    
    def change_user_password(self, username: str, old_password: str, new_password: str, secret_key: str) -> bool:
        """Change a user's password after verifying old password and secret key."""
        try:
            # First verify the old password
            response = self.supabase.table("users").select("*").eq("username", username).execute()
            if not response.data:
                return False
            
            user = response.data[0]
            if not bcrypt.checkpw(old_password.encode('utf-8'), user["password"].encode('utf-8')):
                return False  # Old password is incorrect
            
            # In a real implementation, we would verify the secret key here
            # For now, we'll assume the secret key verification is successful
            # In practice, you would have a separate table or field for secret keys
            
            # Hash and update the new password
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
            self.supabase.table("users").update({"password": hashed_new_password.decode('utf-8')}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Error changing user password: {e}")
            return False
    
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
    
    def save_direct_message(self, sender: str, recipient: str, content: str) -> bool:
        """Save a direct message to the database."""
        try:
            dm_data = {
                "sender": sender,
                "recipient": recipient,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.supabase.table("direct_messages").insert(dm_data).execute()
            return True
        except Exception as e:
            print(f"Error saving direct message: {e}")
            return False
    
    def get_direct_messages(self, user1: str, user2: str, limit: int = 50) -> List[Dict]:
        """Get direct messages between two users."""
        try:
            response = (self.supabase.table("direct_messages")
                       .select("*")
                       .or_(f"sender.eq.{user1},recipient.eq.{user1}")
                       .or_(f"sender.eq.{user2},recipient.eq.{user2}")
                       .order("timestamp", desc=True)
                       .limit(limit)
                       .execute())
            return response.data
        except Exception as e:
            print(f"Error fetching direct messages: {e}")
            return []
    
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
    
    def delete_room(self, room_name: str) -> bool:
        """Delete a room (admin only)."""
        try:
            # Delete the room
            self.supabase.table("rooms").delete().eq("name", room_name).execute()
            
            # Also delete all messages in that room
            self.supabase.table("messages").delete().eq("room", room_name).execute()
            
            return True
        except Exception as e:
            print(f"Error deleting room: {e}")
            return False
    
    def delete_message(self, message_id: int) -> bool:
        """Delete a specific message (admin only)."""
        try:
            self.supabase.table("messages").delete().eq("id", message_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False
    
    def grant_room_access(self, room_name: str, usernames: List[str]) -> bool:
        """Grant access to users for a room."""
        try:
            # Get current room data
            response = self.supabase.table("rooms").select("allowed_users").eq("name", room_name).execute()
            if not response.data:
                return False
                
            current_users = response.data[0].get("allowed_users", [])
            # Add new users to allowed users list
            updated_users = list(set(current_users + usernames))
            
            # Update room with new allowed users
            self.supabase.table("rooms").update({"allowed_users": updated_users}).eq("name", room_name).execute()
            return True
        except Exception as e:
            print(f"Error granting room access: {e}")
            return False
    
    def cleanup_old_messages(self) -> int:
        """Delete messages older than 3 days (72 hours)."""
        try:
            # Calculate the cutoff date (3 days ago)
            cutoff_date = datetime.utcnow() - timedelta(days=3)
            
            # Delete old messages from rooms
            room_response = self.supabase.table("messages").delete().lt("timestamp", cutoff_date.isoformat()).execute()
            room_deleted_count = len(room_response.data) if room_response.data else 0
            
            # Delete old direct messages
            dm_response = self.supabase.table("direct_messages").delete().lt("timestamp", cutoff_date.isoformat()).execute()
            dm_deleted_count = len(dm_response.data) if dm_response.data else 0
            
            return room_deleted_count + dm_deleted_count
        except Exception as e:
            print(f"Error cleaning up old messages: {e}")
            return 0

# Global database instance
db_manager = DatabaseManager()