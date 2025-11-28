from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from backend.models import db, User, AttendanceLog, Session as ClassSession, AnomalyLog
from backend.services.attendance_service import AttendanceService
from datetime import datetime, date
import io
import csv

teacher_bp = Blueprint('teacher', __name__)
attendance_service = AttendanceService()

def require_teacher(f):
    """Decorator to require teacher role"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'teacher':
            return jsonify({'error': 'Teacher access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@teacher_bp.route('/dashboard')
@login_required
@require_teacher
def dashboard():
    # Get today's sessions
    today = date.today()
    today_sessions = ClassSession.query.filter_by(
        teacher_id=current_user.id,
        session_date=today
    ).all()

    # Get recent anomalies
    recent_anomalies = AnomalyLog.query.join(ClassSession)\
        .filter(ClassSession.teacher_id == current_user.id)\
        .order_by(AnomalyLog.timestamp.desc())\
        .limit(10)\
        .all()

    return render_template('teacher/dashboard.html',
                         today_sessions=today_sessions,
                         recent_anomalies=recent_anomalies)

@teacher_bp.route('/sessions')
@login_required
@require_teacher
def sessions():
    all_sessions = ClassSession.query.filter_by(teacher_id=current_user.id)\
        .order_by(ClassSession.session_date.desc())\
        .all()

    return render_template('teacher/sessions.html', sessions=all_sessions)

@teacher_bp.route('/api/create-session', methods=['POST'])
@login_required
@require_teacher
def create_session():
    try:
        data = request.get_json()

        session = ClassSession(
            course_code=data['course_code'],
            course_name=data['course_name'],
            teacher_id=current_user.id,
            session_date=datetime.strptime(data['session_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            is_active=data.get('is_active', False)
        )

        db.session.add(session)
        db.session.commit()

        return jsonify({'success': True, 'session_id': session.id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@teacher_bp.route('/api/toggle-session/<int:session_id>', methods=['POST'])
@login_required
@require_teacher
def toggle_session(session_id):
    session = ClassSession.query.get_or_404(session_id)

    if session.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    session.is_active = not session.is_active
    db.session.commit()

    return jsonify({'success': True, 'is_active': session.is_active})

@teacher_bp.route('/api/delete-session/<int:session_id>', methods=['DELETE'])
@login_required
@require_teacher
def delete_session(session_id):
    try:
        session = ClassSession.query.get_or_404(session_id)

        # Verify teacher owns this session
        if session.teacher_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Delete associated attendance logs
        AttendanceLog.query.filter_by(session_id=session_id).delete()

        # Delete associated anomaly logs
        AnomalyLog.query.filter_by(session_id=session_id).delete()

        # Delete session
        db.session.delete(session)
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@teacher_bp.route('/session/<int:session_id>')
@login_required
@require_teacher
def view_session(session_id):
    session = ClassSession.query.get_or_404(session_id)

    if session.teacher_id != current_user.id:
        return "Unauthorized", 403

    attendance = AttendanceLog.query.filter_by(session_id=session_id).all()
    anomalies = AnomalyLog.query.filter_by(session_id=session_id).all()

    # Get all students who should attend (for now, all students)
    all_students = User.query.filter_by(role='student').all()

    # Create attendance summary
    attendance_map = {a.user_id: a for a in attendance}
    attendance_summary = []

    for student in all_students:
        att_record = attendance_map.get(student.id)
        attendance_summary.append({
            'student': student,
            'attendance': att_record,
            'status': att_record.status if att_record else 'absent'
        })

    return render_template('teacher/session_detail.html',
                         session=session,
                         attendance_summary=attendance_summary,
                         anomalies=anomalies)

@teacher_bp.route('/api/manual-override', methods=['POST'])
@login_required
@require_teacher
def manual_override():
    try:
        data = request.get_json()
        user_id = data['user_id']
        session_id = data['session_id']
        new_status = data['status']
        notes = data.get('notes', '')

        # Verify teacher owns this session
        session = ClassSession.query.get(session_id)
        if not session or session.teacher_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Find or create attendance record
        attendance = AttendanceLog.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).first()

        if attendance:
            success = attendance_service.manual_override(attendance.id, new_status, notes)
        else:
            # Create new attendance record
            attendance = AttendanceLog(
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.utcnow(),
                status=new_status,
                is_manual_override=True,
                notes=notes,
                ble_verified=False,
                face_verified=False,
                liveness_verified=False
            )
            db.session.add(attendance)
            db.session.commit()
            success = True

        return jsonify({'success': success})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@teacher_bp.route('/reports')
@login_required
@require_teacher
def reports():
    return render_template('teacher/reports.html')

@teacher_bp.route('/api/export-attendance/<int:session_id>')
@login_required
@require_teacher
def export_attendance(session_id):
    session = ClassSession.query.get_or_404(session_id)

    if session.teacher_id != current_user.id:
        return "Unauthorized", 403

    attendance = AttendanceLog.query.filter_by(session_id=session_id).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['Roll Number', 'Name', 'Date', 'Time', 'Status', 'BLE Verified',
                    'Face Verified', 'Liveness Verified', 'Notes'])

    # Data
    for att in attendance:
        # Format roll number for Excel to prevent scientific notation
        roll_number = f'="{att.user.roll_number}"'
        
        writer.writerow([
            roll_number,
            att.user.name,
            att.timestamp.strftime('%Y-%m-%d'),
            att.timestamp.strftime('%H:%M:%S'),
            att.status,
            'Yes' if att.ble_verified else 'No',
            'Yes' if att.face_verified else 'No',
            'Yes' if att.liveness_verified else 'No',
            att.notes or ''
        ])

    # Prepare file
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_{session.course_code}_{session.session_date}.csv'
    )

@teacher_bp.route('/manage-students')
@login_required
@require_teacher
def manage_students():
    students = User.query.filter_by(role='student').all()
    return render_template('teacher/manage_students.html', students=students)
