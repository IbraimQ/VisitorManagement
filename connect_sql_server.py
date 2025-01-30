import pyodbc

DRIVER_NAME = 'SQL Server'
SERVER_NAME = 'LAPTOP-77204R0A\\SQLEXPRESS'
DATABASE_NAME = 'pyVisitor'

connection_string = f"""
DRIVER={{{DRIVER_NAME}}};
SERVER={SERVER_NAME};
DATABASE={DATABASE_NAME};
Trust_Connection=yes;
"""

try:
    conn = pyodbc.connect(connection_string)
    print("Connection successful!")
except Exception as e:
    print("Connection failed!")
    print(str(e))
