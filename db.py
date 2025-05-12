import pyodbc
import datetime
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection():
    try:
        conn = pyodbc.connect(
            r'DRIVER={SQL Server};'
            r'SERVER=.;'
            r'DATABASE=KeyFindingApp;'
            r'UID=sa;'
            r'PWD=12345;'
        )
        return conn
    except Exception as e:
        print(f"❌ Lỗi kết nối SQL Server: {e}")
        logging.error(f"Lỗi kết nối SQL Server: {e}")
        return None

def create_tables_if_not_exists():
    conn = get_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='RelationalSchemaLogs' AND xtype='U')
            CREATE TABLE RelationalSchemaLogs (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                U NVARCHAR(255) NOT NULL,
                f_list NVARCHAR(MAX) NOT NULL,
                x_input NVARCHAR(255),
                x_plus NVARCHAR(255),
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='KeyFindingLogs' AND xtype='U')
            CREATE TABLE KeyFindingLogs (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                U NVARCHAR(255) NOT NULL,
                f_list NVARCHAR(MAX) NOT NULL,
                k1 NVARCHAR(255),
                k2 NVARCHAR(255),
                k3 NVARCHAR(255),
                ks1 NVARCHAR(255),  -- Added ks1 column
                ks2 NVARCHAR(255),
                ks3 NVARCHAR(255),
                ks4 NVARCHAR(255),  
                ks5 NVARCHAR(255),
                ks6 NVARCHAR(255),
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='MinimalCoverLogs' AND xtype='U')
            CREATE TABLE MinimalCoverLogs (
                ID INT IDENTITY(1,1) PRIMARY KEY,
                U NVARCHAR(255) NOT NULL,
                f_list NVARCHAR(MAX) NOT NULL,
                f1 NVARCHAR(MAX),
                f2 NVARCHAR(MAX),
                f3 NVARCHAR(MAX),
                created_at DATETIME DEFAULT GETDATE()
            )
        """)
        conn.commit()
        return True
    except Exception as e:
        print(f"Lỗi tạo bảng: {e}")
        logging.error(f"Lỗi tạo bảng: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def insert_log(data):
    if not create_tables_if_not_exists():
        raise Exception("Không thể tạo bảng")

    conn = get_connection()
    if not conn:
        raise Exception("Không thể kết nối SQL Server")

    cursor = conn.cursor()
    try:
        # Lấy thời gian hiện tại để đồng bộ giữa các bảng
        current_time = datetime.datetime.now()

        # Thêm vào bảng RelationalSchemaLogs
        cursor.execute("""
            INSERT INTO RelationalSchemaLogs (U, f_list, x_input, x_plus, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (data['u_set'], data['f_list'], data['x_input'], data['x_plus'], current_time))

        # Thêm vào bảng KeyFindingLogs
        cursor.execute("""
            INSERT INTO KeyFindingLogs (U, f_list, k1, k2, k3, ks1, ks2, ks3, ks4, ks5, ks6, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data['u_set'], data['f_list'], data['k1'], data['k2'], data['k3'], data['ks1'], data['ks2'], data['ks3'],data['ks4'], data['ks5'], data['ks6'], current_time))

        # Thêm vào bảng MinimalCoverLogs
        cursor.execute("""
            INSERT INTO MinimalCoverLogs (U, f_list, f1, f2, f3, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['u_set'], data['f_list'], data['f1'], data['f2'], data['f3'], current_time))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi lưu dữ liệu: {e}")
        logging.error(f"Lỗi khi lưu dữ liệu: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def get_all_logs():
    conn = get_connection()
    if not conn:
        return {'schema_logs': [], 'key_logs': [], 'minimal_logs': []}

    cursor = conn.cursor()
    try:
        # Lấy dữ liệu từ cả 3 bảng, sắp xếp theo created_at
        cursor.execute("SELECT * FROM RelationalSchemaLogs ORDER BY created_at DESC")
        schema_logs = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT ID, U, f_list, k1, k2, k3, ks1, ks2, ks3, ks4, ks5, ks6, created_at FROM KeyFindingLogs ORDER BY created_at DESC")
        key_logs = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM MinimalCoverLogs ORDER BY created_at DESC")
        minimal_logs = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

        return {
            'schema_logs': schema_logs,
            'key_logs': key_logs,
            'minimal_logs': minimal_logs
        }
    except Exception as e:
        print(f"Lỗi truy vấn dữ liệu: {e}")
        logging.error(f"Lỗi truy vấn dữ liệu: {e}")
        return {'schema_logs': [], 'key_logs': [], 'minimal_logs': []}
    finally:
        cursor.close()
        conn.close()

def delete_log(created_at):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        # Xóa các bản ghi dựa trên created_at
        cursor.execute("DELETE FROM KeyFindingLogs WHERE created_at = ?", (created_at,))
        cursor.execute("DELETE FROM MinimalCoverLogs WHERE created_at = ?", (created_at,))
        cursor.execute("DELETE FROM RelationalSchemaLogs WHERE created_at = ?", (created_at,))

        # Sau khi xóa, kiểm tra số bản ghi còn lại trong RelationalSchemaLogs
        cursor.execute("SELECT COUNT(*) FROM RelationalSchemaLogs")
        remaining_count = cursor.fetchone()[0]

        if remaining_count == 0:
            # Nếu không còn bản ghi nào, đặt lại IDENTITY về 1
            cursor.execute("DBCC CHECKIDENT ('RelationalSchemaLogs', RESEED, 0)")
        else:
            # Lấy ID lớn nhất hiện tại và đặt lại IDENTITY để giá trị tiếp theo là ID lớn nhất + 1
            cursor.execute("SELECT MAX(ID) FROM RelationalSchemaLogs")
            max_id = cursor.fetchone()[0]
            if max_id is not None:
                cursor.execute("DBCC CHECKIDENT ('RelationalSchemaLogs', RESEED, ?)", (max_id,))

        # Tương tự cho KeyFindingLogs
        cursor.execute("SELECT COUNT(*) FROM KeyFindingLogs")
        remaining_count = cursor.fetchone()[0]
        if remaining_count == 0:
            cursor.execute("DBCC CHECKIDENT ('KeyFindingLogs', RESEED, 0)")
        else:
            cursor.execute("SELECT MAX(ID) FROM KeyFindingLogs")
            max_id = cursor.fetchone()[0]
            if max_id is not None:
                cursor.execute("DBCC CHECKIDENT ('KeyFindingLogs', RESEED, ?)", (max_id,))

        # Tương tự cho MinimalCoverLogs
        cursor.execute("SELECT COUNT(*) FROM MinimalCoverLogs")
        remaining_count = cursor.fetchone()[0]
        if remaining_count == 0:
            cursor.execute("DBCC CHECKIDENT ('MinimalCoverLogs', RESEED, 0)")
        else:
            cursor.execute("SELECT MAX(ID) FROM MinimalCoverLogs")
            max_id = cursor.fetchone()[0]
            if max_id is not None:
                cursor.execute("DBCC CHECKIDENT ('MinimalCoverLogs', RESEED, ?)", (max_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Lỗi xóa bản ghi: {e}")
        logging.error(f"Lỗi xóa bản ghi: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_combined_logs():
    conn = get_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                r.ID AS schema_log_id,
                r.created_at,
                r.U,
                r.f_list,
                r.x_input,
                r.x_plus,
                k.k1, k.k2, k.k3, k.ks1,k.ks2, k.ks3, k.ks4, k.ks5, k.ks6,
                m.f1, m.f2, m.f3
            FROM RelationalSchemaLogs r
            LEFT JOIN KeyFindingLogs k ON r.created_at = k.created_at
            LEFT JOIN MinimalCoverLogs m ON r.created_at = m.created_at
            ORDER BY r.created_at DESC
        """)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Lỗi get_combined_logs: {e}")
        logging.error(f"Lỗi get_combined_logs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
