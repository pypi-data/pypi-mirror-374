from psycopg2 import pool
import os
from isaadvmutility.logger import get_logger

class DBConnection:
    _instance = None
    _connection_pool = None

    def __init__(self, minconn=1, maxconn=10):
        self.logger = get_logger(self.__class__.__name__)
        # Check if a connection string without sensitive info is provided in the environment
        self.connection_string = os.getenv('DB_CONNECTION_STRING')

        # Retrieve user and password
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')

        if not self.connection_string:
            # Fallback to individual environment variables if connection string isn't provided
            self.dbname = os.getenv('DB_NAME', 'advm')
            hosts = os.getenv('DB_HOST', 'localhost') # If 'DB_HOST' is not set, it defaults to 'localhost'
            ports = os.getenv('DB_PORT', '5432')  # Default port is 5432

            # Construct the connection string without user and password
            self.connection_string = f"postgresql://{hosts}:{ports}/{self.dbname}?target_session_attrs=primary"

        if not DBConnection._connection_pool:
            DBConnection._connection_pool = pool.SimpleConnectionPool(minconn, maxconn,
                dsn=self.connection_string,
                user=self.user,
                password=self.password
                # sslmode="require"  # This can be added if needed
            )
            self.logger.info("Connection pool to PostgreSQL has been established.")

    @classmethod
    def getInstance(cls, minconn=1, maxconn=10):
        if cls._instance is None:
            cls._instance = cls(minconn, maxconn)
        return cls._instance

    def getconn(self):
        return DBConnection._connection_pool.getconn()

    def putconn(self, conn):
        DBConnection._connection_pool.putconn(conn)
