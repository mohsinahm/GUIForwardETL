from flet import *
import SYSConnectToServers as CS
import pandas as pd
import GUILogicTables as LT
import GUIBrdxTemplates as BrdxTemplate

class FormScreen(Container):

    def __init__(self, Query, ColumnSelect, ReportTitle):
        super().__init__()

        self.ETL = CS.ConnectToODSServer()
        self.ColumnNames = []; self.RowsData = []; self.RowValues = ''
        self.Query = Query; self.ColumnSelect = ColumnSelect; self.ReportTitle = ReportTitle
        self.TableData = pd.DataFrame(self.ETL.qryODSGetData(self.Query))
        self.FormScreen = Column(expand=True, controls=[])
        self.CurrentPage = 1; self.TotalPages = (self.TableData.shape[0] + 10 - 1) // 10

    def GetTableData(self):
        for cols in self.TableData.columns.values: self.ColumnNames.append(DataColumn(Text(cols,size=15,color='#AD1457',weight='bold')))
        for index, rows in self.TableData.iterrows():
            self.RowsData.append(DataRow(cells=[DataCell(Text(rows[self.ColumnSelect],color="white",size=15,width=700))]))

    def GetFormScreen(self):
        for cols in self.TableData.columns.values: self.ColumnNames.append(DataColumn(Text(cols,size=15,color='#AD1457',weight='bold')))
        Start = (self.CurrentPage-1); End = Start + 10
        for index, rows in self.TableData[Start:End].iterrows():
            self.RowsData.append(DataRow(cells=[DataCell(Text(value, color="white",size=13))for value in rows.values],on_select_changed = self.PageLogicTables))  
        self.FormTableData = DataTable(expand=True, border=border.all(2,"#ebebeb"), border_radius=10, columns=self.ColumnNames, rows=self.RowsData)
        self.FormFields = Container(expand=True,height=150,bgcolor="white10",border=border.all(1,"#ebebeb"),border_radius=8,padding=15,
                        content=Column(expand=True,controls=[Row(expand=True,controls=self.GetFormFields()),
                        Divider(height=2,color="transparent"),Row(expand=True,alignment=MainAxisAlignment.END,controls=[self.GetFormButton()])]))
        self.Pagination = Container(content=Row(controls=[self.GetPagination()], alignment=MainAxisAlignment.CENTER))
        self.FormTable =  Container(border_radius=10, col = 8, content=Column(expand=True, scroll='auto', controls=[ResponsiveRow([self.FormTableData])]))
        self.FormHeader = Container(expand=True, height=50, bgcolor="#AD1457",border_radius=border_radius.only(top_left=15,top_right=15),
                        padding=padding.only(left=15,right=15),content=Row(expand=True,alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[IconButton(icon=icons.NAVIGATE_BEFORE_ROUNDED,icon_color=colors.WHITE, on_click = self.GetNavigateBack),
                            Container(expand=True,content=Text(self.ReportTitle,text_align="left",size=18,color="white",weight='bold'))]))  
        self.ReportScreen = Column(expand=True,controls=[Row(expand = False, controls=[self.FormHeader]), Row(expand = False, controls=[self.FormFields])
                        ,self.FormTable, self.Pagination])
        self.FormScreen.controls.append(self.ReportScreen)
        return self.FormScreen
       
    async def PageLogicTables(self,e):
        counter = 0
        for cols in self.FormFields.content.controls[0].controls:
            self.FormFields.content.controls[0].controls[counter].content.controls[1].value = e.control.cells[counter].content.value
            counter = counter + 1
        await self.FormFields.update_async()

    async def GetNavigateBack(self, e):
        print(self.ColumnSelect)
        if self.ColumnSelect == 'LogicTable': self.ReportScreen = LT.LogicTables().ReportingScreen
        elif self.ColumnSelect == 'CONID': self.ReportScreen = BrdxTemplate.BrdxTemplates().ReportingScreen
        self.FormScreen.controls.clear()
        self.FormScreen.controls.append(self.ReportScreen)
        await self.FormScreen.update_async()

    async def GetScreenChange(self):
        self.ColumnNames.clear(); self.RowsData.clear()
        self.GetFormScreen()
        self.FormScreen.controls.clear()
        self.FormScreen.controls.append(self.ReportScreen)
        await self.FormScreen.update_async()

    def GetFormButton(self):
        FormButton = Container(alignment=alignment.center,content= Row(controls=[
            ElevatedButton(on_click=[],bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.ADD_ROUNDED,size=12, color=colors.WHITE),
                    Text("Add New", size=10, weight="bold")]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=30,width=100),
            ElevatedButton(on_click=[],bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.UPDATE,size=12, color=colors.WHITE),
                    Text("Update", size=10, weight="bold")]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=30,width=100),
            ElevatedButton(on_click=[],bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.DELETE,size=12, color=colors.WHITE),
                    Text("Delete", size=10, weight="bold")]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=30,width=100)]))
        return FormButton
       
    def GetFormFields(self):
        TableFrameColumns = self.TableData.columns; ColumnNames = []; counter = 0
        for cols in TableFrameColumns:
            ColumnNames.append(Container(expand=2,height=45,bgcolor="#ebebeb",border_radius=6,padding=8,content=Column(spacing=1,controls=[
                Text(value=f'{cols}',size=9,color="black",weight="bold"),TextField(border_color="transparent",height=20,text_size=13,
                content_padding=0,cursor_color="black",cursor_width=1,cursor_height=18,color="black")])))
            counter = counter + 1
        return ColumnNames
    
    def GetPagination(self):
        PreviousButton = ElevatedButton(on_click=self.GetPreviousPage,bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.NAVIGATE_BEFORE_OUTLINED,
                size=12, color=colors.WHITE)]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=20,width=50)
        NextButton = ElevatedButton(on_click=self.GetNextPage,bgcolor="#AD1457",color="white",content=Row(controls=[Icon(name=icons.NAVIGATE_NEXT_OUTLINED,
                size=12, color=colors.WHITE)]),style=ButtonStyle(shape={"":RoundedRectangleBorder(radius=6)},color={"":"white"}),height=20,width=50)
        PageNum = (self.CurrentPage//10) + 1
        PageLabel = Text(f"Page {PageNum} of {self.TotalPages}",color="white")
        Pagination = Row([PreviousButton, PageLabel, NextButton], alignment=MainAxisAlignment.CENTER)
        return Pagination
   
    async def GetNextPage(self,e):
        if self.CurrentPage > 0 and ((self.CurrentPage+10)/10) < self.TotalPages:
            self.CurrentPage = self.CurrentPage + 10
            await self.GetScreenChange()

    async def GetPreviousPage(self,e):
        if self.CurrentPage > 10 and (self.CurrentPage/10) < self.TotalPages:
            self.CurrentPage = self.CurrentPage - 10
            await self.GetScreenChange()