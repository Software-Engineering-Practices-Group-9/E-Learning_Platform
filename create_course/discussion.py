from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import pymysql
from database.connect import get_db_connection
import datetime
import os

discussion_bp = Blueprint('discussion', __name__, template_folder='templates')


@discussion_bp.route('/discussion/<group_name>', methods=['GET', 'POST'])
def discussion_page(group_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 確認群組是否存在
        cursor.execute("SELECT * FROM `groups` WHERE course_name = %s", (group_name,))
        group = cursor.fetchone()

        if not group:
            flash('找不到該討論群組', 'error')
            return redirect(url_for('discussion.discussion_page'))

        # 發布新帖子
        if request.method == 'POST':
            content = request.form['content']
            image = request.files.get('image')
            image_filename = None

            # 處理圖片上傳
            if image and image.filename:
                timestamp = int(datetime.datetime.now().timestamp())
                image_filename = f"{group_name}_{timestamp}_{image.filename}"
                upload_dir = os.path.join('static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                image.save(os.path.join(upload_dir, image_filename))

            try:
                cursor.execute(
                    """
                    INSERT INTO posts (course_id, group_name, username, role, content, image, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        group['course_id'],
                        group_name,
                        session['user_id'],
                        session['role'],
                        content,
                        image_filename,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                )
                conn.commit()
                flash('帖子發表成功！', 'success')
            except Exception as e:
                conn.rollback()
                print(f'Error inserting post: {e}')
                flash(f'發表帖子時發生錯誤：{str(e)}', 'error')

        # 查詢該群組的所有帖子
        cursor.execute("""
            SELECT * FROM posts 
            WHERE group_name = %s 
            ORDER BY timestamp DESC
        """, (group_name,))
        posts = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('discussion/discussion.html', group=group, posts=posts)

    except Exception as e:
        print(f'Error in discussion page: {e}')
        flash('討論區載入時發生錯誤', 'error')
        return redirect(url_for('main.main'))

@discussion_bp.route('/delete_post/<int:post_id>/<group_name>', methods=['POST'])
def delete_post(post_id, group_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 檢查是否為發文者或管理員
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            flash('找不到該訊息', 'error')
            return redirect(url_for('discussion.discussion_page', group_name=group_name))

        # 檢查權限：只有發文者或管理員可以刪除
        if post['username'] != session['user_id'] and session['role'] != 'admin':
            flash('您沒有權限刪除此訊息', 'error')
            return redirect(url_for('discussion.discussion_page', group_name=group_name))

        # 如果有圖片，刪除圖片檔案
        if post['image']:
            try:
                image_path = os.path.join('static', 'uploads', post['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f'Error deleting image file: {e}')

        # 刪除訊息
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()

        flash('訊息已成功刪除', 'success')

    except Exception as e:
        print(f'Error deleting post: {e}')
        flash('刪除訊息時發生錯誤', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('discussion.discussion_page', group_name=group_name))