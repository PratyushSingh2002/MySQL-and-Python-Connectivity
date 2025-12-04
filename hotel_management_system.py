# Hotel management system
# Make sure to install the required libraries, including mysql.connector

import time
import mysql.connector
import csv

# Establish a database connection
connect = mysql.connector.connect(host="localhost", user="root", password="123456")
cursor = connect.cursor()

# Create database if not exists
create_db_query = 'CREATE DATABASE IF NOT EXISTS hotel_management'
cursor.execute(create_db_query)
connect.database = 'hotel_management'


# Create the table (with corrected SQL syntax)
query1 = "CREATE TABLE IF NOT EXISTS hotel_data_customer (name VARCHAR(100), contact varchar(10) , email varchar(200) , address varchar(200) , child int , adult int , no_of_days int , room_no int )"
cursor.execute(query1)
# check out function
def check_out(room_no):
    try:
        delete_query="DELETE FROM hotel_data_customer WHERE room_no = %s"
        cursor.execute(delete_query,(room_no,))
        connect.commit()
    finally:
        cursor.close()
# room booking function
def book_a_room():
    Name = input("First name : - ")
    contact = input("Contact number : - ")
    email = input("Email id : - ")
    address = input("Address : - ")
    days = int(input("No of days : - "))
    child = int(input("No of child : - "))
    adult = int(input("No of adult : - "))
    
    # Check for available rooms
    available_rooms = get_available_rooms()
    if not available_rooms:
        print("Sorry, no rooms available.")
        return
    
    room_no = int(input(f"Available rooms: {available_rooms}\nEnter room no: - "))
    
    query = "INSERT INTO hotel_data_customer VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    data = (Name, contact, email, address, days, child, adult, room_no)
    cursor.execute(query, data)
    connect.commit()
    print("BOOKING SUCCESSFUL")

# Get the list of available rooms
def get_available_rooms():
    total_rooms = set(range(1, 51))
    booked_rooms_query = "SELECT room_no FROM hotel_data_customer"
    cursor.execute(booked_rooms_query)
    booked_rooms = set(row[0] for row in cursor.fetchall())
    available_rooms = total_rooms - booked_rooms
    return list(available_rooms)


# hotel status
def hotel_status():
    available_rooms = get_available_rooms()
    print(f"Available Rooms: {available_rooms}")
    print("""
BOOKING TIMINGS ARE 5:00 AM - 12:00 AM
OTHERWISE SPECIAL ENTRY
FULLY BOOKED ON DIWALI
DISCOUNT AVAILABLE IN ICICI BANK ON UPI ALSO
THANK YOU
VISIT AGAIN""")
# creating login function 
def after_login():
    print("""
=======================================
||  WELCOME TO BANKING MANAGEMENT    ||
=======================================
|| YOU HAVE THESE OPTION AVAILABLE   ||
=======================================
|| 1 . BOOK A ROOM                   ||
=======================================
|| 2 . CHECK OUT                     ||
=======================================
|| 3 . HOTEL STATUS                  ||
=======================================
|| 4 . PAYMENT INFO                  ||
=======================================
|| 5 . CONTACT                       ||
=======================================
|| 6 . Export Data to CSV            ||
=======================================""")
# billing function
def payment_info():
    name=input("Enter name ")
    query="select no_of_days from hotel_data_customer where name = %s"
    cursor.execute(query,(name,))
    result=cursor.fetchone()
    if result:
        number_of_days = result[0]
        print(f"Number of days for {name}: {number_of_days}")
        bill=number_of_days * 2000
        print("YOU ARE TOTAL BILLED OF ",bill)
    else:
        print(f"No data found for {name}.")

# CONTACT  FUNCTION
def contact():
    print("""
==================================================
|            YOU MAY CONTACT US ON               |
==================================================
| 1 . EMAIL - dhruvit@gmail.com               |
==================================================
| 2 . PHONE NUMEBER - 9197828945                 |
==================================================
| 3 . ADDRESS - INDIA      |
==================================================
| 4 . MEETING TIME 10AM-8PM (MONDAY-FRIDAY)      |
==================================================
|                   THANK YOU                    |
==================================================""")

# Export data to CSV
def export_data_to_csv():
    try:
        query = "SELECT * FROM hotel_data_customer"
        cursor.execute(query)
        data = cursor.fetchall()

        if not data:
            print("No data to export.")
            return

        headers = [desc[0] for desc in cursor.description]

        with open('hotel_data_export.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            csv_writer.writerows(data)

        print("Data exported to 'hotel_data_export.csv' successfully.")

    except Exception as e:
        print(f"Error exporting data: {e}")

# creating optional function
def first_option():
    option=int(input("Enter your option "))
    if option==1:
        book_a_room()
    elif option==2:
        room_to_check_out=int(input("Enter room number to check out"))
        check_out(room_to_check_out)
    elif option==3:
        hotel_status()
    elif option==4:
        payment_info()
    elif option==5:
        contact()
    elif option==6:
        export_data_to_csv()
    else:
        print("Wrong input ")


# Password login loop
while True:
    login = input("Enter password to unlock: ")
    if login == "123456":
        line = "Logging in, please wait..."
        words = line.split()
        for word in words:
            print(word, end=' ', flush=True)
            time.sleep(0.5)
        after_login()
        first_option()
        
    else:
        print("Incorrect password. Try again.")


