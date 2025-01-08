# create_course.py
from flask import Blueprint, jsonify, render_template, request, redirect, session, url_for, flash, json
import pymysql
from database.connect import get_db_connection
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import subprocess
import shutil
import uuid

create_course_bp = Blueprint('create_course', __name__, template_folder='templates')

UPLOAD_FOLDER = 'static/videos'
THUMBNAIL_FOLDER = 'static/thumbnails'
TEMP_FOLDER = 'static/temp'  # 暫存資料夾
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# 確保所有需要的資料夾都存在
for folder in [UPLOAD_FOLDER, THUMBNAIL_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(video_path, thumbnail_path):
    try:
        FFMPEG_PATH = "C:\\Program Files\\FFMPEG\\bin\\ffmpeg.exe"
        subprocess.run(
            [
                FFMPEG_PATH,
                "-i",
                video_path,
                "-ss",
                "00:00:01.000",
                "-vframes",
                "1",
                thumbnail_path,
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error generating thumbnail: {e}")

@create_course_bp.route('/', methods=['GET'])
def course_page():
    professor_id = session.get('professor_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM courses WHERE account = %s", (professor_id,))
    courses = cursor.fetchall()
    cursor.close()
    
    return render_template('create_course/create_course.html', courses=courses)

@create_course_bp.route('/temp_upload', methods=['POST'])
def temp_upload():
    if 'video_file' not in request.files:
        return {'success': False, 'message': '沒有選擇檔案'}
        
    video_file = request.files['video_file']
    if video_file.filename == '':
        return {'success': False, 'message': '沒有選擇檔案'}
        
    if video_file and allowed_file(video_file.filename):
        # 使用影片的原始檔案名稱
        temp_filename = secure_filename(video_file.filename)
        temp_video_path = os.path.join(TEMP_FOLDER, temp_filename)
        temp_thumbnail_path = os.path.join(TEMP_FOLDER, f"{os.path.splitext(temp_filename)[0]}.jpg")
        
        # 儲存檔案到暫存資料夾
        video_file.save(temp_video_path)
        create_thumbnail(temp_video_path, temp_thumbnail_path)
        
        return {
            'success': True,
            'temp_filename': temp_filename,
            'thumbnail_url': f'/static/temp/{os.path.splitext(temp_filename)[0]}.jpg'
        }
    
    return {'success': False, 'message': '不支援的檔案格式'}


@create_course_bp.route('/settings', methods=['GET', 'POST'])
def course_settings():
    professor_id = session.get('professor_id')
    
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_id = request.form.get('course_id')
        video_data = json.loads(request.form.get('video_data', '[]'))  # 從表單獲取暫存的影片資訊
        created_date = datetime.now()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 插入課程資料
                cursor.execute("""
                    INSERT INTO courses (account, course_name, course_id, created_date)
                    VALUES (%s, %s, %s, %s)
                """, (professor_id, course_name, course_id, created_date))
                
                # 處理每個暫存的影片
                for video in video_data:
                    temp_filename = video['temp_filename']
                    video_name = video['video_name']
                    
                    # 移動影片從暫存到正式資料夾
                    temp_video_path = os.path.join(TEMP_FOLDER, temp_filename)
                    temp_thumbnail_path = os.path.join(TEMP_FOLDER, f"{os.path.splitext(temp_filename)[0]}.jpg")

                    final_video_path = os.path.join(UPLOAD_FOLDER, temp_filename)
                    final_thumbnail_path = os.path.join(THUMBNAIL_FOLDER, f"{os.path.splitext(temp_filename)[0]}.jpg")

                    # 移動檔案
                    if os.path.exists(temp_video_path):
                        shutil.move(temp_video_path, final_video_path)
                    if os.path.exists(temp_thumbnail_path):
                        shutil.move(temp_thumbnail_path, final_thumbnail_path)

                    # 儲存影片資訊到資料庫
                    cursor.execute("""
                        INSERT INTO course_videos (course_id, video_name, video_url, thumbnail_url)
                        VALUES (%s, %s, %s, %s)
                    """, (course_id, video_name, final_video_path, final_thumbnail_path))
                
                # 建立群組
                members = [str(session['user_id'])]
                cursor.execute("""
                    INSERT INTO `groups` (course_id, course_name, members)
                    VALUES (%s, %s, %s)
                """, (course_id, course_name, json.dumps(members)))
                
                conn.commit()
                flash("課程創建成功！", "success")
                return redirect(url_for('create_course.course_page'))
                
        except Exception as e:
            print(f"Error: {e}")
            flash(f"發生錯誤: {e}", "danger")
            conn.rollback()
        finally:
            conn.close()
            
    return render_template('create_course/course_settings.html')

@create_course_bp.route('/delete/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 獲取課程相關的所有影片資訊
        cursor.execute("SELECT * FROM course_videos WHERE course_id = %s", (course_id,))
        videos = cursor.fetchall()
        
        for video in videos:
            video_url = video['video_url']
            thumbnail_url = video['thumbnail_url']
            
            # 刪除影片檔案和縮圖檔案
            if video_url and os.path.exists(video_url):
                os.remove(video_url)
            if thumbnail_url and os.path.exists(thumbnail_url):
                os.remove(thumbnail_url)
        
        # 刪除資料庫中的影片和課程資訊
        cursor.execute("DELETE FROM course_videos WHERE course_id = %s", (course_id,))
        cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
        conn.commit()
        
        flash("課程刪除成功！", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash(f"刪除失敗: {e}", "danger")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('create_course.course_page'))


@create_course_bp.route('/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        course_id_new = request.form.get('course_id')
        video_data = json.loads(request.form.get('video_data', '[]'))
        
        try:
            # 更新課程資訊
            cursor.execute("""
                UPDATE courses SET course_name = %s, course_id = %s WHERE id = %s
            """, (course_name, course_id_new, course_id))
            
            # 處理新上傳的影片
            for video in video_data:
                temp_filename = video['temp_filename']
                video_name = video['video_name']
                
                # 移動影片從暫存到正式資料夾
                temp_video_path = os.path.join(TEMP_FOLDER, temp_filename)
                temp_thumbnail_path = os.path.join(TEMP_FOLDER, f"{os.path.splitext(temp_filename)[0]}.jpg")
                
                final_filename = f"{uuid.uuid4()}_{os.path.basename(temp_filename)}"
                final_video_path = os.path.join(UPLOAD_FOLDER, final_filename)
                final_thumbnail_path = os.path.join(THUMBNAIL_FOLDER, f"{os.path.splitext(final_filename)[0]}.jpg")
                
                if os.path.exists(temp_video_path):
                    shutil.move(temp_video_path, final_video_path)
                if os.path.exists(temp_thumbnail_path):
                    shutil.move(temp_thumbnail_path, final_thumbnail_path)
                
                # 儲存影片資訊到資料庫
                cursor.execute("""
                    INSERT INTO course_videos (course_id, video_name, video_url, thumbnail_url)
                    VALUES (%s, %s, %s, %s)
                """, (course_id, video_name, final_video_path, final_thumbnail_path))
            
            conn.commit()
            flash("課程更新成功！", "success")
            return redirect(url_for('create_course.course_page'))
            
        except Exception as e:
            print(f"Error: {e}")
            flash(f"更新失敗: {e}", "danger")
            conn.rollback()
        
    # GET 請求處理
    cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    
    cursor.execute("SELECT * FROM course_videos WHERE course_id = %s", (course_id,))
    videos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('create_course/course_edit.html', course=course)


@create_course_bp.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 獲取影片資訊
        cursor.execute("SELECT video_url, thumbnail_url FROM course_videos WHERE id = %s", (video_id,))
        video = cursor.fetchone()
        
        if video:
            # 刪除影片檔案和縮圖
            if os.path.exists(video['video_url']):
                os.remove(video['video_url'])
            if os.path.exists(video['thumbnail_url']):
                os.remove(video['thumbnail_url'])
            
            # 從資料庫刪除記錄
            cursor.execute("DELETE FROM course_videos WHERE id = %s", (video_id,))
            conn.commit()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': '找不到影片'})
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': str(e)})
        
    finally:
        cursor.close()
        conn.close()


@create_course_bp.route('/add_question', methods=['POST'])
def add_question():
    if request.method == 'POST':
        # 上傳的題目檔案
        file = request.files['json_file']
        if file:
            file_name = file.filename

            # 檢查該檔名是否已經上傳過
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE file_name = %s", [file_name])
            existing_file = cursor.fetchone()

            if existing_file:
                flash(f'檔案 {file_name} 已經上傳過！', 'warning')
                return redirect(url_for('create_course.course_page'))

            # 獲取大標題
            chap = request.form['chap']

            # 解析 JSON 檔案
            content = file.read()
            questions = json.loads(content)
            
            # 獲取 course_id
            course_id = request.form.get('course_id')

            try:
                for question in questions:
                    # 插入每道題目到資料庫
                    query = """
                    INSERT INTO questions (course_id, chap, num, question, option_1, option_2, option_3, option_4, answer, explains, file_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (course_id, chap, question['num'], question['question'], 
                           question['select_1'], question['select_2'],
                           question['select_3'], question['select_4'], 
                           question['answer'], question['explains'], file_name)
                    
                    cursor.execute(query, data)
                
                conn.commit()
                cursor.close()
                conn.close()

                flash('題目已成功上傳！', 'success')
                return redirect(url_for('create_course.edit_course', course_id=course_id))
            except Exception as e:
                conn.rollback()
                flash(f'上傳失敗：{str(e)}', 'danger')
                return redirect(url_for('create_course.edit_course', course_id=course_id))

    return 'Error'