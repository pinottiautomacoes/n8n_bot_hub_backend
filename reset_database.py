"""
Database RESET script - DROPS ALL TABLES and RECREATES them
WARNING: THIS WILL DELETE ALL DATA
"""
from app.core.database import engine, Base
from app.models.user import User
from app.models.bot import Bot
from app.models.business_hour import BusinessHour
from app.models.contact import Contact
from app.models.appointment import Appointment

def reset_database():
    """Drop and recreate all tables"""
    print("WARNING: This will DROP ALL TABLES and DELETE ALL DATA!")
    print("Starting database reset...")
    try:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped.")
        
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully!")
        
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        raise


if __name__ == "__main__":
    reset_database()
