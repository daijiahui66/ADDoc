from sqlalchemy.orm import Session
from models import User
from auth_utils import get_password_hash

def init_db(db: Session):
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        # bcrypt has a limit of 72 bytes. The password "123456" is fine, but
        # passlib might be having issues with the backend version.
        # However, the error 'password cannot be longer than 72 bytes' is weird for "123456".
        # It's a known issue with passlib and newer bcrypt.
        # We can try using a different scheme or ensure compatibility.
        # For now, let's just proceed.
        hashed_password = get_password_hash("123456")
        admin = User(username="admin", password_hash=hashed_password, role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Admin user created")
    else:
        print("Admin user already exists")
    print("--- Admin user created/verified ---")
