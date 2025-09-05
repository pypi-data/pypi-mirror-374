from typing import Optional
from datetime import datetime
from fasthtml_auth.models import User

class UserRepository:
    """Handles all database operations for users"""
    def __init__(self, db):
        self.db = db
        self.users = db.t.user

    def _dict_to_user(self, user_dict) -> User:
        """Convert dictionary from database to User object"""
        if isinstance(user_dict, User):
            return user_dict
        
        return User(
            id=user_dict.get('id'),
            username=user_dict['username'],
            email=user_dict['email'],
            password=user_dict['password'],
            role=user_dict.get('role', 'user'),
            created_at=user_dict.get('created_at', ''),
            last_login=user_dict.get('last_login', ''),
            active=user_dict.get('active', True)
        )        
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username using parameterized query"""
        try:
            user_found = self.users("username=?", (username,))
            if len(user_found) == 1:
                if isinstance(user_found[0], User):
                    return user_found[0]
                else:
                    return self._dict_to_user(user_found[0])
                return user_found[0]  # Return the single user object
            elif len(user_found) == 0:
                return None
            else:
                raise Exception(f"Multiple users found with username: {username}")
        except Exception as e:
            print(f"Error in get_by_username: {e}")
            return None
        
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user_dict = self.users[user_id]
            if user_dict:
                return self._dict_to_user(user_dict)
            return None
        except Exception as e:
            print(f"Error in get_by_id: {e}")
            return None
    
    def create(self, username: str, email: str, password: str, role: str = "user") -> User:
        """Create new user.  Note that the dates will be updated by the class -_post_init__ method """
        user = User(
            username=username,
            email=email,
            password=password,  # Use static method
            role=role,
            active=True,
            created_at="",
            last_login=""
        )
        inserted_user = self.users.insert(user)
        if isinstance(inserted_user, dict):
            return self._dict_to_user(inserted_user)
        else:
            return inserted_user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and update last_login"""
        user = self.get_by_username(username)
        print(f"User: {user}")
        if user and user.active and User.verify_password(password, user.password):
            # Update last_login using the new fastlite approach
            from datetime import datetime
            now = datetime.now().isoformat()
            self.users.update(last_login=now, id=user.id)
            return user
        return None
    
    def update(self, user_id: int, **kwargs) -> bool:
        """Update user fields using fastlite kwargs approach"""
        try:
            # Hash password if being updated                    # <- NEW
            if 'password' in kwargs and kwargs['password']:     # <- NEW
                if not User.is_hashed(kwargs['password']):      # <- NEW
                    kwargs['password'] = User.get_hashed_password(kwargs['password'])  # <- NEW
            
            # Include the primary key in the update kwargs
            self.users.update(id=user_id, **kwargs)
            return True
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return False
    
    def list_all(self) -> list[User]:
        """Get all users"""
        try:
            users = []
            for user_dict in self.users():
                users.append(self._dict_to_user(user_dict))
            return users
        except Exception as e:
            print(f"Error listing users: {e}")
            return []
        
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash - delegates to User class"""
        return User.verify_password(password, hashed)