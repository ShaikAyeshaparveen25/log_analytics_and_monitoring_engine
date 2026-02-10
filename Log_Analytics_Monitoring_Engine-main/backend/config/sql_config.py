import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="W7301@jqir#",
            database="log_analytics",   # ⚠️ use this DB
            port=3306
        )

        if connection.is_connected():
            print("Connection successful!")
            return connection
        else:
            print("Unable to connect!")
            return None

    except Error as e:
        print("MySQL Error:", e)
        return None
