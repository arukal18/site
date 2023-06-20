
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename  # Add this line
import matplotlib
matplotlib.use('Agg') 
import time
import math
import json
import matplotlib.pyplot as plt
import fitz
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./uploads"
leaderboard = []

@app.route('/')
def index():
    return render_template('index.html', leaderboard=leaderboard)  # Pass the leaderboard to the template

@app.route('/', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        plot_file_path, count3, count4, count5, average_grade, name = betyg_analys(file_path)
        existing_entry = next((entry for entry in leaderboard if entry['name'] == name), None)

        if existing_entry:
            # If the name exists, update the average grade
            existing_entry['average_grade'] = average_grade
        else:
            # If the name doesn't exist, add a new entry
            leaderboard.append({'name': name, 'average_grade': average_grade})
        leaderboard.sort(key=lambda x: x['average_grade'], reverse=True)

        return render_template('results.html', name=name, data=[count3, count4, count5], total=count3+count4+count5, avg_grade=average_grade, leaderboard=leaderboard)

    else:
        return "File not allowed. Please upload a PDF file."


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

def betyg_analys(file_path):

    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:   
            text += page.get_text()
    char = text.splitlines()
    name = char[5]

    count3 = 0
    count4 = 0
    count5 = 0
    
    for x in char:
        if x == '5':
            count5 +=1
        if x == '4':
            count4 +=1
        if x == '3':
            count3 +=1
        
    labels = '3', '4', '5'
    sizes = [count3,count4,count5]
    fig1, ax1 = plt.subplots()
    fig1.suptitle(name, fontsize=16)

    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')

    # Get a unique filename by using the current datetime
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
    filepath = os.path.join('static', 'images', filename)
    grades = {
        3: count3,
        4: count4,
        5: count5
    }

    total_score = 0
    total_frequency = 0

    # Calculate the total score and frequency
    for grade, frequency in grades.items():
        total_score += grade * frequency
        total_frequency += frequency

    # Calculate the average grade
    average_grade = round(total_score / total_frequency, 2)

    # Print the average grade
    print("Average Grade:", round(average_grade, 2))
    # Save the plot to a unique file
    fig1.savefig(filepath)

    return filepath, count3, count4, count5, average_grade, name

if __name__ == "__main__":
    app.run()
