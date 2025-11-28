# PRESENCE - AI-Powered Attendance Management System

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-blue.svg)](https://flask.palletsprojects.com/)

PRESENCE is a comprehensive, AI-enabled proxy-free attendance management system designed for educational institutions. It combines Bluetooth Low Energy (BLE) proximity detection with advanced facial recognition and liveness detection to ensure accurate, secure, and tamper-proof attendance tracking.

## 🚀 Key Features

### 🔒 Multi-Layer Authentication
- **BLE Proximity Detection**: Verifies physical presence in classroom environment (RSSI ≥ -70 dBm)
- **AI Facial Recognition**: Confirms user identity through 128-dimensional facial embeddings using FaceNet
- **Liveness Detection**: Prevents spoofing with interactive challenges (blink detection, head movement)
- **Anomaly Detection**: Identifies proxy attempts through multi-face detection and behavioral analysis

### 👥 Dual Role Support
- **Student Portal**: Face registration, attendance marking, personal attendance history
- **Teacher Portal**: Session management, real-time monitoring, manual overrides, comprehensive reports

### 🛡️ Security & Compliance
- Secure password hashing with bcrypt
- Role-based access control (RBAC)
- Comprehensive audit logging
- Encrypted data storage
- Input validation and sanitization

### 📊 Advanced Analytics
- Real-time attendance monitoring
- Anomaly detection and alerting
- CSV export functionality
- Attendance statistics and trends

## 🏗️ Architecture

```
PRESENCE System Overview
├── Frontend (HTML/CSS/JS)
│   ├── Authentication (Login/Register)
│   ├── Student Portal (Face Registration, Attendance)
│   └── Teacher Dashboard (Session Management, Reports)
├── Backend (Flask/Python)
│   ├── AI Services (Face Recognition, Liveness, BLE)
│   ├── Database Models (SQLAlchemy)
│   └── REST API Endpoints
└── Database (SQLite/PostgreSQL)
    ├── Users, Sessions, Attendance Logs
    └── Face Embeddings & Anomalies
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0+
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **Authentication**: Flask-Login with session management

### AI/ML Components
- **Face Recognition**: FaceNet with MTCNN (pretrained on VGGFace2)
- **Liveness Detection**: MediaPipe FaceMesh with EAR algorithm
- **Deep Learning**: PyTorch for model inference
- **Computer Vision**: OpenCV for image processing

### Hardware Integration
- **BLE**: bleak library for Bluetooth Low Energy scanning
- **Webcam**: Real-time video capture and processing

### Frontend
- **Templates**: Jinja2 templating
- **Styling**: Responsive CSS with modern design
- **JavaScript**: Vanilla JS with async/await for camera access

### Additional Services
- **Notifications**: SendGrid API for email alerts
- **Deployment**: Gunicorn WSGI server support

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **Webcam** (for face registration and attendance marking)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **BLE-capable Device** (for proximity verification)
- **4GB+ RAM** recommended for AI processing

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/TanishkaJadaun/PRESENCE.git
cd presence_project
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

> **Note**: Installation may take 5-10 minutes due to AI/ML libraries.

### 4. Initialize Database
```bash
python backend/init_db.py
```

### 5. Configure Environment (Optional)
```bash
# Copy environment template
cp .env.example .env

# Edit .env file for custom settings
```

### 6. Run the Application
```bash
# Quick launcher (recommended)
python run.py

# Or directly
python backend/app.py
```

### 7. Access the Web Interface
Open your browser and navigate to: **http://127.0.0.1:5000**

## 👥 Usage Guide

### First-Time Setup

#### Create Teacher Account
1. Navigate to the login page
2. Click "Register here" link
3. Fill registration form:
   - **Roll Number**: `ADMIN001`
   - **Name**: `Administrator`
   - **Email**: `admin@school.edu`
   - **Password**: Secure password
   - **Role**: Select "Teacher"
   - **BLE Device**: Code from HM-10 Module
4. Click "Register"

#### Create Class Session
1. Login as teacher
2. Click "Manage Sessions" → "Create New Session"
3. Fill session details and activate

### Student Workflow

#### 1. Account Registration
- Register with unique roll number
- Provide BLE device address
- Set role as "Student"

#### 2. Face Registration
1. Login to student dashboard
2. Click "Register Face"
3. Grant camera permissions
4. Look directly at camera for 10 seconds
5. System processes and saves facial data

#### 3. Mark Attendance
1. Login as student
2. Click "Mark Attendance"
3. Select active session
4. Complete verification:
   - **BLE Proximity**: Automatic detection
   - **Face Recognition**: Real-time matching
   - **Liveness Challenge**: Interactive prompts

### Teacher Workflow

#### Session Management
- Create and configure class sessions
- Activate/deactivate sessions
- Monitor real-time attendance

#### Manual Overrides
- Override attendance for technical issues
- Add notes for manual entries

#### Reports & Analytics
- View session attendance details
- Export data to CSV
- Review anomaly logs

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///instance/presence.db

# Face Recognition
FACE_MATCH_THRESHOLD=0.6
FACE_CAPTURE_DURATION=10
FACE_CAPTURE_FPS=10

# BLE
BLE_RSSI_THRESHOLD=-70

# Notifications
SENDGRID_API_KEY=your-sendgrid-api-key
```

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:create_app()
```

#### Docker Support
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install -r backend/requirements.txt
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

## 🧪 Testing

### Run Unit Tests
```bash
# All tests
pytest tests/ -v

# Specific test categories
pytest tests/test_models.py -v
pytest tests/test_services.py -v
pytest tests/test_integration.py -v
```

### System Health Check
```bash
python -c "
from backend.app import create_app
app = create_app()
with app.test_client() as client:
    response = client.get('/')
    print('✅ Server running' if response.status_code == 200 else '❌ Server error')
"
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Student API
- `GET /student/dashboard` - Student dashboard
- `POST /student/api/register-face` - Face registration
- `POST /student/api/mark-attendance` - Mark attendance
- `GET /student/api/attendance-history` - Attendance history

### Teacher API
- `GET /teacher/dashboard` - Teacher dashboard
- `POST /teacher/api/create-session` - Create session
- `POST /teacher/api/toggle-session/<id>` - Toggle session
- `GET /teacher/api/export-attendance/<id>` - Export CSV

## 🐛 Troubleshooting

### Common Issues

#### Camera Not Working
- Ensure browser camera permissions
- Try refreshing the page
- Check other applications aren't using camera

#### Face Registration Failing
- Ensure good lighting
- Remove glasses if causing reflections
- Look directly at camera, keep steady

#### BLE Proximity Issues
- Verify device address format (XX:XX:XX:XX:XX:XX)
- Check device is powered and in range
- Ensure no interference from other devices

#### Database Errors
```bash
python backend/init_db.py  # Reinitialize database
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FaceNet**: Facial recognition model by Google
- **MediaPipe**: Face mesh detection by Google
- **Flask**: Web framework
- **OpenCV**: Computer vision library
- **PyTorch**: Deep learning framework

## 📞 Support

For questions or issues:
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
- Review [REQUIREMENTS.md](REQUIREMENTS.md) for specifications
- Open an issue on GitHub

---

**🎉 Welcome to PRESENCE - Your AI-Powered Attendance Solution!**

*Built with ❤️ for secure and efficient attendance management*
