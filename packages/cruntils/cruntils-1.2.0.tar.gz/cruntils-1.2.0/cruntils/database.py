
import psycopg

class Database:
    """
    Class wrapping some database convenience functions.

    Example connection info:

    host=localhost port=5432 dbname=postgres connect_timeout=10 user=postgres password=password
    """
    def __init__(self, conn_info):
        """Constructor."""

        # Connect to database.
        self.conn_info = conn_info
        self.conn = psycopg.connect(self.conn_info)

    def __del__(self):
        """Destructor."""
        self.disconnect()

    def disconnect(self):
        if self.conn != None:
            self.conn.close()

    def execute(self, sql, values=(), commit=True):
        """Execute command."""

        # Make sure we're connected first.
        if self.conn == None:
            return

        # Execute the command.
        with self.conn.cursor() as curs:
            curs.execute(sql, values)

        # Commit.
        if commit:
            self.conn.commit()

    def fetch_one(self, sql, values=()):
        """"""
        with self.conn.cursor() as curs:
            curs.execute(sql, values)
            return curs.fetchone()

    def fetch_all(self, sql, values=()):
        """"""
        with self.conn.cursor() as curs:
            curs.execute(sql, values)
            return curs.fetchall()