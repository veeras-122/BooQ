#!/usr/bin/env python3
"""
LibraSync — Library Management System
Run this file to start the application.
"""
from app import app

if __name__ == '__main__':
    print("\n" + "="*55)
    print("  LibraSync — Smart Library Management System")
    print("="*55)
    print("  URL: http://127.0.0.1:5000")
    print("  Librarian Login: admin / admin123")
    print("  Students must register, then get approved.")
    print("="*55 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
