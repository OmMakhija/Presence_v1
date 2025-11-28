import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import db

def init_database():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

if __name__ == '__main__':
    init_database()
