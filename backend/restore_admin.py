from database import SessionLocal
import models

def restore_admin():
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if admin:
            admin.role = "admin"
            db.commit()
            print("Admin privileges restored.")
        else:
            print("Admin user not found.")
    finally:
        db.close()

if __name__ == "__main__":
    restore_admin()
