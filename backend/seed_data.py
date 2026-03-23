import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

conn = sqlite3.connect("railway.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


# ---------------- DROP TABLES ----------------
cursor.executescript("""
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS USERS;
DROP TABLE IF EXISTS RESERVES;
DROP TABLE IF EXISTS ASSIGNED_TO;
DROP TABLE IF EXISTS TRAIN_TIMING;
DROP TABLE IF EXISTS TRAIN_INSTANCE;
DROP TABLE IF EXISTS TRAIN;
DROP TABLE IF EXISTS PASSENGER;
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS AGE_INFO;
DROP TABLE IF EXISTS STATION;
DROP TABLE IF EXISTS COACH_ATTENDANT;
DROP TABLE IF EXISTS DRIVER;

PRAGMA foreign_keys = ON;
""")


# ---------------- CREATE TABLES ----------------
cursor.executescript("""
CREATE TABLE STATION (
station_code TEXT PRIMARY KEY,
name TEXT,
city TEXT,
state TEXT,
country TEXT
);

CREATE TABLE TRAIN (
train_no TEXT PRIMARY KEY,
train_name TEXT,
source TEXT,
destination TEXT,
train_type TEXT,
total_seats INTEGER
);

CREATE TABLE TRAIN_INSTANCE (
train_no TEXT,
date TEXT,
available_seats INTEGER,
PRIMARY KEY (train_no, date)
);

CREATE TABLE PASSENGER (
passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
phone TEXT
);

CREATE TABLE EMPLOYEE (
emp_id TEXT PRIMARY KEY,
dob TEXT,
station_code TEXT,
name TEXT,
role TEXT,
salary INTEGER
);

CREATE TABLE AGE_INFO (
dob TEXT PRIMARY KEY,
age INTEGER
);

CREATE TABLE ASSIGNED_TO (
train_no TEXT,
emp_id TEXT,
PRIMARY KEY (train_no, emp_id)
);

CREATE TABLE RESERVES (
reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
passenger_id INTEGER,
train_no TEXT,
date TEXT,
from_station TEXT,
to_station TEXT,
seats INTEGER
);

CREATE TABLE USERS (
User_id INTEGER PRIMARY KEY AUTOINCREMENT,
Username TEXT UNIQUE,
Password TEXT,
Role TEXT,
Ref_id TEXT
);

CREATE TABLE TRAIN_TIMING (
train_no TEXT,
station_code TEXT,
day_no INTEGER,
arrival_time TEXT,
departure_time TEXT,
PRIMARY KEY (train_no, station_code)
);

CREATE TABLE COACH_ATTENDANT (
emp_id TEXT PRIMARY KEY,
language TEXT
);

CREATE TABLE DRIVER (
emp_id TEXT PRIMARY KEY,
experience INTEGER,
license_no TEXT
);
""")


cursor.executescript("""
INSERT INTO STATION VALUES 
('MAS','Chennai','Chennai','TN','India'),
('SBC','Bangalore','Bangalore','KA','India'),
('HYB','Hyderabad','Hyderabad','TS','India'),
('NDLS','Delhi','Delhi','DL','India'),
('CSTM','Mumbai','Mumbai','MH','India'),
('PUNE','Pune','Pune','MH','India'),
('KOL','Kolkata','Kolkata','WB','India'),
('JP','Jaipur','Jaipur','RJ','India'),
('LKO','Lucknow','Lucknow','UP','India'),
('BPL','Bhopal','Bhopal','MP','India');
""")

cursor.executescript("""
INSERT INTO TRAIN VALUES 
('T101','Chennai Express','MAS','NDLS','SUPERFAST',1200),
('T102','Bangalore Mail','SBC','NDLS','EXPRESS',900),
('T103','Hyderabad Express','HYB','MAS','SUPERFAST',1000),
('T104','Mumbai Rajdhani','CSTM','NDLS','RAJDHANI',800),
('T105','Pune Express','PUNE','SBC','PASSENGER',700),
('T106','Kolkata Express','KOL','MAS','EXPRESS',950),
('T107','Jaipur Express','JP','NDLS','EXPRESS',800),
('T108','Lucknow Mail','LKO','NDLS','EXPRESS',850),
('T109','Bhopal Shatabdi','BPL','NDLS','SHATABDI',750),
('T110','South Link','MAS','CSTM','SUPERFAST',1100);
""")


cursor.executescript("""
INSERT INTO TRAIN_INSTANCE VALUES 
('T101','2026-04-01',800),
('T102','2026-04-01',600),
('T103','2026-04-01',700),
('T104','2026-04-01',500),
('T105','2026-04-01',400),
('T106','2026-04-01',750),
('T107','2026-04-01',550),
('T108','2026-04-01',500),
('T109','2026-04-01',600),
('T110','2026-04-01',900);
""")



employees = [
("EMP101",'1990-01-01','MAS','Ravi','Driver',50000),
("EMP102",'1991-02-02','SBC','Anil','Coach Attendant',40000),
("EMP103",'1989-03-03','HYB','Kumar','Driver',52000),
("EMP104",'1992-04-04','MAS','Suresh','Coach Attendant',42000),
("EMP105",'1988-05-05','SBC','Manoj','Driver',38000),
("EMP106",'1993-06-06','CSTM','Ajay','Driver',55000),
("EMP107",'1994-07-07','MAS','Vikram','Coach Attendant',30000),
("EMP108",'1995-08-08','HYB','Rahul','Coach Attendant',41000),
("EMP109",'1996-09-09','PUNE','Karthik','Driver',32000),
("EMP110",'1997-10-10','KOL','Deepak','Coach Attendant',36000),
]

cursor.executemany("INSERT INTO EMPLOYEE VALUES (?,?,?,?,?,?)", employees)


# ---------------- AGE_INFO ----------------
def calculate_age(dob):
    dob_dt = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    return today.year - dob_dt.year

age_data = [(emp[1], calculate_age(emp[1])) for emp in employees]
cursor.executemany("INSERT INTO AGE_INFO VALUES (?, ?)", age_data)


# ---------------- ASSIGNMENTS ----------------
assignments = [
('T101','EMP101'),('T102','EMP102'),('T103','EMP103'),
('T104','EMP106'),('T105','EMP105'),
('T106','EMP110'),('T107','EMP109'),
('T108','EMP108'),('T109','EMP104'),('T110','EMP107')
]

cursor.executemany("INSERT INTO ASSIGNED_TO VALUES (?, ?)", assignments)


# ---------------- TRAIN TIMING ----------------
cursor.executescript("""
INSERT INTO TRAIN_TIMING VALUES
('T101','MAS',1,NULL,'06:00'),
('T101','HYB',1,'14:30','14:45'),
('T101','BPL',2,'02:00','02:15'),
('T101','NDLS',2,'10:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T102','SBC',1,NULL,'08:00'),
('T102','HYB',1,'16:00','16:15'),
('T102','BPL',2,'03:30','03:45'),
('T102','NDLS',2,'12:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T103','HYB',1,NULL,'07:00'),
('T103','BPL',1,'12:00','12:15'),
('T103','SBC',1,'20:00','20:15'),
('T103','MAS',2,'02:30',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T104','CSTM',1,NULL,'17:00'),
('T104','PUNE',1,'20:00','20:10'),
('T104','BPL',2,'04:00','04:15'),
('T104','JP',2,'12:00','12:15'),
('T104','NDLS',2,'16:30',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T105','PUNE',1,NULL,'09:00'),
('T105','CSTM',1,'12:30','12:45'),
('T105','HYB',1,'22:00','22:15'),
('T105','SBC',2,'06:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T106','KOL',1,NULL,'05:00'),
('T106','BPL',1,'18:00','18:15'),
('T106','HYB',2,'04:00','04:15'),
('T106','SBC',2,'14:00','14:15'),
('T106','MAS',2,'18:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T107','JP',1,NULL,'06:30'),
('T107','LKO',1,'14:00','14:15'),
('T107','NDLS',1,'20:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T108','LKO',1,NULL,'22:00'),
('T108','BPL',2,'06:00','06:15'),
('T108','JP',2,'14:00','14:15'),
('T108','NDLS',2,'20:30',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T109','BPL',1,NULL,'06:00'),
('T109','JP',1,'12:00','12:10'),
('T109','NDLS',1,'16:00',NULL);

INSERT INTO TRAIN_TIMING VALUES
('T110','MAS',1,NULL,'10:00'),
('T110','SBC',1,'16:00','16:15'),
('T110','PUNE',2,'06:00','06:15'),
('T110','CSTM',2,'10:00',NULL);
""")


# ---------------- COACH ATTENDANTS ----------------
coach_attendants = [
    ('EMP102', 'Hindi'),
    ('EMP104', 'English'),
    ('EMP107', 'Kannada'),
    ('EMP108', 'Tamil'),
    ('EMP110', 'Telugu'),
]
cursor.executemany("INSERT INTO COACH_ATTENDANT VALUES (?, ?)", coach_attendants)


# ---------------- DRIVERS ----------------
drivers = [
    ('EMP101', 15, 'DL-2010-0001'),
    ('EMP103', 20, 'DL-2005-0042'),
    ('EMP105', 12, 'DL-2013-0077'),
    ('EMP106', 8, 'DL-2017-0103'),
    ('EMP109', 5, 'DL-2020-0055'),
]
cursor.executemany("INSERT INTO DRIVER VALUES (?, ?, ?)", drivers)


# ---------------- ADDITIONAL TRAIN INSTANCES ----------------
additional_instances = [
    ('T101','2026-04-02',750), ('T101','2026-04-03',900), ('T101','2026-04-05',650), ('T101','2026-04-10',1000),
    ('T102','2026-04-02',550), ('T102','2026-04-03',700), ('T102','2026-04-05',480), ('T102','2026-04-10',800),
    ('T103','2026-04-02',680), ('T103','2026-04-03',750), ('T103','2026-04-05',600), ('T103','2026-04-10',900),
    ('T104','2026-04-02',450), ('T104','2026-04-03',600), ('T104','2026-04-05',380), ('T104','2026-04-10',700),
    ('T105','2026-04-02',350), ('T105','2026-04-03',500), ('T105','2026-04-05',300), ('T105','2026-04-10',600),
    ('T106','2026-04-02',700), ('T106','2026-04-03',800), ('T106','2026-04-05',620), ('T106','2026-04-10',850),
    ('T107','2026-04-02',500), ('T107','2026-04-03',650), ('T107','2026-04-05',420), ('T107','2026-04-10',750),
    ('T108','2026-04-02',480), ('T108','2026-04-03',600), ('T108','2026-04-05',400), ('T108','2026-04-10',700),
    ('T109','2026-04-02',550), ('T109','2026-04-03',650), ('T109','2026-04-05',500), ('T109','2026-04-10',700),
    ('T110','2026-04-02',850), ('T110','2026-04-03',950), ('T110','2026-04-05',780), ('T110','2026-04-10',1000),
]
cursor.executemany("INSERT INTO TRAIN_INSTANCE VALUES (?, ?, ?)", additional_instances)


conn.commit()
conn.close()

print("✅ CLEAN SEED DATA (NO PASSENGERS)")