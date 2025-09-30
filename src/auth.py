import os  # used to build file paths
import json  # used to read and write small local data files
import uuid  # used to make a simple random token
from typing import Optional, Dict, Any  # type hints for clarity
from settings import ASSETS_DIR  # base assets directory from settings


class AuthContext:
    """Local auth manager with multi-user storage in a single JSON file.

    File schema ex. (user.json):
    {
      "current_user": "alice" | "",
      "users": {
        "alice": {"token": "...", "pfp_path": "...", "high_score": 0},
        "bob": {"token": "...", "pfp_path": "...", "high_score": 0}
      }
    }
    """

    def __init__(self):
        # path to json file holding all users and the active user
        self.user_file_path = os.path.join(ASSETS_DIR, "user.json")
        # in-memory model matching the schema above
        self._store: Dict[str, Any] = {"current_user": "", "users": {}}
        # load existing user info if present
        self._load_user()

    def _load_user(self) -> None:
        # Read user.json if it exists; otherwise initialize an empty store
        if os.path.exists(self.user_file_path):
            try:
                with open(self.user_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Get the current user
                cu = data.get("current_user", "")
                # Get the users dictionary
                users = data.get("users", {})
                # If the users dictionary is not a dictionary, set it to an empty dictionary
                if not isinstance(users, dict):
                    users = {}
                # Set the store to the current user and users dictionary
                self._store = {"current_user": cu if isinstance(cu, str) else "", "users": users}
            except Exception:
                # If the user.json file is not valid, set the store to an empty dictionary
                self._store = {"current_user": "", "users": {}}
        else:
            self._store = {"current_user": "", "users": {}}

    def _save_user(self) -> None:
        # write current store to user.json (creates/overwrites)
        try:
            with open(self.user_file_path, "w", encoding="utf-8") as f:
                json.dump(self._store, f)
        except Exception:
            pass

    def is_logged_in(self) -> bool:
        # user is logged in if current_user exists and has a non-empty token
        cu = self._store.get("current_user") or ""
        users = self._store.get("users", {})
        if cu and isinstance(users, dict):
            rec = users.get(cu) or {}
            return bool(rec.get("token"))
        return False

    def get_username(self) -> Optional[str]:
        cu = self._store.get("current_user") or ""
        return cu or None

    def get_token(self) -> Optional[str]:
        cu = self._store.get("current_user") or ""
        users = self._store.get("users", {})
        if cu and isinstance(users, dict):
            rec = users.get(cu) or {}
            tok = rec.get("token")
            return tok if tok else None
        return None

    def get_pfp_path(self) -> Optional[str]:
        cu = self._store.get("current_user") or ""
        users = self._store.get("users", {})
        if cu and isinstance(users, dict):
            rec = users.get(cu) or {}
            p = rec.get("pfp_path") or ""
            return p if p else None
        return None

    def set_pfp_path(self, path: str) -> None:
        cu = self._store.get("current_user") or ""
        if not cu:
            return
        users = self._store.setdefault("users", {})
        rec = users.setdefault(cu, {"token": "", "pfp_path": "", "high_score": 0})
        rec["pfp_path"] = path
        self._save_user()

    def get_high_score(self):
        # Get the current user's high score from the store
        cu = self._store.get("current_user") or ""
        # Get the users dictionary
        users = self._store.get("users", {})
        # If the current user exists and the users dictionary is a dictionary, get the record for the current user
        if cu and isinstance(users, dict):
            # Get the record for the current user
            rec = users.get(cu) or {}
            # Get the high score from the record
            score = rec.get("high_score", 0)
            # If the high score is an integer, return it, otherwise return 0
            return score if isinstance(score, int) else 0
        return 0

    def set_high_score(self, score: int) -> bool:
        # Update high score if new score is better, returns True if it's a new high score
        cu = self._store.get("current_user") or ""
        # If the current user does not exist, return False
        if not cu:
            return False
        users = self._store.setdefault("users", {})
        # Get the record for the current user
        rec = users.setdefault(cu, {"token": "", "pfp_path": "", "high_score": 0})
        # Get the current high score from the record
        current_high = rec.get("high_score", 0)
        # If the new score is greater than the current high score, update the high score and return True
        if score > current_high:
            # Update the high score in the record
            rec["high_score"] = score
            # Save the user to the store
            self._save_user()
            return True
        return False

    def issue_token(self, username: str) -> str:
        # create or refresh the user record, set as current, and store a token
        token = uuid.uuid4().hex
        users = self._store.setdefault("users", {})
        # Create a record for the new user
        rec = users.setdefault(username, {"token": "", "pfp_path": "", "high_score": 0})
        # Set the token for the new user
        rec["token"] = token
        # Set the current user to the new user
        self._store["current_user"] = username
        # Save the user to the store
        self._save_user()
        return token

    def logout(self) -> None:
        # Clear token for the active user and unset current_user
        cu = self._store.get("current_user") or ""
        users = self._store.get("users", {})
        if cu and isinstance(users, dict):
            rec = users.get(cu) or {}
            rec["token"] = ""
        self._store["current_user"] = ""
        self._save_user()
