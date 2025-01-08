from flask import Blueprint, flash, redirect, render_template, session, url_for
import pymysql
from database.connect import get_db_connection

home_bp = Blueprint('main', __name__, template_folder='templates')


@home_bp.route('/')
def main():
    conn = get_db_connection()
    user_id = session.get('user_id')
    role = session.get('role')

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 如果是學生，獲取已註冊的課程清單
    enrolled_courses = set()
    if role == '學生':
        cursor.execute("SELECT course_id FROM student_courses WHERE account = %s", (user_id,))
        enrolled_courses = {course['course_id'] for course in cursor.fetchall()}

    if role == '教授':
        cursor.execute("SELECT * FROM courses WHERE account = %s", (user_id,))
    else:
        cursor.execute("SELECT * FROM courses")
    
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    # 將 courses 和已註冊資訊傳遞到模板
    return render_template('main/index.html', 
                         courses=courses, 
                         enrolled_courses=enrolled_courses)


@home_bp.route('/enroll/<int:course_id>', methods=['POST'])
def enroll_course(course_id):

    conn = get_db_connection()
    user_id = session.get('user_id')
    role = session.get('role')
    
    if not user_id:
        flash("請先登入", "danger")
        return redirect(url_for('login_logout.login'))
    
    if role != '學生':
        flash("教授無法註冊課程", "danger")
        return redirect(url_for('main.main'))
    
    # 檢查是否已經註冊過這門課
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_courses WHERE account = %s AND course_id = %s", (user_id, course_id))
    existing_enrollment = cursor.fetchone()
    
    if existing_enrollment:
        flash("您已經註冊過這門課程", "warning")
    else:
        # 註冊新課程
        cursor.execute("""
            INSERT INTO student_courses (account, course_id) VALUES (%s, %s)""", (user_id, course_id))
        conn.commit()
        flash("已成功註冊課程！", "success")
    
    cursor.close()
    conn.close()
    return redirect(url_for('main.main'))