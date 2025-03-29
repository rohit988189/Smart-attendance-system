import sqlite3

def delete_all_entries():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()
    print("All entries deleted!")

def delete_by_name(name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    print(f"Entries for {name} deleted!")

def delete_by_date(date):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE date = ?", (date,))
    conn.commit()
    conn.close()
    print(f"Entries for {date} deleted!")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Delete all entries")
    print("2. Delete entries by name")
    print("3. Delete entries by date")
    
    choice = input("Enter your choice (1/2/3): ")
    
    if choice == "1":
        delete_all_entries()
    elif choice == "2":
        name = input("Enter name to delete: ")
        delete_by_name(name)
    elif choice == "3":
        date = input("Enter date (YYYY-MM-DD): ")
        delete_by_date(date)
    else:
        print("Invalid choice!")