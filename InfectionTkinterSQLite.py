#
# Python Tkinter GUI Exercise
# 
# Date:2022/04/29
# 
# Features:
#   具有讀取SQLite資料庫與資料清單畫面分頁換頁控制功能
#
# Install Packets List:
# 1. pip install tkinter --user --no-warn-script-location
# 2. pip requests tkinter --user --no-warn-script-location
#
import tkinter as tk
import tkinter.ttk as ttk
import requests
import csv
from tkinter import *
import sqlite3 

# Define the remote URL
gsUrl = "https://data.nhi.gov.tw/Datasets/Download.ashx?rid=A21030000I-D03001-001&l=https://data.nhi.gov.tw/resource/Nhi_Fst/Fstdata.csv"

dbName ='screeningMeta.db'
gfSearch = 0
gsSearchString =''

#   從帶入的網址取得到政府公開資料
#
def get_web_open_data(url):
    # Send HTTP GET request via requests
    data = requests.get(url)

    # Convert to iterator by splitting on \n chars
    lines = data.text.splitlines()

    # Parse as CSV object
    reader = csv.reader(lines)

    return reader
# ---- end of get_web_open_data() ------------------------

#   將資料寫入指定的資料庫/資料表中
#   (包含刪除原始資料庫與新建資料表操作)
#
def write_into_db(conn, datas):
    # Creating a cursor object to execute
    # SQL queries on a database table
    cursor = conn.cursor()
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

    # SQL query to insert data into the
    # meta table
    insert_records = "INSERT INTO meta (idcode, name, addr, longitude, latitude, tel, type, stock, lastsync, note) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    # Importing the contents of the file
    # into our meta table
    cursor.executemany(insert_records, datas)

    # Committing the changes
    conn.commit()
# ----- end of write_into_db() -------------------------------

#   取得資料表內所有已儲存的資料筆數總數
#
def get_total_rows(conn, tableName):
    r_set=conn.execute("SELECT count(*) as no from meta")
    data_row=r_set.fetchone()
    # Total number of rows in table
    no_rec=data_row[0]
    return no_rec
# ----- end of get_total_rows() -------------------------------

#   
#
def populate_all(conn, window, offset):
    # 宣告顯示分頁一次顯示資料筆數
    limit = 8; 
    cowswidthtbl = [15, 30, 6, 18, 35];
    frame_datatable = Frame(window)
    frame_datatable.grid(row=2, column=0)

    totalRows = get_total_rows(conn, 'meta')
    q="SELECT name, addr, stock, lastsync, note from meta LIMIT "+ str(offset) +","+str(limit)
    r_set=conn.execute(q);
    # row value inside the loop 
    i=0 
    for meta in r_set: 
        for j in range(len(meta)):
            # 轉換表格顯示欄位長度
            #tw=len(meta[j])+5
            e = Entry(frame_datatable, width=cowswidthtbl[j], fg='blue') 
            e.grid(row=i, column=j) 
            e.insert(END, meta[j])
        i=i+1
    # required to blank the balance rows if they are less    
    while (i<limit):  
        for j in range(len(meta)):
            #e = Entry(window, width=tw, fg='blue') 
            e = Entry(frame_datatable, width=cowswidthtbl[j], fg='blue') 
            e.grid(row=i, column=j) 
            e.insert(END, "")
        i=i+1
 # 顯示上、下頁面功能按鍵以及頁面切換反映
    back = offset - limit # This value is used by Previous button
    next = offset + limit # This value is used by Next button       
    b1 = tk.Button(frame_datatable, text='Next >', command=lambda: populate_all(conn, window, next))
    b1.grid(row=16,column=1)
    b2 = tk.Button(frame_datatable, text='< Prev', command=lambda: populate_all(conn, window, back))
    b2.grid(row=16,column=0)
    if(totalRows <= next): 
        # disable next button
        b1["state"]="disabled" 
    else:
        # enable next button
        b1["state"]="active"  
            
    if(back >= 0):
        # enable Prev button
        b2["state"]="active"  
    else:
        # disable Prev button    
        b2["state"]="disabled"

# ----- end of populate_all() -------------------------------

def search_btn_event(combobox):
    print(combobox.current(), combobox.get())
    gsSearchString = combobox.get()
    gfSearch = 1

def clear_btn_event(combobox):
    #print(combobox.current(), combobox.get())
    combobox.current(0)
    gsSearchString = ''
    gfSearch = 0

def main():
    offset = 0
    conlimit = 8

    #建立資料庫連線
    dbconn = sqlite3.connect(dbName) 

    window = tk.Tk()
    # 視窗標題
    window.title('實名快篩剩餘數量查詢')
    #視窗尺寸 
    window.geometry('900x400')

    frame_citysearch = Frame(window)
    frame_citysearch.grid(row=1, column=0)

    comboboxList = ['三重','台北','雲林','台中','蘆洲','新莊']
    citycombobox = ttk.Combobox(frame_citysearch, state='readonly')
    citycombobox['values'] = comboboxList
    citycombobox.grid(row=1, column=0)
    citycombobox.current(0)
    search_btn = tk.Button(frame_citysearch, text='Search', command=search_btn_event(citycombobox))
    search_btn.grid(row=1, column=1, pady=20)
    clear_btn = tk.Button(frame_citysearch, text='Clear', command=clear_btn_event(citycombobox))
    clear_btn.grid(row=1, column=2, pady=20)

    # 取得網址公開資料
    ret = get_web_open_data(gsUrl)

    # 將獲取到的資料寫入資料庫中
    write_into_db(dbconn, ret)

    while(1):
        if gfSearch == 0:
            populate_all(dbconn, window, offset)
        
        window.mainloop()
        
    # Release Resource
    dbconn.close()

if __name__ == '__main__':
    main()