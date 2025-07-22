from flet import *
import SYSConnectToServers as CS
import pandas as pd
import GUIForm as GF
import GUIBordereaux as Brdx


class BrdxTemplates(Container):
    def __init__(self):
        super().__init__()

        self.ETL = CS.ConnectToODSServer()
        self.ColumnNames = []; self.RowsData = []; self.RowValues = ''
        self.ColumnSelect = 'CONID'; self.ReportTitle = 'Bordereaux Templates'
        self.Query = f"select distinct CONID from RESVBrdxReportTemplates"
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
        if self.ColumnSelect == 'CONID': self.GetCONID()
        print(self.Query)
        self.TableData = pd.DataFrame(self.ETL.qryODSGetData(self.Query))
        self.CurrentPage = 1; self.TotalPages = (self.TableData.shape[0] + 10 - 1) // 10
        await self.GetScreenChange()

    async def GetNavigateBack(self, e):
        print(self.ColumnSelect)
        if self.ColumnSelect == 'CONID': self.ReportScreen = Brdx.Bordereaux().ReportingScreen
        self.ReportingScreen.controls.clear()
        self.ReportingScreen.controls.append(self.ReportScreen)
        await self.ReportingScreen.update_async()

    async def GetScreenChange(self):
        self.ColumnNames.clear(); self.RowsData.clear()
        if self.ColumnSelect == 'CONID': self.ReportScreen = GF.FormScreen(self.Query, self.ColumnSelect, self.ReportTitle).GetFormScreen()
        else: self.GetReportScreen()
        self.ReportingScreen.controls.clear()
        self.ReportingScreen.controls.append(self.ReportScreen)
        await self.ReportingScreen.update_async()

    def GetCONID(self):
        self.Query = 'Select * from RESVBrdxReportTemplates'
        self.ColumnSelect = 'CONID'; self.ReportTitle = f"{self.RowValues} - Bordereaux Template"





