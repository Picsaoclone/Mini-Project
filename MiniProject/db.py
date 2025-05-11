import cx_Oracle

def get_connection():
    dsn = cx_Oracle.makedsn("localhost", 1521, sid="ORCL21")
    conn = cx_Oracle.connect(
        user="C##MiniProject",
        password="mini",
        dsn=dsn
    )
    return conn
