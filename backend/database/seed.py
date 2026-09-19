from database.database import SessionLocal
from models.hospital import Hospital
from models.user import User
from core.security import hash_password
from auth.roles import UserRole


def seed_users():
    db = SessionLocal()

    try:
        hospital = db.query(Hospital).filter(
            Hospital.id == 1
        ).first()

        if not hospital:
            print("Hospital with ID 1 not found.")
            return

        existing_user = db.query(User).filter(
            User.email == "campaign@apollo-demo.com"
        ).first()

        if existing_user:
            print("Campaign Manager already exists.")
            return

        user = User(
            hospital_id=hospital.id,
            email="campaign@apollo-demo.com",
            full_name="Campaign Manager",
            password_hash=hash_password("Campaign@12345"),
            role=UserRole.CAMPAIGN_MANAGER.value,
            is_active=True
        )

        db.add(user)
        db.commit()

        print("Campaign Manager created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()