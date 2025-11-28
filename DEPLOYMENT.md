# PRESENCE Attendance System - Deployment Guide

## 🚀 Quick Start Guide

The PRESENCE Attendance System is a complete, production-ready AI-powered attendance management solution. Follow this guide to set up and run the system.

---

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **Webcam** (for face registration and attendance)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **4GB+ RAM** recommended for AI processing

---

## 🛠️ Installation & Setup

### Step 1: Clone & Navigate
```bash
# The project is already set up in your current directory
cd f:/presence_project
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

**Note**: This may take 5-10 minutes as it installs AI/ML libraries including PyTorch and OpenCV.

### Step 4: Initialize Database
```bash
# Initialize the database
python backend/init_db.py
```

### Step 5: Configure Environment (Optional)
```bash
# Copy environment template
copy .env.example .env

# Edit .env file for custom settings (optional)
# Default settings work for development
```

---

## 🎯 Running the Application

### Start the PRESENCE Server
```bash
# From project root directory
python backend/app.py
```

**Expected Output:**
```
* Serving Flask app 'backend.app'
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### Access the Web Interface
1. Open your web browser
2. Navigate to: **http://127.0.0.1:5000**
3. You'll see the PRESENCE login page

---

## 👥 User Guide

### First-Time Setup

#### 1. Create Teacher Account
1. Go to the login page
2. Click "Register here" link
3. Fill in registration form:
   - **Roll Number**: `ADMIN001` (or any unique ID)
   - **Name**: `Administrator`
   - **Email**: `admin@school.edu`
   - **Password**: Choose a secure password
   - **Role**: Select "Teacher"
   - **Target Device**: The code from the HM-10 Module
4. Click "Register"

#### 2. Login as Teacher
1. Use your teacher credentials to log in
2. You'll be redirected to the Teacher Dashboard

#### 3. Create a Class Session
1. Click "Manage Sessions" from the dashboard
2. Click "Create New Session"
3. Fill in session details:
   - **Course Code**: `CS101`
   - **Course Name**: `Introduction to Computer Science`
   - **Date**: Select today's date
   - **Start Time**: `09:00`
   - **End Time**: `10:30`
   - **Activate immediately**: Check this box
4. Click "Create Session"

#### 4. Create Student Account
1. Logout from teacher account
2. Register a new student account:
   - **Roll Number**: `STUDENT001`
   - **Name**: `John Doe`
   - **Email**: `john@student.edu`
   - **Password**: Choose a password
   - **Role**: Select "Student"

### Student Face Registration

#### Step 1: Login as Student
1. Login with student credentials
2. You'll see "Face Not Registered" warning

#### Step 2: Register Face
1. Click "Register Face" button
2. Grant camera permissions when prompted
3. Read the instructions carefully
4. Click "Start Capture"
5. Look directly at camera for 10 seconds
6. System will process and save your face data

### Attendance Marking

#### Step 1: Access Attendance
1. Login as student
2. Click "Mark Attendance"
3. Select the active session from the list

#### Step 2: Complete Verification
1. **BLE Check**: System simulates proximity verification
2. **Face Recognition**: Position face in camera frame
3. **Liveness Challenge** (if required): Follow on-screen instructions
4. Attendance will be marked automatically

#### Step 3: View Results
- Success: "Attendance marked successfully!"
- Check your dashboard for attendance history

---

## 🔧 Advanced Configuration

### Environment Variables (.env file)

```bash
# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/presence.db

# Face Recognition
FACE_MATCH_THRESHOLD=0.6
FACE_CAPTURE_DURATION=10
FACE_CAPTURE_FPS=10

# BLE Configuration
BLE_RSSI_THRESHOLD=-70

# SendGrid (for email notifications)
SENDGRID_API_KEY=your-sendgrid-api-key
```

### Production Deployment

#### Using Gunicorn (Production WSGI Server)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.app:create_app()
```

#### Using Docker
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app
RUN pip install -r backend/requirements.txt

EXPOSE 5000
CMD ["python", "backend/app.py"]
```

---

## 🧪 Testing the System

### Run Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_models.py -v
pytest tests/test_services.py -v
pytest tests/test_integration.py -v
```

### Run System Health Check
```bash
# Quick system verification
python -c "
from backend.app import create_app
app = create_app()
with app.test_client() as client:
    response = client.get('/')
    print('✅ Server running' if response.status_code == 200 else '❌ Server error')
"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Camera Not Working
- Ensure camera permissions are granted in browser
- Try refreshing the page
- Check if other applications are using the camera

#### 2. Face Registration Failing
- Ensure good lighting
- Remove glasses if causing reflections
- Look directly at camera
- Keep face steady during capture

#### 3. Database Errors
- Run `python backend/init_db.py` to reinitialize
- Check file permissions on database file

#### 4. Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r backend/requirements.txt`

#### 5. Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process and restart
```

---

## 📊 System Architecture

```
PRESENCE System Overview
├── Frontend (HTML/CSS/JS)
│   ├── Authentication (Login/Register)
│   ├── Student Portal (Face Reg, Attendance)
│   └── Teacher Dashboard (Session Mgmt, Reports)
├── Backend (Flask/Python)
│   ├── AI Services (Face Recog, Liveness, BLE)
│   ├── Database Models (SQLAlchemy)
│   └── REST API Endpoints
└── Database (SQLite/PostgreSQL)
    ├── Users, Sessions, Attendance Logs
    └── Face Embeddings & Anomalies
```

---

## 🔒 Security Features

- **Password Hashing**: Secure bcrypt hashing
- **Session Management**: Flask-Login with secure sessions
- **Role-Based Access**: Student/Teacher permissions
- **Input Validation**: Comprehensive form validation
- **Face Data Security**: Encrypted embedding storage

---

## 📈 Performance Optimization

### For Production Use:
- Use PostgreSQL instead of SQLite
- Enable database connection pooling
- Configure reverse proxy (nginx)
- Set up SSL/TLS certificates
- Enable caching for static files

---

## 📞 Support & Documentation

### Key Files:
- `REQUIREMENTS.md` - Complete system specifications
- `README.md` - Project overview and features
- `backend/config.py` - Configuration settings
- `backend/models/` - Database schema
- `backend/services/` - AI and business logic
- `frontend/templates/` - HTML templates
- `frontend/static/` - CSS and JavaScript

### API Endpoints:
- `GET /` - Home page
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /student/api/register-face` - Face registration
- `POST /student/api/mark-attendance` - Mark attendance
- `POST /teacher/api/create-session` - Create session

---

## 🎯 Next Steps

1. **Explore Features**: Try different user roles and scenarios
2. **Customize**: Modify CSS for your institution's branding
3. **Extend**: Add new features like attendance analytics
4. **Deploy**: Set up production server with proper security

---

**🎉 Welcome to PRESENCE - Your AI-Powered Attendance Solution!**

For questions or issues, refer to the comprehensive documentation in `REQUIREMENTS.md` and `README.md`.
