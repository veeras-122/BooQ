from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Librarian, Student, Notification
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

def get_user_by_id(user_id):
    if user_id.startswith('lib_'):
        return Librarian.query.get(int(user_id[4:]))
    elif user_id.startswith('stu_'):
        return Student.query.get(int(user_id[4:]))
    return None

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'librarian':
            return redirect(url_for('librarian.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'librarian':
            return redirect(url_for('librarian.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student')

        if role == 'librarian':
            user = Librarian.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user, remember=True)
                return redirect(url_for('librarian.dashboard'))
            flash('Invalid librarian credentials.', 'danger')
        else:
            user = Student.query.filter(
                (Student.student_id == username) | (Student.email == username)
            ).first()
            if user and user.check_password(password):
                if not user.is_approved:
                    flash('Your account is pending approval by the librarian.', 'warning')
                    return redirect(url_for('auth.login'))
                login_user(user, remember=True)
                return redirect(url_for('student.dashboard'))
            flash('Invalid student credentials.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))

    departments = [
        'Computer Science', 'Electronics & Communication', 'Mechanical Engineering',
        'Civil Engineering', 'Electrical Engineering', 'Information Technology',
        'Chemical Engineering', 'Biotechnology', 'Mathematics', 'Physics'
    ]

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not all([student_id, name, email, department, year, password]):
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html', departments=departments)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', departments=departments)

        if Student.query.filter_by(student_id=student_id).first():
            flash('Student ID already registered.', 'danger')
            return render_template('auth/register.html', departments=departments)

        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', departments=departments)

        student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone,
            department=department,
            year=int(year),
            is_approved=False
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful! Please wait for librarian approval before logging in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', departments=departments)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
