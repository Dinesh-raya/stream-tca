import pymongo
import bcrypt
import os
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    """Manages database connections and operations for the TCA application."""
    
    def __init__(self):
        """Initialize database connection."""
        self.client = None
        self.db = None
        self.users_collection = None
        self.rooms_collection = None
        self.messages_collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB database."""
        try:
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/tca_db")
            self.client = pymongo.MongoClient(mongo_uri)
            self.db = self.client.tca_db
            self.users_collection = self.db.users
            self.rooms_collection = self.db.rooms
            self.messages_collection = self.db.messages
            
            # Create indexes for better performance
            self.users_collection.create_index("username", unique=True)
            self.rooms_collection.create_index("name", unique=True)
            self.messages_collection.create_index("room")
            self.messages_collection.create_index("timestamp")
            
        except Exception as e:
            print(f"Database connection error: {e}")
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user in the database."""
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_doc = {
                "username": username,
                "password": hashed_password,
                "role": role,
                "created_at": datetime.utcnow()
            }
            self.users_collection.insert_one(user_doc)
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return user data if successful."""
        try:
            user = self.users_collection.find_one({"username": username})
            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
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
            # For simplicity, we'll return all rooms for now
            # In a real implementation, you'd check user permissions
            rooms = self.rooms_collection.find()
            user_rooms = []
            for room in rooms:
                if username in room.get("allowed_users", []) or room.get("is_public", False):
                    user_rooms.append(room["name"])
            return user_rooms
        except Exception as e:
            print(f"Error fetching user rooms: {e}")
            return []
    
    def get_room_messages(self, room_name: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a room."""
        try:
            messages = self.messages_collection.find({"room": room_name}).sort("timestamp", -1).limit(limit)
            return list(messages)
        except Exception as e:
            print(f"Error fetching room messages: {e}")
            return []
    
    def save_message(self, room: str, username: str, content: str) -> bool:
        """Save a message to the database."""
        try:
            message_doc = {
                "room": room,
                "username": username,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            self.messages_collection.insert_one(message_doc)
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def create_room(self, room_name: str, allowed_users: List[str] = None, is_public: bool = False) -> bool:
        """Create a new room."""
        try:
            room_doc = {
                "name": room_name,
                "allowed_users": allowed_users or [],
                "is_public": is_public,
                "created_at": datetime.utcnow()
            }
            self.rooms_collection.insert_one(room_doc)
            return True
        except Exception as e:
            print(f"Error creating room: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()