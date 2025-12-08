### Declare the database connection
#
# Database schema:
# 
# CREATE TABLE cdr_files (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    filename TEXT NOT NULL,
#    hash TEXT NOT NULL,
#    changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#    status TEXT CHECK(status IN ('Arrived', 'Sent', 'Confirmed', 'Deleted')) DEFAULT 'Arrived'
#)
#
DATABASE_PATH = ""