import csv
import json
import os
from datetime import datetime

from connect import get_connection

PAGE_SIZE = 5

def _exec(sql, params=None, fetch=False, commit=True):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            result = cur.fetchall() if fetch else None
            if commit:
                conn.commit()
            return result
    finally:
        conn.close()

def _parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None

def list_contacts():
    group = input("Group filter (Family/Work/Friend/Other, blank=all): ").strip() or None
    email = input("Email contains (blank=any): ").strip() or None
    sort = input("Sort by (name/birthday/created_at) [name]: ").strip() or "name"
    if sort not in ("name", "birthday", "created_at"):
        sort = "name"

    offset = 0
    while True:
        rows = _exec(
            "SELECT * FROM get_contacts_page(%s,%s,%s,%s,%s);",
            (group, email, sort, PAGE_SIZE, offset),
            fetch=True,
        )
        os.system("clear" if os.name != "nt" else "cls")
        print(f"--- Page (offset={offset}) | group={group} | email~{email} | sort={sort} ---")
        if not rows:
            print("(no more results)")
        for r in rows:
            cid, name, mail, bday, grp, created, phones = r
            print(f"[{cid}] {name} | {mail or '-'} | bday={bday or '-'} | "
                  f"group={grp or '-'} | phones={phones or '-'} | added={created:%Y-%m-%d}")
        cmd = input("\n[n]ext / [p]rev / [q]uit: ").strip().lower()
        if cmd == "n":
            offset += PAGE_SIZE
        elif cmd == "p":
            offset = max(0, offset - PAGE_SIZE)
        elif cmd == "q":
            break

def advanced_search():
    q = input("Search query (name/phone/email): ").strip()
    rows = _exec("SELECT * FROM search_contacts(%s);", (q,), fetch=True)
    print(f"\n{len(rows)} result(s):")
    for cid, name, mail, bday, grp, phones in rows:
        print(f"[{cid}] {name} | {mail or '-'} | bday={bday or '-'} | "
              f"group={grp or '-'} | phones={phones or '-'}")

def import_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"].strip()
            email = row.get("email") or None
            bday = _parse_date(row.get("birthday"))
            grp = row.get("group") or None
            phone = row.get("phone") or None
            ptype = row.get("type") or "mobile"

            
            gid = None
            if grp:
                r = _exec("SELECT id FROM groups WHERE name=%s;", (grp,), fetch=True)
                if r:
                    gid = r[0][0]
                else:
                    r = _exec(
                        "INSERT INTO groups(name) VALUES(%s) RETURNING id;",
                        (grp,), fetch=True,
                    )
                    gid = r[0][0]

           
            r = _exec("SELECT id FROM contacts WHERE name=%s;", (name,), fetch=True)
            if r:
                cid = r[0][0]
                _exec(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s;",
                    (email, bday, gid, cid),
                )
            else:
                r = _exec(
                    "INSERT INTO contacts(name,email,birthday,group_id) "
                    "VALUES(%s,%s,%s,%s) RETURNING id;",
                    (name, email, bday, gid), fetch=True,
                )
                cid = r[0][0]

            if phone:
                _exec(
                    "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s);",
                    (cid, phone, ptype),
                )
    print(f"Imported from {path}")

def export_json(path):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name,
                       COALESCE(json_agg(json_build_object(
                           'phone', p.phone, 'type', p.type))
                           FILTER (WHERE p.id IS NOT NULL), '[]')
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                LEFT JOIN phones p ON p.contact_id = c.id
                GROUP BY c.id, c.name, c.email, c.birthday, g.name
                ORDER BY c.id;
            """)
            rows = cur.fetchall()
        data = [
            {
                "name": r[1],
                "email": r[2],
                "birthday": r[3].isoformat() if r[3] else None,
                "group": r[4],
                "phones": r[5],
            }
            for r in rows
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(data)} contact(s) to {path}")
    finally:
        conn.close()

def import_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        name = item["name"]
        email = item.get("email")
        bday = _parse_date(item.get("birthday"))
        grp = item.get("group")
        phones = item.get("phones", [])

        
        gid = None
        if grp:
            r = _exec("SELECT id FROM groups WHERE name=%s;", (grp,), fetch=True)
            if r:
                gid = r[0][0]
            else:
                r = _exec(
                    "INSERT INTO groups(name) VALUES(%s) RETURNING id;",
                    (grp,), fetch=True,
                )
                gid = r[0][0]

        existing = _exec("SELECT id FROM contacts WHERE name=%s;", (name,), fetch=True)
        if existing:
            ans = input(f"Contact '{name}' exists. [s]kip / [o]verwrite? ").strip().lower()
            if ans != "o":
                continue
            cid = existing[0][0]
            _exec(
                "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s;",
                (email, bday, gid, cid),
            )
            _exec("DELETE FROM phones WHERE contact_id=%s;", (cid,))
        else:
            r = _exec(
                "INSERT INTO contacts(name,email,birthday,group_id) "
                "VALUES(%s,%s,%s,%s) RETURNING id;",
                (name, email, bday, gid), fetch=True,
            )
            cid = r[0][0]

        for ph in phones:
            _exec(
                "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s);",
                (cid, ph["phone"], ph.get("type", "mobile")),
            )
    print(f"Imported {len(data)} contact(s) from {path}")

def call_add_phone():
    name = input("Contact name: ").strip()
    phone = input("Phone: ").strip()
    ptype = input("Type (home/work/mobile): ").strip()
    try:
        _exec("CALL add_phone(%s,%s,%s);", (name, phone, ptype))
        print("Phone added.")
    except Exception as e:
        print("Error:", e)

def call_move_to_group():
    name = input("Contact name: ").strip()
    grp = input("Group name: ").strip()
    try:
        _exec("CALL move_to_group(%s,%s);", (name, grp))
        print("Group updated.")
    except Exception as e:
        print("Error:", e)

def main():
    while True:
        print("""
=== PhoneBook (Extended) ===
1. List / browse contacts (paginated)
2. Advanced search (name/phone/email)
3. Add phone to contact        (procedure)
4. Move contact to group       (procedure)
5. Import CSV (extended)
6. Export JSON
7. Import JSON
0. Exit
""")
        choice = input("> ").strip()
        try:
            if choice == "1":
                list_contacts()
            elif choice == "2":
                advanced_search()
            elif choice == "3":
                call_add_phone()
            elif choice == "4":
                call_move_to_group()
            elif choice == "5":
                import_csv(input("CSV path: ").strip())
            elif choice == "6":
                export_json(input("JSON path [contacts.json]: ").strip() or "contacts.json")
            elif choice == "7":
                import_json(input("JSON path [contacts.json]: ").strip() or "contacts.json")
            elif choice == "0":
                break
            else:
                print("Unknown option")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
