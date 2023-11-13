from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit
import mysql.connector

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'SoftwareProject'
        self.app.config['SESSION_COOKIE_NAME'] = 'user_session'
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

    def accept_uploaded_file(self, file, socket_number):
        emit('IN Accept uploads, also testing wt emit does')
        file.save(f"uploads/{file.filename}")

    def process_csv(self, file_path):
        # Read the CSV file, process it and append 0 or 1 to each row
        pass

    def start(self):
        @self.socketio.on('connect')
        def handle_connect():
            if 'username' in session:
                username = session['username']
                emit('show_username', {'username': username})

            if self.available_sockets:
                socket_number = self.available_sockets.pop(0)
                client_sid = request.sid
                self.clients.append({'sid': client_sid, 'socket_number': socket_number})
                emit('assign_socket', socket_number)
            else:
                emit('no_available_sockets')

        @self.socketio.on('upload_file')
        def handle_upload(data):
            client = next((client for client in self.clients if client['sid'] == request.sid), None)
            if client:
                socket_number = client['socket_number']
                uploaded_file = data['file']
                self.accept_uploaded_file(uploaded_file, socket_number)
                result = self.process_csv(f"uploads/{uploaded_file.filename}")
                emit('csv_processed', {'socket_number': socket_number, 'result': result})

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                user = self.query_database(username, password)
                print('User is:', user)
                if user:
                    session['username'] = username
                    return redirect(url_for('results'))
            return render_template('login.html')
        
        @self.app.route('/results', methods=['GET', 'POST'])
        def results():
            uploaded_filename = None  # Initialize uploaded_filename as None
            if 'username' in session:
                username = session['username']
                if request.method == 'POST':
                    uploaded_file = request.files['file']
                    handle_upload(uploaded_file)
                    if uploaded_file.filename != '':
                        client = next((client for client in self.clients if client['sid'] == request.sid), None)
                        if client:
                            socket_number = client['socket_number']
                            self.accept_uploaded_file(uploaded_file, socket_number)
                            result = self.process_csv(f"uploads/{uploaded_file.filename}")
                            emit('csv_processed', {'socket_number': socket_number, 'result': result})
                            uploaded_filename = uploaded_file.filename  # Set uploaded_filename if the file is uploaded
                return render_template('results.html', username=username, uploaded_filename=uploaded_filename)
            return redirect(url_for('login'))
        
        @self.app.route('/')
        def about():
            return render_template('about.html')
        
        @self.app.route('/download/<filename>', methods=['GET'])
        def download_file(filename):
            return send_from_directory('uploads', filename, as_attachment=True)

        if __name__ == '__main__':
            self.socketio.run(self.app, debug=True)

# Create an instance of the Server class
server = Server()
server.start()
