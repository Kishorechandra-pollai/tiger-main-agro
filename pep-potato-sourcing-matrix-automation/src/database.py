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


def get_user_pwd():
    user_name = get_secret("Username")  # Replace with the actual secret name in key vault
    psd = get_secret("Password")
    return user_name, psd


if 'AKS_ENV' in os.environ:
    if os.environ['AKS_ENV'] == "DEV":
        username, pwd = get_user_pwd()
        host = "cgfpsmadevsql.database.windows.net,1433"
        db = "cgfpsmadevsqlDB"
    elif os.environ['AKS_ENV'] == "QA":
        username, pwd = get_user_pwd()
        host = "cgfpsmaqasql.database.windows.net,1433"
        db = "cgfpsmaqasqlDB"
    elif os.environ['AKS_ENV'] == "PROD":
        username, pwd = get_user_pwd()
        host = "cgfpsmaprodsql.database.windows.net,1433"
        db = "cgfpsmaprodsqlDB"
else:
    username, pwd = get_user_pwd()
    host = "cgfpsmadevsql.database.windows.net,1433"
    db = "cgfpsmadevsqlDB"

# username = get_secret("Username")
# pwd = get_secret("Password")
# host = "cgfpsmadevsql.database.windows.net,1433"
# # username = settings.MSSQL_USER
# # pwd = settings.MSSQL_PASSWORD
# db = "cgfpsmadevsqlDB"

driver = "{ODBC Driver 18 for SQL Server}"
params = urllib.parse.quote_plus("DRIVER=" + driver +
                                 ";SERVER=" + host +
                                 ";DATABASE=" + db +
                                 ";UID=" + username +
                                 ";PWD=" + pwd)

engine = create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
