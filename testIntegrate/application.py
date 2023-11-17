from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
from io import StringIO

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.UPLOAD_FOLDER = '.\\uploads'
        self.ALLOWED_EXTENSIONS = {'csv'}
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        self.app.config['SECRET_KEY'] = 'SoftwareProject'
        self.app.config['SESSION_COOKIE_NAME'] = 'user_session'
        self.app.add_url_rule(
            "/uploads/<name>", endpoint="download_file", build_only=True
        )
        self.socketio = SocketIO(self.app)
        
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mandarin143!",
            database="company"
        )

        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")

        self.available_sockets = list(range(1, 101))
        self.clients = []

    def query_database(self, username, password):
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        return result

    def process_csv(self, file_path):
        # Read the CSV file, process it, and append '0' to each row
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            rows = [row + ['0'] for row in reader]

        # Write the modified CSV to a new file
        modified_file_path = f"{file_path}_modified.csv"
        with open(modified_file_path, 'w', newline='') as modified_file:
            writer = csv.writer(modified_file)
            writer.writerows(rows)

        return modified_file_path

    def start(self):
        @self.socketio.on('connect')
        def handle_connect():
            if 'username' in session:
                username = session['username']
                emit('show_username', {'username': username})

            if self.available_sockets:
                socket_number = self.available_sockets.pop(0)
                client_sid = flask.request.namespace.sid
                self.clients.append({'sid': client_sid, 'socket_number': socket_number})
                emit('assign_socket', socket_number)
            else:
                emit('no_available_sockets')

        @self.socketio.on('upload_file')
        def handle_upload(data):
        
            if client:
                socket_number = client['socket_number']
                uploaded_file = data['file']
                self.accept_uploaded_file(uploaded_file, socket_number)
                result = self.process_csv(f"uploads/{uploaded_file.filename}")

                # Provide a link for the client to download the modified CSV file
                download_link = url_for('download_file', filename=f'modified_{uploaded_file.filename}', _external=True)
                emit('csv_processed', {'socket_number': socket_number, 'result': result, 'download_link': download_link})

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
MAX_CLIENTS = 100
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'SoftwareProject'
app.config['SESSION_COOKIE_NAME'] = 'user_session'
socketio = SocketIO(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mandarin143!",
    database="Hearthealth"
)

cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")

available_sockets = list(range(1, 101))
clients = []

def query_database(username, password):
    query = "SELECT * FROM users WHERE username=%s AND password=%s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result

def process_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows = [row + ['0'] for row in reader]

    modified_file_path = f"{file_path}_modified.csv"
    with open(modified_file_path, 'w', newline='') as modified_file:
        writer = csv.writer(modified_file)
        writer.writerows(rows)

    return modified_file_path

@socketio.on('connect')
def handle_connect():
    if len(clients) < MAX_CLIENTS:
        if 'username' in session:
            username = session['username']
            emit('show_username', {'username': username})

        if available_sockets:
            socket_number = available_sockets.pop(0)
            client_sid = request.sid
            clients.append({'sid': client_sid, 'socket_number': socket_number})
            emit('assign_socket', socket_number)
        else:
            emit('no_available_sockets', {'message': 'Please wait. No available sockets.'})
    else:
        emit('no_available_sockets', {'message': 'Please wait. No available sockets.'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_database(username, password)
        print('User is:', user)
        if user is not None:
            print(f"Redirecting to results for {username}")
            session['username'] = username
            return redirect(url_for('results'))
    return render_template('login.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    uploaded_filename = None
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for('results'))

            uploaded_file = request.files['file']

            if uploaded_file.filename == '':
                flash('No selected file')
                return redirect(url_for('results'))

            if uploaded_file and uploaded_file.filename.endswith('.csv'):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Save the uploaded file
                uploaded_file.save(file_path)

                # Process the CSV file and get the modified file path
                modified_file_path = process_csv(file_path)

                # Set up response to allow file download
                return send_file(
                    modified_file_path,
                    as_attachment=True,
                    download_name=f'modified_{filename}',
                    mimetype='text/csv'
                )

        return render_template('results.html', username=username, uploaded_filename=uploaded_filename)
    
    return redirect(url_for('login'))

@app.route('/')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)