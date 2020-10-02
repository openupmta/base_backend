import sqlite3

connection = sqlite3.connect('quitt.db')

cursor = connection.cursor()

create_table_user = """CREATE TABLE user (
                            id TEXT PRIMARY KEY,
                            username TEXT NOT NULL,
                            password_hash TEXT NOT NULL,
                            force_change_password NUMERIC NOT NULL,
                            create_date NUMERIC NOT NULL,
                            modified_date NUMERIC NOT NULL,
                            is_active NUMERIC NOT NULL,
                            firstname TEXT NOT NULL,
                            lastname TEXT NOT NULL,
                            company TEXT,
                            address TEXT,
                            mobile TEXT,
                            modified_date_password NUMERIC NOT NULL
                            )"""
cursor.execute(create_table_user)
insert_query_user = "INSERT INTO user VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
# user = ("1", "bootai", "bootai", 1, 1111, 1111, 1, "bootai", "bootai", "bootai", "bootai", "bootai", 1111)
# cursor.execute(insert_query_user, user)

create_table_token = """CREATE TABLE token (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            jti TEXT NOT NULL,
                            token_type TEXT NOT NULL,
                            user_identity TEXT NOT NULL,
                            revoked NUMERIC NOT NULL,
                            expires NUMERIC NOT NULL
                            )"""
cursor.execute(create_table_token)
insert_query_token = "INSERT INTO token VALUES (?, ?, ?, ?, ?, ?)"
# token = (1, "bootai", "bootai", "bootai", 1, 1111)
# cursor.execute(insert_query_token, token)

create_table_history = """CREATE TABLE predict_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL,
                            label TEXT,
                            score NUMERIC,
                            description TEXT
                            )"""
cursor.execute(create_table_history)

connection.commit()
connection.close()