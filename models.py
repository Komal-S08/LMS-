from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Many-to-Many Enrollment Table
enrollments = db.Table(
    'enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')

    enrolled_courses = db.relationship(
        'Course',
        secondary=enrollments,
        back_populates='students'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self):
        return self.role == "teacher"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)

    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # NEW FEATURES
    material_file = db.Column(db.String(300))   # PDF filename
    video_url = db.Column(db.String(500))
    price = db.Column(db.Float, default=0.0)
    is_free = db.Column(db.Boolean, default=True)

    students = db.relationship(
        'User',
        secondary=enrollments,
        back_populates='enrolled_courses'
    )