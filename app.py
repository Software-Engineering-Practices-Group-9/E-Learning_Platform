from flask import Flask
import os
from dotenv import load_dotenv
from main.main import home_bp
from account_management.account import account_mgmt_bp
from login_system.register import register_bp
from login_system.login_logout import login_logout_bp
from create_course.create_course import create_course_bp
from student_course.student_course import student_course_bp
from create_course.discussion import discussion_bp
from student_course.course import course_bp
from student_course.quiz import quiz_bp
from student_course.calendar import calendar_bp

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(home_bp)
app.register_blueprint(account_mgmt_bp, url_prefix='/account')
app.register_blueprint(register_bp, url_prefix='/register')
app.register_blueprint(login_logout_bp, url_prefix='/login')
app.register_blueprint(create_course_bp, url_prefix='/create_course')
app.register_blueprint(student_course_bp, url_prefix='/student_course')
app.register_blueprint(discussion_bp, url_prefix='/course_list')
app.register_blueprint(course_bp, url_prefix='/course')
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(calendar_bp, url_prefix='/calendar')

if __name__ == '__main__':
    app.run(debug=True)