import sqlite3

conn = sqlite3.connect("db.db")
cur = conn.cursor()

def user_check(user, id):
    cur.execute("SELECT telegram_id FROM Users WHERE name = (?)", (user,))
    result = cur.fetchone()
    if result:
        return f"Hello {user}!"
    else:
        cur.execute("INSERT INTO Users (telegram_id, name) VALUES (?, ?)", (id, user,))
        conn.commit()
        return f"Welcome new user {user}, lets start!"

def select_categories():
    cur.execute("PRAGMA table_info(spends)")
    result = cur.fetchall()[2:]
    lst = list()
    for item in result:
        lst.append(item[1])
    lst.sort()
    return lst

def add_spend(user,category,amount):
    categories = select_categories()
    if category in categories:
        cur.execute(f"""INSERT INTO spends (user_id, date, {category})
                        VALUES (?, datetime('now','localtime'), ?)""",
                    (user, amount,))
        conn.commit()
        return "Done!"
    else:
        return "Wrong category!"

def get_today_statistics(user, category):
        cur.execute(f"""SELECT SUM(spends.{category}) FROM spends WHERE user_id = (?)
                        AND date(date) = date('now')""", (user,))
        result = cur.fetchall()[0][0]
        return result
