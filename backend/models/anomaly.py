from datetime import datetime
from backend.models.user import db

class AnomalyLog(db.Model):
    __tablename__ = 'anomaly_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    anomaly_type = db.Column(db.String(50), nullable=False)
    # Types: 'multi_face', 'no_face', 'liveness_failed', 'rapid_attempts',
    #        'ble_failed', 'duplicate_ip', 'low_confidence'

    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    description = db.Column(db.Text)
    extra_metadata = db.Column(db.JSON)  # Store additional context (IP, face count, etc.)
    resolved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'description': self.description,
            'metadata': self.extra_metadata,
            'resolved': self.resolved
        }
