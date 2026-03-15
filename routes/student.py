from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Student, Book, BorrowBook, Notification
from datetime import date, timedelta
from functools import wraps

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Auto-generate due date notifications
    for borrow in current_user.borrows.filter_by(status='borrowed').all():
        days_left = borrow.days_until_due
        if days_left is not None and days_left <= 3 and days_left >= 0:
            existing = Notification.query.filter_by(
                student_id=current_user.id,
                message=f'Reminder: "{borrow.book.title}" is due in {days_left} day(s)!'
            ).first()
            if not existing:
                notif = Notification(
                    student_id=current_user.id,
                    message=f'Reminder: "{borrow.book.title}" is due in {days_left} day(s)!',
                    notification_type='warning'
                )
                db.session.add(notif)
        elif days_left is not None and days_left < 0:
            existing = Notification.query.filter_by(
                student_id=current_user.id,
                message=f'OVERDUE: "{borrow.book.title}" is {abs(days_left)} day(s) overdue!'
            ).first()
            if not existing:
                notif = Notification(
                    student_id=current_user.id,
                    message=f'OVERDUE: "{borrow.book.title}" is {abs(days_left)} day(s) overdue!',
                    notification_type='danger'
                )
                db.session.add(notif)
    db.session.commit()

    # Recommended books by department
    recommended = Book.query.filter_by(department=current_user.department).filter(
        Book.available_copies > 0
    ).order_by(Book.created_at.desc()).limit(10).all()

    active_borrows = current_user.borrows.filter(
        BorrowBook.status.in_(['borrowed', 'reserved'])
    ).all()

    notifications = Notification.query.filter_by(
        student_id=current_user.id, is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()

    return render_template('student/dashboard.html',
        recommended=recommended,
        active_borrows=active_borrows,
        notifications=notifications
    )

@student_bp.route('/catalog')
@login_required
@student_required
def catalog():
    query = request.args.get('q', '')
    dept = request.args.get('dept', '')
    category = request.args.get('category', '')

    books = Book.query
    if query:
        books = books.filter(
            (Book.title.ilike(f'%{query}%')) |
            (Book.author.ilike(f'%{query}%')) |
            (Book.category.ilike(f'%{query}%'))
        )
    if dept:
        books = books.filter_by(department=dept)
    if category:
        books = books.filter_by(category=category)

    books = books.order_by(Book.title).all()
    departments = db.session.query(Book.department).distinct().all()
    departments = [d[0] for d in departments]
    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]

    # Check which books user has already reserved/borrowed
    user_book_ids = {b.book_id for b in current_user.borrows.filter(
        BorrowBook.status.in_(['reserved', 'borrowed'])
    ).all()}

    return render_template('student/catalog.html',
        books=books, departments=departments, categories=categories,
        query=query, selected_dept=dept, selected_cat=category,
        user_book_ids=user_book_ids
    )

@student_bp.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
@student_required
def reserve_book(book_id):
    book = Book.query.get_or_404(book_id)

    # Check max books limit
    active_count = current_user.borrows.filter(
        BorrowBook.status.in_(['reserved', 'borrowed'])
    ).count()
    if active_count >= 4:
        flash('You have reached the maximum limit of 4 books.', 'danger')
        return redirect(url_for('student.catalog'))

    # Check already reserved this book
    existing = current_user.borrows.filter_by(book_id=book_id).filter(
        BorrowBook.status.in_(['reserved', 'borrowed'])
    ).first()
    if existing:
        flash('You already have this book reserved or borrowed.', 'warning')
        return redirect(url_for('student.catalog'))

    # Check availability
    if book.available_copies <= 0:
        flash('This book is currently not available.', 'danger')
        return redirect(url_for('student.catalog'))

    # Reserve the book
    borrow = BorrowBook(
        student_id=current_user.id,
        book_id=book_id,
        status='reserved'
    )
    book.available_copies -= 1
    db.session.add(borrow)
    db.session.commit()

    flash(f'"{book.title}" reserved! Show your ID card to the librarian to collect the book.', 'success')
    return redirect(url_for('student.catalog'))

@student_bp.route('/my_books')
@login_required
@student_required
def my_books():
    borrows = current_user.borrows.order_by(BorrowBook.created_at.desc()).all()
    return render_template('student/my_books.html', borrows=borrows)

@student_bp.route('/profile')
@login_required
@student_required
def profile():
    borrows = current_user.borrows.order_by(BorrowBook.created_at.desc()).all()
    pending_fine = current_user.pending_fine
    return render_template('student/profile.html', borrows=borrows, pending_fine=pending_fine)

@student_bp.route('/notifications/mark_read', methods=['POST'])
@login_required
@student_required
def mark_notifications_read():
    Notification.query.filter_by(student_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})

@student_bp.route('/notifications')
@login_required
@student_required
def notifications():
    notifs = Notification.query.filter_by(student_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    # Mark all as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('student/notifications.html', notifications=notifs)
