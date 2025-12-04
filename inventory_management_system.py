import mysql.connector
import time
import sys
import csv
from mysql.connector import errorcode

DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "123456"
DB_NAME = "inventory_management_system"

def get_conn(db=None):
    cfg = {"host": DB_HOST, "user": DB_USER, "password": DB_PASS, "autocommit": False}
    if db:
        cfg["database"] = db
    return mysql.connector.connect(**cfg)

def ensure_db_and_table():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        conn.database = DB_NAME
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL UNIQUE,
                quantity INT NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except mysql.connector.Error as e:
        print("DB error:", e)
        sys.exit(1)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def add_item(name, qty):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)", (name, qty))
        conn.commit()
        print(f"Added '{name}' with qty {qty}.")
    except mysql.connector.IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            print("Item already exists. Use update/increase instead.")
        else:
            print("DB integrity error:", e)
    except Exception as e:
        print("Error adding item:", e)
    finally:
        cur.close()
        conn.close()

def delete_item(name):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM inventory WHERE product_name = %s", (name,))
        conn.commit()
        if cur.rowcount:
            print(f"Deleted '{name}'.")
        else:
            print("No such product found.")
    except Exception as e:
        print("Error deleting item:", e)
    finally:
        cur.close()
        conn.close()

def update_quantity(name, qty):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.execute("UPDATE inventory SET quantity = %s WHERE product_name = %s", (qty, name))
        conn.commit()
        if cur.rowcount:
            print(f"Set '{name}' quantity to {qty}.")
        else:
            print("No such product found.")
    except Exception as e:
        print("Error updating quantity:", e)
    finally:
        cur.close()
        conn.close()

def change_quantity_delta(name, delta):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        # use single statement to avoid race conditions
        cur.execute("UPDATE inventory SET quantity = GREATEST(0, quantity + %s) WHERE product_name = %s", (delta, name))
        conn.commit()
        if cur.rowcount:
            print(f"Changed '{name}' by {delta}.")
        else:
            print("No such product found.")
    except Exception as e:
        print("Error changing quantity:", e)
    finally:
        cur.close()
        conn.close()

def view_inventory(limit=None):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        q = "SELECT id, product_name, quantity, last_updated FROM inventory ORDER BY product_name"
        if limit:
            q += " LIMIT %s"
            cur.execute(q, (limit,))
        else:
            cur.execute(q)
        rows = cur.fetchall()
        if not rows:
            print("Inventory empty.")
            return
        print("{:<4} {:<30} {:<8} {:<20}".format("ID", "Product", "Qty", "Last updated"))
        for r in rows:
            print("{:<4} {:<30} {:<8} {:<20}".format(r[0], r[1], r[2], str(r[3])))
    except Exception as e:
        print("Error viewing inventory:", e)
    finally:
        cur.close()
        conn.close()

def search_items(term):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        like = f"%{term}%"
        cur.execute("SELECT id, product_name, quantity FROM inventory WHERE product_name LIKE %s ORDER BY product_name", (like,))
        rows = cur.fetchall()
        if not rows:
            print("No matches.")
            return
        print("{:<4} {:<30} {:<8}".format("ID", "Product", "Qty"))
        for r in rows:
            print("{:<4} {:<30} {:<8}".format(r[0], r[1], r[2]))
    except Exception as e:
        print("Error searching:", e)
    finally:
        cur.close()
        conn.close()

def export_csv(filename="inventory_export.csv"):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT product_name, quantity, last_updated FROM inventory ORDER BY product_name")
        rows = cur.fetchall()
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["product_name", "quantity", "last_updated"])
            writer.writerows(rows)
        print("Exported to", filename)
    except Exception as e:
        print("Error exporting CSV:", e)
    finally:
        cur.close()
        conn.close()

def import_csv(filename):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("product_name")
                qty = row.get("quantity") or 0
                try:
                    qty = int(qty)
                except:
                    qty = 0
                # Try insert, if duplicate then update quantity
                try:
                    cur.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)", (name, qty))
                except mysql.connector.IntegrityError:
                    cur.execute("UPDATE inventory SET quantity = %s WHERE product_name = %s", (qty, name))
        conn.commit()
        print("Imported from", filename)
    except FileNotFoundError:
        print("File not found:", filename)
    except Exception as e:
        print("Error importing CSV:", e)
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def low_stock(threshold=5):
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT product_name, quantity FROM inventory WHERE quantity <= %s ORDER BY quantity ASC", (threshold,))
        rows = cur.fetchall()
        if not rows:
            print("No low-stock items (threshold =", threshold, ")")
            return
        print("Low stock items (<= {})".format(threshold))
        for r in rows:
            print(f"- {r[0]} : {r[1]}")
    except Exception as e:
        print("Error checking low stock:", e)
    finally:
        cur.close()
        conn.close()

def seed_sample_data():
    samples = [
        ("Pens", 50),
        ("Notebooks", 120),
        ("Stapler", 10),
        ("Marker", 3),
        ("Glue", 0),
    ]
    try:
        conn = get_conn(DB_NAME)
        cur = conn.cursor()
        for name, qty in samples:
            try:
                cur.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s, %s)", (name, qty))
            except mysql.connector.IntegrityError:
                cur.execute("UPDATE inventory SET quantity = %s WHERE product_name = %s", (qty, name))
        conn.commit()
        print("Sample data seeded.")
    except Exception as e:
        print("Error seeding sample data:", e)
    finally:
        cur.close()
        conn.close()

def prompt_int(prompt, allow_empty=False, default=None):
    while True:
        s = input(prompt).strip()
        if s == "" and allow_empty:
            return default
        try:
            return int(s)
        except ValueError:
            print("Please enter an integer.")

def main():
    ensure_db_and_table()
    while True:
        print("\n1. Add item\n2. Delete item\n3. Update (set) quantity\n4. Increase/Decrease quantity (delta)\n5. View inventory\n6. Search items\n7. Export CSV\n8. Import CSV\n9. Low stock items\n10. Seed sample data\n11. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            name = input("Product name: ").strip()
            if not name:
                print("Name required.")
                continue
            qty = prompt_int("Quantity (integer): ")
            add_item(name, qty)
        elif choice == "2":
            name = input("Product name to delete: ").strip()
            if name:
                delete_item(name)
        elif choice == "3":
            name = input("Product name: ").strip()
            if not name:
                print("Name required.")
                continue
            qty = prompt_int("New quantity: ")
            update_quantity(name, qty)
        elif choice == "4":
            name = input("Product name: ").strip()
            delta = prompt_int("Delta (use negative to decrease): ")
            change_quantity_delta(name, delta)
        elif choice == "5":
            l = input("Limit rows? (press enter for all): ").strip()
            limit = int(l) if l.isdigit() else None
            view_inventory(limit)
        elif choice == "6":
            term = input("Search term: ").strip()
            if term:
                search_items(term)
        elif choice == "7":
            fn = input("Export filename (default inventory_export.csv): ").strip() or "inventory_export.csv"
            export_csv(fn)
        elif choice == "8":
            fn = input("Import filename (CSV): ").strip()
            if fn:
                import_csv(fn)
        elif choice == "9":
            th = input("Threshold (default 5): ").strip()
            thv = int(th) if th.isdigit() else 5
            low_stock(thv)
        elif choice == "10":
            seed_sample_data()
        elif choice == "11":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    while True:
        pwd = input("Enter password to unlock: ")
        if pwd == DB_PASS:
            for w in "Logging in, please wait...".split():
                print(w, end=" ", flush=True)
                time.sleep(0.2)
            print()
            main()
            break
        else:
            print("Incorrect password.")
