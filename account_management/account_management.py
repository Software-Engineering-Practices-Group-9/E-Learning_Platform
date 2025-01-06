from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from Online_exam_web.utils import load_accounts, save_accounts

import json

account_mgmt_bp = Blueprint('account_management', __name__, template_folder='templates')

# ---------------------------- 首頁 ----------------------------
@account_mgmt_bp.route('/')
def index():
    if 'user_id' not in session:
        flash("請先登入！")
        return redirect(url_for('account_management.login_page'))
    return redirect(url_for('exam_main_web.index'))

# ---------------------------- 登入頁面 ----------------------------
@account_mgmt_bp.route('/login_page')
def login_page():
    return render_template('account_management/login.html')

# ---------------------------- 註冊頁面 ----------------------------
@account_mgmt_bp.route('/register_page')
def register_page():
    return render_template('account_management/register.html')

# ---------------------------- 登入邏輯 ----------------------------
@account_mgmt_bp.route('/login', methods=['POST'])
def login():
    accounts = load_accounts()
    login_id = request.form.get('login_id')
    login_password = request.form.get('login_password')

    # 驗證使用者帳號與密碼
    for account in accounts:
        if account['id'] == login_id and account['password'] == login_password:
            session['user_id'] = login_id
            flash(f"{account['name']}，歡迎登入成功！")
            return redirect(url_for('exam_main_web.index'))

    flash("登入失敗，請檢查學號或密碼是否正確！")
    return redirect(url_for('account_management.login_page'))

# ---------------------------- 註冊邏輯 ----------------------------
@account_mgmt_bp.route('/register', methods=['POST'])
def register():
    accounts = load_accounts()
    new_id = request.form.get('register_id')
    new_name = request.form.get('register_name')
    new_password = request.form.get('register_password')

    # 防止重複註冊
    for account in accounts:
        if account['id'] == new_id:
            flash("此學號已經存在，請使用其他學號！")
            return redirect(url_for('account_management.register_page'))

    # 建立新使用者並存檔
    new_account = {
        "id": new_id,
        "name": new_name,
        "password": new_password
    }
    accounts.append(new_account)
    save_accounts(accounts)
    flash("註冊成功！請使用新帳號登入。")
    return redirect(url_for('account_management.login_page'))
