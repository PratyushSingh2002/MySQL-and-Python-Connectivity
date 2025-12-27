import mysql.connector
from datetime import timedelta, datetime

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456"
)
cursor = connection.cursor()

db = "gym_management"
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
connection.database = db

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(15),
    membership_start DATE,
    membership_end DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    workout_date DATE,
    duration_minutes INT,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
)
""")

def add_member(name, email, phone, days):
    start = datetime.now().date()
    end = start + timedelta(days=days)
    cursor.execute(
        "INSERT INTO members (name,email,phone,membership_start,membership_end) VALUES (%s,%s,%s,%s,%s)",
        (name, email, phone, start, end)
    )
    connection.commit()
    print("Member added")

def remove_member(mid):
    cursor.execute("SELECT id FROM members WHERE id=%s", (mid,))
    if not cursor.fetchone():
        print("Member not found")
        return
    cursor.execute("DELETE FROM members WHERE id=%s", (mid,))
    connection.commit()
    print("Member removed")

def log_workout(mid, date, mins):
    cursor.execute("SELECT id FROM members WHERE id=%s", (mid,))
    if not cursor.fetchone():
        print("Member does not exist")
        return
    cursor.execute(
        "INSERT INTO workouts (member_id,workout_date,duration_minutes) VALUES (%s,%s,%s)",
        (mid, date, mins)
    )
    connection.commit()
    print("Workout saved")

def view_workouts(mid):
    cursor.execute("SELECT * FROM workouts WHERE member_id=%s ORDER BY workout_date DESC", (mid,))
    data = cursor.fetchall()
    if not data:
        print("No records")
        return
    for w in data:
        print(f"{w[0]}  {w[2]}  {w[3]} min")

def list_members():
    cursor.execute("SELECT * FROM members")
    data = cursor.fetchall()
    for m in data:
        print(f"{m[0]}  {m[1]}  {m[3]}  {m[5]}")

def check_status(mid):
    cursor.execute("SELECT membership_end FROM members WHERE id=%s", (mid,))
    res = cursor.fetchone()
    if not res:
        print("Member not found")
        return
    if datetime.now().date() > res[0]:
        print("Membership expired")
    else:
        print("Active till", res[0])

while True:
    print("\n1 Add\n2 Remove\n3 Workout\n4 History\n5 Members\n6 Status\n7 Exit")
    ch = input("Choice: ")

    if ch == "1":
        add_member(input("Name: "), input("Email: "), input("Phone: "), int(input("Days: ")))
    elif ch == "2":
        remove_member(int(input("ID: ")))
    elif ch == "3":
        mid = int(input("ID: "))
        d = input("Date (YYYY-MM-DD) or blank: ")
        d = datetime.now().date() if d == "" else datetime.strptime(d, "%Y-%m-%d").date()
        log_workout(mid, d, int(input("Minutes: ")))
    elif ch == "4":
        view_workouts(int(input("ID: ")))
    elif ch == "5":
        list_members()
    elif ch == "6":
        check_status(int(input("ID: ")))
    elif ch == "7":
        cursor.close()
        connection.close()
        break
    else:
        print("Wrong choice")
