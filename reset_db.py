import sqlite3
import os

DB_PATH = 'db.sqlite3'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("База данных удалена")

# Создаём новую
conn = sqlite3.connect(DB_PATH)
conn.close()
print("Новая база данных создана")
