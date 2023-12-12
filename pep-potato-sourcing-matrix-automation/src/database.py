import urllib
import sqlalchemy
from sqlalchemy import create_engine
import pyodbc

from sqlalchemy.orm import sessionmaker
from config import settings, Settings
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL
import os


def get_secret(secret_name):
    try:
        with open(f"/mnt/psmdev-secret/{secret_name}", "r") as secret_file:
            return secret_file.read().strip()
    except IOError:
        return os.environ[secret_name]

username = get_secret("Username") # Replace with the actual secret name in key vault
pwd = get_secret("Password") 

driver = settings.MSSQl_DRIVER
host = settings.MSSQL_HOSTNAME
# username = settings.MSSQL_USER
# pwd = settings.MSSQL_PASSWORD
db = settings.MSSQL_DB
print("driver-name=" + driver)
params = urllib.parse.quote_plus("DRIVER=" + driver +
                                 ";SERVER=" + host +
                                 ";DATABASE=" + db +
                                 ";UID=" + username +
                                 ";PWD=" + pwd)



# params = "DRIVER=" + driver + ";Server=tcp:" + host + ";Database=" + db + ";Uid=" + username + ";Pwd=" + pwd + ";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30" + ";Authentication=ActiveDirectoryPassword"

print(" ------------- params -------------")
print(params)

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

print(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

print(SessionLocal)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
