from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
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
    try:
        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute(f'''
        select TaskName, Day 
        from events_{db_abbrevs[country]}, tasks_{db_abbrevs[country]} 
        where events_{db_abbrevs[country]}.TaskID == tasks_{db_abbrevs[country]}.TaskID 
        and Month == {month}''')
        tasks = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        tasks = []
    finally:
        conn.close()
    return tasks

def retrieve_task_list(country):
    try:
        conn = sqlite3.connect("test_database.db")
        cursor = conn.cursor()
        cursor.execute(f'''
        select TaskName 
        from tasks_{db_abbrevs[country]}
        ''')
        tasks = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        tasks = []
    finally:
        conn.close()
    return tasks


#define the default calendar view
@app.route('/')
def calendar_view():
    try:
        month = datetime.now().month
        country = request.args.get('country', 'UK')
        if country not in db_abbrevs:
            flash(f"Invalid country", "error")
            country = "UK"
        tasks = current_month_tasks(month, country)
        today = date.today()
        cal = calendar.Calendar()
        days = cal.monthdatescalendar(today.year, today.month)
        selected_month = today.strftime('%B %Y')
    except Exception as e:
        flash(f"Error: {e}", "error")
        tasks = []
        days = []
        selected_month = ''

    return render_template('index.html', 
                           tasks=tasks, 
                           month=days,
                           selected_month=selected_month,
                           current_month=today.month,
                           current_year=today.year)

#get the desired month and country from the URL and return the days and tasks in JSON format
@app.route('/update_calendar')
def update_calendar():
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        country = request.args.get('country')

        if not year or not month or not country:
            return jsonify({"error": "Missing required parameters"}), 400
        
        year = int(year)
        month = int(month)

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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)

@app.route('/modify_tasks')
def show_form():
    try:
        option = request.args.get("operation")
        country = request.args.get("country_modify")

        if not option or not country:
            flash("Missing required parameters", "error")
            return redirect(url_for('calendar_view'))
        
        session["country"] = country

        if option == "Add":
            return render_template("add_form.html")
        elif option == "Delete":
            tasks = retrieve_task_list(country)
            return render_template("delete_form.html",
                                    tasks=tasks)
        
    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect(url_for('calendar_view'))

@app.route('/add_task', methods=['POST'])
def add_task():
    conn = None
    try:
        name = request.form["task_name"]
        dates = request.form.getlist("date[]")
        country = session["country"]

        if not name:
            flash("Task name is required", "error")
            return redirect(url_for('show_form', operation='Add', country_modify=country))
        
        if not dates or all(date.strip() == '' for date in dates):
            flash("At least one date is required", "error")
            return redirect(url_for('show_form', operation='Add', country_modify=country))
        
        if not country:
            flash("Invalid country selected", "error")
            return redirect(url_for('calendar_view'))

        if name and dates and country:
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
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('calendar_view'))

@app.route('/delete_task', methods=['POST'])
def delete_task():
    conn = None
    try:
        task = request.form["task_select"]
        country = session["country"]

        if not task or not country:
            flash("All fields are required", "error")
            return redirect(url_for('show_form', operation='Delete', country_modify=country))

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
    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        if conn:
            conn.close()
    
    return redirect(url_for('calendar_view'))

if __name__ == '__main__':
    app.run(debug="True", host="0.0.0.0", port=10000)