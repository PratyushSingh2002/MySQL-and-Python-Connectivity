import mysql.connector
import time
import sys

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "123456"
DB_NAME = "inventory_management_system"

def get_conn(db=None):
    cfg = {"host": DB_HOST, "user": DB_USER, "password": DB_PASS}
    if db:
        cfg["database"] = db
    return mysql.connector.connect(**cfg)

def ensure_db_and_table():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cur.execute(f"USE `{DB_NAME}`")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error as e:
        print("DB error:", e)
        sys.exit(1)

def add_item(name, qty):
    conn = get_conn(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)", (name, qty))
    conn.commit()
    cur.close()
    conn.close()

def update_quantity(name, qty):
    conn = get_conn(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE inventory SET quantity = %s WHERE product_name = %s", (qty, name))
    conn.commit()
    cur.close()
    conn.close()

def view_inventory():
    conn = get_conn(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, product_name, quantity FROM inventory")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        print("Inventory empty.")
    else:
        print("{:<4} {:<30} {:<8}".format("ID", "Product", "Qty"))
        for r in rows:
            print("{:<4} {:<30} {:<8}".format(r[0], r[1], r[2]))

def main():
    ensure_db_and_table()
    while True:
        print("\n1. Add item\n2. Update quantity\n3. View inventory\n4. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            name = input("Product name: ").strip()
            try:
                qty = int(input("Quantity: ").strip())
            except ValueError:
                print("Enter integer quantity.")
                continue
            add_item(name, qty)
            print("Added.")
        elif choice == "2":
            name = input("Product name: ").strip()
            try:
                qty = int(input("New quantity: ").strip())
            except ValueError:
                print("Enter integer quantity.")
                continue
            update_quantity(name, qty)
            print("Updated.")
        elif choice == "3":
            view_inventory()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    while True:
        pwd = input("Enter password to unlock: ")
        if pwd == DB_PASS:
            for w in "Logging in, please wait...".split():
                print(w, end=" ", flush=True)
                time.sleep(0.3)
            print()
            main()
            break
        else:
            print("Incorrect password.")
