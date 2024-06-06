from flask import Flask, render_template, request, jsonify, session
import sqlite3
from datetime import date, datetime
import calendar

#instantiate a Flask object
app = Flask(__name__)
app.secret_key = "helixr"

#store the suffixes of the database tables
db_abbrevs = {
    "UK": "uk",
    "Ireland": "ir",
    "India": "in",
    "FinanceTeam": "fi"
}

#select the events for a particular month and country and return an array of tuples storing task and date
def current_month_tasks(month, country):
    conn = sqlite3.connect("test_database.db")
    cursor = conn.cursor()
    cursor.execute(f'''
    select TaskName, Day 
    from events_{db_abbrevs[country]}, tasks_{db_abbrevs[country]} 
    where events_{db_abbrevs[country]}.TaskID == tasks_{db_abbrevs[country]}.TaskID 
    and Month == {month}''')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def retrieve_task_list(country):
    conn = sqlite3.connect("test_database.db")
    cursor = conn.cursor()
    cursor.execute(f'''
    select TaskName 
    from tasks_{db_abbrevs[country]}
    ''')
    tasks = cursor.fetchall()
    conn.close()
    return tasks


#define the default calendar view
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

#get the desired month and country from the URL and return the days and tasks in JSON format
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

@app.route('/modify_tasks')
def show_form():
    option = request.args.get("operation")
    country = request.args.get("country_modify")
    session["country"] = country

    if option == "Add":
        return render_template("add_form.html")
    elif option == "Delete":
        tasks = retrieve_task_list(country)
        return render_template("delete_form.html",
                               tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    name = request.form["task_name"]
    dates = request.form.getlist("date[]")
    country = session["country"]

    conn = sqlite3.connect("test_database.db")
    cursor = conn.cursor()
    
    cursor.execute(f'''
    insert into tasks_{db_abbrevs[country]} (TaskName)
    values (?)
    ''', (name, ))
    new_id = cursor.lastrowid
    conn.commit()

    
    for date in dates:
        new_date = datetime.strptime(date, "%Y-%m-%d")
        month = new_date.month
        day = new_date.day

        cursor.execute(f'''
        insert into events_{db_abbrevs[country]} (TaskID, Month, Day)
        values (?, ?, ?)
        ''', (new_id, month, day))
    
    conn.commit()
    conn.close()

    return render_template("index.html")

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task = request.form["task_select"]
    country = session["country"]

    conn = sqlite3.connect("test_database.db")
    cursor = conn.cursor()
    cursor.execute(f'''
    select TaskID from tasks_{db_abbrevs[country]}
    where TaskName = ?
    ''', (task,))
    task_id = cursor.fetchone()

    if task_id:
        task_id = task_id[0]
        cursor.execute(f'''
        delete from tasks_{db_abbrevs[country]}
        where TaskID = ?
        ''', (task_id,))
        cursor.execute(f'''
        delete from events_{db_abbrevs[country]}
        where TaskID = ?
        ''', (task_id,))
        conn.commit()
    
    conn.close()
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug="True")