import sys
import time
from flask import Flask, render_template, redirect, url_for, request, session
import json 
from Online_exam_web.utils import load_questions
def answer_check_handler(chapter, question_selected, question_index):
    questions = load_questions(chapter)
    print(chapter)
    # 確保索引在範圍內
    if question_index < 0 or question_index >= len(questions):
        return f"題目索引超出範圍: {question_index}"

    # 取得題目並檢查答案
    question = questions[question_index]
    answer_key = question["answer"]  # 正確答案的 key
    if answer_key == question_selected:  # 直接比較選項名稱
        return "Correct"
    else:
        return "Wrong"