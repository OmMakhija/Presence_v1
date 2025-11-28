from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.config import Config
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sg_api_key = Config.SENDGRID_API_KEY
        self.enabled = bool(self.sg_api_key)

    def send_email(self, to_email, subject, content):
        """
        Send email notification via SendGrid.

        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email body (HTML or plain text)

        Returns:
            bool: Success status
        """
        if not self.enabled:
            logger.warning("SendGrid not configured, skipping email")
            return False

        try:
            message = Mail(
                from_email='noreply@presence.edu',
                to_emails=to_email,
                subject=subject,
                html_content=content
            )

            sg = SendGridAPIClient(self.sg_api_key)
            response = sg.send(message)

            return response.status_code == 202

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False

    def notify_anomaly(self, teacher_email, student_name, anomaly_type, session_info):
        """Send anomaly alert to teacher"""
        subject = f"[PRESENCE] Attendance Anomaly Detected"
        content = f"""
        <h2>Attendance Anomaly Alert</h2>
        <p><strong>Student:</strong> {student_name}</p>
        <p><strong>Anomaly Type:</strong> {anomaly_type}</p>
        <p><strong>Session:</strong> {session_info}</p>
        <p>Please review the attendance logs for this session.</p>
        """
        return self.send_email(teacher_email, subject, content)

    def notify_low_attendance(self, student_email, student_name, attendance_percentage):
        """Send low attendance warning to student"""
        subject = f"[PRESENCE] Attendance Warning"
        content = f"""
        <h2>Low Attendance Alert</h2>
        <p>Dear {student_name},</p>
        <p>Your current attendance is <strong>{attendance_percentage}%</strong>.</p>
        <p>Please ensure regular attendance to meet the minimum requirement.</p>
        """
        return self.send_email(student_email, subject, content)
