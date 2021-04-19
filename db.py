import sqlite3
from datetime import datetime, timedelta


now = datetime.now()
today_raw = now.replace(day=1)
today = now.strftime("%Y-%m-%d")
month = today_raw.strftime("%Y-%m-%d")


conn = sqlite3.connect("db.db")
cur = conn.cursor()

def get_user_id(name):
    cur.execute("SELECT id FROM users WHERE name = (?)", (name,))
    result = cur.fetchone()[0]
    return result

def get_category_id(name):
    cur.execute("SELECT id FROM category WHERE name = (?)", (name,))
    result = cur.fetchone()[0]
    return result

def user_check(user, id):
    cur.execute("SELECT telegram_id FROM users WHERE name = (?)", (user,))
    result = cur.fetchone()
    if result:
        return f"Hello {user}!"
    else:
        cur.execute("INSERT INTO users (telegram_id, name) VALUES (?, ?)", (id, user,))
        conn.commit()
        return f"Welcome new user {user}, lets start!"

def select_categories():
    cur.execute("SELECT * FROM category")
    result = cur.fetchall()
    lst = list()
    for item in result:
        lst.append(item[1])
    #lst.sort()
    return lst

def add_spend(user,category,amount):
    username_id = get_user_id(user)
    category_id = get_category_id(category)
    try:
        amount = float(amount)
        cur.execute("""INSERT INTO spend (user_id, category_id, amount, date)
                     VALUES (?, ?, ?, datetime('now','localtime'))""",
                     (username_id, category_id, amount,))
        conn.commit()
        return "Done!"
    except:
        return "Something wrong!"

def get_today_statistics(user,category):
    username_id = get_user_id(user)
    category_id = get_category_id(category)
    cur.execute(f"""SELECT SUM(amount) FROM spend WHERE user_id = (?) AND category_id = (?)
                        AND date(date) = date('{today}')""", (username_id, category_id))
    result = cur.fetchone()[0]
    return result


def get_month_statistics(user,category):
    username_id = get_user_id(user)
    category_id = get_category_id(category)
    cur.execute(f"""SELECT SUM(amount) FROM spend WHERE user_id = (?) AND category_id = (?)
                        AND date(date) >= date('{month}')""", (username_id, category_id))
    result = cur.fetchone()[0]
    return result
