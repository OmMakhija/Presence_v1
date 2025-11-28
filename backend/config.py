import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///presence.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Face Recognition Settings
    FACE_MATCH_THRESHOLD = float(os.getenv('FACE_MATCH_THRESHOLD', 0.6))
    FACE_CAPTURE_DURATION = int(os.getenv('FACE_CAPTURE_DURATION', 10))
    FACE_CAPTURE_FPS = int(os.getenv('FACE_CAPTURE_FPS', 10))

    # BLE Settings
    BLE_RSSI_THRESHOLD = int(os.getenv('BLE_RSSI_THRESHOLD', -70))

    # SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')

    # Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
