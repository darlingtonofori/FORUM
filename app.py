from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Session key

# PostgreSQL connection
DATABASE_URL = os.getenv('postgresql://forum_db_e89m_user:ZyAxYHd3eSU8AHDbjTh591yYAO6hjs4X@dpg-d0hpuae3jp1c73bscca0-a/forum_db_e89m')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv('dtuu8azzg'),
    api_key=os.getenv('513114514133159'),
    api_secret=os.getenv('-lrJPrTiynlAPS0lCjcscMzV6tA')
)

# Routes
@app.route('/')
def home():
    cursor.execute("SELECT threads.id, threads.title, threads.content, users.username, threads.created_at, threads.file_url FROM threads JOIN users ON threads.user_id = users.id ORDER BY threads.created_at DESC")
    threads = cursor.fetchall()
    return render_template('index.html', threads=threads)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add user to DB (make sure to hash password in production)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]  # Assuming user ID is in the first column
            return redirect(url_for('home'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/post_thread', methods=['POST'])
def post_thread():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']

        # Upload file to Cloudinary
        file_url = None
        if file:
            upload_response = cloudinary.uploader.upload(file)
            file_url = upload_response['url']

        # Insert thread into DB
        cursor.execute("INSERT INTO threads (title, content, file_url, user_id) VALUES (%s, %s, %s, %s)",
                       (title, content, file_url, session['user_id']))
        conn.commit()
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
