from flask import Blueprint, render_template, request, redirect, url_for, flash
import json
from Online_exam_web.exam_answer_check import answer_check_handler
exam_question_web_bp = Blueprint('exam_question_web', __name__, template_folder='templates')

# 定義 JSON 檔案路徑
CHAP_1_FILE = "question_bank/chap_1.json"

def load_questions(chapter):
    """根據章節載入題目"""
    if chapter == "chap1":
        try:
            with open(CHAP_1_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    return []

@exam_question_web_bp.route('/exam')
def index():
    chapter = request.args.get('chapter', '未選擇章節')
    questions = load_questions(chapter)
    return render_template('exam_question.html', chapter=chapter, questions=questions)

@exam_question_web_bp.route('/submit_exam', methods=['POST'])
def submit_exam():
    chapter = request.form.get('chapter')
    questions = load_questions(chapter)

    # 收集用戶提交的答案與判斷結果
    user_answers = {}
    status_check = {}  # 改為字典，針對每題存放結果

    for index, question in enumerate(questions, start=1):
        answer = request.form.get(f"answer_{index}")
        if not answer:
            flash(f"請完成題目 {question['question']} 後再提交！")
            return redirect(url_for('exam_question_web.index', chapter=chapter))
        
        # 儲存每一題的狀態檢查
        parts = answer.split("_")
        question_num = question["num"]
        user_answers[question["num"]] = parts[1]
        print(question_num)
        status_check[question["num"]] = answer_check_handler(chapter, answer,question_num)
        
    # 顯示使用者提交的答案（可擴展成計算成績）
    return render_template('exam_result.html', 
                        user_answers=user_answers, 
                        questions=questions, 
                        chapter=chapter, 
                        status_check=status_check)