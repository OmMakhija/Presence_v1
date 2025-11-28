"""
Unit tests for AI services
"""
import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.face_recognition import FaceRecognitionService
from backend.services.liveness_detection import LivenessDetectionService
from backend.services.ble_service import BLEProximityService
from backend.services.attendance_service import AttendanceService
from backend.services.notification_service import NotificationService


class TestFaceRecognitionService:
    """Test Face Recognition Service"""

    def setup_method(self):
        """Initialize service"""
        self.service = FaceRecognitionService()

    def test_initialization(self):
        """Test service initialization"""
        assert self.service.mtcnn is not None
        assert self.service.resnet is not None
        assert self.service.match_threshold == 0.6

    def test_detect_multiple_faces_no_faces(self):
        """Test multi-face detection with empty frame"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        face_count = self.service.detect_multiple_faces(dummy_frame)
        assert face_count == 0

    def test_get_embedding_from_frame_no_face(self):
        """Test embedding extraction with no face"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        with pytest.raises(ValueError, match="No face detected"):
            self.service.get_embedding_from_frame(dummy_frame)

    def test_register_user_face_method_exists(self):
        """Test that register_user_face method exists (can't test without DB)"""
        assert hasattr(self.service, 'register_user_face')
        assert callable(self.service.register_user_face)


class TestLivenessDetectionService:
    """Test Liveness Detection Service"""

    def setup_method(self):
        """Initialize service"""
        self.service = LivenessDetectionService()

    def test_initialization(self):
        """Test service initialization"""
        assert self.service.face_mesh is not None
        assert self.service.EAR_THRESHOLD == 0.25
        assert self.service.BLINK_FRAMES == 3

    def test_detect_blink_no_face(self):
        """Test blink detection with no face"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.service.detect_blink(dummy_frame)
        assert result['blink_detected'] == False
        assert result['ear'] is None

    def test_detect_head_pose_no_face(self):
        """Test head pose detection with no face"""
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.service.detect_head_pose(dummy_frame)
        assert result['direction'] == 'unknown'
        assert result['angles'] is None

    def test_verify_liveness_unknown_challenge(self):
        """Test liveness verification with unknown challenge type"""
        result = self.service.verify_liveness_challenge('unknown', [])
        assert result['success'] == False
        assert result['confidence'] == 0.0
        assert 'error' in result['details']

    def test_verify_blink_challenge_empty_frames(self):
        """Test blink challenge verification with empty frames"""
        result = self.service._verify_blink_challenge([])
        assert result['success'] == False
        assert result['confidence'] == 0.0
        assert result['details']['blinks_detected'] == 0


from backend.app import create_app
from backend.models import db, User
import asyncio

class TestBLEProximityService:
    """Test BLE Proximity Service"""

    def setup_method(self):
        """Initialize service and db"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        
        self.service = BLEProximityService()

    def teardown_method(self):
        """Clean up"""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_initialization(self):
        """Test service initialization"""
        assert self.service.rssi_threshold == -70

    def test_check_proximity_no_user(self):
        """Test check_proximity for non-existent user"""
        # Run async method synchronously
        result = asyncio.run(self.service.check_proximity(999))
        assert result['verified'] == False
        assert result['error'] == 'Device not registered'

    def test_check_proximity_no_device(self):
        """Test check_proximity for user without device"""
        user = User(roll_number='TEST001', name='Test', email='test@test.com')
        db.session.add(user)
        db.session.commit()
        
        result = asyncio.run(self.service.check_proximity(user.id))
        assert result['verified'] == False
        assert result['error'] == 'Device not registered'


class TestNotificationService:
    """Test Notification Service"""

    def setup_method(self):
        """Initialize service"""
        self.service = NotificationService()

    def test_initialization(self):
        """Test service initialization"""
        # Should be disabled without SendGrid key
        assert self.service.enabled == False

    def test_send_email_disabled(self):
        """Test email sending when service is disabled"""
        result = self.service.send_email('test@example.com', 'Test', 'Content')
        assert result == False

    def test_notify_anomaly(self):
        """Test anomaly notification (should fail gracefully)"""
        result = self.service.notify_anomaly('teacher@example.com', 'John Doe', 'multi_face', 'CS101 Session')
        assert result == False  # Should fail without SendGrid key

    def test_notify_low_attendance(self):
        """Test low attendance notification (should fail gracefully)"""
        result = self.service.notify_low_attendance('student@example.com', 'Jane Doe', 65.5)
        assert result == False  # Should fail without SendGrid key


class TestAttendanceServiceIntegration:
    """Test Attendance Service integration with other services"""

    def setup_method(self):
        """Initialize service"""
        self.service = AttendanceService()

    def test_initialization(self):
        """Test service initialization and dependencies"""
        assert hasattr(self.service, 'face_service')
        assert hasattr(self.service, 'liveness_service')
        assert hasattr(self.service, 'ble_service')
        assert isinstance(self.service.face_service, FaceRecognitionService)
        assert isinstance(self.service.ble_service, BLEProximityService)
        assert isinstance(self.service.liveness_service, LivenessDetectionService)

    def test_mark_attendance_method_exists(self):
        """Test that mark_attendance method exists (can't test without DB setup)"""
        assert hasattr(self.service, 'mark_attendance')
        assert callable(self.service.mark_attendance)

    def test_get_session_attendance_empty(self):
        """Test getting attendance for session with no records"""
        # This would normally require database setup, but we're testing the method exists
        assert hasattr(self.service, 'get_session_attendance')

    def test_get_user_attendance_history_empty(self):
        """Test getting user attendance history (empty)"""
        # This would normally require database setup, but we're testing the method exists
        assert hasattr(self.service, 'get_user_attendance_history')

    def test_manual_override_method_exists(self):
        """Test that manual override method exists"""
        assert hasattr(self.service, 'manual_override')
