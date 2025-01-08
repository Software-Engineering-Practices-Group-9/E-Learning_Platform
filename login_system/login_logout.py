from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.connect import get_db_connection

login_logout_bp = Blueprint('login_logout', __name__, template_folder='templates')

conn = get_db_connection()

@login_logout_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form.get('account')
        password = request.form.get('password')

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE account = %s AND password = %s", (account, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[1]
            session['role'] = user[3]
            flash('登入成功！', 'success')

            if session['role'] == '學生':
                return redirect(url_for('main.main'))
            elif session['role'] == '教授':
                session['professor_id'] = user[1]
                return redirect(url_for('create_course.course_page'))
        else:
            flash('登入失敗，請檢查帳號和密碼', 'danger')

    return render_template('login_system/login.html')

@login_logout_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.main'))