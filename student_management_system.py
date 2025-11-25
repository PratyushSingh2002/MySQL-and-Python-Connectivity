import mysql.connector
import csv

connect = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    charset='utf8'
)
cursor = connect.cursor()

cursor.execute('CREATE DATABASE IF NOT EXISTS student_data_manager')
connect.database = 'student_data_manager'

cursor.execute('''
CREATE TABLE IF NOT EXISTS student_datas (
    name VARCHAR(100),
    address VARCHAR(100),
    phone VARCHAR(10),
    fname VARCHAR(100),
    mname VARCHAR(100),
    roll_no INT PRIMARY KEY
)
''')
connect.commit()

def add_student():
    name = input("Enter Student Name: ")
    address = input("Enter Student's Address: ")
    phone = input("Enter Student's Phone number: ")
    fname = input("Enter Student's Father Name: ")
    mname = input("Enter Student's Mother Name: ")
    roll_no = int(input("Enter Student's Roll No.: "))
    query = 'INSERT INTO student_datas (name, address, phone, fname, mname, roll_no) VALUES (%s, %s, %s, %s, %s, %s)'
    data = (name, address, phone, fname, mname, roll_no)
    try:
        cursor.execute(query, data)
        connect.commit()
        print("Data entered successfully.")
    except mysql.connector.IntegrityError:
        print("Roll number already exists.")

def view_student():
    roll_no = int(input("Enter Roll Number of Student: "))
    query = 'SELECT * FROM student_datas WHERE roll_no = %s'
    cursor.execute(query, (roll_no,))
    result = cursor.fetchone()
    if result:
        print("Student found:")
        print("Name:", result[0])
        print("Address:", result[1])
        print("Phone:", result[2])
        print("Father:", result[3])
        print("Mother:", result[4])
        print("Roll No:", result[5])
    else:
        print("Student not found.")

def delete_data():
    roll_no = int(input("Enter roll number to delete (0 to cancel): "))
    if roll_no == 0:
        print("Cancelled.")
        return
    query = 'DELETE FROM student_datas WHERE roll_no = %s'
    cursor.execute(query, (roll_no,))
    connect.commit()
    if cursor.rowcount > 0:
        print("Deleted successfully.")
    else:
        print("Record not found.")

def update_data():
    roll_no = int(input("Enter roll number of Student: "))
    cursor.execute('SELECT * FROM student_datas WHERE roll_no = %s', (roll_no,))
    if not cursor.fetchone():
        print("Student not found.")
        return

    name = input("Enter new name: ")
    address = input("Enter new address: ")
    phone = input("Enter new phone: ")
    fname = input("Enter new father name: ")
    mname = input("Enter new mother name: ")
    fields = []
    values = []

    if name:
        fields.append("name=%s")
        values.append(name)
    if address:
        fields.append("address=%s")
        values.append(address)
    if phone:
        fields.append("phone=%s")
        values.append(phone)
    if fname:
        fields.append("fname=%s")
        values.append(fname)
    if mname:
        fields.append("mname=%s")
        values.append(mname)

    if not fields:
        print("Nothing to update.")
        return

    query = f"UPDATE student_datas SET {', '.join(fields)} WHERE roll_no=%s"
    values.append(roll_no)
    cursor.execute(query, tuple(values))
    connect.commit()
    print("Updated successfully.")

def save_to_csv():
    cursor.execute('SELECT * FROM student_datas')
    data = cursor.fetchall()
    if data:
        with open('student_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Address", "Phone", "Father", "Mother", "Roll No"])
            writer.writerows(data)
        print("Exported to student_data.csv")
    else:
        print("No data available.")

def main_menu():
    while True:
        print("""
========================================
|      Student Management System       |
========================================
| 1. Add Student                      |
| 2. View Student Data                |
| 3. Update Student Data              |
| 4. Delete Student Data              |
| 5. Export to CSV                    |
| 6. Exit                             |
========================================
        """)
        ch = input("Enter your option: ")
        if ch == '1':
            add_student()
        elif ch == '2':
            view_student()
        elif ch == '3':
            update_data()
        elif ch == '4':
            delete_data()
        elif ch == '5':
            save_to_csv()
        elif ch == '6':
            break
        else:
            print("Invalid choice.")

while True:
    p = input("Enter password: ")
    if p == '123456':
        print("Login successful.")
        main_menu()
        break
    else:
        print("Wrong password.")
