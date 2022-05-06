#
# 下載實名制快篩藥局剩餘數量
#
#
# Date:2022/04/28
#
#

import requests
import csv
import numpy as np
import sqlite3

# 連結"快篩資料庫"
connection = sqlite3.connect('screeningMeta.db')

# Creating a cursor object to execute
# SQL queries on a database table
cursor = connection.cursor()

# 檢查是不是已經有指定的資料表，如果有則刪除掉它
drop_table = '''DROP TABLE IF EXISTS meta'''
cursor.execute(drop_table)

# 如果指定資料表不存在則建立 "meta" 資料表
create_table = '''CREATE TABLE IF NOT EXISTS meta(
                no INTEGER PRIMARY KEY AUTOINCREMENT,
                idcode INTEGER NOT NULL,
                name TEXT NOT NULL,
                addr TEXT NOT NULL,
                longitude INTEGER NOT NULL,
                latitude INTEGER NOT NULL,
                tel TEXT NOT NULL,
                type TEXT NOT NULL,
                stock INTEGER NOT NULL,
                lastsync TEXT NOT NULL,
                note TEXT NOT NULL);
                '''

# Creating the table into our
# database
cursor.execute(create_table)

# Define the remote URL
url = "https://data.nhi.gov.tw/Datasets/Download.ashx?rid=A21030000I-D03001-001&l=https://data.nhi.gov.tw/resource/Nhi_Fst/Fstdata.csv"

# Send HTTP GET request via requests
data = requests.get(url)

# Convert to iterator by splitting on \n chars
lines = data.text.splitlines()

# Parse as CSV object
reader = csv.reader(lines)
#data = csv.DictReader(lines)
#column = [row['醫事機構名稱'] for row in data]

#to_db = [(i['快篩試劑截至目前結餘存貨數量'], i['來源資料時間'], i['備註'], i['醫事機構名稱']) for i in data]

#cursor.executemany("UPDATE meta SET stock = ?, lastsync = ?, note = ? WHERE name = ?", to_db)

# SQL query to insert data into the
# meta table
insert_records = "INSERT INTO meta (idcode, name, addr, longitude, latitude, tel, type, stock, lastsync, note) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

# Importing the contents of the file
# into our meta table
cursor.executemany(insert_records, reader)

# Committing the changes
connection.commit()

localName = "土城"
# SQL query to retrieve all data from
select_all = "SELECT name, addr, stock, lastsync, note FROM meta WHERE addr LIKE '%'||?||'%' ORDER BY stock"
rows = cursor.execute(select_all,(localName,)).fetchall()

# closing the database connection
connection.close()

# Output to the console screen
for r in rows:
    print(r)
