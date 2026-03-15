from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Librarian, Student, Book, BorrowBook, Notification
from datetime import date, datetime, timedelta
from functools import wraps
import os
from werkzeug.utils import secure_filename
from config import Config

librarian_bp = Blueprint('librarian', __name__, url_prefix='/librarian')

def librarian_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'librarian':
            flash('Access denied. Librarian only.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

DEPARTMENTS = [
    'Computer Science', 'Electronics & Communication', 'Mechanical Engineering',
    'Civil Engineering', 'Electrical Engineering', 'Information Technology',
    'Chemical Engineering', 'Biotechnology', 'Mathematics', 'Physics'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ─── Dashboard ───────────────────────────────────────────────────────────────

@librarian_bp.route('/dashboard')
@login_required
@librarian_required
def dashboard():
    total_books = Book.query.count()
    total_students = Student.query.filter_by(is_approved=True).count()
    pending_approvals = Student.query.filter_by(is_approved=False).count()
    active_borrows = BorrowBook.query.filter_by(status='borrowed').count()
    pending_reservations = BorrowBook.query.filter_by(status='reserved').count()
    overdue_books = []
    for b in BorrowBook.query.filter_by(status='borrowed').all():
        if b.is_overdue:
            overdue_books.append(b)
    recent_activity = BorrowBook.query.order_by(BorrowBook.created_at.desc()).limit(8).all()
    return render_template('librarian/dashboard.html',
        total_books=total_books,
        total_students=total_students,
        pending_approvals=pending_approvals,
        active_borrows=active_borrows,
        pending_reservations=pending_reservations,
        overdue_count=len(overdue_books),
        recent_activity=recent_activity
    )

# ─── Book Management ─────────────────────────────────────────────────────────

@librarian_bp.route('/books')
@login_required
@librarian_required
def books():
    query = request.args.get('q', '')
    dept = request.args.get('dept', '')
    category = request.args.get('category', '')
    books = Book.query
    if query:
        books = books.filter(
            (Book.title.ilike(f'%{query}%')) |
            (Book.author.ilike(f'%{query}%')) |
            (Book.isbn.ilike(f'%{query}%'))
        )
    if dept:
        books = books.filter_by(department=dept)
    if category:
        books = books.filter_by(category=category)
    books = books.order_by(Book.title).all()
    categories = db.session.query(Book.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template('librarian/books.html', books=books, departments=DEPARTMENTS,
                           categories=categories, query=query, selected_dept=dept, selected_cat=category)

@librarian_bp.route('/books/add', methods=['GET', 'POST'])
@login_required
@librarian_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '')
        edition = request.form.get('edition', '').strip()
        isbn = request.form.get('isbn', '').strip()
        total_copies = int(request.form.get('total_copies', 1))
        description = request.form.get('description', '').strip()

        image_filename = 'default_book.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(Config.UPLOAD_FOLDER, unique_name))
                image_filename = unique_name

        book = Book(
            title=title, author=author, category=category, department=department,
            year=int(year) if year else None, edition=edition, isbn=isbn,
            total_copies=total_copies, available_copies=total_copies,
            image=image_filename, description=description
        )
        db.session.add(book)
        db.session.commit()
        flash(f'Book "{title}" added successfully!', 'success')
        return redirect(url_for('librarian.books'))

    return render_template('librarian/add_book.html', departments=DEPARTMENTS)

@librarian_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@librarian_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.category = request.form.get('category', '').strip()
        book.department = request.form.get('department', '').strip()
        book.edition = request.form.get('edition', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.description = request.form.get('description', '').strip()
        year = request.form.get('year', '')
        book.year = int(year) if year else None
        new_total = int(request.form.get('total_copies', book.total_copies))
        diff = new_total - book.total_copies
        book.total_copies = new_total
        book.available_copies = max(0, book.available_copies + diff)

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(Config.UPLOAD_FOLDER, unique_name))
                book.image = unique_name

        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('librarian.books'))

    return render_template('librarian/edit_book.html', book=book, departments=DEPARTMENTS)

@librarian_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
@librarian_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'info')
    return redirect(url_for('librarian.books'))

# ─── Student Management ───────────────────────────────────────────────────────

@librarian_bp.route('/students')
@login_required
@librarian_required
def students():
    query = request.args.get('q', '')
    filter_status = request.args.get('status', 'all')
    students = Student.query
    if query:
        students = students.filter(
            (Student.name.ilike(f'%{query}%')) |
            (Student.student_id.ilike(f'%{query}%')) |
            (Student.email.ilike(f'%{query}%'))
        )
    if filter_status == 'pending':
        students = students.filter_by(is_approved=False)
    elif filter_status == 'approved':
        students = students.filter_by(is_approved=True)
    students = students.order_by(Student.created_at.desc()).all()
    return render_template('librarian/students.html', students=students, query=query, filter_status=filter_status)

@librarian_bp.route('/students/approve/<int:student_id>', methods=['POST'])
@login_required
@librarian_required
def approve_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_approved = True
    notif = Notification(
        student_id=student.id,
        message=f'Welcome {student.name}! Your library account has been approved. You can now login and access our collection.',
        notification_type='success'
    )
    db.session.add(notif)
    db.session.commit()
    flash(f'Student {student.name} approved.', 'success')
    return redirect(url_for('librarian.students'))

@librarian_bp.route('/students/reject/<int:student_id>', methods=['POST'])
@login_required
@librarian_required
def reject_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student registration rejected and removed.', 'info')
    return redirect(url_for('librarian.students'))

@librarian_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@librarian_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('librarian.students'))

@librarian_bp.route('/students/<int:student_id>')
@login_required
@librarian_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    borrows = BorrowBook.query.filter_by(student_id=student_id).order_by(BorrowBook.created_at.desc()).all()
    return render_template('librarian/student_detail.html', student=student, borrows=borrows)

# ─── Borrow Management ────────────────────────────────────────────────────────

@librarian_bp.route('/borrows')
@login_required
@librarian_required
def borrows():
    status = request.args.get('status', 'all')
    query = request.args.get('q', '')
    borrows = BorrowBook.query
    if status != 'all':
        borrows = borrows.filter_by(status=status)
    borrows = borrows.order_by(BorrowBook.created_at.desc()).all()
    if query:
        borrows = [b for b in borrows if
                   query.lower() in b.student.name.lower() or
                   query.lower() in b.student.student_id.lower() or
                   query.lower() in b.book.title.lower()]
    return render_template('librarian/borrows.html', borrows=borrows, status=status, query=query)

@librarian_bp.route('/borrows/issue/<int:borrow_id>', methods=['POST'])
@login_required
@librarian_required
def issue_book(borrow_id):
    borrow = BorrowBook.query.get_or_404(borrow_id)
    if borrow.status != 'reserved':
        flash('This reservation is not pending.', 'warning')
        return redirect(url_for('librarian.borrows'))

    days = int(request.form.get('days', 10))
    days = min(max(days, 1), 30)

    borrow.status = 'borrowed'
    borrow.borrow_date = date.today()
    borrow.due_date = date.today() + timedelta(days=days)

    notif = Notification(
        student_id=borrow.student_id,
        message=f'Your book "{borrow.book.title}" has been issued. Due date: {borrow.due_date.strftime("%d %b %Y")}.',
        notification_type='info'
    )
    db.session.add(notif)
    db.session.commit()
    flash('Book issued successfully!', 'success')
    return redirect(url_for('librarian.borrows'))

@librarian_bp.route('/borrows/return/<int:borrow_id>', methods=['POST'])
@login_required
@librarian_required
def return_book(borrow_id):
    borrow = BorrowBook.query.get_or_404(borrow_id)
    if borrow.status != 'borrowed':
        flash('This book is not currently borrowed.', 'warning')
        return redirect(url_for('librarian.borrows'))

    fine = borrow.current_fine
    borrow.status = 'returned'
    borrow.return_date = date.today()
    borrow.fine_amount = fine

    # Restore book availability
    borrow.book.available_copies = min(borrow.book.total_copies, borrow.book.available_copies + 1)

    if fine > 0:
        borrow.student.total_fine += fine
        notif = Notification(
            student_id=borrow.student_id,
            message=f'Book "{borrow.book.title}" returned. Fine of ₹{fine:.2f} has been added to your account.',
            notification_type='warning'
        )
    else:
        notif = Notification(
            student_id=borrow.student_id,
            message=f'Book "{borrow.book.title}" returned successfully. No fine incurred!',
            notification_type='success'
        )
    db.session.add(notif)
    db.session.commit()
    flash(f'Book returned. Fine: ₹{fine:.2f}', 'success' if fine == 0 else 'warning')
    return redirect(url_for('librarian.borrows'))

@librarian_bp.route('/borrows/reject/<int:borrow_id>', methods=['POST'])
@login_required
@librarian_required
def reject_reservation(borrow_id):
    borrow = BorrowBook.query.get_or_404(borrow_id)
    borrow.book.available_copies += 1
    notif = Notification(
        student_id=borrow.student_id,
        message=f'Your reservation for "{borrow.book.title}" was rejected by the librarian.',
        notification_type='danger'
    )
    db.session.add(notif)
    db.session.delete(borrow)
    db.session.commit()
    flash('Reservation rejected.', 'info')
    return redirect(url_for('librarian.borrows'))

@librarian_bp.route('/fines')
@login_required
@librarian_required
def fines():
    students_with_fines = Student.query.filter(Student.total_fine > Student.fine_paid).all()
    return render_template('librarian/fines.html', students=students_with_fines)

@librarian_bp.route('/fines/mark_paid/<int:student_id>', methods=['POST'])
@login_required
@librarian_required
def mark_fine_paid(student_id):
    student = Student.query.get_or_404(student_id)
    amount = float(request.form.get('amount', 0))
    student.fine_paid += amount
    notif = Notification(
        student_id=student.id,
        message=f'Fine payment of ₹{amount:.2f} recorded. Thank you!',
        notification_type='success'
    )
    db.session.add(notif)
    db.session.commit()
    flash(f'Fine of ₹{amount:.2f} marked as paid for {student.name}.', 'success')
    return redirect(url_for('librarian.fines'))
