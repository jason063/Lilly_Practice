
# import socket
# import json

# HOST = "127.0.0.1"
# PORT = 9009

# def generate_llm_reply(user_text: str) -> str:
#     # TODO: Replace with Azure AI Foundry call
#     return f"LLM says: {user_text[::-1]}"  # demo: reverse text

# def recv_lines(conn):
#     """Yield newline-delimited lines from a TCP socket."""
#     buffer = b""
#     while True:
#         chunk = conn.recv(4096)
#         if not chunk:
#             return
#         buffer += chunk
#         while b"\n" in buffer:
#             line, buffer = buffer.split(b"\n", 1)
#             if line.strip():
#                 yield line.decode("utf-8", errors="replace")

# def main():
#     # Raw TCP server using Python socket module
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
#         server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         server.bind((HOST, PORT))
#         server.listen(5)
#         print(f"[TCP] Listening on {HOST}:{PORT}")

#         while True:
#             conn, addr = server.accept()
#             print(f"[TCP] Client connected: {addr}")
#             with conn:
#                 try:
#                     for line in recv_lines(conn):
#                         msg = json.loads(line)
#                         if msg.get("type") == "user":
#                             request_id = msg.get("id")
#                             text = msg.get("text", "")
#                             reply_text = generate_llm_reply(text)

#                             out = {
#                                 "type": "bot",
#                                 "id": request_id,
#                                 "text": reply_text
#                             }
#                             conn.sendall((json.dumps(out) + "\n").encode("utf-8"))
#                 except Exception as e:
#                     print("[TCP] Error:", e)

# if __name__ == "__main__":
#     main()




import re
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from flask import Flask, jsonify, request, redirect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError, DuplicateKeyError,CollectionInvalid

# ----------------------------
# Logging Setup
# ----------------------------
NAME_REGEX = re.compile(r"^[A-Za-z ]+$")
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NUMBER_REGEX = re.compile(r"^[0-9]+$")


VALID_ROLES = {"user", "assistant", "system"}
VALID_STATUS = {"active", "ended"}



def setup_logger():
    logger = logging.getLogger("bot_api")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers in reload mode
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    file_handler = RotatingFileHandler("bot_api.log", maxBytes=2_000_000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger()



def utcnow():
    return datetime.now(timezone.utc)

def parse_iso_dt(value, default_to_now=False):
    """
    Parses ISO-8601 timestamps like '2025-12-30T11:35:00Z'.
    Returns a timezone-aware UTC datetime.
    """
    if value is None:
        return utcnow() if default_to_now else None
    if isinstance(value, datetime):
        # Make sure it's UTC-aware
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        # Allow 'Z' at end
        if isinstance(value, str) and value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value) if isinstance(value, str) else value
        return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return utcnow() if default_to_now else None


# ----------------------------
# Validation helpers
# ----------------------------


def validate_login_payload(user_name: str, user_email: str):
    """
    Returns (is_valid: bool, message: str)
    """
    if not user_name or not user_email:
        return False, "user_name and user_email are required"

    if not NAME_REGEX.match(user_name):
        return False, "user_name must contain only alphabets and spaces"

    if not EMAIL_REGEX.match(user_email):
        return False, "user_email must be a valid email"

    return True, ""


# ----------------------------
# DAO Layer
# ----------------------------
class UserDao:
    def __init__(self):
        try:
            self.client = MongoClient(
                uri="mongodb+srv://cluster0.2lydxwr.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&appName=Cluster0",
                tls=True,
                tlsCertificateKeyFile="/content/X509-cert-8170842190196660167.pem",
                server_api=ServerApi("1")
            )
            self.db = self.client["Music"]
            self.collection = self.db["users"]

            # optional: ensure schema validation exists
            # self._ensure_users_collection_validator()

            # optional: indexes (recommended)
            #self.collection.create_index("user_email", unique=True)

            logger.info("MongoDB connection initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize MongoDB client.")
            raise

    # def _ensure_users_collection_validator(self):
    #     """
    #     Creates collection with schema validation if not exists.
    #     If exists, it will just pass.
    #     """
    #     try:
    #         self.db.create_collection(
    #             "users",
    #             validator={
    #                 "$jsonSchema": {
    #                     "bsonType": "object",
    #                     "required": ["user_name", "user_email", "user_number"],
    #                     "properties": {
    #                         "user_name": {
    #                             "bsonType": "string",
    #                             "pattern": "^[A-Za-z ]+$",
    #                             "description": "Only alphabetic characters allowed"
    #                         },
    #                         "user_email": {
    #                             "bsonType": "string",
    #                             "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
    #                             "description": "Must be a valid email"
    #                         },
    #                         "user_number": {
    #                             "bsonType": "string",
    #                             "pattern": "^[0-9]+$",
    #                             "description": "Only numbers allowed"
    #                         }
    #                     }
    #                 }
    #             }
    #         )
    #         logger.info("Collection 'users' created with validator.")
    #     except CollectionInvalid:
    #         logger.info("Collection 'users' already exists; validator assumed present.")
    #     except PyMongoError:
    #         logger.exception("Error while ensuring collection validator.")
    #         # Do not raise necessarily; depends on your strictness
    #         raise

    def check_user(self, user_name: str, user_email: str) -> bool:
        """
        True only if BOTH match in DB.
        """
        try:
            user_email = user_email.strip().lower()
            user_name = user_name.strip()

            result = self.collection.find_one(
                {"user_name": user_name, "user_email": user_email},
                {"_id": 1}
            )
            return result is not None
        except PyMongoError:
            logger.exception("DB error while checking user.")
            raise

    def add_user(self, user_name, user_email, user_number):
        """
        Optional: for onboarding / admin usage only
        """
        try:
            user = {
                "user_name": user_name.strip(),
                "user_email": user_email.strip().lower(),
                "user_number": user_number.strip()
            }
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
        except PyMongoError:
            logger.exception("DB error while inserting user.")
            raise


class SessionDao:
    def __init__(self, logger):
        try:
            # IMPORTANT: Use '&' not HTML-escaped '&amp;'
            self.client = MongoClient(
                uri="mongodb+srv://cluster0.2lydxwr.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&appName=Cluster0",
                tls=True,
                tlsCertificateKeyFile="/content/X509-cert-8170842190196660167.pem",
                server_api=ServerApi("1")
            )
            # Use ChatDB and chat_sessions
            self.db = self.client["ChatDB"]
            self.collection = self.db["chat_sessions"]

            # Ensure validator/indexes exist (idempotent)
            self._ensure_chat_sessions_collection_validator()
            self._ensure_indexes()

            logger.info("MongoDB ChatDB.chat_sessions connection initialized successfully.")
        except Exception:
            logger.exception("Failed to initialize MongoDB client for sessions.")
            raise

    # def _ensure_chat_sessions_collection_validator(self):
    #     schema = {
    #         "bsonType": "object",
    #         "required": ["user_email", "user_name", "user_number", "session_id", "messages", "status", "started_at"],
    #         "properties": {
    #             "user_email": {
    #                 "bsonType": "string",
    #                 "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    #             },
    #             "user_name": {
    #                 "bsonType": "string",
    #                 "pattern": "^[A-Za-z ]+$"
    #             },
    #             "user_number": {
    #                 "bsonType": "string",
    #                 "pattern": "^[0-9]+$"
    #             },
    #             "session_id": {"bsonType": "string"},
    #             "messages": {
    #                 "bsonType": "array",
    #                 "items": {
    #                     "bsonType": "object",
    #                     "required": ["role", "content", "timestamp"],
    #                     "properties": {
    #                         "role": {"enum": ["user", "assistant", "system"]},
    #                         "content": {"bsonType": "string"},
    #                         "timestamp": {"bsonType": "date"}
    #                     }
    #                 }
    #             },
    #             "final_response": {
    #                 "bsonType": "object",
    #                 "required": ["content", "timestamp"],
    #                 "properties": {
    #                     "content": {"bsonType": "string"},
    #                     "timestamp": {"bsonType": "date"}
    #                 }
    #             },
    #             "feedback": {
    #                 "bsonType": "object",
    #                 "properties": {
    #                     "submitted": {"bsonType": "bool"},
    #                     "value": {"enum": ["yes", "no"]},
    #                     "submitted_at": {"bsonType": "date"}
    #                 }
    #             },
    #             "status": {"enum": ["active", "ended"]},
    #             "started_at": {"bsonType": "date"},
    #             "ended_at": {"bsonType": "date"},
    #             "meta": {"bsonType": "object", "additionalProperties": True}
    #         },
    #         "additionalProperties": True
    #     }

    #     try:
    #         self.db.create_collection("chat_sessions", validator={"$jsonSchema": schema})
    #     except CollectionInvalid:
    #         # Already exists; we assume validator present.
    #         pass

    # def _ensure_indexes(self):
    #     try:
    #         self.collection.create_index([("session_id", 1)], unique=True)
    #         self.collection.create_index([("user_email", 1), ("user_number", 1), ("started_at", -1)])
    #         self.collection.create_index([("status", 1), ("ended_at", -1)])
    #     except PyMongoError:
    #         # Index creation errors should be logged but not fatal for inserts
    #         pass

    def _validate_session_payload(self, payload: dict):
        """
        Returns (is_valid: bool, message: str)
        Performs basic application-level validation before DB insert.
        """
        if not isinstance(payload, dict):
            return False, "Payload must be a JSON object"

        user_email = (payload.get("user_email") or "").strip().lower()
        user_name = (payload.get("user_name") or "").strip()
        user_number = (payload.get("user_number") or "").strip()
        session_id = (payload.get("session_id") or "").strip()
        status = (payload.get("status") or "").strip().lower()
        messages = payload.get("messages") or []

        if not user_email or not EMAIL_REGEX.match(user_email):
            return False, "user_email is required and must be valid"
        if not user_name or not NAME_REGEX.match(user_name):
            return False, "user_name is required and must contain only alphabets and spaces"
        if not user_number or not NUMBER_REGEX.match(user_number):
            return False, "user_number is required and must contain only digits"
        if not session_id:
            return False, "session_id is required"
        if status not in VALID_STATUS:
            return False, "status must be 'active' or 'ended'"
        if not isinstance(messages, list) or len(messages) == 0:
            return False, "messages must be a non-empty array"

        for m in messages:
            if not isinstance(m, dict):
                return False, "Each message must be an object"
            role = m.get("role")
            content = m.get("content")
            timestamp = m.get("timestamp")
            if role not in VALID_ROLES:
                return False, "message.role must be one of user|assistant|system"
            if not content or not isinstance(content, str):
                return False, "message.content must be a non-empty string"
            # timestamp may be ISO string; DB schema enforces date type. We'll convert later.

        # Optional blocks validation
        feedback = payload.get("feedback")
        if feedback:
            val = feedback.get("value")
            submitted = feedback.get("submitted")
            if submitted not in (True, False):
                return False, "feedback.submitted must be boolean"
            if val is not None and val not in ("yes", "no"):
                return False, "feedback.value must be 'yes' or 'no'"

        final_response = payload.get("final_response")
        if status == "ended" and not final_response:
            return False, "final_response is required when status is 'ended'"

        return True, ""

    def add_session_history(self, session_payload: dict) -> str:
        """
        Validates and inserts a complete chat session document into chat_sessions.
        Converts any ISO strings to proper UTC datetimes.
        Returns inserted_id as a string.
        """
        is_valid, msg = self._validate_session_payload(session_payload)
        if not is_valid:
            raise ValueError(msg)

        # Normalize fields
        doc = {}
        doc["user_email"] = session_payload["user_email"].strip().lower()
        doc["user_name"] = session_payload["user_name"].strip()
        doc["user_number"] = session_payload["user_number"].strip()
        doc["session_id"] = session_payload["session_id"].strip()
        doc["status"] = session_payload["status"].strip().lower()

        # Dates
        doc["started_at"] = parse_iso_dt(session_payload.get("started_at"), default_to_now=True)
        doc["ended_at"] = parse_iso_dt(session_payload.get("ended_at")) if doc["status"] == "ended" else None

        # Meta (optional)
        doc["meta"] = session_payload.get("meta") or {}

        # Messages → coerce timestamps to datetime
        messages = []
        for m in session_payload.get("messages", []):
            messages.append({
                "role": m["role"],
                "content": m["content"],
                "timestamp": parse_iso_dt(m.get("timestamp"), default_to_now=True)
            })
        doc["messages"] = messages

        # final_response (optional unless status=ended)
        fr = session_payload.get("final_response")
        if fr:
            doc["final_response"] = {
                "content": fr["content"],
                "timestamp": parse_iso_dt(fr.get("timestamp"), default_to_now=True)
            }

        # feedback (optional)
        fb = session_payload.get("feedback")
        if fb:
            # Only set submitted_at when submitted true
            submitted_at = parse_iso_dt(fb.get("submitted_at"), default_to_now=True) if fb.get("submitted") else None
            # Build feedback subdoc
            doc["feedback"] = {
                "submitted": bool(fb.get("submitted", False)),
                "value": fb.get("value") if fb.get("value") in ("yes", "no") else None,
                "submitted_at": submitted_at
            }

        # If status=ended and ended_at missing, set now
        if doc["status"] == "ended" and not doc.get("ended_at"):
            doc["ended_at"] = utcnow()

        # Insert
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)



# ----------------------------
# Flask App
# ----------------------------
flask_app = Flask(__name__)
userDao = UserDao()
sessionDao=SessionDao()

BOT_URL = "https://your-bot-url"  # put your bot url here

@flask_app.route("/insert_session", methods=["POST"])
def insert_session():
    data = request.get_json(silent=True


@flask_app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        user_name = (data.get("user_name") or "").strip()
        user_email = (data.get("user_email") or "").strip().lower()

        is_valid, msg = validate_login_payload(user_name, user_email)
        if not is_valid:
            logger.info(f"Login validation failed: {msg}")
            return jsonify({"status": "bad request", "message": msg}), 400

        if userDao.check_user(user_name, user_email):
            logger.info(f"Login success for: {user_email}")
            # Option 1: return url and client redirects
            #return jsonify({"status": "logged in", "bot_url": BOT_URL}), 200

            # Option 2: redirect directly
            return redirect(BOT_URL, code=302)

        logger.warning(f"Login failed for: {user_email}")
        return jsonify({"status": "login failed"}), 401

    except PyMongoError:
        # DB error
        return jsonify({"status": "error", "message": "Database error"}), 500
    except Exception:
        logger.exception("Unexpected error in /login")
        return jsonify({"status": "error", "message": "Internal server error"}), 500



@flask_app.route("/add_user", methods=["POST"])
def add_user():
    try:
        # Ensure request is JSON
        if not request.is_json:
            return jsonify({
                "status": "bad request",
                "message": "Content-Type must be application/json"
            }), 400

        data = request.get_json(silent=True) or {}

        # Read values dynamically from JSON body
        user_name = (data.get("user_name") or "").strip()
        user_email = (data.get("user_email") or "").strip().lower()
        user_number = (data.get("user_number") or "").strip()

        # Validate name + email using existing helper
        is_valid, msg = validate_login_payload(user_name, user_email)
        if not is_valid:
            logger.info(f"Add user validation failed: {msg}")
            return jsonify({"status": "bad request", "message": msg}), 400

        # Validate phone/number
        if not user_number:
            return jsonify({"status": "bad request", "message": "user_number is required"}), 400

        if not NUMBER_REGEX.match(user_number):
            return jsonify({"status": "bad request", "message": "user_number must contain only digits"}), 400

        # Insert document
        inserted_id = userDao.add_user(user_name, user_email, user_number)

        logger.info(f"User created successfully: {user_email}")
        return jsonify({
            "status": "created",
            "inserted_id": str(inserted_id)  # IMPORTANT: convert ObjectId to string
        }), 201

    except DuplicateKeyError:
        logger.warning(f"User already exists (duplicate email): {data}")
        return jsonify({"status": "conflict", "message": "user_email already exists"}), 409

    except PyMongoError:
        logger.exception("Database error in /add_user")
        return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception:
        logger.exception("Unexpected error in /add_user")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@flask_app.route("/insert_session", methods=["POST"])
def insert_session():
    """
    Inserts a chat session document into ChatDB.chat_sessions.
    Validates payload using SessionDao._validate_session_payload before insert.
    Expects JSON body with fields:
      - user_email, user_name, user_number (strings)
      - session_id (string, unique per session)
      - messages: [{role: 'user'|'assistant'|'system', content: str, timestamp: ISO8601 or date}]
      - status: 'active'|'ended'
      - started_at: ISO8601 (optional; default now)
      - ended_at: ISO8601 (required if status='ended'; else optional)
      - final_response: {content, timestamp} (required if status='ended')
      - feedback: {submitted: bool, value: 'yes'|'no', submitted_at} (optional)
      - meta: object (optional)
    """
    try:
        # Ensure JSON
        if not request.is_json:
            return jsonify({
                "status": "bad request",
                "message": "Content-Type must be application/json"
            }), 400

        # Parse payload
        data = request.get_json(silent=True) or {}

        # Validate using DAO's validator (pre-checks before insert)
        is_valid, msg = sessionDao._validate_session_payload(data)
        if not is_valid:
            logger.info(f"/insert_session validation failed: {msg}")
            return jsonify({"status": "bad request", "message": msg}), 400

        # Insert (add_session_history also normalizes timestamps to UTC datetimes)
        inserted_id = sessionDao.add_session_history(data)
        logger.info(f"/insert_session success: inserted_id={inserted_id}")

        return jsonify({
            "status": "created",
            "inserted_id": inserted_id
        }), 201

    except DuplicateKeyError:
        # session_id is unique-indexed
        logger.warning("/insert_session duplicate session_id")
        return jsonify({"status": "conflict", "message": "session_id already exists"}), 409

    except ValueError as ve:
        # Any additional validation errors raised by DAO
        logger.info(f"/insert_session validation error: {ve}")
        return jsonify({"status": "bad request", "message": str(ve)}), 400

    except PyMongoError:
        logger.exception("/insert_session database error")
        return jsonify({"status": "error", "message": "Database error"}), 500

    except Exception:
        logger.exception("/insert_session unexpected error")
        return jsonify({"status": "error", "message": "Internal server error"}), 500



@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
