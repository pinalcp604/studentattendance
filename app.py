import os
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Load student credentials and attendance data from Excel files
students_df = pd.read_excel('students.xlsx', engine='openpyxl')
students_df['Student ID'] = students_df['Student ID'].astype(str)

attendance_df = pd.read_excel('attendance.xlsx', engine='openpyxl')
attendance_df['Student ID'] = attendance_df['Student ID'].astype(str)


@app.route('/')
def home():
    if 'student_id' in session:
        return redirect(url_for('attendance'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = str(request.form['student_id']).strip()
        password = request.form['password'].strip()
        if authenticate(student_id, password):
            session['student_id'] = student_id
            return redirect(url_for('attendance'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')


@app.route('/attendance')
def attendance():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student_id = session['student_id']
    student_attendance = attendance_df[attendance_df['Student ID'] == student_id]
    if student_attendance.empty:
        return "No attendance records found."
    return render_template('attendance.html', tables=[student_attendance.to_html(classes='data', header=True)], titles=student_attendance.columns.values)


@app.route('/logout')
def logout():
    session.pop('student_id', None)
    return redirect(url_for('home'))


def authenticate(student_id, password):
    student = students_df[(students_df['Student ID'].str.strip() == student_id) & (
        students_df['Password'].str.strip() == password)]
    return not student.empty


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
