from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import db, User
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        password = request.form.get('password')

        user = User.query.filter_by(roll_number=roll_number).first()

        if user and user.check_password(password):
            login_user(user)

            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('teacher.dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form

        # Check if user exists (by roll number OR email)
        existing = User.query.filter(
            (User.roll_number == data['roll_number']) | 
            (User.email == data['email'])
        ).first()
        
        if existing:
            flash('User with this Roll Number or Email already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(
            roll_number=data['roll_number'],
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'student'),
            device_uuid=data.get('device_uuid')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')
