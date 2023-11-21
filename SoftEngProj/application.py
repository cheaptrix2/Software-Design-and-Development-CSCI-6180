from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
import sys
import time  # Import the time module to use for creating unique filenames

bigfolder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(bigfolder_path)
from ML.ECGClass import ECGClassifier

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
    database="HEARTHEALTH"
)

# Initializing NN model
ecg_classifier = ECGClassifier()
ecg_classifier.load_model()

cursor = db.cursor()

available_sockets = list(range(1, 101))
clients = []

def query_database(username, password):
    query = "SELECT * FROM Users WHERE Username=%s AND Password=%s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result

def process_csv(file_path):
    ecg_classifier.load_data(file_path)
    ecg_classifier.predict()
    results = ecg_classifier.print_predictions()
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows = []
        for row, result in zip(reader, results):
            rows.append(row + [result])

    modified_file_path = f"{file_path}_modified.csv"
    with open(modified_file_path, 'w', newline='') as modified_file:
        writer = csv.writer(modified_file)
        writer.writerows(rows)

    #Format results for display
    print('CSV RESULTS ARE:', results)
    pretty_results = []
    for i,label in enumerate(results):
        pretty_results.append(f'{i+1}. {label}')
    print('CSV PRETTY VErsions', pretty_results)
    return modified_file_path, pretty_results

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
    formatted_results = []
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

            # Save the uploaded file to the uploads folder
            temp_filename = f"{secure_filename(uploaded_file.filename)}_{int(time.time())}.csv"
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(temp_filepath)

            # Process the CSV file and get the modified file path
            modified_file_path, formatted_results = process_csv(temp_filepath)



            # Set up response to allow file download
            downloads_folder = os.path.expanduser("~")
            modified_file_name = f'modified_{secure_filename(uploaded_file.filename)}'
            modified_file_destination = os.path.join(downloads_folder, modified_file_name)

            # Check if the destination file already exists, and change the name if it does
            #to avoid naming errors
            counter = 1
            while os.path.exists(modified_file_destination):
                modified_file_name = f'modified_{counter}_{secure_filename(uploaded_file.filename)}'
                modified_file_destination = os.path.join(downloads_folder, modified_file_name)
                counter += 1
            #rename the file
            os.rename(modified_file_path, modified_file_destination)
            
            print('FOrmatted results are:', formatted_results)
            # Delete the original uploaded file
            os.remove(temp_filepath)
            return return_file(modified_file_destination, modified_file_name)
            
        
        return render_template('results.html', username=username, uploaded_filename=uploaded_filename, formatted_results=formatted_results)

    return redirect(url_for('login'))
@app.route('/')
def about():
    return render_template('about.html')


def return_file(modified_file_destination, modified_file_name):
    #Send the file to users downloads folder
        return send_file(
            modified_file_destination,
            as_attachment=True,
            download_name=modified_file_name,
            mimetype='text/csv'
        )
if __name__ == '__main__':
    socketio.run(app, debug=True)
