from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os, json
from datetime import datetime

#..............\\\
#    
#    debug:
#    重整時會新增留言、創建群組未開發(V)、flash->js的alert(V)、有人加入時通知所有人(V)，查看聊天室的成員  
#    
#..............///

app = Flask(__name__)
app.secret_key = 'secret_key'  # 替換為更安全的密鑰

# 設置 JSON 資料儲存檔案
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            # 如果 'posts' 不存在，設置為空列表
            if 'posts' not in data:
                data['posts'] = []
            return data
    return {'users': [], 'groups': [], 'posts': []}


def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# 首頁
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

# 註冊頁面
@app.route('/register', methods=['GET', 'POST'])
def register():
    data = load_data()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # 檢查是否已存在帳號
        if any(user['username'] == username for user in data['users']):
            flash('帳號已存在！')
            return redirect(url_for('register'))

        # 新增使用者
        data['users'].append({'username': username, 'password': password, 'role': role})
        save_data(data)
        flash('註冊成功！請登入')
        return redirect(url_for('login'))

    return render_template('register.html')

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = load_data()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 驗證帳號
        user = next((user for user in data['users'] if user['username'] == username and user['password'] == password), None)
        if user:
            session['username'] = username
            session['role'] = user['role']
            flash('登入成功！')
            return redirect(url_for('dashboard'))
        else:
            flash('登入失敗，請檢查帳號或密碼')

    return render_template('login.html')

# 加入群組
@app.route('/join_group/<group_name>', methods=['GET'])
def join_group(group_name):
    if 'username' not in session:
        flash('請先登入！')
        return redirect(url_for('login'))

    data = load_data()
    group = next((g for g in data['groups'] if g['name'] == group_name), None)

    if not group:
        flash('群組不存在！')
        return redirect(url_for('dashboard'))

    # 檢查使用者是否已經加入群組
    if session['username'] not in group['members']:
        group['members'].append(session['username'])  # 將使用者加入群組
        save_data(data)

        # 新增一條訊息到群組的帖子中，顯示 [XXX 已加入群組]
        post = {
            'group_name': group_name,
            'username': '系統通知',  # 系統發佈的訊息
            'role': 'system',
            'content': f"[{session['username']}] 已加入群組",
            'image': None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 保存該訊息
        data['posts'].append(post)
        save_data(data)

        flash(f'成功加入 {group_name} 群組')
    else:
        flash('您已經加入此群組')

    return redirect(url_for('group', group_name=group_name))


# 創建群組
@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'username' not in session:
        flash('請先登入！')
        return redirect(url_for('login'))

    if request.method == 'POST':
        group_name = request.form['group_name']
        
        data = load_data()
        
        # 檢查群組名稱是否已存在
        if any(group['name'] == group_name for group in data['groups']):
            flash('群組名稱已存在！')
            return redirect(url_for('create_group'))
        
        # 新增群組
        new_group = {
            'name': group_name,
            'members': [session['username']]  # 預設將創建者加入群組
        }
        data['groups'].append(new_group)
        save_data(data)
        
        flash(f'成功創建群組 {group_name}')
        return redirect(url_for('dashboard'))

    return render_template('create_group.html')


# 儀表板
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('請先登入！')
        return redirect(url_for('login'))

    data = load_data()
    groups = data['groups']

    # 創建一個字典來保存每個群組是否已加入
    group_status = {}
    for group in groups:
        group_status[group['name']] = session['username'] in group['members']

    return render_template('dashboard.html', username=session['username'], role=session['role'], groups=groups, group_status=group_status)


# 創建群組
@app.route('/group/<group_name>', methods=['GET', 'POST'])
def group(group_name):
    if 'username' not in session:
        flash('請先登入！')
        return redirect(url_for('login'))

    data = load_data()
    group = next((g for g in data['groups'] if g['name'] == group_name), None)

    if not group:
        flash('討論區不存在！')
        return redirect(url_for('dashboard'))

    # 處理發佈新帖子的功能
    if request.method == 'POST':
        content = request.form['content']
        image = request.files.get('image')
        image_filename = None

        # 上傳圖片
        if image:
            image_filename = f"{group_name}_{len(data['posts']) + 1}.jpg"
            image.save(os.path.join('static', 'uploads', image_filename))

        post = {
            'group_name': group_name,
            'username': session['username'],
            'role': session['role'],
            'content': content,
            'image': image_filename,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 保存帖子
        data['posts'].append(post)
        save_data(data)
        flash('帖子發表成功！')

    # 顯示該群組的帖子
    posts = [post for post in data['posts'] if post['group_name'] == group_name]

    return render_template('group.html', group_name=group_name, posts=posts)

# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash('登出成功！')
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        save_data({'users': [], 'groups': [], 'posts': []})
    app.run(debug=True) 
