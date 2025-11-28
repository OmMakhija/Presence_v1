from datetime import datetime
from backend.models import db, AttendanceLog, Session, AnomalyLog, User
from backend.services.face_recognition import FaceRecognitionService
from backend.services.liveness_detection import LivenessDetectionService
from backend.services.ble_service import BLEProximityService

class AttendanceService:
    def __init__(self):
        self.face_service = FaceRecognitionService()
        self.liveness_service = LivenessDetectionService()
        self.ble_service = BLEProximityService()

    def mark_attendance(self, user_id, session_id, frame, ble_data, liveness_frames=None, liveness_challenge=None):
        """
        Complete attendance marking workflow.

        Args:
            user_id: Student user ID
            session_id: Active session ID
            frame: Captured frame for face recognition
            ble_data: BLE proximity verification data
            liveness_frames: Frames for liveness verification (optional)
            liveness_challenge: Type of liveness challenge given (optional)

        Returns:
            dict: Attendance result with status and details
        """
        result = {
            'success': False,
            'attendance_id': None,
            'ble_verified': False,
            'ble_details': ble_data,
            'face_verified': False,
            'liveness_verified': False,
            'anomalies': [],
            'errors': []
        }

        # Verify session is active
        session = Session.query.get(session_id)
        if not session or not session.is_active:
            result['errors'].append('Session not active')
            return result

        # Step 1: BLE Proximity Check
        if not ble_data or not ble_data.get('verified'):
            result['errors'].append('BLE proximity verification failed')
            self._log_anomaly(user_id, session_id, 'ble_failed',
                            f"RSSI: {ble_data.get('rssi', 'N/A')}")
            return result

        result['ble_verified'] = True

        # Step 2: Multi-face Detection
        face_count = self.face_service.detect_multiple_faces(frame)
        if face_count == 0:
            result['errors'].append('No face detected')
            self._log_anomaly(user_id, session_id, 'no_face', 'No face in frame')
            return result
        elif face_count > 1:
            result['anomalies'].append('multiple_faces')
            self._log_anomaly(user_id, session_id, 'multi_face',
                            f'Detected {face_count} faces')

        # Step 3: Face Recognition
        try:
            probe_embedding = self.face_service.get_embedding_from_frame(frame)
            match_found, distance = self.face_service.verify_face(user_id, probe_embedding)

            result['face_verified'] = match_found
            result['face_distance'] = distance

            if not match_found:
                result['errors'].append(f'Face verification failed (Distance: {distance:.4f})')
                self._log_anomaly(user_id, session_id, 'low_confidence',
                                f'Distance: {distance}')
                return result

        except Exception as e:
            result['errors'].append(f'Face recognition error: {str(e)}')
            return result

        # Step 4: Liveness Detection (if frames provided)
        if liveness_frames and liveness_challenge:
            liveness_result = self.liveness_service.verify_liveness_challenge(
                liveness_challenge, liveness_frames
            )
            result['liveness_verified'] = liveness_result['success']
            result['liveness_confidence'] = liveness_result['confidence']

            if not liveness_result['success']:
                result['anomalies'].append('liveness_failed')
                self._log_anomaly(user_id, session_id, 'liveness_failed',
                                f"Challenge: {liveness_challenge}")
        else:
            # If no liveness check, mark as verified (optional feature)
            result['liveness_verified'] = True

        # Step 5: Check for duplicate attendance
        existing = AttendanceLog.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).first()

        if existing:
            result['errors'].append('Attendance already marked for this session')
            result['attendance_id'] = existing.id
            return result

        # Step 6: Create Attendance Record
        attendance = AttendanceLog(
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.utcnow(),
            ble_rssi=ble_data.get('rssi'),
            ble_verified=result['ble_verified'],
            face_confidence=distance,
            face_verified=result['face_verified'],
            liveness_verified=result['liveness_verified'],
            liveness_challenge=liveness_challenge,
            status='present'
        )

        db.session.add(attendance)
        db.session.commit()

        result['success'] = True
        result['attendance_id'] = attendance.id

        return result

    def _log_anomaly(self, user_id, session_id, anomaly_type, description):
        """Log anomaly to database"""
        anomaly = AnomalyLog(
            user_id=user_id,
            session_id=session_id,
            anomaly_type=anomaly_type,
            description=description,
            severity='medium'
        )
        db.session.add(anomaly)
        db.session.commit()

    def get_session_attendance(self, session_id):
        """Get all attendance records for a session"""
        attendance = AttendanceLog.query.filter_by(session_id=session_id).all()
        return [a.to_dict() for a in attendance]

    def get_user_attendance_history(self, user_id, limit=50):
        """Get attendance history for a user"""
        attendance = AttendanceLog.query.filter_by(user_id=user_id)\
            .order_by(AttendanceLog.timestamp.desc())\
            .limit(limit)\
            .all()
        return [a.to_dict() for a in attendance]

    def manual_override(self, attendance_id, new_status, notes):
        """Allow teacher to manually override attendance"""
        attendance = AttendanceLog.query.get(attendance_id)
        if attendance:
            attendance.status = new_status
            attendance.is_manual_override = True
            attendance.notes = notes
            db.session.commit()
            return True
        return False
