from datetime import datetime
from backend.models.user import db

class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # BLE Data
    ble_rssi = db.Column(db.Float)
    ble_verified = db.Column(db.Boolean, default=False)

    # Face Recognition Data
    face_confidence = db.Column(db.Float)  # Euclidean distance
    face_verified = db.Column(db.Boolean, default=False)

    # Liveness Detection
    liveness_verified = db.Column(db.Boolean, default=False)
    liveness_challenge = db.Column(db.String(100))  # Type of challenge given

    # Status
    status = db.Column(db.String(20), default='present')  # present, absent, proxy_suspected
    is_manual_override = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ble_rssi': self.ble_rssi,
            'ble_verified': self.ble_verified,
            'face_confidence': self.face_confidence,
            'face_verified': self.face_verified,
            'liveness_verified': self.liveness_verified,
            'status': self.status,
            'is_manual_override': self.is_manual_override
        }
