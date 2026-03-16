# 📚 BooQ — Smart Library Management System

A fully-featured digital library management system built with Flask, SQLite, and Bootstrap.

---

## 🚀 Quick Start

### Windows
1. Make sure Python 3.9+ is installed from https://python.org
2. Double-click `start.bat` — it will set everything up automatically
3. Open your browser and go to **http://127.0.0.1:5000**

### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```
Then open **http://127.0.0.1:5000**

### Manual Setup
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## 🔑 Default Login

| Role      | Username | Password |
|-----------|----------|----------|
| Librarian | admin    | admin123 |

**Students:** Register via the Register page → Wait for librarian approval → Login

---

## ✨ Features

### Librarian
- Dashboard with stats and recent activity
- Book Management: Add / Edit / Delete books with cover images
- Student Management: Approve / Reject registrations
- Borrow Management: Issue books to students, set custom loan periods
- Return Management: Process returns, auto-calculate fines
- Fine Management: Track and mark fine payments
- Filter books by department, category, search

### Student
- Register and await librarian approval
- Department-wise book recommendations on dashboard
- Full book catalog with search (title, author, category, dept)
- Reserve books online (show ID at library counter to collect)
- View active borrows, due dates, overdue warnings
- Due date notifications (auto-generated when 3 days or less)
- Profile page with full borrowing history
- Maximum 4 books at a time (enforced)

---

## 🗂️ Project Structure

```
library_system/
├── app.py              # Main Flask app + seeding
├── config.py           # Configuration
├── run.py              # Entry point
├── requirements.txt
├── start.bat           # Windows startup
├── start.sh            # Linux/Mac startup
├── models/
│   └── models.py       # Database models (Librarian, Student, Book, BorrowBook, Notification)
├── routes/
│   ├── auth.py         # Login, Register, Logout
│   ├── librarian.py    # All librarian routes
│   └── student.py      # All student routes
├── static/
│   ├── css/main.css    # Stylesheet
│   ├── js/main.js      # JavaScript
│   └── uploads/        # Book cover images
└── templates/
    ├── base.html
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── librarian/
    │   ├── dashboard.html
    │   ├── books.html
    │   ├── add_book.html
    │   ├── edit_book.html
    │   ├── students.html
    │   ├── student_detail.html
    │   ├── borrows.html
    │   └── fines.html
    └── student/
        ├── dashboard.html
        ├── catalog.html
        ├── my_books.html
        ├── profile.html
        └── notifications.html
```

---

## 📊 Database Schema

| Table         | Key Fields |
|---------------|------------|
| librarians    | id, username, email, password_hash, name |
| students      | id, student_id, name, email, phone, department, year, is_approved, total_fine, fine_paid |
| books         | id, title, author, category, department, year, edition, isbn, total_copies, available_copies, image |
| borrow_books  | id, student_id, book_id, borrow_date, due_date, return_date, status, fine_amount |
| notifications | id, student_id, message, is_read, notification_type |

---

## 💡 Business Rules

- Max 4 books per student (reserved + borrowed combined)
- Book availability decreases immediately on reservation
- Default loan period: 10 days (librarian can set 1–30 days)
- Fine: ₹5 per day after due date
- Students must be approved by librarian before they can login
- Librarian issues books by verifying student ID card physically
- Fines auto-calculated on return; librarian marks payment

---

## 🔧 Configuration (config.py)

| Setting           | Default  | Description           |
|-------------------|----------|-----------------------|
| MAX_BOOKS_PER_STUDENT | 4    | Book borrowing limit  |
| DEFAULT_BORROW_DAYS   | 10   | Default loan period   |
| FINE_PER_DAY          | 5    | Fine in rupees/day    |

---

## 📖 Seeded Data

The system automatically seeds ~100 books across 10 departments:
- Computer Science, Electronics & Communication, Mechanical Engineering
- Civil Engineering, Electrical Engineering, Information Technology
- Chemical Engineering, Biotechnology, Mathematics, Physics

---
Built with Flask · SQLAlchemy · Bootstrap 5 · Playfair Display + DM Sans
