
import csv
from connect import get_connection
def create_table():
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL UNIQUE
                );
            """)
            conn.commit()
        conn.close()

def import_from_csv(filename):
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cur.execute(
                            "INSERT INTO phonebook (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING;",
                            (row['name'], row['phone'])
                        )
                    except Exception as e:
                        print(f"Қате ( {row['name']} ): {e}")
            conn.commit()
        conn.close()
        print("CSV-дан импорттау аяқталды!")

def insert_from_console():
    name = input("Аты-жөні: ")
    phone = input("Телефон нөмірі: ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s);", (name, phone))
                conn.commit()
                print("Сәтті қосылды!")
            except Exception as e:
                print(f"Қате: {e}")
        conn.close()

def update_contact():
    old_phone = input("Жаңартылатын контактінің телефон нөмірі: ")
    new_name = input("Жаңа аты (өзгертпесеңіз бос қалдырыңыз): ")
    new_phone = input("Жаңа телефон (өзгертпесеңіз бос қалдырыңыз): ")
    
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            if new_name:
                cur.execute("UPDATE phonebook SET name = %s WHERE phone = %s;", (new_name, old_phone))
            if new_phone:
                cur.execute("UPDATE phonebook SET phone = %s WHERE phone = %s;", (new_phone, old_phone))
            conn.commit()
            print("Жаңартылды!")
        conn.close()

def search_contacts():
    query = input("Іздеу сөзі (ат немесе телефон басы): ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, phone FROM phonebook WHERE name ILIKE %s OR phone LIKE %s;",
                (f'%{query}%', f'{query}%')
            )
            rows = cur.fetchall()
            if rows:
                print("\nТабылған контактілер:")
                for row in rows:
                    print(f"ID: {row[0]} | Аты: {row[1]} | Телефон: {row[2]}")
            else:
                print("Ештеңе табылмады.")
        conn.close()

def delete_contact():
    phone = input("Жойылатын контактінің телефон нөмірі: ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM phonebook WHERE phone = %s;", (phone,))
            conn.commit()
            print("Жойылды!")
        conn.close()

def main_menu():
    create_table() 
    while True:
        print("\n--- PhoneBook Мәзірі ---")
        print("1. CSV-дан импорттау")
        print("2. Консольден қосу")
        print("3. Жаңарту")
        print("4. Іздеу")
        print("5. Жою")
        print("0. Шығу")
        choice = input("Таңдауыңыз: ")
        
        if choice == '1':
            import_from_csv('contacts.csv')
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            search_contacts()
        elif choice == '5':
            delete_contact()
        elif choice == '0':
            print("Бағдарлама жабылды.")
            break
        else:
            print("Қате таңдау!")

if __name__ == "__main__":
    main_menu()
