'''
To Do's:

test number of client connection


match methods / classes to the document

'''
#Imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from werkzeug.utils import secure_filename
import csv
import sys
import time  

#Add folder housing the project to the filepath
bigfolder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(bigfolder_path)
from ML.ECGClass import ECGClassifier

#App settings 
MAX_CLIENTS = 100
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'SoftwareProject'
app.config['SESSION_COOKIE_NAME'] = 'user_session'
socketio = SocketIO(app)

#DB connections
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mandarin143!",
    database="HEARTHEALTH"
)
cursor = db.cursor()

# Initializing NN model
ecg_classifier = ECGClassifier()
ecg_classifier.load_model()


#Possible client connections
available_sockets = list(range(1, MAX_CLIENTS+1))
clients = []

#CHeck username and password
def query_database(username, password):
    query = "SELECT * FROM Users WHERE Username=%s AND Password=%s"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result

#Process clients file for normal/abnormal labels.
#Returns path to the file, and the classification formatted 
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
    pretty_results = []
    for i,label in enumerate(results):
        pretty_results.append(f'{i+1}. {label}')
    
    return modified_file_path, pretty_results

#CHeck if the csv is uploaded in the format the ML model expexts
def verifyFileFormat(file_path):
    expectedColumns = 140
    format_column_counts = []
    col_count = []
    goodFormat = True
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        
        for row_count, row in enumerate(reader):
            column_count = len(row)
            format_column_counts.append(f'Row {row_count+1} Column Count: {column_count}')
            col_count.append(column_count)
    
    if any(count != expectedColumns for count in col_count):
        goodFormat = False
    
    return goodFormat, format_column_counts

#Handle client connections
@socketio.on('connect')
def handle_connect():
    if (len(clients)> MAX_CLIENTS):
        return render_template('about.html', full = True)
    
    print('Handling connection, length client at top =',len(clients))
    #If there is enough space for this client, assign them a socket and add them to the list
    if len(clients) < MAX_CLIENTS and available_sockets:
        socket_number = available_sockets.pop(0)
        client_sid = request.sid
        clients.append({'sid': client_sid, 'socket_number': socket_number})
        print(f'Length of clients is: {len(clients)}')
        emit('assign_socket', socket_number)
    else:
        emit('no_available_sockets', {'message': 'Please wait. No available sockets.'})

#Take username and password from form
#Check if the user is in the database
#If they are forward them to the results page.
@app.route('/login', methods=['GET', 'POST'])
def login():

    if (len(clients)> MAX_CLIENTS):
        return render_template('about.html', full = True)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_database(username, password)
        
        if user is not None:
            print(f"Redirecting to results for {username}")
            session['username'] = username
            return redirect(url_for('results'))
    return render_template('login.html')

#Restricted to logged in users only
#User can upload a csv file which will be classified and returned to them
#Results will be shown on the page as well.
#Once classified, the file the user uploaded is deleted from the server
@app.route('/results', methods=['GET', 'POST'])
def results():

    if(len(clients) > MAX_CLIENTS):
        return render_template('about.html', full = True)
    col_formatting   = [] #Here or render error on dynamic html content
    formatted_results = [] #Needs to be here or you get rendering error
    uploaded_filename = None
    modified_file_name = None
    #if user is logged in take their file
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

            # Save the uploaded file to the uploads folder with unique timestamp to avoid same filename errors
            temp_filename = f"{secure_filename(uploaded_file.filename)}_{int(time.time())}.csv"
            temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(temp_filepath)

            #Check if the file is has the correct format to process
            goodFormat, col_formatting = verifyFileFormat(temp_filepath)
            #IF bad format, return formatting error to html
            if( not goodFormat):
                os.remove(temp_filepath) #Delete temp file
                return render_template('results.html', username=username, uploaded_filename=uploaded_filename, formatted_results=formatted_results, column_errors = col_formatting)
            else:    
                col_formatting = [] #Reset dynamic div so results can show up
                # Process the CSV file and get the modified file path
                modified_file_path, formatted_results = process_csv(temp_filepath)

                # Set up response to allow file download
                #Get users downlad folder path
                downloads_folder = os.path.expanduser("~")
                modified_file_name = f'modified_{secure_filename(uploaded_file.filename)}'
                modified_file_destination = os.path.join(downloads_folder, modified_file_name)

                # Check if the destination file already exists, and change the name if it does
                #to avoid naming errors. Adds 1 to a number until the filename is unique.
                counter = 1
                while os.path.exists(modified_file_destination):
                    modified_file_name = f'modified_{counter}_{secure_filename(uploaded_file.filename)}'
                    modified_file_destination = os.path.join(downloads_folder, modified_file_name)
                    counter += 1
                
                #rename the file to the unique filename
                os.rename(modified_file_path, modified_file_destination)
                
                
                # Delete the original uploaded file
                os.remove(temp_filepath)
                    
                #Display the results of classification on the results page
        return render_template('results.html', username=username, uploaded_filename=uploaded_filename,formatted_results=formatted_results, modified_file_name=modified_file_name)
    else:
        #if user isnt valid send back to login
        return redirect(url_for('login'))

#After the user has submitted a file and it is classified, send modified folder to their downloads folder
@app.route('/download/<filename>')
def download_file(filename):
    downloads_folder = os.path.expanduser("~")
    file_path = os.path.join(downloads_folder, filename)
    return send_file(file_path, as_attachment=True)


#home page
@app.route('/')
def about():
    clients.append('Test')
    if(len(clients) > MAX_CLIENTS):
        return render_template('about.html', full = True)
    
    else:
        return render_template('about.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
