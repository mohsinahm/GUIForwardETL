from flet import *
import SYSConnectToServers as CS
import pandas as pd
import GUIForm as GF


class LogicTables(Container):
    def __init__(self):
        super().__init__()

        self.ETL = CS.ConnectToODSServer()
        self.ColumnNames = []; self.RowsData = []; self.RowValues = ''
        self.ColumnSelect = 'ProductName'; self.ReportTitle = 'Logic Tables'
        self.Query = f"select distinct ProductName from RESVProductLogic"
        self.TableData = pd.DataFrame(self.ETL.qryODSGetData(self.Query))
        self.GetReportScreen()
        self.ReportingScreen = Column(expand=True, controls=[self.ReportScreen])

    def GetReportScreen(self):
        self.GetTableData()
        self.ReportTableData = DataTable(expand=True,border_radius=8,border=border.all(2,"#263238"),columns=self.ColumnNames,rows=self.RowsData)
        self.ReportHeader = Container(expand=True, height=50, bgcolor="#AD1457",border_radius=border_radius.only(top_left=15,top_right=15),
                            padding=padding.only(left=15,right=15),content=Row(expand=True,alignment=MainAxisAlignment.SPACE_BETWEEN,
                            controls=[IconButton(icon=icons.NAVIGATE_BEFORE_ROUNDED, icon_color=colors.WHITE, on_click = self.GetNavigateBack),
                            Container(expand=True,content=Text(self.ReportTitle,text_align="Center",size=20,color="white",weight='bold'))]))
        self.ReportScreen = Column(expand=True,controls=[Row(controls=[Row(expand=True,controls=[self.ReportHeader]),Divider(height=2,
                            color="transparent")]),Column(scroll="hidden",expand=True,controls=[Row([self.ReportTableData])])])


    def GetTableData(self):
        for cols in self.TableData.columns.values: self.ColumnNames.append(DataColumn(Text(cols,size=15,color='#AD1457',weight='bold')))
        for index, rows in self.TableData.iterrows():
            self.RowsData.append(DataRow(cells=[DataCell(Text(rows[self.ColumnSelect],color="white",size=15,width=700))],
            on_select_changed = self.GetNavigateFront))
           
    async def GetNavigateFront(self, e):
        self.RowValues = ''
        for value in e.control.cells:
            self.RowValues = str(value.content.value)
        if self.ColumnSelect == 'ProductName': self.GetLogicList()
        elif self.ColumnSelect == 'TableNames': self.GetLogicTable()
        print(self.Query)
        self.TableData = pd.DataFrame(self.ETL.qryODSGetData(self.Query))
        self.CurrentPage = 1; self.TotalPages = (self.TableData.shape[0] + 10 - 1) // 10
        await self.GetScreenChange()

    async def GetNavigateBack(self, e):
        if self.ColumnSelect == 'TableNames': self.GetProductList()
        elif self.ColumnSelect == 'LogicTable': self.RowValues = self.ProductName; self.GetLogicList()
        self.TableData = pd.DataFrame(self.ETL.qryODSGetData(self.Query))
        await self.GetScreenChange()

    async def GetScreenChange(self):
        self.ColumnNames.clear(); self.RowsData.clear()
        if self.ColumnSelect == 'LogicTable': self.ReportScreen = GF.FormScreen(self.Query, self.ColumnSelect, self.ReportTitle).GetFormScreen()
        else: self.GetReportScreen()
        self.ReportingScreen.controls.clear()
        self.ReportingScreen.controls.append(self.ReportScreen)
        await self.ReportingScreen.update_async()

    def GetProductList(self):
        self.Query=f"select distinct ProductName from RESVProductLogic"
        self.ColumnSelect = 'ProductName'
        self.ReportTitle = 'Product List'

    def GetLogicList(self):
        self.Query=f"select * from SYSLogicTables"
        self.ProductName = self.RowValues
        ProductCode = f"select distinct ProductCode from RESVProductLogic where ProductName = '{self.ProductName}'"
        self.ProductCode = self.ETL.qryODSGetData(ProductCode).values[0][0]
        self.ColumnSelect = 'TableNames'; self.ReportTitle = f'{self.ProductName} - Logic List'

    def GetLogicTable(self):
        self.ColumnSelect = 'LogicTable'; self.TableName = self.RowValues; self.ReportTitle = 'Logic Table'
        if self.TableName == 'RESVProductLogic': self.Query = f"select ProductLogicID, ProductCode, PremiumLogic, SharePrcntLogic, ContractNumberLogic, \
        PremiumCategory from {self.TableName} where ProductCode = '{self.ProductCode}'"
        elif self.TableName == 'RESVVariableLogic': self.Query = f"select VariableNameID, ColumnName, DataType, Source, TableName, Description, {self.ProductCode} from\
        RESVVariablesLogic where {self.ProductCode} = 'Activate'"
        elif self.TableName == 'RESVEQZoneLogic': self.Query = f"select * from {self.TableName}"
        else: self.Query = f"select * from {self.TableName} where ProductCode = '{self.ProductCode}'"





