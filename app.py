from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import date, datetime
import calendar

app = Flask(__name__)

db_abbrevs = {
    "UK": "uk",
    "Ireland": "ir",
    "India": "in",
    "FinanceTeam": "fi"
}

def current_month_tasks(month, country):
    conn = sqlite3.connect("country_database.db")
    cursor = conn.cursor()
    cursor.execute(f'''
    select TaskName, Day 
    from events_{db_abbrevs[country]}, tasks_{db_abbrevs[country]} 
    where events_{db_abbrevs[country]}.TaskID == tasks_{db_abbrevs[country]}.TaskID 
    and Month == {month}''')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.route('/')
def calendar_view():
    month = datetime.now().month
    country = request.args.get('country', 'UK')
    tasks = current_month_tasks(month, country)
    today = date.today()
    cal = calendar.Calendar()
    days = cal.monthdatescalendar(today.year, today.month)

    selected_month = today.strftime('%B %Y')

    return render_template('index.html', 
                           tasks=tasks, 
                           month=days,
                           selected_month=selected_month,
                           current_month=today.month,
                           current_year=today.year)

@app.route('/update_calendar')
def update_calendar():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    country = request.args.get('country')

    tasks = current_month_tasks(month, country)
    cal = calendar.Calendar()
    days = cal.monthdatescalendar(year, month)

    task_dict = {}
    for task in tasks:
        day = task[1]
        if day not in task_dict:
            task_dict[day] = []
        task_dict[day].append(task[0])

    formatted_days = [
        [
            {'day': day.day, 'tasks': task_dict.get(day.day, [])}
            for day in week
        ]
        for week in days
    ]
    selected_month = datetime(year, month, 1).strftime('%B %Y')

    data = {
        'selected_month': selected_month,
        'month': formatted_days
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug="True")