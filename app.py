from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, Librarian, Student
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('lib_'):
            return Librarian.query.get(int(user_id[4:]))
        elif user_id.startswith('stu_'):
            return Student.query.get(int(user_id[4:]))
        return None

    from routes.auth import auth_bp
    from routes.librarian import librarian_bp
    from routes.student import student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(librarian_bp)
    app.register_blueprint(student_bp)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    from models import Librarian, Book, Student
    from werkzeug.security import generate_password_hash

    # Create default librarian
    if not Librarian.query.first():
        librarian = Librarian(
            username='admin',
            email='admin@library.edu',
            name='Head Librarian',
            role='librarian'
        )
        librarian.set_password('admin123')
        db.session.add(librarian)
        db.session.commit()
        print("Default librarian created: admin / admin123")

    # Seed books if empty
    if Book.query.count() < 10:
        seed_books()

def seed_books():
    from models import Book
    books_data = [
        # Computer Science
        ("Introduction to Algorithms", "Thomas H. Cormen", "Algorithms", "Computer Science", 2022, "4th", "978-0262046305"),
        ("Clean Code", "Robert C. Martin", "Software Engineering", "Computer Science", 2008, "1st", "978-0132350884"),
        ("The Pragmatic Programmer", "Andrew Hunt", "Software Engineering", "Computer Science", 2019, "2nd", "978-0135957059"),
        ("Design Patterns", "Gang of Four", "Software Design", "Computer Science", 1994, "1st", "978-0201633610"),
        ("Computer Networks", "Andrew S. Tanenbaum", "Networking", "Computer Science", 2021, "6th", "978-0137523214"),
        ("Operating System Concepts", "Abraham Silberschatz", "Operating Systems", "Computer Science", 2018, "10th", "978-1119456339"),
        ("Database System Concepts", "Abraham Silberschatz", "Databases", "Computer Science", 2019, "7th", "978-0078022159"),
        ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "Artificial Intelligence", "Computer Science", 2020, "4th", "978-0134610993"),
        ("Python Crash Course", "Eric Matthes", "Programming", "Computer Science", 2023, "3rd", "978-1718502703"),
        ("Structure and Interpretation of Computer Programs", "Harold Abelson", "Programming", "Computer Science", 1996, "2nd", "978-0262510875"),
        ("The Art of Computer Programming", "Donald Knuth", "Algorithms", "Computer Science", 2011, "3rd", "978-0201485417"),
        ("Compilers: Principles, Techniques, Tools", "Alfred V. Aho", "Compilers", "Computer Science", 2006, "2nd", "978-0321486813"),
        ("Computer Architecture", "John L. Hennessy", "Architecture", "Computer Science", 2017, "6th", "978-0128119051"),
        ("Machine Learning", "Tom M. Mitchell", "Machine Learning", "Computer Science", 1997, "1st", "978-0070428072"),
        ("Deep Learning", "Ian Goodfellow", "Deep Learning", "Computer Science", 2016, "1st", "978-0262035613"),
        ("Data Structures and Algorithm Analysis", "Mark Allen Weiss", "Data Structures", "Computer Science", 2012, "3rd", "978-0132576277"),
        ("Software Engineering", "Ian Sommerville", "Software Engineering", "Computer Science", 2015, "10th", "978-0133943030"),
        ("Web Development with Node.js", "Ethan Brown", "Web Development", "Computer Science", 2019, "2nd", "978-1491943953"),
        ("JavaScript: The Good Parts", "Douglas Crockford", "Programming", "Computer Science", 2008, "1st", "978-0596517748"),
        ("Linux Command Line", "William Shotts", "Operating Systems", "Computer Science", 2019, "2nd", "978-1593279523"),

        # Electronics & Communication
        ("Electronic Devices and Circuit Theory", "Robert L. Boylestad", "Electronics", "Electronics & Communication", 2012, "11th", "978-0132622264"),
        ("Signals and Systems", "Alan V. Oppenheim", "Signal Processing", "Electronics & Communication", 1996, "2nd", "978-0138147570"),
        ("Communication Systems", "Haykin Simon", "Communications", "Electronics & Communication", 2001, "4th", "978-0471178699"),
        ("Microelectronics Circuit Analysis", "Donald A. Neamen", "Microelectronics", "Electronics & Communication", 2009, "4th", "978-0073529608"),
        ("Digital Communications", "John G. Proakis", "Digital Communications", "Electronics & Communication", 2007, "5th", "978-0072957167"),
        ("VLSI Design", "Wayne Wolf", "VLSI", "Electronics & Communication", 2008, "2nd", "978-0131433403"),
        ("Antenna Theory", "Constantine A. Balanis", "Antennas", "Electronics & Communication", 2016, "4th", "978-1118642061"),
        ("Electromagnetic Fields and Waves", "Paul Lorrain", "Electromagnetics", "Electronics & Communication", 1988, "3rd", "978-0716718239"),
        ("Microprocessor Architecture", "Barry B. Brey", "Microprocessors", "Electronics & Communication", 2008, "8th", "978-0135012642"),
        ("Control Systems Engineering", "Norman S. Nise", "Control Systems", "Electronics & Communication", 2019, "7th", "978-1119474227"),
        ("Digital Signal Processing", "John G. Proakis", "Signal Processing", "Electronics & Communication", 2006, "4th", "978-0131873742"),
        ("Power Electronics", "Ned Mohan", "Power Electronics", "Electronics & Communication", 2002, "3rd", "978-0471226932"),
        ("Wireless Communications", "Andrea Goldsmith", "Wireless", "Electronics & Communication", 2005, "1st", "978-0521837163"),
        ("Fundamentals of Electric Circuits", "Charles K. Alexander", "Circuit Theory", "Electronics & Communication", 2016, "6th", "978-0078028229"),
        ("Optical Fiber Communications", "Gerd Keiser", "Optical Communications", "Electronics & Communication", 2021, "5th", "978-1260454550"),

        # Mechanical Engineering
        ("Engineering Mechanics: Statics", "J.L. Meriam", "Mechanics", "Mechanical Engineering", 2016, "8th", "978-1118919736"),
        ("Thermodynamics: An Engineering Approach", "Yunus Cengel", "Thermodynamics", "Mechanical Engineering", 2018, "9th", "978-1259822674"),
        ("Fluid Mechanics", "Frank M. White", "Fluid Mechanics", "Mechanical Engineering", 2015, "8th", "978-0073398273"),
        ("Mechanics of Materials", "Ferdinand Beer", "Mechanics", "Mechanical Engineering", 2014, "7th", "978-0073398235"),
        ("Machine Design", "Robert L. Norton", "Machine Design", "Mechanical Engineering", 2013, "5th", "978-0133356717"),
        ("Manufacturing Engineering & Technology", "Serope Kalpakjian", "Manufacturing", "Mechanical Engineering", 2013, "7th", "978-0133128741"),
        ("Heat Transfer", "Jack P. Holman", "Heat Transfer", "Mechanical Engineering", 2009, "10th", "978-0073529363"),
        ("Shigley's Mechanical Engineering Design", "Richard G. Budynas", "Machine Design", "Mechanical Engineering", 2014, "10th", "978-0073398204"),
        ("Internal Combustion Engine Fundamentals", "John B. Heywood", "Engines", "Mechanical Engineering", 1988, "1st", "978-0070286375"),
        ("Robotics: Modelling, Planning and Control", "Bruno Siciliano", "Robotics", "Mechanical Engineering", 2008, "1st", "978-1846286414"),

        # Civil Engineering
        ("Structural Analysis", "R.C. Hibbeler", "Structural Engineering", "Civil Engineering", 2017, "10th", "978-0134610672"),
        ("Soil Mechanics and Foundations", "Muni Budhu", "Geotechnical Engineering", "Civil Engineering", 2010, "3rd", "978-0470556846"),
        ("Reinforced Concrete Design", "Chu-Kia Wang", "Concrete Structures", "Civil Engineering", 1998, "6th", "978-0471008996"),
        ("Highway Engineering", "Paul H. Wright", "Transportation", "Civil Engineering", 1996, "6th", "978-0471002758"),
        ("Environmental Engineering", "Howard S. Peavy", "Environmental", "Civil Engineering", 1985, "1st", "978-0070491809"),
        ("Surveying", "Francis H. Moffitt", "Surveying", "Civil Engineering", 1987, "8th", "978-0060445348"),
        ("Construction Management", "Daniel W. Halpin", "Construction", "Civil Engineering", 2011, "4th", "978-0470447239"),
        ("Hydraulics and Fluid Mechanics", "Modi P.N.", "Hydraulics", "Civil Engineering", 2019, "21st", "978-9385041419"),

        # Electrical Engineering
        ("Electric Machinery Fundamentals", "Stephen J. Chapman", "Electrical Machines", "Electrical Engineering", 2011, "5th", "978-0073529547"),
        ("Power System Analysis", "John J. Grainger", "Power Systems", "Electrical Engineering", 1994, "1st", "978-0070612938"),
        ("Electric Power Systems", "Weedy B.M.", "Power Systems", "Electrical Engineering", 2012, "5th", "978-0470682685"),
        ("Electrical Technology", "B.L. Theraja", "General Electrical", "Electrical Engineering", 2005, "24th", "978-8121924405"),
        ("High Voltage Engineering", "M.S. Naidu", "High Voltage", "Electrical Engineering", 2013, "3rd", "978-0071333116"),
        ("Switchgear and Protection", "Sunil S. Rao", "Protection", "Electrical Engineering", 2008, "15th", "978-8177000054"),

        # Information Technology
        ("Information Security Management", "Harold F. Tipton", "Security", "Information Technology", 2007, "6th", "978-0849374951"),
        ("Network Security Essentials", "William Stallings", "Network Security", "Information Technology", 2017, "6th", "978-0134527338"),
        ("Cloud Computing", "Thomas Erl", "Cloud Computing", "Information Technology", 2013, "1st", "978-0133387520"),
        ("Big Data Analytics", "Anil Maheshwari", "Data Analytics", "Information Technology", 2018, "1st", "978-0199469864"),
        ("Cybersecurity Essentials", "Charles J. Brooks", "Cybersecurity", "Information Technology", 2018, "1st", "978-1119362395"),
        ("IT Project Management", "Kathy Schwalbe", "Project Management", "Information Technology", 2018, "9th", "978-1337101356"),
        ("Systems Analysis and Design", "Alan Dennis", "Systems Design", "Information Technology", 2018, "7th", "978-1119496489"),
        ("Enterprise Resource Planning", "Mary Sumner", "ERP", "Information Technology", 2005, "1st", "978-0131330788"),

        # Biotechnology
        ("Molecular Biology of the Cell", "Bruce Alberts", "Cell Biology", "Biotechnology", 2014, "6th", "978-0815344322"),
        ("Biochemistry", "Jeremy M. Berg", "Biochemistry", "Biotechnology", 2018, "9th", "978-1319114671"),
        ("Genetics: Analysis and Principles", "Robert J. Brooker", "Genetics", "Biotechnology", 2018, "6th", "978-1259700903"),
        ("Microbiology: An Introduction", "Gerard J. Tortora", "Microbiology", "Biotechnology", 2018, "13th", "978-0134605180"),
        ("Bioreactor Design", "Pauline M. Doran", "Bioprocess Engineering", "Biotechnology", 2012, "2nd", "978-0122208515"),

        # Mathematics
        ("Calculus", "James Stewart", "Calculus", "Mathematics", 2015, "8th", "978-1285740621"),
        ("Linear Algebra and Its Applications", "David C. Lay", "Linear Algebra", "Mathematics", 2015, "5th", "978-0321982384"),
        ("Probability and Statistics", "Murray R. Spiegel", "Statistics", "Mathematics", 2013, "4th", "978-0071795579"),
        ("Abstract Algebra", "David S. Dummit", "Algebra", "Mathematics", 2003, "3rd", "978-0471433347"),
        ("Real Analysis", "Walter Rudin", "Analysis", "Mathematics", 1987, "3rd", "978-0070542358"),
        ("Numerical Methods", "Steven C. Chapra", "Numerical Methods", "Mathematics", 2014, "7th", "978-0073397962"),
        ("Differential Equations", "Dennis G. Zill", "Differential Equations", "Mathematics", 2017, "10th", "978-1305965799"),
        ("Graph Theory", "Frank Harary", "Graph Theory", "Mathematics", 1994, "1st", "978-0201027877"),

        # Physics
        ("University Physics", "Hugh D. Young", "General Physics", "Physics", 2019, "15th", "978-0135159552"),
        ("Introduction to Quantum Mechanics", "David J. Griffiths", "Quantum Mechanics", "Physics", 2018, "3rd", "978-1107189638"),
        ("Classical Mechanics", "Herbert Goldstein", "Mechanics", "Physics", 2001, "3rd", "978-0201657029"),
        ("Electrodynamics", "David J. Griffiths", "Electrodynamics", "Physics", 2017, "4th", "978-1108420419"),
        ("Statistical Mechanics", "R.K. Pathria", "Statistical Mechanics", "Physics", 2011, "3rd", "978-0123821881"),
        ("Optics", "Eugene Hecht", "Optics", "Physics", 2017, "5th", "978-0133977226"),
        ("Nuclear Physics", "Krane Kenneth", "Nuclear Physics", "Physics", 1987, "1st", "978-047180553X"),

        # Chemical Engineering
        ("Chemical Reaction Engineering", "Octave Levenspiel", "Reaction Engineering", "Chemical Engineering", 1999, "3rd", "978-0471254249"),
        ("Transport Phenomena", "R. Byron Bird", "Transport Phenomena", "Chemical Engineering", 2006, "2nd", "978-0470115398"),
        ("Mass Transfer Operations", "Robert E. Treybal", "Mass Transfer", "Chemical Engineering", 1987, "3rd", "978-0070651760"),
        ("Chemical Engineering Design", "Gavin Towler", "Process Design", "Chemical Engineering", 2012, "2nd", "978-0080966595"),
        ("Process Dynamics and Control", "Dale E. Seborg", "Process Control", "Chemical Engineering", 2016, "4th", "978-1119285915"),
    ]

    for title, author, category, dept, year, edition, isbn in books_data:
        if not Book.query.filter_by(title=title, author=author).first():
            book = Book(
                title=title, author=author, category=category,
                department=dept, year=year, edition=edition, isbn=isbn,
                total_copies=3, available_copies=3
            )
            db.session.add(book)
    db.session.commit()
    print(f"Books seeded successfully!")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
