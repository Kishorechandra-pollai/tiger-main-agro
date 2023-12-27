import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os


def get_secret(secret_name):
    try:
        with open(f"/mnt/psmdev-secret/{secret_name}", "r") as secret_file:
            return secret_file.read().strip()
    except IOError:
        return os.environ[secret_name]


username = get_secret("Username")  # Replace with the actual secret name in key vault
pwd = get_secret("Password")

driver = "{ODBC Driver 18 for SQL Server}"
host = "cgfpsmadevsql.database.windows.net,1433"
# username = settings.MSSQL_USER
# pwd = settings.MSSQL_PASSWORD
db = "cgfpsmadevsqlDB"
params = urllib.parse.quote_plus("DRIVER=" + driver +
                                 ";SERVER=" + host +
                                 ";DATABASE=" + db +
                                 ";UID=" + username +
                                 ";PWD=" + pwd)

print("---- loading ----")

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
