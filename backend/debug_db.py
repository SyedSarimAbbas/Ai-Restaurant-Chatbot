
from database import SessionLocal, engine, Base
from models import MenuItem
from main import seed_database
from sqlalchemy.orm import Session

# Create tables if not exist
Base.metadata.create_all(bind=engine)

def debug_seed():
    db = SessionLocal()
    try:
        # Check current items
        count = db.query(MenuItem).count()
        print(f"Current count: {count}")
        
        # Try seeding
        print("Attempting to seed...")
        # We can't call main.seed_database directly because it expects FastAPI dependency
        # So I'll just check if I can insert one item with ingredients
        
        try:
            item = MenuItem(
                item="Test Pizza",
                price=10.0,
                category="Pizza",
                description="Test desc",
                ingredients="Test Ingredients",
                image_url="http://test.com"
            )
            db.add(item)
            db.commit()
            print("Successfully inserted item with ingredients!")
            
            # Now try to read it back
            fetched = db.query(MenuItem).filter(MenuItem.item == "Test Pizza").first()
            print(f"Fetched ingredients: {fetched.ingredients}")
            
            # Clean up
            db.delete(fetched)
            db.commit()
            
        except Exception as e:
            print(f"Error inserting: {e}")
            db.rollback()
            
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_seed()
