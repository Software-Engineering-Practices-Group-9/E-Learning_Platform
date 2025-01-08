from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connect import get_db_connection

register_bp = Blueprint('register', __name__, template_folder='templates')

conn = get_db_connection()

@register_bp.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        account = request.form.get('account')
        name = request.form.get('name')
        role = request.form.get('role')
        department = request.form.get('department')
        password = request.form.get('password')

        if not account or not password:
            flash('此帳號已存在', 'danger')
        else:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE account = %s", (account,))
                    if cursor.fetchone():
                        flash('這個 ID 已經存在，請使用其他 ID。', 'danger')
                        return redirect(url_for('register.register'))

                    sql = """
                        INSERT INTO users (account, name, role, department, password) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (account, name, role, department, password))
                    conn.commit()
                flash('帳戶成功建立！', 'success')
            except Exception as e:
                flash(f'錯誤：{e}', 'danger')

    return render_template('login_system/register.html')