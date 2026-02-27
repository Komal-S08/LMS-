import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Course
from forms import CourseForm
from auth import auth_bp, teacher_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)

    # Ensure upload folder exists
    os.makedirs("static/uploads", exist_ok=True)

    # ---------------- HOME ----------------
    @app.route('/')
    def index():
        courses = Course.query.all()
        return render_template('index.html', courses=courses)

    # ---------------- DASHBOARD ----------------
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.is_teacher():
            my_courses = Course.query.filter_by(
                instructor_id=current_user.id
            ).all()
            return render_template('dashboard.html',
                                   teaching_courses=my_courses,
                                   enrolled_courses=[])
        else:
            return render_template('dashboard.html',
                                   teaching_courses=[],
                                   enrolled_courses=current_user.enrolled_courses)

    # ---------------- CREATE COURSE ----------------
    @app.route('/course/create', methods=['GET', 'POST'])
    @teacher_required
    def create_course():
        form = CourseForm()

        if form.validate_on_submit():

            filename = None
            if form.material_file.data:
                file = form.material_file.data
                filename = secure_filename(file.filename)
                file.save(os.path.join("static/uploads", filename))

            price = form.price.data or 0.0

            course = Course(
                title=form.title.data,
                code=form.code.data,
                description=form.description.data,
                material_file=filename,
                video_url=form.video_url.data,
                price=price,
                is_free=(price == 0),
                instructor_id=current_user.id
            )

            db.session.add(course)
            db.session.commit()

            flash("Course created successfully!", "success")
            return redirect(url_for('dashboard'))

        return render_template('create_course.html', form=form)

    # ---------------- COURSE DETAIL ----------------
    @app.route('/course/<int:course_id>')
    def course_detail(course_id):
        course = Course.query.get_or_404(course_id)

        is_enrolled = False
        if current_user.is_authenticated:
            is_enrolled = course in current_user.enrolled_courses

        return render_template('course_detail.html',
                               course=course,
                               is_enrolled=is_enrolled)

    # ---------------- ENROLL ----------------
    @app.route('/course/<int:course_id>/enroll', methods=['POST'])
    @login_required
    def enroll_course(course_id):

        course = Course.query.get_or_404(course_id)

        if current_user.is_teacher():
            flash("Teachers cannot enroll in courses.", "danger")
            return redirect(url_for('course_detail', course_id=course_id))

        if course in current_user.enrolled_courses:
            flash("Already enrolled.", "info")
            return redirect(url_for('course_detail', course_id=course_id))

        if not course.is_free:
            flash("Payment integration coming soon.", "info")
            return redirect(url_for('course_detail', course_id=course_id))

        current_user.enrolled_courses.append(course)
        db.session.commit()
        flash("Successfully enrolled!", "success")

        return redirect(url_for('course_detail', course_id=course_id))

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)