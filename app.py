from flask import Flask, render_template, request
import sqlite3
from datetime import date, datetime
import calendar

app = Flask(__name__)


def current_month_tasks():
    month = datetime.now().month
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f'''
    select TaskName, Day 
    from events, tasks 
    where events.TaskID == tasks.TaskID 
    and Month == {month}''')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.route('/')
def calendar_view():
    tasks = current_month_tasks()
    today = date.today()
    calendar = calendar.Calendar()
    days = calendar.monthdatescalendar(today.year, today.month)

    return render_template('index.html', tasks=tasks, month=days)

if __name__ == '__main__':
    app.run(debug=True)