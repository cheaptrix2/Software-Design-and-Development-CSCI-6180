# Hearthealth
# An application by Adel Mahfooz, Soma Ezzadpanah, Joseph May, and Taylor Hartman to classify preprocessed ECG data.

## Problem Statement
With the dramatic increase of patients to doctors, a need has arisen to be able to diagnose and treat patients faster and with the same accuracy, and also to diagnose with less doctor intervention.​ The use of artificial intelligence, when implemented safely and responsibly, can help with these tasks.

## Project Scope
Make a full stack web application using Flask, Socket.io, MySQL, and TensorFlow so authorized healthcare providers can submit processed ECG data and have classifications of normal or abnormal appeneded to the readings.

## Database
- Install MySQL Workbench
- Navigate to ./HeartHealth.sql
- Run all queries in file

## Starting Server
- Install Flask.
- Navigate to ./SoftEngProj/
```
$python application.py
```

## Opening Site
- Open web browser of your choice
- In address bar type: ```localhost:5000/``` or ```127.0.0.1:5000/```
- Site navigation is at the top left of the pages

## Data submission
- Login to site
- Click "Upload" button
- Submit approved file type and data type (test.csv is provided for functional testing)
- Click "Upload"
- Results displayed on screen
- Optional: click "Download" to get your submitted file's contents with the classifications appended to the end of the corresponding row/s.
