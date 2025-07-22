from flet import *
import SYSConnectToServers as CS
import pandas as pd
import ETLBrdxReport as EBR
import GUIBordereaux as Brdx

class BrdxReports(Container):
    def __init__(self):
        super().__init__()

        # self.ETL = CS.ConnectToETLServer()
        self.ColumnNames = []; self.RowsData = []; self.RowValues = ''
        self.ColumnSelect = 'ReportingYear'; self.ReportTitle = 'Bordereaux Reports'
        self.Query = f"select distinct ReportingYear from FACTData"
        # self.TableData = pd.DataFrame(self.ETL.qryETLGetData(self.Query))
        self.TableData = pd.DataFrame({'ReportingYear':['2023','2024','2025']})
        self.GetReportScreen()
        self.ReportingScreen = Column(expand=True, controls=[self.ReportScreen])

    def GetReportScreen(self):
        self.GetTableData()
        self.ReportTableData = DataTable(expand=True,border_radius=8,border=border.all(2,"#263238"),columns=self.ColumnNames,rows=self.RowsData)
        self.ReportHeader = Container(expand=True, height=50, bgcolor="#AD1457",border_radius=border_radius.only(top_left=15,top_right=15),
                            padding=padding.only(left=15,right=15),content=Row(expand=True,alignment=MainAxisAlignment.SPACE_BETWEEN,
                            controls=[IconButton(icon=icons.NAVIGATE_BEFORE_ROUNDED, icon_color=colors.WHITE, on_click = self.GetNavigateBack),
                            Container(expand=True,content=Text(self.ReportTitle,text_align="Center",size=18,color="white",weight='bold'))]))
        self.ReportScreen = Column(expand=True,controls=[Row(controls=[Row(expand=True,controls=[self.ReportHeader]),Divider(height=2,
                            color="transparent")]),Column(scroll="hidden",expand=True,controls=[Row([self.ReportTableData])])])
       
    def GetBrdxScreen(self):
        for cols in self.TableData.columns.values: self.ColumnNames.append(DataColumn(Text(cols,size=15,color='#AD1457',weight='bold')))
        Start = (self.CurrentPage-1); End = Start + 10
        for index, rows in self.TableData[Start:End].iterrows():
            self.RowsData.append(DataRow(cells=[DataCell(Text(value, color="white",size=13))for value in rows.values]))  
        self.ReportHeader = Container(expand=True, height=100, bgcolor="#AD1457",border_radius=border_radius.only(top_left=15,top_right=15),
                            padding=padding.only(left=15,right=15),content=Column(expand=True, controls=[Row(expand=True,alignment=MainAxisAlignment.SPACE_BETWEEN,                                                  
                            controls=[IconButton(icon=icons.NAVIGATE_BEFORE_ROUNDED, icon_color=colors.WHITE, on_click = self.GetNavigateBack),
                            Container(expand=True,content=Text(self.ReportTitle,text_align="Center",size=18,color="white",weight='bold')),
                            IconButton(icon=icons.DOWNLOAD_OUTLINED, icon_color=colors.WHITE, on_click = lambda e : self.GetBrdxDownload(e))]),
                            Row(expand=True,alignment=MainAxisAlignment.SPACE_BETWEEN,controls=[Container(expand=True,height=50,bgcolor="#AD1457",border_radius=10,padding=8,
                            content=Row(expand=2,spacing=1,controls=[TextField(label='Total Lines',value=f'{self.TableData.shape[0]}',
                            disabled=True,height=20,text_size=13,color="white")]))])]))
        self.Pagination = Container(content=Row(controls=[self.GetPagination()], alignment=MainAxisAlignment.CENTER))
        self.ReportScreen = Column(expand=True,controls=[Row(controls=[Row(expand=True,controls=[self.ReportHeader]),Divider(height=2,
                            color="transparent")]),Column(scroll="auto",expand=True,controls=[Row([self.ReportTableData],scroll='always'), self.Pagination])])
       
    def GetBrdxSelectScreen(self):
        self.ReportProgressRing = Container(expand=True, height=5, bgcolor="#00E676",border_radius=border_radius.only(top_left=15,top_right=15),
                            padding=padding.only(left=15,right=15),content=Column(expand=True, controls=[ProgressBar(aspect_ratio=5.0,height=2,width=3,color="#AD1457")]))

        self.ReportScreen = Column(expand=True,controls=[Row(controls=[Row(expand=True,controls=[self.ReportHeader]),Divider(height=2,
                            color="transparent")]),Column(scroll="hidden",expand=True,controls=[Row([self.ReportProgressRing])])])
       
    def GetBrdxDownload(self, e):
        writer = pd.ExcelWriter('Enhanced.xlsx', engine='xlsxwriter')
        self.TableData.to_excel(writer, index=False, sheet_name='BrdxReport')
        workbook = writer.book; worksheet = writer.sheets['BrdxReport']
        worksheet.set_zoom(50)
        header_format = workbook.add_format({'bold': True,'text_wrap': True,'valign': 'top','fg_color': '#D7E4BC','border': 1})
        for col_num, value in enumerate(self.TableData.columns.values):
            worksheet.write(0, col_num + 1, value, header_format)        
        writer.close()
        print('this is test')
        pass

    def GetTableData(self):
        for cols in self.TableData.columns.values: self.ColumnNames.append(DataColumn(Text(cols,size=15,color='#AD1457',weight='bold')))
        for index, rows in self.TableData.iterrows():
            self.RowsData.append(DataRow(cells=[DataCell(Text(rows[self.ColumnSelect],color="white",size=15,width=700))],
            on_select_changed = lambda e : self.GetNavigateFront(e)))
           
    def GetNavigateFront(self, e):
        self.RowValues = ''
        for value in e.control.cells:
            self.RowValues = str(value.content.value)
        if self.ColumnSelect == 'ReportingYear': self.GetReportingPeriods()
        elif self.ColumnSelect == 'ReportingPeriod': self.GetReportingCONIDs()
        elif self.ColumnSelect == 'CONID': self.GetReportingContracts()
        elif self.ColumnSelect == 'ContractNumber': self.GetReportingCategory()
        elif self.ColumnSelect == 'PremiumCategory': self.GetReportingProductCodes()
        elif self.ColumnSelect == 'ProductCode': self.GetReportsBordereaux()
        print(self.Query)
        self.TableData = pd.DataFrame(self.ETL.qryETLGetData(self.Query))
        self.CurrentPage = 1; self.TotalPages = (self.TableData.shape[0] + 15 - 1) // 15
        self.GetScreenChange()

    async def UpdateScreen(self, MainScreen):
        print('Im Here')
        self.ReportingScreen.controls.clear()
        self.ReportingScreen.controls.append(MainScreen)
        await self.ReportingScreen.update_async()


    async def GetNavigateBack(self, e):
        print(self.ColumnSelect)
        if self.ColumnSelect == 'ReportingYear':  MainScreen = Brdx.Bordereaux().ReportingScreen; await self.UpdateScreen(MainScreen)
        else:
            if self.ColumnSelect == 'ReportingPeriod': self.GetReportingYears()
            elif self.ColumnSelect == 'CONID': self.RowValues = self.ReportingYear; self.GetReportingPeriods()
            elif self.ColumnSelect == 'ContractNumber': self.RowValues = self.ReportingPeriod; self.GetReportingCONIDs()
            elif self.ColumnSelect == 'PremiumCategory': self.RowValues = self.CONID; self.GetReportingContracts()
            elif self.ColumnSelect == 'ProductCode': self.RowValues = self.ContractNumber; self.GetReportingCategory()
            elif self.ColumnSelect == 'BrdxReport': self.RowValues = self.PremiumCategory; self.GetReportingProductCodes()
            self.TableData = pd.DataFrame(self.ETL.qryETLGetData(self.Query))
            await self.GetScreenChange()

    def GetScreenChange(self):
        self.ColumnNames.clear(); self.RowsData.clear()
        if self.ColumnSelect == 'BrdxReportSelect': self.GetBrdxSelectScreen()
        elif self.ColumnSelect == 'BrdxReport': self.GetBrdxScreen()
        else: self.GetReportScreen()
        self.ReportingScreen.controls.clear()
        self.ReportingScreen.controls.append(self.ReportScreen)
        self.ReportingScreen.update()

    def GetReportingYears(self):
        self.Query=f"select distinct ReportingYear from FACTData"
        self.ColumnSelect = 'ReportingYear'
        self.ReportTitle = 'Bordereaux Reports'

    def GetReportingPeriods(self):
        self.Query=f"select distinct ReportingPeriod from FACTData where ReportingYear = '{self.RowValues}'"
        self.ColumnSelect = 'ReportingPeriod'; self.ReportingYear = self.RowValues
        self.ReportTitle = f'{self.ReportingYear} - Reporting Periods'

    def GetReportingCONIDs(self):
        self.Query=f"select distinct CONID from FACTData where ReportingYear = '{self.ReportingYear}' and ReportingPeriod = '{self.RowValues}'"
        self.ColumnSelect = 'CONID'; self.ReportingPeriod = self.RowValues
        self.ReportTitle = f'{self.ReportingPeriod} - Contract ID'

    def GetReportingContracts(self):
        self.Query=f"select distinct ContractNumber from FACTData where ReportingYear = '{self.ReportingYear}' and ReportingPeriod = '{self.ReportingPeriod}'\
             and CONID = '{self.RowValues}'"
        self.ColumnSelect = 'ContractNumber'; self.CONID = self.RowValues
        self.ReportTitle = f'{self.ReportingPeriod}-{self.CONID} - Contrat Numbers'

    def GetReportingCategory(self):
        self.Query=f"select distinct PremiumCategory from FACTData where ReportingYear = '{self.ReportingYear}' and ReportingPeriod = '{self.ReportingPeriod}'\
             and CONID = '{self.CONID}' and ContractNumber = '{self.RowValues}'"
        self.ColumnSelect = 'PremiumCategory'; self.ContractNumber = self.RowValues
        self.ReportTitle = f'{self.ReportingPeriod}-{self.CONID}-{self.ContractNumber} - Premium Category'

    def GetReportingProductCodes(self):
        self.Query=f"select distinct ProductCode from FACTData where ReportingYear = '{self.ReportingYear}' and ReportingPeriod = '{self.ReportingPeriod}'\
             and CONID = '{self.CONID}' and ContractNumber = '{self.ContractNumber}'  and PremiumCategory = '{self.RowValues}'"
        self.ColumnSelect = 'ProductCode'; self.PremiumCategory = self.RowValues
        self.ReportTitle = f'{self.ReportingPeriod}-{self.CONID}-{self.ContractNumber}-{self.PremiumCategory} - Product Codes'

    def GetReportsBordereaux(self):
        self.ProductCode = self.RowValues
        self.ColumnSelect = 'BrdxReportSelect'
        self.GetScreenChange()
        EBR.JDownloadBrdxReport(self.ReportingPeriod, self.CONID, self.ContractNumber, self.PremiumCategory, self.ProductCode).GetBrdxDownloadData()
        self.Query = f"Select * from tempBrdxDownloadFinal"
        self.ColumnSelect = 'BrdxReport'
        self.ReportTitle = f'{self.ReportingPeriod}-{self.CONID}-{self.ContractNumber}-{self.PremiumCategory}-{self.ProductCode}'

    def GetPagination(self):
        PreviousButton = ElevatedButton(on_click=self.GetPreviousPage,bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.NAVIGATE_BEFORE_OUTLINED,
                size=12, color=colors.WHITE)]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=20,width=50)
        NextButton = ElevatedButton(on_click=self.GetNextPage,bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.NAVIGATE_NEXT_OUTLINED,
                size=12, color=colors.WHITE)]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=20,width=50)
        PageNum = (self.CurrentPage//10) + 1
        PageLabel = Text(f"Page {PageNum} of {self.TotalPages}",color="white")
        Pagination = Row([PreviousButton, PageLabel, NextButton], alignment=MainAxisAlignment.CENTER)
        return Pagination
   
    def GetNextPage(self,e):
        if self.CurrentPage > 0 and ((self.CurrentPage+10)/10) < self.TotalPages:
            self.CurrentPage = self.CurrentPage + 10
            self.GetScreenChange()

    def GetPreviousPage(self,e):
        if self.CurrentPage > 10 and (self.CurrentPage/10) < self.TotalPages:
            self.CurrentPage = self.CurrentPage - 10
            self.GetScreenChange()


def main(page: Page):

    page.title = "Navigation"
    page.theme_mode = "dark"
    page.padding = 10
    page.scroll = "never"

    page.add(BrdxReports().ReportingScreen)
    page.update()

if __name__ == "__main__":
    app(target=main)

