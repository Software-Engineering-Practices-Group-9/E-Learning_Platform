from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pymysql
from database.connect import get_db_connection
import datetime
import os

course_bp = Blueprint('course', __name__, template_folder='templates')

@course_bp.route('/<course_id>', methods=['GET'])
def course_page(course_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Get course data
        cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
        course_data = cursor.fetchone()

        if not course_data:
            flash('課程不存在', 'error')
            return redirect(url_for('student_course.student_page'))

        course_name = course_data['course_name']

        # Check if system notification for this user already exists
        cursor.execute("""
            SELECT 1 FROM posts 
            WHERE course_id = %s AND username = '系統通知' AND role = 'system' 
            AND content LIKE %s
        """, (course_id, f"%{session['user_id']}] 已進入課程%"))
        
        system_post_exists = cursor.fetchone()

        if not system_post_exists:
            # Add system notification
            cursor.execute("""
                INSERT INTO posts (course_id, group_name, username, role, content, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                course_id,
                course_name,
                '系統通知',
                'system',
                f"[{session['user_id']}] 已進入課程",
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()

        # Get discussion posts
        cursor.execute("""
            SELECT * FROM posts 
            WHERE course_id = %s 
            ORDER BY timestamp DESC
        """, (course_id,))
        posts = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('student_course/course.html',
                               course_name=course_name,
                               course_id=course_id,
                               group_name=course_name,
                               posts=posts)

    except Exception as e:
        print(f'Error in course page: {e}')
        flash('發生錯誤，請稍後再試', 'error')
        return redirect(url_for('student_course.student_page'))



@course_bp.route('/<course_id>/post', methods=['POST'])
def add_post(course_id):
    if 'user_id' not in session:
        flash('請先登入！', 'error')
        return redirect(url_for('login_logout.login'))

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # Get group_name from course_id
        cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
        course_data = cursor.fetchone()
        group_name = course_data['course_name']

        content = request.form['content']
        image = request.files.get('image')
        image_filename = None

        # Handle image upload
        if image and image.filename:
            timestamp = int(datetime.datetime.now().timestamp())
            image_filename = f"{group_name}_{timestamp}_{image.filename}"
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            image.save(os.path.join(upload_dir, image_filename))

        cursor.execute(
            """
            INSERT INTO posts (course_id, group_name, username, role, content, image, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                course_id,
                group_name,
                session['user_id'],
                session['role'],
                content,
                image_filename,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        conn.commit()
        flash('發布成功！', 'success')

    except Exception as e:
        conn.rollback()
        print(f'Error posting message: {e}')
        flash('發布失敗，請稍後再試', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('course.course_page', course_id=course_id))


@course_bp.route('/delete_post/<int:post_id>/<course_id>', methods=['POST'])
def delete_post(post_id, course_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Check post existence
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            flash('找不到該訊息', 'error')
            return redirect(url_for('course.course_page', course_id=course_id))

        # Check permissions
        if post['username'] != session['user_id'] and session['role'] != 'admin':
            flash('您沒有權限刪除此訊息', 'error')
            return redirect(url_for('course.course_page', course_id=course_id))

        # Delete image if exists
        if post['image']:
            try:
                image_path = os.path.join('static', 'uploads', post['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f'Error deleting image: {e}')

        # Delete post
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()

        flash('訊息已成功刪除', 'success')

    except Exception as e:
        print(f'Error deleting post: {e}')
        flash('刪除訊息時發生錯誤', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('course.course_page', course_id=course_id))