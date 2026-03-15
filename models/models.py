from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta

db = SQLAlchemy()

class Librarian(UserMixin, db.Model):
    __tablename__ = 'librarians'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='librarian')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"lib_{self.id}"


class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    total_fine = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(20), default='student')

    borrows = db.relationship('BorrowBook', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"stu_{self.id}"

    @property
    def active_borrows_count(self):
        return self.borrows.filter_by(status='borrowed').count()

    @property
    def pending_fine(self):
        total = 0.0
        for borrow in self.borrows.filter_by(status='borrowed').all():
            total += borrow.current_fine
        return total + (self.total_fine - self.fine_paid)

    @property
    def pending_reservations(self):
        return self.borrows.filter_by(status='reserved').count()


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    edition = db.Column(db.String(50))
    isbn = db.Column(db.String(20))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    image = db.Column(db.String(255), default='default_book.jpg')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrows = db.relationship('BorrowBook', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_available(self):
        return self.available_copies > 0


class BorrowBook(db.Model):
    __tablename__ = 'borrow_books'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrow_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='reserved')  # reserved, borrowed, returned, rejected
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def current_fine(self):
        if self.status == 'borrowed' and self.due_date:
            today = date.today()
            if today > self.due_date:
                overdue_days = (today - self.due_date).days
                return overdue_days * 5.0  # ₹5 per day
        return 0.0

    @property
    def is_overdue(self):
        if self.status == 'borrowed' and self.due_date:
            return date.today() > self.due_date
        return False

    @property
    def days_until_due(self):
        if self.status == 'borrowed' and self.due_date:
            delta = self.due_date - date.today()
            return delta.days
        return None


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(30), default='info')  # info, warning, danger
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref='notifications')
