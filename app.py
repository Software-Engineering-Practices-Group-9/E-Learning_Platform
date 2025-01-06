from flask import Flask
from Online_exam_web.exam_main_web import exam_main_web_bp
from Online_exam_web.exam_question_web import exam_question_web_bp

app = Flask(__name__)
app.secret_key = "fc5f7d32ab1ebbb48e388b731819cb64"

app.register_blueprint(exam_main_web_bp)
app.register_blueprint(exam_question_web_bp)

if __name__ == "__main__":
    app.run(debug=True)
