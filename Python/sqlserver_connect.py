
import pyodbc

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=EcommerceDB;"
    "Trusted_Connection=yes;"
)

try:
    db = pyodbc.connect(connection_string)

    print("SQL Server connected successfully!")

    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM sys.tables")

    result = cursor.fetchone()

    print("Total tables:", result[0])

    cursor.close()
    db.close()

except pyodbc.Error as error:
    print("Connection error:", error)


