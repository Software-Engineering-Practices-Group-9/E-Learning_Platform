import datetime
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
import pymysql

from database.connect import get_db_connection

student_course_bp = Blueprint('student_course', __name__, template_folder='templates')

@student_course_bp.route('/', methods=['GET', 'POST'])
def student_page():
    conn = get_db_connection()
    user_id = session.get('user_id')
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 使用 JOIN 來獲取完整的課程信息
    cursor.execute("""SELECT c.* FROM courses c JOIN student_courses sc ON c.course_id = sc.course_id WHERE sc.account = %s """, (user_id,))
    
    enrolled_courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('student_course/student_course.html', courses=enrolled_courses)

@student_course_bp.route('/unenroll/<course_id>', methods=['POST'])
def unenroll_course(course_id):
    conn = get_db_connection()
    user_id = session.get('user_id')
    
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM student_courses WHERE account = %s AND course_id = %s""", (user_id, course_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("已成功退選課程！", "success")
    return redirect(url_for('student_course.student_page'))