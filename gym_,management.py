import mysql.connector
from datetime import timedelta, datetime

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456"
)
cursor = connection.cursor()

database_name = "gym_management"
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
connection.database = database_name

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
        FOREIGN KEY (member_id) REFERENCES members(id)
    )
""")

def add_member(name, email, phone, membership_duration_days):
    membership_start = datetime.now().date()
    membership_end = membership_start + timedelta(days=membership_duration_days)
    sql = """
        INSERT INTO members (name, email, phone, membership_start, membership_end)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (name, email, phone, membership_start, membership_end)
    cursor.execute(sql, values)
    connection.commit()
    print("Member added successfully")

def remove_member(member_id):
    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()
    if not member:
        print("Member not found")
        return

    cursor.execute("DELETE FROM workouts WHERE member_id = %s", (member_id,))
    cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
    connection.commit()
    print("Member removed successfully")

def log_workout(member_id, workout_date, duration_minutes):
    sql = "INSERT INTO workouts (member_id, workout_date, duration_minutes) VALUES (%s, %s, %s)"
    values = (member_id, workout_date, duration_minutes)
    cursor.execute(sql, values)
    connection.commit()
    print("Workout logged successfully")

def view_workout_history(member_id):
    sql = "SELECT * FROM workouts WHERE member_id = %s ORDER BY workout_date DESC"
    cursor.execute(sql, (member_id,))
    workouts = cursor.fetchall()
    if not workouts:
        print("No workout history found")
    else:
        print(f"Workout history for Member ID {member_id}:")
        for workout in workouts:
            print(f"Workout ID: {workout[0]}, Date: {workout[2]}, Duration: {workout[3]} minutes")

def list_all_members():
    sql = "SELECT * FROM members"
    cursor.execute(sql)
    members = cursor.fetchall()
    if not members:
        print("No members found")
    else:
        print("List of all members:")
        for member in members:
            print(
                f"Member ID: {member[0]}, Name: {member[1]}, Email: {member[2]}, "
                f"Phone: {member[3]}, Start: {member[4]}, End: {member[5]}"
            )

while True:
    print("\n1. Add Member")
    print("2. Remove Member")
    print("3. Log Workout")
    print("4. View Workout History")
    print("5. List All Members")
    print("6. Exit")

    choice = input("Enter your choice (1-6): ")

    if choice == "1":
        name = input("Enter member name: ")
        email = input("Enter member email: ")
        phone = input("Enter member phone: ")
        duration = int(input("Enter membership duration (in days): "))
        add_member(name, email, phone, duration)

    elif choice == "2":
        member_id = int(input("Enter Member ID to remove: "))
        remove_member(member_id)

    elif choice == "3":
        member_id = int(input("Enter Member ID: "))
        date_str = input("Enter workout date (YYYY-MM-DD) or leave blank for today: ").strip()
        if date_str == "":
            workout_date = datetime.now().date()
        else:
            workout_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        duration_minutes = int(input("Enter workout duration (in minutes): "))
        log_workout(member_id, workout_date, duration_minutes)

    elif choice == "4":
        member_id = int(input("Enter Member ID: "))
        view_workout_history(member_id)

    elif choice == "5":
        list_all_members()

    elif choice == "6":
        print("Exiting...")
        break

    else:
        print("Invalid choice")
