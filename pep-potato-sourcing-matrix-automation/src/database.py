import urllib

import sqlalchemy
from sqlalchemy import create_engine
import pyodbc

from sqlalchemy.orm import sessionmaker
from config import settings, Settings
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL

driver = settings.MSSQl_DRIVER
host = settings.MSSQL_HOSTNAME
username = settings.MSSQL_USER
pwd = settings.MSSQL_PASSWORD
db1 = settings.MSSQL_DB
print("driver-name=" + driver)
params = urllib.parse.quote_plus("DRIVER=" + driver + ";"
                                                      "SERVER=" + host + ";"
                                                                         "DATABASE=" + db1 + ";"
                                                                                             "UID=" + username + ";"
                                                                                                                 "PWD=" + pwd + "")

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_connection():
    connection = engine.raw_connection()
    return connection

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
