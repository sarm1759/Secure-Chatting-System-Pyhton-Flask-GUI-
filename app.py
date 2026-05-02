from flask import Flask, render_template, request, session, redirect, jsonify, url_for
from models import db, User, Message
from datetime import datetime, timedelta
from sqlalchemy import or_
import chaos_logic as cipher 
import os

app = Flask(__name__)
app.secret_key = "ultra_chaos_shield_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Database initialization aur Super Admin creation
with app.app_context():
    db.create_all()
    # Auto-check and create admin if not exists
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        new_admin = User(
            username='admin', 
            password='admin123', 
            role='admin',
            q1='admin', 
            q2='admin'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Super Admin account ready!")

# --- Root Routes ---
@app.route('/')
def index():
    if 'user_id' in session: 
        if session.get('role') == 'admin':
            return redirect(url_for('admin_panel'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        return redirect(url_for('index'))
    
    curr = session['username']
    msgs = Message.query.filter(or_(Message.sender == curr, Message.receiver == curr)).all()
    chat_partners = {m.receiver if m.sender == curr else m.sender for m in msgs}
    
    if 'admin' in chat_partners: chat_partners.remove('admin')
    if curr in chat_partners: chat_partners.remove(curr)
    
    return render_template('dashboard.html', active_chats=chat_partners)

# --- Authentication ---
@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('username')
    p = request.form.get('password')
    user = User.query.filter_by(username=u).first()

    if user:
        if user.lock_until and datetime.now() < user.lock_until:
            return jsonify({"status": "error", "message": "Account is BLACKLISTED/LOCKED."}), 403
            
        if user.password == p:
            user.failed_attempts = 0
            user.lock_until = None
            db.session.commit()
            session.update({'user_id': user.id, 'username': user.username, 'role': user.role})
            
            target = "/admin_panel" if user.role == 'admin' else "/dashboard"
            return jsonify({"status": "success", "message": "Welcome!", "redirect": target})
        else:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.lock_until = datetime.now() + timedelta(minutes=5)
            db.session.commit()
            return jsonify({"status": "error", "message": "Invalid credentials!"}), 401
            
    return jsonify({"status": "error", "message": "User not found!"}), 404

@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    u = data.get('username')
    a1 = data.get('ans1')
    a2 = data.get('ans2')
    new_p = data.get('new_password')

    user = User.query.filter_by(username=u).first()
    if user and user.q1 == a1 and user.q2 == a2:
        user.password = new_p
        db.session.commit()
        return jsonify({"status": "success", "message": "Password updated successfully!"})
    
    return jsonify({"status": "error", "message": "Invalid username or answers!"}), 400

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_action():
    u = request.form.get('username')
    p = request.form.get('password')
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')

    if User.query.filter_by(username=u).first():
        return jsonify({"status": "error", "message": "Username already taken!"}), 400

    if len(p) < 8 or not any(char.isdigit() for char in p):
        return jsonify({"status": "error", "message": "Password weak! Use 8+ chars and 1 number."}), 400

    new_user = User(username=u, password=p, q1=q1, q2=q2, role='user')
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "success", "message": "Signup successful! Please login."})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- Admin Functionalities ---

@app.route('/admin_panel')
def admin_panel():
    if 'role' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', users=users, now=datetime.now())

@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    if session.get('role') != 'admin': return "Unauthorized", 401
    u = request.form.get('username')
    p = request.form.get('password')
    if not User.query.filter_by(username=u).first():
        new_u = User(username=u, password=p, role='user', q1='admin_added', q2='admin_added')
        db.session.add(new_u)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/blacklist/<int:id>')
def blacklist_user(id):
    if session.get('role') != 'admin': return "Unauthorized", 401
    user = User.query.get(id)
    if user and user.role != 'admin':
        user.lock_until = datetime.now() + timedelta(days=36500)
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/unblacklist/<int:id>')
def unblacklist_user(id):
    if session.get('role') != 'admin': return "Unauthorized", 401
    user = User.query.get(id)
    if user:
        user.lock_until = None
        user.failed_attempts = 0
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if session.get('role') != 'admin': return "Unauthorized", 401
    user = User.query.get(id)
    if user and user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_panel'))

# --- Search & Messaging Logic ---

@app.route('/search_user', methods=['POST'])
def search_user():
    if 'username' not in session: return jsonify({"status": "error"}), 401
    query = request.json.get('username', '').strip()
    curr_user = session.get('username')
    user = User.query.filter(User.username == query, User.username != curr_user).first()
    if user: return jsonify({"status": "success", "username": user.username})
    return jsonify({"status": "error", "message": "User not found!"})

@app.route('/set_temp_session', methods=['POST'])
def set_temp_session():
    data = request.json
    mode = data.get('mode') 
    session[f'temp_{mode}'] = data.get('params')
    expiry = datetime.now() + timedelta(minutes=int(data.get('duration', 5)))
    session[f'{mode}_expiry'] = expiry.timestamp()
    return jsonify({"status": "success", "expiry": session[f'{mode}_expiry']})

@app.route('/send_msg', methods=['POST'])
def send():
    receiver = request.form.get('receiver')
    msg_text = request.form.get('message')
    m_params = request.form.get('manual_params') 
    try:
        if m_params:
            params = [float(x) for x in m_params.split(',')]
        else:
            params = [float(x) for x in session['temp_send_keys']]
        enc_txt, enc_key = cipher.encrypt_hybrid(msg_text, params)
        db.session.add(Message(sender=session['username'], receiver=receiver, content=enc_txt, enc_key=enc_key))
        db.session.commit()
        return jsonify({"status": "success"})
    except: return jsonify({"status": "error", "message": "Keys Expired"}), 401

@app.route('/fetch_chat/<receiver>')
def fetch_chat(receiver):
    curr = session.get('username')
    messages = Message.query.filter(or_((Message.sender==curr)&(Message.receiver==receiver),(Message.sender==receiver)&(Message.receiver==curr))).order_by(Message.timestamp.asc()).all()
    return jsonify([{"id": m.id, "sender": m.sender, "content": m.content, "timestamp": m.timestamp.strftime('%H:%M')} for m in messages])

@app.route('/decrypt_single_msg', methods=['POST'])
def decrypt_single():
    data = request.json
    msg = Message.query.get(data.get('msg_id'))
    m_params = data.get('manual_params')
    try:
        params = [float(x) for x in m_params.split(',')] if m_params else [float(x) for x in session['temp_my_keys']]
        plaintext = cipher.decrypt_hybrid(msg.content, msg.enc_key, params)
        return jsonify({"status": "success", "plaintext": plaintext})
    except: return jsonify({"status": "error"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)