from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import json

exam_main_web_bp = Blueprint('exam_main_web', __name__, template_folder='templates')
user_history_folder = 'account_management/database/user_history'
question_bank_folder = 'question_bank'

@exam_main_web_bp.route('/exammain')
def index():
    if 'user_id' not in session:
        flash("請先登入")
        return redirect(url_for('account_management.login'))
    return render_template('chapter_section.html')

# 處理按鈕提交的章節選擇
@exam_main_web_bp.route('/submit_chapter', methods=['POST'])
def submit_chapter():
    selected_chapter = request.form.get('chapter')
    if selected_chapter:
        return redirect(url_for('exam_question_web.index', chapter=selected_chapter))
    else:
        flash("請選擇一個章節！")
        return redirect(url_for('exam_main_web.index'))

# 進入歷史紀錄頁面（僅顯示目前使用者的紀錄）
@exam_main_web_bp.route('/exam_history')
def exam_history():
    if 'user_id' not in session:
        flash("請先登入")
        return redirect(url_for('account_management.login'))
    
    current_user_id = session['user_id']
    history_data = []

    for file in os.listdir(user_history_folder):
        file_path = os.path.join(user_history_folder, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data_list = json.load(f)
                # 只顯示目前登入使用者的紀錄
                for data in data_list:
                    if data['user_id'] == current_user_id:
                        history_data.append(data)
            except json.JSONDecodeError:
                flash(f"{file} 格式錯誤")
    return render_template('exam_history.html', history_data=history_data)


# 顯示單一測驗紀錄的詳細資訊（修正版）
@exam_main_web_bp.route('/exam_history_display/<int:history_id>')
def exam_history_display(history_id):
    if 'user_id' not in session:
        flash("請先登入")
        return redirect(url_for('account_management.login'))

    current_user_id = session['user_id']

    # 在這裡遍歷所有紀錄並根據 record_index 查找對應紀錄
    for file in os.listdir(user_history_folder):
        history_file_path = os.path.join(user_history_folder, file)
        with open(history_file_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
            for record in data_list:
                if record['record_index'] == history_id and record['user_id'] == current_user_id:
                    history_data = record
                    # 加載題庫
                    temp = history_data['chapter'][:4] + '_' + history_data['chapter'][4:]
                    
                    question_file_path = os.path.join(question_bank_folder, f"{temp}.json")

                    if os.path.exists(question_file_path):
                        with open(question_file_path, 'r', encoding='utf-8') as qf:
                            questions = json.load(qf)
                        print(history_data)
                        return render_template('exam_history_display.html', history_data=history_data, questions=questions)
                    else:
                        flash("找不到對應的題目檔案")
                        return redirect(url_for('exam_main_web.exam_history'))
                    
    flash("找不到此紀錄")
    return redirect(url_for('exam_main_web.exam_history'))
