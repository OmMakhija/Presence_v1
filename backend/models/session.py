from datetime import datetime
from backend.models.user import db

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    ble_device_id = db.Column(db.String(100))  # BLE beacon identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teacher = db.relationship('User', backref='teaching_sessions')
    attendance_logs = db.relationship('AttendanceLog', backref='session', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'teacher_id': self.teacher_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
