# PRESENCE System Requirements Document

## 1. System Overview

PRESENCE is a comprehensive, AI-enabled proxy-free attendance management system designed for educational institutions. The system combines Bluetooth Low Energy (BLE) proximity detection with advanced facial recognition and liveness detection to ensure accurate, secure, and tamper-proof attendance tracking.

### Core Objectives:
- Automated attendance marking with smart web interface
- Prevention of proxy attendance through AI-powered face and liveness checks
- Physical presence verification using BLE devices in classrooms
- Real-time anomaly detection and alerting for suspicious activities

### Architecture:
The system implements a hybrid authentication approach combining:
- **BLE Proximity Detection**: Verifies physical presence in the classroom environment
- **AI Facial Recognition**: Confirms user identity through 128-dimensional facial embeddings
- **Liveness Detection**: Prevents spoofing attacks with interactive challenges (blink, head movement)
- **Anomaly Detection**: Identifies proxy attempts through multi-face detection and behavioral analysis

### Key Components:
- **BLE Proximity Check**: Validates student presence within classroom range (RSSI ≥ -70 dBm)
- **Face Detection & Recognition**: Uses FaceNet with MTCNN for detection and InceptionResnetV1 for embedding
- **Liveness Verification**: Interactive challenges with real-time facial motion tracking
- **Local Database**: Secure storage of user profiles, facial embeddings, and attendance records
- **Attendance Logger**: Comprehensive logging with timestamps, verification status, and anomaly flags

## 2. Technology Stack

- **Backend**: Flask (Python 3.8+)
- **Frontend**: HTML5, CSS3, JavaScript (responsive web application)
- **Database**: PostgreSQL (hosted on Amazon RDS for production)
- **Cloud Infrastructure**: AWS EC2 for compute, S3 for media file storage
- **AI/ML Stack**:
  - PyTorch: Deep learning model inference
  - facenet-pytorch: MTCNN for face detection, InceptionResnetV1 for embeddings (pretrained on VGGFace2)
  - OpenCV: Webcam capture, video processing, real-time frame display, face bounding boxes
  - NumPy: Vector operations, embedding averaging, distance calculations
  - MediaPipe/Dlib: Facial landmark analysis for liveness detection
- **Authentication**: OAuth 2.0 or institutional Single Sign-On (SSO)
- **Notifications**: SendGrid API for automated email/SMS alerts
- **Hardware**: Bluetooth Low Energy Device (HM-10 Module) for proximity detection

## 3. Hardware Requirements

### BLE Infrastructure:
- Classroom-integrated BLE scanner/beacon (HM-10 Module)
- Passive detection of student mobile devices broadcasting unique BLE identifiers
- Pre-registered devices with cryptographically signed UUID
- Periodic scanning capability (e.g., 15-minute and 45-minute intervals)
- RSSI threshold: -70 dBm (approximately 5-10 meters range)

### Client Devices:
- Webcam-enabled devices (desktop, laptop, tablet, smartphone)
- Minimum 720p webcam resolution for facial recognition
- Bluetooth Low Energy capable mobile devices for proximity verification
- Cross-platform compatibility (Windows, macOS, Linux, iOS, Android)

## 4. Functional Requirements

### 4.1 Student Portal
- **User Registration**: Account creation with facial data capture (10 seconds at 10 FPS)
- **Login/Authentication**: Secure login with role-based access
- **BLE Proximity Verification**: Automatic detection within classroom range
- **Facial Recognition Authentication**: Real-time face matching against stored embeddings
- **Liveness Challenge Completion**: Interactive prompts (blink twice, head movement)
- **Attendance History**: View personal attendance records with timestamps and verification status

### 4.2 Admin/Teacher Portal
- **Secure Login**: Teacher-only access with elevated permissions
- **Session Management**: Create, modify, and activate/deactivate class sessions
- **Real-time Attendance Monitoring**: Live view of attendance during active sessions
- **Manual Attendance Override**: Ability to mark attendance when automated systems fail
- **Report Generation**: Export attendance data in CSV/PDF formats
- **Anomaly Review**: View and investigate flagged suspicious activities
- **Student Management**: View and manage student registrations

### 4.3 Core Features
- **BLE Proximity Detection**: RSSI-based verification (threshold ≥ -70 dBm)
- **Facial Recognition**: 128-dimensional embeddings with Euclidean distance matching (threshold < 0.6)
- **Liveness Detection**: Real-time validation of blink and head movement challenges
- **Multi-face Detection**: Automatic flagging of multiple faces in single frame
- **Proxy Detection**: Behavioral analysis including rapid sequential attempts, identical backgrounds
- **Automated Notifications**: Email/SMS alerts for anomalies and low attendance warnings

## 5. Database Schema

### Users Table
- id (Primary Key, Integer)
- roll_number (String, Unique, Indexed)
- name (String, 200 chars)
- email (String, 200 chars, Unique)
- password_hash (String, 256 chars)
- role (String, 20 chars: 'student' or 'teacher')
- is_active (Boolean, default True)
- created_at (DateTime)

### Face Embeddings Table
- id (Primary Key, Integer)
- user_id (Foreign Key to Users, Indexed)
- embedding (PickleType: numpy array, 128-dimensional)
- created_at (DateTime)
- updated_at (DateTime)

### Sessions Table
- id (Primary Key, Integer)
- course_code (String, 50 chars)
- course_name (String, 200 chars)
- teacher_id (Foreign Key to Users)
- session_date (Date)
- start_time (Time)
- end_time (Time)
- is_active (Boolean, default False)
- ble_device_id (String, 100 chars, optional)
- created_at (DateTime)

### Attendance Logs Table
- id (Primary Key, Integer)
- user_id (Foreign Key to Users, Indexed)
- session_id (Foreign Key to Sessions, Indexed)
- timestamp (DateTime, default UTC now)
- ble_rssi (Float, optional)
- ble_verified (Boolean, default False)
- face_confidence (Float: Euclidean distance)
- face_verified (Boolean, default False)
- liveness_verified (Boolean, default False)
- liveness_challenge (String, 100 chars: challenge type)
- status (String, 20 chars: 'present', 'absent', 'proxy_suspected')
- is_manual_override (Boolean, default False)
- notes (Text, optional)

### Anomaly Logs Table
- id (Primary Key, Integer)
- user_id (Foreign Key to Users, optional)
- session_id (Foreign Key to Sessions, optional)
- timestamp (DateTime, default UTC now)
- anomaly_type (String, 50 chars: 'multi_face', 'no_face', 'liveness_failed', 'rapid_attempts', 'ble_failed', 'duplicate_ip', 'low_confidence')
- severity (String, 20 chars: 'low', 'medium', 'high')
- description (Text)
- metadata (JSON: additional context like IP, face count, etc.)
- resolved (Boolean, default False)

## 6. API Endpoints Required

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Student Portal Endpoints
- `GET /student/dashboard` - Student dashboard
- `GET /student/register-face` - Face registration page
- `POST /student/api/register-face` - Register facial embeddings
- `GET /student/mark-attendance` - Attendance marking page
- `POST /student/api/mark-attendance` - Mark attendance with verification
- `GET /student/api/attendance-history` - Get attendance history

### Teacher Portal Endpoints
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/sessions` - Session management page
- `POST /teacher/api/create-session` - Create new session
- `POST /teacher/api/toggle-session/<session_id>` - Activate/deactivate session
- `GET /teacher/session/<session_id>` - View session details and attendance
- `POST /teacher/api/manual-override` - Manual attendance override
- `GET /teacher/reports` - Reports page
- `GET /teacher/api/export-attendance/<session_id>` - Export attendance CSV
- `GET /teacher/manage-students` - Student management page

## 7. Security Requirements

- **Data Encryption**: All sensitive data encrypted at rest and in transit (HTTPS/TLS)
- **Authentication**: OAuth 2.0 or institutional SSO integration
- **Authorization**: Role-based access control (RBAC) with teacher/student permissions
- **Facial Data Security**: Secure storage of 128-dimensional embeddings with access controls
- **Session Management**: Secure session handling with automatic timeouts
- **Input Validation**: Comprehensive validation of all user inputs
- **Audit Logging**: Complete logging of all attendance and authentication events

## 8. Non-Functional Requirements

- **Performance**: Face recognition response time < 2 seconds, page load times < 3 seconds
- **Scalability**: Support for multiple concurrent users (50+ students per session)
- **Compatibility**: Cross-platform support (Chrome, Firefox, Safari, Edge browsers)
- **Mobile Support**: Responsive design for mobile devices with webcam access
- **Reliability**: 99.9% uptime with automatic failover capabilities
- **Video Quality**: Minimum 720p webcam resolution for accurate facial recognition
- **Real-time Processing**: Live video processing for immediate feedback
- **Data Retention**: Configurable retention policies for attendance and anomaly logs

## 9. Development Timeline

### Week 1: Foundation Setup
- Flask environment configuration
- PostgreSQL database schema implementation
- Initial UI framework and responsive design
- Basic authentication system

### Week 2: Enrollment Interface
- Student registration system
- Face registration interface with webcam integration
- Backend routes for enrollment workflow
- Database integration for user and embedding storage

### Week 3: Facial Recognition Implementation
- FaceNet model integration with OpenCV
- Real-time face detection and embedding generation
- Face matching algorithm with distance thresholding
- Authentication endpoint development

### Week 4: Liveness Detection
- MediaPipe/Dlib integration for facial landmarks
- Blink detection using Eye Aspect Ratio (EAR)
- Head movement tracking and validation
- Interactive challenge system

### Week 5: BLE Integration & Completion
- BLE proximity simulation for development
- Session management system
- Teacher dashboard with attendance monitoring
- CSV export functionality and anomaly detection

## 10. Testing Requirements

- **Unit Tests**: Individual component testing (face recognition, BLE, liveness)
- **Integration Tests**: End-to-end workflow testing (registration → attendance marking)
- **Performance Tests**: Load testing with multiple concurrent users
- **Security Tests**: Penetration testing and vulnerability assessment
- **Cross-browser Testing**: Compatibility across major browsers and devices
- **User Acceptance Testing**: Real-world scenario validation with actual users
