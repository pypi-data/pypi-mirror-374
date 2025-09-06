from hdbcli import dbapi
from common import (
    DB_Systems
)

DbPoolManager = {}

class DbConnector:
    def __init__(self,  address: str, 
                        port: int, 
                        user: str, 
                        password: str,
                        validate_cert: bool=False):
        try:
            self.conn = dbapi.connect(
                address=address,
                port=port,
                user=user,
                password=password,
                sslValidateCertificate=validate_cert
            )
            self.connected = True
        except:
            self.connected = False

    def execute(self, sql) -> list:
        cursor = self.conn.cursor()
        sql = sql.strip()
        sql = sql[:-1] if sql[-1] == ';' else sql

        result: list = [
            tuple(["Result"]),
            tuple(["No Record"])
        ]
        try:
            cursor.execute(f"""
                SELECT TOP 100 * FROM ({sql})
            """)
            data = cursor.fetchall()
            columns = []
            for idx, _ in enumerate(cursor.description):
                columns.append(_[0])

            result = [
                tuple(columns)
            ]
            for _ in data:
                result.append(tuple(_))
        except Exception as e:
            result = [
                tuple(["Error"]),
                tuple([e.__str__()])
            ]
        cursor.close()
        return result

    def close(self) -> None:
        if self.connected:
            self.conn.close()

class DbManager:
    def add_connection(name: str) -> None:
        if name in DbPoolManager:
            DbManager.remove_connection(name)
        
        DbPoolManager[name] = DbConnector(
            DB_Systems.file_content[name]['host'],
            int(DB_Systems.file_content[name]['port']) if DB_Systems.file_content[name]['port'] and DB_Systems.file_content[name]['port'].isdigit() else 0,
            DB_Systems.file_content[name]['user'],
            DB_Systems.file_content[name]['password'],
        )

    def remove_connection(name: str) -> None:
        if name in DbPoolManager:
            conn = DbPoolManager[name]
            conn.close()
            del DbPoolManager[name]
