import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="hospital_management_system"
    )

def initialize_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="123456")
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS hospital_management_system")
    conn.database = "hospital_management_system"

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        age INT,
        gender VARCHAR(10),
        admission_date DATE,
        discharge_date DATE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        specialization VARCHAR(255)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS PatientDoctor (
        patient_id INT,
        doctor_id INT,
        PRIMARY KEY (patient_id, doctor_id),
        FOREIGN KEY (patient_id) REFERENCES Patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES Doctors(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    cur.close()
    conn.close()

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None

def add_patient(conn, name, age, gender, admission_date, discharge_date):
    cur = conn.cursor()
    adm = parse_date(admission_date)
    dis = parse_date(discharge_date)
    cur.execute("""
        INSERT INTO Patients (name, age, gender, admission_date, discharge_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, age, gender, adm, dis))
    conn.commit()
    pid = cur.lastrowid
    cur.close()
    print(f"Patient added with id: {pid}")

def add_doctor(conn, name, specialization):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Doctors (name, specialization)
        VALUES (%s, %s)
    """, (name, specialization))
    conn.commit()
    did = cur.lastrowid
    cur.close()
    print(f"Doctor added with id: {did}")

def exists_patient(conn, patient_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Patients WHERE id=%s", (patient_id,))
    found = cur.fetchone() is not None
    cur.close()
    return found

def exists_doctor(conn, doctor_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Doctors WHERE id=%s", (doctor_id,))
    found = cur.fetchone() is not None
    cur.close()
    return found

def assign_doctor_to_patient(conn, patient_id, doctor_id):
    if not exists_patient(conn, patient_id):
        print("No such patient id.")
        return
    if not exists_doctor(conn, doctor_id):
        print("No such doctor id.")
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO PatientDoctor (patient_id, doctor_id)
            VALUES (%s, %s)
        """, (patient_id, doctor_id))
        conn.commit()
        print("Doctor assigned to patient.")
    except Error as e:
        # duplicate primary key or other db error
        if e.errno == 1062:
            print("This doctor is already assigned to that patient.")
        else:
            print("Database error:", e)
    finally:
        cur.close()

def get_all_patients(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, gender, admission_date, discharge_date FROM Patients")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_all_doctors(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, specialization FROM Doctors")
    rows = cur.fetchall()
    cur.close()
    return rows

def get_patient_doctor_assignments(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name AS patient_name, d.name AS doctor_name, p.id AS patient_id, d.id AS doctor_id
        FROM PatientDoctor pd
        JOIN Patients p ON pd.patient_id = p.id
        JOIN Doctors d ON pd.doctor_id = d.id
        ORDER BY p.id
    """)
    rows = cur.fetchall()
    cur.close()
    return rows

def display_patients(conn):
    print("\nPatients:")
    for p in get_all_patients(conn):
        print(f"ID:{p[0]} | {p[1]} | age:{p[2]} | {p[3]} | admission:{p[4]} | discharge:{p[5]}")

def display_doctors(conn):
    print("\nDoctors:")
    for d in get_all_doctors(conn):
        print(f"ID:{d[0]} | {d[1]} | specialization:{d[2]}")

def display_assignments(conn):
    print("\nAssignments:")
    for a in get_patient_doctor_assignments(conn):
        print(f"Patient ID {a[2]} ({a[0]})  - Doctor ID {a[3]} ({a[1]})")

def main_menu():
    initialize_db()
    conn = create_connection()
    try:
        while True:
            print("\n1.Add Patient  2.Add Doctor  3.Assign Doctor  4.Show Patients  5.Show Doctors  6.Show Assignments  7.Exit")
            choice = input("Choice: ").strip()
            if choice == "1":
                name = input("Patient name: ").strip()
                age = input("Age: ").strip()
                age = int(age) if age.isdigit() else None
                gender = input("Gender: ").strip()
                admission_date = input("Admission date (YYYY-MM-DD or blank): ").strip()
                discharge_date = input("Discharge date (YYYY-MM-DD or blank): ").strip()
                if admission_date and not parse_date(admission_date):
                    print("Invalid admission date format.")
                    continue
                if discharge_date and not parse_date(discharge_date):
                    print("Invalid discharge date format.")
                    continue
                add_patient(conn, name, age, gender, admission_date, discharge_date)
            elif choice == "2":
                name = input("Doctor name: ").strip()
                specialization = input("Specialization: ").strip()
                add_doctor(conn, name, specialization)
            elif choice == "3":
                display_patients(conn)
                pid = input("Enter patient ID: ").strip()
                display_doctors(conn)
                did = input("Enter doctor ID: ").strip()
                if pid.isdigit() and did.isdigit():
                    assign_doctor_to_patient(conn, int(pid), int(did))
                else:
                    print("IDs must be integers.")
            elif choice == "4":
                display_patients(conn)
            elif choice == "5":
                display_doctors(conn)
            elif choice == "6":
                display_assignments(conn)
            elif choice == "7":
                break
            else:
                print("Invalid.")
    finally:
        conn.close()

if __name__ == "__main__":
    main_menu()