from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import pandas as pd
import pyodbc

   
class ConnectToODSServer():

    def __init__(self):
        Driver ='ODBC Driver 17 for SQL Server'
        ODSServer = 'testingforwardetl.database.windows.net,1433'; ODSDatabase ='ForwardETL'; ODSUser = 'mohsinahm'; ODSPassword='mos@5481'
        self.ODSConnectionString = f'Driver={Driver};Server={ODSServer};Database={ODSDatabase};UID={ODSUser};PWD={ODSPassword};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        self.ODSConnection = URL.create("mssql+pyodbc", query={"odbc_connect": self.ODSConnectionString})
        self.engineODS = create_engine(self.ODSConnection, use_setinputsizes = False, echo = False)
        self.ODSConnectionPandas = self.engineODS.connect()
        self.ODSConnection = pyodbc.connect(self.ODSConnectionString)


    def qryODSAppendData(self, query):
        self.ODSConnection.execute(query).commit()
   
    def qryODSGetData(self, query):
        return pd.read_sql(query, con=self.ODSConnectionPandas)