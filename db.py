import sqlite3
from datetime import datetime, timedelta


now = datetime.now()
lastmonth = now - timedelta(weeks=6)
endoflastmonth = lastmonth.replace(day=30)
month2 = endoflastmonth.strftime("%Y-%m-%d")

this_month_raw = now.replace(day=1)
this_month = this_month_raw.strftime("%Y-%m-%d")


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
        cur.execute("""INSERT INTO spend (user_id, category_id, amount, date)
                     VALUES (?, ?, ?, datetime('now','localtime'))""",
                     (username_id, category_id, amount,))
        conn.commit()
        return "Done!"
    except:
        return "Wrong category!"

def get_today_statistics(user,category):
    username_id = get_user_id(user)
    category_id = get_category_id(category)
    cur.execute(f"""SELECT SUM(amount) FROM spend WHERE user_id = (?) AND category_id = (?)
                        AND date(date) = date('now')""", (username_id, category_id))
    result = cur.fetchone()[0]
    return result


def get_month_statistics(user,category):
    cur.execute(f"""SELECT SUM(spends.{category}) FROM spends WHERE user_id = (?)
                    AND date(date) >= date({this_month})""", (user,))
    result = cur.fetchall()[0][0]
    return result
