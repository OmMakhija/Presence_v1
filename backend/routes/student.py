from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from backend.models import db, User, FaceEmbedding, AttendanceLog, Session as ClassSession
from backend.services.face_recognition import FaceRecognitionService
from backend.services.liveness_detection import LivenessDetectionService
from backend.services.ble_service import BLEProximityService
from backend.services.attendance_service import AttendanceService
import cv2
import numpy as np
import base64
import asyncio
from datetime import datetime

student_bp = Blueprint('student', __name__)

face_service = FaceRecognitionService()
attendance_service = AttendanceService()
ble_service = BLEProximityService()
liveness_service = LivenessDetectionService()

def require_student(f):
    """Decorator to require student role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            return jsonify({'error': 'Student access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/dashboard')
@login_required
@require_student
def dashboard():
    # Get recent attendance
    recent_attendance = AttendanceLog.query.filter_by(user_id=current_user.id)\
        .order_by(AttendanceLog.timestamp.desc())\
        .limit(10)\
        .all()

    # Check if face is registered
    has_face = FaceEmbedding.query.filter_by(user_id=current_user.id).first() is not None

    return render_template('student/dashboard.html',
                         recent_attendance=recent_attendance,
                         has_face=has_face)

@student_bp.route('/register-face')
@login_required
@require_student
def register_face_page():
    return render_template('student/register.html')

@student_bp.route('/api/register-face', methods=['POST'])
@login_required
@require_student
def register_face_api():
    """API endpoint to register facial data from webcam frames"""
    try:
        data = request.get_json()
        frames_b64 = data.get('frames', [])

        if len(frames_b64) < 10:
            return jsonify({'success': False, 'error': 'Insufficient frames captured'}), 400

        # Convert base64 frames to OpenCV format
        embeddings = []
        for frame_b64 in frames_b64:
            # Decode base64
            img_data = base64.b64decode(frame_b64.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            try:
                embedding = face_service.get_embedding_from_frame(frame)
                embeddings.append(embedding)
            except ValueError:
                continue  # Skip frames without faces

        if len(embeddings) < 5:
            return jsonify({'success': False, 'error': 'Not enough valid face captures'}), 400

        # Average embeddings
        avg_embedding = np.mean(embeddings, axis=0)

        # Store in database
        face_service.register_user_face(current_user.id, avg_embedding)

        return jsonify({'success': True, 'message': 'Face registered successfully'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'errors': [str(e)]}), 500

@student_bp.route('/mark-attendance')
@login_required
@require_student
def mark_attendance_page():
    # Get active sessions
    active_sessions = ClassSession.query.filter_by(is_active=True).all()
    return render_template('student/attendance.html', active_sessions=active_sessions)

@student_bp.route('/api/mark-attendance', methods=['POST'])
@login_required
@require_student
def mark_attendance_api():
    """API endpoint to mark attendance with face verification"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        frame_b64 = data.get('frame')
        liveness_frames_b64 = data.get('liveness_frames', [])
        liveness_challenge = data.get('liveness_challenge')

        # Decode frame
        img_data = base64.b64decode(frame_b64.split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Decode liveness frames if provided
        liveness_frames = []
        if liveness_frames_b64:
            for lf_b64 in liveness_frames_b64:
                img_data = base64.b64decode(lf_b64.split(',')[1])
                nparr = np.frombuffer(img_data, np.uint8)
                lf = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                liveness_frames.append(lf)

        # Perform BLE Proximity Check
        # Run async BLE check synchronously
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        ble_data = loop.run_until_complete(ble_service.check_proximity(current_user.id))

        # Mark attendance
        result = attendance_service.mark_attendance(
            user_id=current_user.id,
            session_id=session_id,
            frame=frame,
            ble_data=ble_data,
            liveness_frames=liveness_frames if liveness_frames else None,
            liveness_challenge=liveness_challenge
        )

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'errors': [str(e)]}), 500

@student_bp.route('/api/attendance-history')
@login_required
@require_student
def attendance_history_api():
    """Get attendance history for current user"""
    history = attendance_service.get_user_attendance_history(current_user.id)
    return jsonify({'attendance': history})
