from flask import Blueprint, render_template, request, redirect, url_for, flash

exam_main_web_bp = Blueprint('exam_main_web', __name__, template_folder='templates')

@exam_main_web_bp.route('/')
def index():
    return render_template('chapter_section.html')

# 處理按鈕提交的章節選擇
@exam_main_web_bp.route('/submit_chapter', methods=['POST'])
def submit_chapter():
    selected_chapter = request.form.get('chapter')
    if selected_chapter:
        # Redirect 到 exam_question 頁面，並傳遞所選章節
        return redirect(url_for('exam_question_web.index', chapter=selected_chapter))
    else:
        flash("請選擇一個章節！")
        return redirect(url_for('exam_main_web.index'))
