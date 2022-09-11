import time
import sqlite3
import os

print("Total Reset process [ WEEK ]")

path = "DB/"
file_list = os.listdir(path)
db_list = [file for file in file_list if file.endswith(".db")]
print(db_list)

while True:
    time.sleep(604800)
    path = "DB/"
    file_list = os.listdir(path)
    db_list = [file for file in file_list if file.endswith(".db")]
    print(db_list)
    for db in range(len(db_list)):
        con = sqlite3.connect(f"DB/{db_list[db]}")
        cur = con.cursor()
        try:
            cur.execute("UPDATE total SET tw = ?, gw = ?, bw = ?;",(0, 0, 0))
            con.commit()
            con.close()
            print(f"{db} : Total Week Reset Completed")
        except:
            pass