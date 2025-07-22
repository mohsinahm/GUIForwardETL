from flet import *
import SYSConnectToServers as CS
import pandas as pd
import GUIForm as GF


class GUIVariableList(Container):
    def __init__(self):
        super().__init__()

        self.ETL = CS.ConnectToODSServer()
        self.ColumnNames = []; self.RowsData = []; self.RowValues = ''
        self.ColumnSelect = 'VariableList'; self.ReportTitle = 'Variable List'
        self.Query = f"select VariableNameID, ColumnName, DataType, Source, TableName, Description from RESVVariablesLogic"
        self.GetScreenChange()
        self.ReportingScreen


    def GetScreenChange(self):
        self.ReportingScreen = GF.FormScreen(self.Query, self.ColumnSelect, self.ReportTitle).GetFormScreen()




