from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.connect import get_db_connection


account_mgmt_bp = Blueprint('account_management', __name__, template_folder='templates')

conn = get_db_connection()

@account_mgmt_bp.route('/')
def index():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT account, name, role, department FROM users")
            account = cursor.fetchall()
        accounts = [
            {"account": row[0], "name": row[1], "role": row[2], "department": row[3]}
            for row in account
        ]
        conn.commit()  # 強制同步資料庫更新
        return render_template('account_management/account_management.html', accounts=accounts)
    except Exception as e:
        flash(f'錯誤：{e}', 'danger')
        return render_template('account_management/account_management.html', accounts=[])


@account_mgmt_bp.route('/delete/<string:account_id>', methods=['POST'])
def delete(account_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE account = %s", (account_id,))
            conn.commit()
            flash('帳號刪除成功！', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'刪除失敗：{e}', 'danger')

    return redirect(url_for('account_management.index'))


@account_mgmt_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    accounts = []

    try:
        with conn.cursor() as cursor:
            sql = "SELECT account, name, role, department FROM users WHERE account LIKE %s OR name LIKE %s"
            like_query = f"%{query}%"
            cursor.execute(sql, (like_query, like_query))
            accounts = cursor.fetchall()
    except Exception as e:
        flash(f'資料庫搜尋錯誤：{e}', 'danger')

    # Convert tuple to dictionary
    accounts = [
        {"account": row[0], "name": row[1], "role": row[2], "department": row[3]}
        for row in accounts
    ]
    
    return render_template('account_management/account_management.html', accounts=accounts)

