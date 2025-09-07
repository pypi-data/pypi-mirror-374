from .database import block_db
from datetime import datetime

def show_blocked_users():
    users = block_db.get_blocked_users()
    print("Blocked users:")
    for user in users:
        user_id, reason, timestamp, expires_at, permanent = user
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        status = "PERMANENT" if permanent else f"expires: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"ID: {user_id}, Reason: {reason}, Date: {date}, {status}")

def unblock_user(user_id):
    block_db.remove_block(user_id)
    print(f"User {user_id} unblocked")

def cleanup_blocks():
    block_db.cleanup_expired()
    print("Expired blocks cleaned up")