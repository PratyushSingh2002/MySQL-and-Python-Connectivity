import mysql.connector
import time

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "123456"
DB_NAME = "inventory_management_system"

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_inventory_table_if_missing(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            quantity INT NOT NULL
        )
    """)

def add_item(cursor, product_name, quantity):
    cursor.execute(
        "INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)",
        (product_name, quantity)
    )

def update_quantity(cursor, product_name, new_quantity):
    cursor.execute(
        "UPDATE inventory SET quantity = %s WHERE product_name = %s",
        (new_quantity, product_name)
    )

def get_inventory_list(cursor):
    cursor.execute("SELECT * FROM inventory")
    return cursor.fetchall()

def main():
    conn = connect_to_database()
    if not conn:
        print("Could not connect to DB.")
        return

    cursor = conn.cursor()
    create_inventory_table_if_missing(cursor)
    conn.commit()

    while True:
        print("\n1. Add item to inventory")
        print("2. Update quantity")
        print("3. View inventory")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            product_name = input("Enter product name: ").strip()
            try:
                quantity = int(input("Enter quantity: ").strip())
            except ValueError:
                print("Enter a valid number.")
                continue
            add_item(cursor, product_name, quantity)
            conn.commit()
            print("Item added.")

        elif choice == "2":
            product_name = input("Enter product name: ").strip()
            try:
                new_quantity = int(input("Enter new quantity: ").strip())
            except ValueError:
                print("Enter a valid number.")
                continue
            update_quantity(cursor, product_name, new_quantity)
            conn.commit()
            print("Quantity updated.")

        elif choice == "3":
            inventory_list = get_inventory_list(cursor)
            print("\nInventory List:")
            for item in inventory_list:
                print(f"ID: {item[0]}, Product: {item[1]}, Quantity: {item[2]}")

        elif choice == "4":
            break

        else:
            print("Invalid choice.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    while True:
        login = input("Enter password to unlock: ")
        if login == DB_PASS:
            line = "Logging in, please wait..."
            for word in line.split():
                print(word, end=' ', flush=True)
                time.sleep(0.5)
            print()
            main()
            break
        else:
            print("Incorrect password.")
