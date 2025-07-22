
import SYSConnectToServers as CS
import pandas as pd

class DownloadBrdxReport():

    def __init__(self):
        self.ODS = CS.ConnectToODSServer()
        self.ETL = CS.ConnectToETLServer()
   
    def GetBrdxTemplate(self, CONID):
        LogicData = pd.DataFrame(self.ODS.qryODSGetData(f"Select * from RESVBrdxReportTemplates where CONID = '{CONID}' order by ColumnSequence"))
        self.ETL.qryETLAppendData(f"if OBJECT_ID (N'tempBrdxDownloadFinal', N'U') IS NOT NULL drop table tempBrdxDownloadFinal")
        qryCreateTemplate = ""
        for index, BrdxRows in LogicData.iterrows():
            ColumnName=BrdxRows["ColumnOutput"]; DataType=BrdxRows["DataType"]; AllowNull=BrdxRows["AllowNull"]
            qryCreateTemplate = qryCreateTemplate + " [" + (ColumnName) + "] " + (DataType) + " " + AllowNull + ", "
        qryCreateTemplate  = qryCreateTemplate[0:(len(qryCreateTemplate)-2)]  
        qryCreateTemplate = f"Create table tempBrdxDownloadFinal ({qryCreateTemplate})"
        # print(qryCreateTemplate); input()
        self.ETL.qryETLAppendData(qryCreateTemplate)

    def GetBrdxDownloadData(self, ReportingPeriod, CONID, PremiumCategory, ProductCode, ContractNumber):  
        qrySelect = ''; qryInsert = ''
        LogicData = pd.DataFrame(self.ODS.qryODSGetData(query = f"Select * from RESVBrdxReportVariables where CONID = '{CONID}' and ProductCode = '{ProductCode}'"))
        for index, BrdxRows in LogicData.iterrows():
            ColumnName=BrdxRows["ColumnOutput"]; SourceData=BrdxRows["TableName"]; ColumnValue=BrdxRows["Variables"]
            qrySelect = qrySelect + " [" + (ColumnName) + "], "
            if SourceData == 'Manual Input': qryInsert = qryInsert + "'" + str(ColumnValue) + "' AS [" + ColumnName +'], '
            elif SourceData == 'Function': qryInsert = qryInsert + str(ColumnValue) + " AS [" + ColumnName +'], '
            else: qryInsert = qryInsert + "dbo." + str(SourceData) + "." + str(ColumnValue) + " AS [" + ColumnName +'], '
        qrySelect1  = qrySelect[0:(len(qrySelect)-2)]; qryInsert1  = qryInsert[0:(len(qryInsert)-2)]

        qryRelation = f" FROM dbo.DIMALISReconData RIGHT JOIN (dbo.DIMLiabilityData RIGHT JOIN (dbo.DIMAddressData RIGHT JOIN (dbo.DIMEQData \
            RIGHT JOIN (dbo.DIMTIVData RIGHT JOIN (dbo.DIMPremiumData RIGHT JOIN (dbo.DIMSharePrcntData RIGHT JOIN (dbo.DIMContractData \
            RIGHT JOIN (dbo.DIMJETData RIGHT JOIN (dbo.FACTData LEFT JOIN dbo.DIMBrdxData ON dbo.FACTData.UID = dbo.DIMBrdxData.UID) \
            ON dbo.DIMJETData.UID = dbo.FACTData.UID) ON dbo.DIMContractData.UID = dbo.FACTData.UID) ON dbo.DIMSharePrcntData.UID = dbo.FACTData.UID) \
            ON dbo.DIMPremiumData.UID = dbo.FACTData.UID) ON dbo.DIMTIVData.UID = dbo.FACTData.UID) ON dbo.DIMEQData.UID = dbo.FACTData.UID) \
            ON dbo.DIMAddressData.UID = dbo.FACTData.UID) ON dbo.DIMLiabilityData.UID = dbo.FACTData.UID) ON dbo.DIMALISReconData.UID = dbo.FACTData.UID"

        qryWhere = f" WHERE dbo.FACTData.ReportingPeriod='{ReportingPeriod}' AND dbo.FACTData.ContractNumber='{ContractNumber}' AND dbo.FACTData.CONID='{CONID}' \
            AND dbo.FACTData.ProductCode='{ProductCode}' AND dbo.FACTData.PremiumCategory='{PremiumCategory}';"
       
        qryLoadData = f'INSERT INTO tempBrdxDownloadFinal (' + qrySelect1 + ') Select ' + qryInsert1 + qryRelation + qryWhere
        # print(qryLoadData);input()
        self.ETL.qryETLAppendData(qryLoadData)




