"""
In-memory database configuration and setup for Mergington High School API
"""

from argon2 import PasswordHasher, exceptions as argon2_exceptions
from typing import Dict, List, Any, Optional

# In-memory database
_activities_db: List[Dict[str, Any]] = []
_teachers_db: Dict[str, Dict[str, Any]] = {}

# Mock collection classes to mimic MongoDB interface
class InMemoryCollection:
    def __init__(self, data_store):
        self.data_store = data_store
    
    def find(self, query: Optional[Dict] = None):
        if query is None:
            query = {}
        results = []
        for item in self.data_store if isinstance(self.data_store, list) else self.data_store.values():
            if self._matches(item, query):
                results.append(item)
        return results
    
    def find_one(self, query: Dict):
        if "_id" in query:
            if isinstance(self.data_store, dict):
                return self.data_store.get(query["_id"])
            else:
                for item in self.data_store:
                    if item.get("_id") == query["_id"]:
                        return item
        for item in self.data_store if isinstance(self.data_store, list) else self.data_store.values():
            if self._matches(item, query):
                return item
        return None
    
    def insert_one(self, document: Dict):
        if isinstance(self.data_store, list):
            self.data_store.append(document)
        else:
            self.data_store[document["_id"]] = document
        return type('InsertResult', (), {'inserted_id': document.get("_id")})()
    
    def insert_many(self, documents: List[Dict]):
        for doc in documents:
            self.insert_one(doc)
    
    def update_one(self, query: Dict, update: Dict):
        item = self.find_one(query)
        if item:
            if "$set" in update:
                item.update(update["$set"])
            if "$push" in update:
                for key, value in update["$push"].items():
                    if key not in item:
                        item[key] = []
                    item[key].append(value)
    
    def count_documents(self, query: Dict):
        return len(self.find(query))
    
    def _matches(self, item: Dict, query: Dict) -> bool:
        if not query:
            return True
        for key, value in query.items():
            if key.startswith("$"):
                continue
            if isinstance(value, dict):
                if "$in" in value:
                    item_value = item.get(key)
                    if isinstance(item_value, list):
                        if not any(v in item_value for v in value["$in"]):
                            return False
                    elif item_value not in value["$in"]:
                        return False
                elif "$gte" in value:
                    if item.get(key, "") < value["$gte"]:
                        return False
                elif "$lte" in value:
                    if item.get(key, "") > value["$lte"]:
                        return False
            elif item.get(key) != value:
                return False
        return True

activities_collection = InMemoryCollection(_activities_db)
teachers_collection = InMemoryCollection(_teachers_db)

# Methods


def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Verify a plain password against an Argon2 hashed password.

    Returns True when the password matches, False otherwise.
    """
    ph = PasswordHasher()
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2_exceptions.VerifyMismatchError:
        return False
    except Exception:
        # For any other exception (e.g., invalid hash), treat as non-match
        return False


def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})

    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one(
                {"_id": teacher["username"], **teacher})
    
    # Initialize announcements if empty
    if announcements_collection.count_documents({}) == 0:
        for announcement in initial_announcements:
            announcements_collection.insert_one(announcement)


# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
    },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

initial_announcements = [
    {
        "title": "Spring Activities Fair",
        "message": "Join us for the Spring Activities Fair on March 15th! Explore all available clubs and sign up for your favorites. Free refreshments will be provided!",
        "start_date": "2026-03-01",
        "expiration_date": "2026-03-15",
        "created_by": "principal"
    },
    {
        "title": "Welcome Back Students!",
        "message": "We're excited to have you back for the new semester. Check out our updated activity schedule and join something new today!",
        "start_date": None,
        "expiration_date": "2026-02-28",
        "created_by": "principal"
    }
]
