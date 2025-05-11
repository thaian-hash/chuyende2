import pyodbc

print("📦 Danh sách các ODBC driver hiện có:")
for driver in pyodbc.drivers():
    print(f" - {driver}")