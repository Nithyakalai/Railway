from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

app.secret_key = "secret"
DB = "railway.db"


def query_db(query, args=(), one=False):
    try:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except:
        return None


@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", message=str(e)), 500


@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = query_db("SELECT * FROM USERS WHERE Username=?", (username,), one=True)

            if user and check_password_hash(user['Password'], password):
                session['user'] = dict(user)

                if user['Role'] == 'PASSENGER':
                    return redirect('/passenger')
                else:
                    return redirect('/employee')

            return render_template("login.html", error="Invalid credentials")

        return render_template('login.html')

    except Exception as e:
        return render_template("error.html", message=str(e))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role', 'PASSENGER')

            conn = sqlite3.connect(DB)
            cur = conn.cursor()

            if role == 'EMPLOYEE':
                cur.execute("SELECT 1 FROM EMPLOYEE WHERE emp_id=?", (username,))
                if not cur.fetchone():
                    conn.close()
                    return render_template('signup.html', error="Employee ID not found. Your username must be your Employee ID (e.g. EMP101).")

                cur.execute("""
                INSERT INTO USERS (Username, Password, Role, Ref_id)
                VALUES (?, ?, 'EMPLOYEE', ?)
                """, (username, generate_password_hash(password), username))
            else:
                name = request.form.get('name', '')
                email = request.form.get('email', '')
                phone = request.form.get('phone', '')

                cur.execute("""
                INSERT INTO PASSENGER (name, email, phone)
                VALUES (?, ?, ?)
                """, (name, email, phone))

                passenger_id = cur.lastrowid

                cur.execute("""
                INSERT INTO USERS (Username, Password, Role, Ref_id)
                VALUES (?, ?, 'PASSENGER', ?)
                """, (username, generate_password_hash(password), passenger_id))

            conn.commit()
            conn.close()

            return redirect('/')

        return render_template('signup.html')

    except Exception as e:
        return render_template("error.html", message=str(e))

@app.route('/passenger')
def passenger():
    try:
        user = session.get('user')
        if not user:
            return redirect('/')

        passenger_id = user['Ref_id']

        bookings = query_db("""
        SELECT COUNT(*) as total FROM RESERVES WHERE passenger_id=?
        """, (passenger_id,), one=True)

        passenger_info = query_db("""
        SELECT name, email, phone FROM PASSENGER WHERE passenger_id=?
        """, (passenger_id,), one=True)

        stations = query_db("SELECT station_code, name FROM STATION") or []

        return render_template(
            'passenger.html',
            total=bookings['total'] if bookings else 0,
            passenger={
                'name': passenger_info['name'],
                'email': passenger_info['email'],
                'phone': passenger_info['phone']
            } if passenger_info else {'name': '', 'email': '', 'phone': ''},
            stations=stations
        )

    except Exception as e:
        return render_template("error.html", message=str(e))


@app.route('/search_trains', methods=['POST'])
def search_trains():
    try:
        data = request.json or {}

        from_station = data.get('from')
        to_station = data.get('to')

        if not data.get('date') or not from_station or not to_station:
            return jsonify([])

        trains = query_db("""
        SELECT t.train_no, t.train_name, t.source, t.destination,
               ti.available_seats,
               tt_from.departure_time,
               tt_to.arrival_time,
               tt_from.day_no AS from_day_no,
               date(ti.date, '+' || (tt_from.day_no - 1) || ' days') AS boarding_date
        FROM TRAIN t
        JOIN TRAIN_INSTANCE ti ON t.train_no = ti.train_no
        JOIN TRAIN_TIMING tt_from ON t.train_no = tt_from.train_no
            AND tt_from.station_code = ?
        JOIN TRAIN_TIMING tt_to ON t.train_no = tt_to.train_no
            AND tt_to.station_code = ?
        WHERE ti.date = ?
          AND ti.available_seats > 0
          AND tt_from.day_no <= tt_to.day_no
        """, (from_station, to_station, data['date'])) or []

        results = []
        for row in trains:
            results.append({
                'train_no': row['train_no'],
                'train_name': row['train_name'],
                'source': row['source'],
                'destination': row['destination'],
                'available_seats': row['available_seats'],
                'departure_time': row['departure_time'],
                'arrival_time': row['arrival_time'],
                'boarding_date': row['boarding_date'],
                'from_station': from_station,
                'to_station': to_station
            })

        return jsonify(results)

    except:
        return jsonify([])

@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    try:
        data = request.json or {}

        required = ['train_no', 'date', 'from', 'to', 'seats']
        if not all(k in data for k in required):
            return jsonify({"status": "❌ Missing data"})

        seats = int(data['seats'])

        user = session.get('user')
        if not user:
            return jsonify({"status": "❌ Login required"})

        passenger_id = user['Ref_id']

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

       
        cur.execute("""
        UPDATE TRAIN_INSTANCE
        SET available_seats = available_seats - ?
        WHERE train_no=? AND date=? AND available_seats >= ?
        """, (seats, data['train_no'], data['date'], seats))

        if cur.rowcount == 0:
            return jsonify({"status": "❌ Not enough seats"})

        cur.execute("""
        INSERT INTO RESERVES (passenger_id, train_no, date, from_station, to_station, seats)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            passenger_id,
            data['train_no'],
            data['date'],
            data['from'],
            data['to'],
            seats
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": "✅ Booked successfully"})

    except Exception as e:
        return jsonify({"status": f"❌ Error: {str(e)}"})


@app.route('/reservations')
def reservations():
    try:
        user = session.get('user')
        if not user:
            return redirect('/')

        passenger_id = user['Ref_id']

        data = query_db("""
        SELECT train_no, date, from_station, to_station, seats
        FROM RESERVES
        WHERE passenger_id=?
        """, (passenger_id,)) or []

        return render_template('reservations.html', data=data)

    except Exception as e:
        return render_template("error.html", message=str(e))

@app.route('/employee')
def employee():
    try:
        user = session.get('user')
        if not user:
            return redirect('/')

        emp = query_db("""
            SELECT e.*, a.age
            FROM EMPLOYEE e
            LEFT JOIN AGE_INFO a ON e.dob = a.dob
            WHERE e.emp_id=?
        """, (user['Ref_id'],), one=True)

        role_details = None
        if emp:
            if emp['role'] == 'Driver':
                role_details = query_db("""
                    SELECT experience AS driving_hours, license_no FROM DRIVER WHERE emp_id=?
                """, (user['Ref_id'],), one=True)
            elif emp['role'] == 'Coach Attendant':
                role_details = query_db("""
                    SELECT language FROM COACH_ATTENDANT WHERE emp_id=?
                """, (user['Ref_id'],), one=True)

        trains = query_db("""
        SELECT t.train_no, t.train_name, MIN(ti.date) AS next_date
        FROM ASSIGNED_TO at
        JOIN TRAIN t ON at.train_no = t.train_no
        JOIN TRAIN_INSTANCE ti ON t.train_no = ti.train_no
        WHERE at.emp_id = ?
          AND ti.date >= date('now')
        GROUP BY t.train_no, t.train_name
        """, (user['Ref_id'],)) or []

        return render_template('employee.html', emp=emp, trains=trains, role_details=role_details)

    except Exception as e:
        return render_template("error.html", message=str(e))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)