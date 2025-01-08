from flask import Blueprint, Flask, flash, render_template, request, redirect, url_for, session
import json
from database.connect import get_db_connection

quiz_bp = Blueprint('quiz', __name__, template_folder='templates')

conn = get_db_connection()

@quiz_bp.route('/')
def index():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE chap")
    chapters = cursor.fetchall()
    cursor.close()
    return render_template('quiz/main.html', chapters=chapters)

@quiz_bp.route('/')
def main():
    return render_template('student_course/course.html')

@quiz_bp.route('/quiz/<chap>', methods=['GET', 'POST'])
def quiz(chap):
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login_logout.login'))
        
    student_id = session['user_id']
    course_id = session.get('course_id')
    
    if request.method == 'POST':
        cursor = conn.cursor()
        # 獲取該章節的最新測驗次數
        cursor.execute("""
            SELECT MAX(attempt) FROM student_answers 
            WHERE student_id = %s AND chap = %s
        """, (student_id, chap))
        last_attempt = cursor.fetchone()[0] or 0
        new_attempt = last_attempt + 1

        # 取得問題及正確答案
        cursor.execute("""
            SELECT num, answer, question, option_1, option_2, option_3, option_4, explains
            FROM questions
            WHERE chap = %s AND course_id = %s
        """, [chap, course_id])
        questions = cursor.fetchall()

        # 檢查答案並儲存結果
        answers = request.form.to_dict(flat=True)
        results = []
        for question in questions:
            num = question[0]
            correct_answer = question[1]
            selected_option = answers.get(f'question_{num}', None)
            is_correct = (selected_option == correct_answer)

            results.append({
                "num": num,
                "question": question[2],
                "options": [question[3], question[4], question[5], question[6]],
                "correct_answer": correct_answer,
                "selected_option": selected_option,
                "is_correct": is_correct,
                "explanation": question[7],
            })

            # 儲存學生答題結果
            cursor.execute("""
                INSERT INTO student_answers 
                (student_id, course_id, chap, question_num, selected_option, is_correct, attempt)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (student_id, course_id, chap, num, selected_option, is_correct, new_attempt))
        
        conn.commit()
        cursor.close()
        return render_template('quiz/display.html', results=results, chap=chap)

    # GET 方法，顯示題目
    cursor = conn.cursor()
    cursor.execute("SELECT num, question, option_1, option_2, option_3, option_4 FROM questions WHERE chap = %s", [chap])
    questions = cursor.fetchall()
    cursor.close()
    return render_template('quiz/quiz.html', questions=questions, chap=chap)

@quiz_bp.route('/history')
def history():
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login_logout.login'))
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT chap, attempt, DATE(created_at) AS test_date
        FROM student_answers
        WHERE student_id = %s AND course_id = %s
        GROUP BY chap, attempt, DATE(created_at)
        ORDER BY test_date DESC, attempt DESC
    """, [session['user_id'], session.get('course_id')])
    history_records = cursor.fetchall()
    cursor.close()
    return render_template('quiz/history.html', records=history_records)

@quiz_bp.route('/history/<chap>/<int:attempt>')
def history_details(chap, attempt):
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('login_logout.login'))
        
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.num, q.question, q.option_1, q.option_2, q.option_3, q.option_4, q.answer, q.explains,
               sa.selected_option, sa.is_correct
        FROM questions q
        JOIN student_answers sa ON q.num = sa.question_num AND q.chap = sa.chap
        WHERE sa.student_id = %s 
        AND sa.course_id = %s
        AND sa.chap = %s 
        AND sa.attempt = %s
        ORDER BY q.num
    """, [session['user_id'], session.get('course_id'), chap, attempt])
    results = cursor.fetchall()
    cursor.close()

    detailed_results = []
    for result in results:
        detailed_results.append({
            "num": result[0],
            "question": result[1],
            "options": [result[2], result[3], result[4], result[5]],
            "correct_answer": result[6],
            "selected_option": result[8],
            "is_correct": result[9],
            "explanation": result[7],
        })

    return render_template('quiz/results.html', results=detailed_results, chap=chap, attempt=attempt)