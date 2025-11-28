"""
Unit tests for database models
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app
from backend.models import db, User, FaceEmbedding, Session, AttendanceLog, AnomalyLog
from datetime import date, time


class TestUserModel:
    """Test User model functionality"""

    def setup_method(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def teardown_method(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_user_creation(self):
        """Test user creation and password hashing"""
        user = User(
            roll_number='TEST001',
            name='Test User',
            email='test@example.com',
            role='student'
        )
        user.set_password('testpass123')

        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.roll_number == 'TEST001'
        assert user.check_password('testpass123')
        assert not user.check_password('wrongpass')

    def test_user_to_dict(self):
        """Test user serialization"""
        user = User(
            roll_number='TEST002',
            name='Test User 2',
            email='test2@example.com',
            role='teacher'
        )

        data = user.to_dict()
        assert data['roll_number'] == 'TEST002'
        assert data['name'] == 'Test User 2'
        assert data['role'] == 'teacher'

    def test_user_relationships(self):
        """Test user relationships with other models"""
        user = User(roll_number='TEST003', name='Test User', email='test3@example.com', role='student')
        db.session.add(user)
        db.session.commit()

        # Test face embedding relationship
        embedding = FaceEmbedding(user_id=user.id, embedding=[0.1] * 128)
        db.session.add(embedding)
        db.session.commit()

        assert len(user.face_embeddings) == 1
        assert user.face_embeddings[0].embedding == [0.1] * 128


class TestSessionModel:
    """Test Session model functionality"""

    def setup_method(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test teacher
        self.teacher = User(
            roll_number='TEACHER001',
            name='Test Teacher',
            email='teacher@example.com',
            role='teacher'
        )
        db.session.add(self.teacher)
        db.session.commit()

    def teardown_method(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_session_creation(self):
        """Test session creation"""
        session = Session(
            course_code='CS101',
            course_name='Computer Science 101',
            teacher_id=self.teacher.id,
            session_date=date(2025, 1, 15),
            start_time=time(9, 0),
            end_time=time(10, 30)
        )

        db.session.add(session)
        db.session.commit()

        assert session.id is not None
        assert session.course_code == 'CS101'
        assert not session.is_active

    def test_session_to_dict(self):
        """Test session serialization"""
        session = Session(
            course_code='MATH101',
            course_name='Mathematics 101',
            teacher_id=self.teacher.id,
            session_date=date(2025, 1, 16),
            start_time=time(10, 0),
            end_time=time(11, 30),
            is_active=True
        )

        data = session.to_dict()
        assert data['course_code'] == 'MATH101'
        assert data['is_active'] == True
        assert data['start_time'] == '10:00:00'

    def test_session_relationships(self):
        """Test session relationships"""
        session = Session(
            course_code='PHY101',
            course_name='Physics 101',
            teacher_id=self.teacher.id,
            session_date=date.today(),
            start_time=time(14, 0),
            end_time=time(15, 30)
        )
        db.session.add(session)
        db.session.commit()

        # Test teacher relationship
        assert session.teacher.name == 'Test Teacher'

        # Test attendance relationship (should be empty initially)
        assert len(session.attendance_logs) == 0


class TestAttendanceLogModel:
    """Test AttendanceLog model functionality"""

    def setup_method(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test user and session
        self.user = User(roll_number='STUDENT001', name='Test Student', email='student@example.com', role='student')
        self.teacher = User(roll_number='TEACHER002', name='Test Teacher', email='teacher2@example.com', role='teacher')
        db.session.add_all([self.user, self.teacher])
        db.session.commit()

        self.session = Session(
            course_code='TEST101',
            course_name='Test Course',
            teacher_id=self.teacher.id,
            session_date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0)
        )
        db.session.add(self.session)
        db.session.commit()

    def teardown_method(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_attendance_creation(self):
        """Test attendance log creation"""
        attendance = AttendanceLog(
            user_id=self.user.id,
            session_id=self.session.id,
            ble_rssi=-65.0,
            ble_verified=True,
            face_confidence=0.4,
            face_verified=True,
            liveness_verified=True,
            status='present'
        )

        db.session.add(attendance)
        db.session.commit()

        assert attendance.id is not None
        assert attendance.status == 'present'
        assert attendance.ble_verified == True

    def test_attendance_to_dict(self):
        """Test attendance serialization"""
        attendance = AttendanceLog(
            user_id=self.user.id,
            session_id=self.session.id,
            ble_rssi=-70.0,
            ble_verified=True,
            face_confidence=0.8,
            face_verified=True,
            liveness_verified=False,
            status='present'
        )

        data = attendance.to_dict()
        assert data['ble_rssi'] == -70.0
        assert data['face_confidence'] == 0.8
        assert data['status'] == 'present'


class TestAnomalyLogModel:
    """Test AnomalyLog model functionality"""

    def setup_method(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test user and session
        self.user = User(roll_number='STUDENT002', name='Test Student 2', email='student2@example.com', role='student')
        self.teacher = User(roll_number='TEACHER003', name='Test Teacher 2', email='teacher3@example.com', role='teacher')
        db.session.add_all([self.user, self.teacher])
        db.session.commit()

        self.session = Session(
            course_code='SEC101',
            course_name='Security 101',
            teacher_id=self.teacher.id,
            session_date=date.today(),
            start_time=time(11, 0),
            end_time=time(12, 0)
        )
        db.session.add(self.session)
        db.session.commit()

    def teardown_method(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_anomaly_creation(self):
        """Test anomaly log creation"""
        anomaly = AnomalyLog(
            user_id=self.user.id,
            session_id=self.session.id,
            anomaly_type='multi_face',
            description='Multiple faces detected in frame',
            severity='medium'
        )

        db.session.add(anomaly)
        db.session.commit()

        assert anomaly.id is not None
        assert anomaly.anomaly_type == 'multi_face'
        assert anomaly.severity == 'medium'
        assert anomaly.resolved == False

    def test_anomaly_to_dict(self):
        """Test anomaly serialization"""
        anomaly = AnomalyLog(
            user_id=self.user.id,
            session_id=self.session.id,
            anomaly_type='low_confidence',
            description='Face recognition confidence too low',
            severity='high',
            resolved=True
        )

        data = anomaly.to_dict()
        assert data['anomaly_type'] == 'low_confidence'
        assert data['severity'] == 'high'
        assert data['resolved'] == True


class TestFaceEmbeddingModel:
    """Test FaceEmbedding model functionality"""

    def setup_method(self):
        """Set up test database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create test user
        self.user = User(roll_number='STUDENT003', name='Test Student 3', email='student3@example.com', role='student')
        db.session.add(self.user)
        db.session.commit()

    def teardown_method(self):
        """Clean up test database"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_face_embedding_creation(self):
        """Test face embedding storage"""
        embedding_data = [0.1] * 128  # 128-dimensional vector
        face_emb = FaceEmbedding(
            user_id=self.user.id,
            embedding=embedding_data
        )

        db.session.add(face_emb)
        db.session.commit()

        assert face_emb.id is not None
        assert len(face_emb.embedding) == 128
        assert face_emb.embedding[0] == 0.1
