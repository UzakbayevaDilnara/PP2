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


# PRACTICE 8 

def search_by_pattern():
    pattern = input("Іздеу паттерні (ат немесе телефон бөлігі): ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s);", (pattern,))
            rows = cur.fetchall()
            if rows:
                for row in rows:
                    print(f"ID: {row[0]} | Аты: {row[1]} | Телефон: {row[2]}")
            else:
                print("Ештеңе табылмады.")
        conn.close()

def call_upsert():
    name = input("Аты: ")
    phone = input("Телефон: ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s);", (name, phone))
            conn.commit()
            print("Сәтті қосылды/жаңартылды!")
        conn.close()

def call_insert_many():
    print("Көп контактіні қосу (мысал ретінде қатты кодталған):")
    names = ['Асқар', 'Мадина', 'Ерлан']
    phones = ['87011234567', 'abc123', '87029876543']
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM insert_many_contacts(%s, %s, '');", (names, phones))
            invalid = cur.fetchone()[0]
            conn.commit()
            print(f"Қате деректер: {invalid}")
        conn.close()

def call_pagination():
    try:
        limit = int(input("Қанша жол шығару (Limit): "))
        offset = int(input("Қанша жолды өткізіп жіберу (Offset): "))
    except ValueError:
        print("Қате: Сан енгізу керек!")
        return
        
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
            rows = cur.fetchall()
            for row in rows:
                print(f"ID: {row[0]} | Аты: {row[1]} | Телефон: {row[2]}")
        conn.close()

def call_delete():
    name = input("Жойылатын аты (бос қалдырсаңыз Enter): ")
    phone = input("Жойылатын телефоны (бос қалдырсаңыз Enter): ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s, %s);", (name if name else None, phone if phone else None))
            conn.commit()
            print("Жойылды!")
        conn.close()


# MAIN MENU)

def main_menu():
    create_table() 
    while True:
        print("\n--- PhoneBook Мәзірі ---")
        print("1. CSV-дан импорттау")
        print("2. Консольден қосу")
        print("3. Жаңарту (ескі)")
        print("4. Іздеу (ескі)")
        print("5. Жою (ескі)")
        print("6. Паттерн бойынша іздеу (SQL Function)")
        print("7. Upsert (SQL Procedure)")
        print("8. Көп контактіні қосу (SQL Procedure)")
        print("9. Беттеу/Pagination (SQL Function)")
        print("10. Аты/телефоны бойынша жою (SQL Procedure)")
        print("0. Шығу")
        
        choice = input("Таңдауыңыз: ")
        
        if choice == '1': import_from_csv('contacts.csv')
        elif choice == '2': insert_from_console()
        elif choice == '3': update_contact()
        elif choice == '4': search_contacts()
        elif choice == '5': delete_contact()
        # --- PRACTICE 8 ---
        elif choice == '6': search_by_pattern()
        elif choice == '7': call_upsert()
        elif choice == '8': call_insert_many()
        elif choice == '9': call_pagination()
        elif choice == '10': call_delete()
        elif choice == '0':
            print("Бағдарлама жабылды.")
            break
        else:
            print("Қате таңдау!")

if __name__ == "__main__":
    main_menu()

