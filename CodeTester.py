import pandas as pd
import webgen.web_report as web
import regression.database_reader as rd
import regression.report as autogen

'''
'''

database_path = r'\\lightspeed1\workspace\work_rpatel\database\dohrety\results\pdetDerate/'
#database_path = r'C:\Users\Rishi.Patel\iDocuments\Maxim\projects\dortey\data\multDcOsOpt/'


files = []
#files.append('TT_20140520T222811.csv')
#files.append('TTT_110B_sysChar_20140521T141204.csv')
#files.append('TTT_110B_sysChar_20140521T153010.csv')
#files.append('TTT_110B_sysChar_20140521T212356.csv')
#files.append('TTT_GLD_sysChar_20140514T090857.csv')
#files.append('TTT_GLD_sysChar_20140515T090843.csv')
# Below should all be same board (not clear by names saved in .csv)
#files.append('TempCo_fwCompareUncal_20140616T173039.csv')  # Koala + Delay + Doherty + 10MHz Waveform Results
#files.append('TempCo_fwCompareUncal_20140616T230015.csv')  # Koala + Delay + Doherty + 20MHz Waveform Results
files.append('TempCo_fwCompareUncal_20140617T113614.csv')  # Koala + Delay + Doherty + 20MHz Waveform Results

pdetRepeat = ['currentTemp_degrees', 'pmPaGainDB', 'Temp',\
              'PdetIndexAFine', 'EdetIndexAFine', 'PmuRffbA', 'PmuRfinA',\
              'PdetIndexBFine', 'EdetIndexBFine', 'PmuRffbB', 'PmuRfinB',\
               ]
#pdetRepeat = []
settings = {
            'path_db': database_path,
            'files': files,
            'repeat': ['r_RepeatNumWithReset', 'r_RepeatNumWithoutReset'] + pdetRepeat,
            'sweep': ['s_Fw', 's_Waveform', 's_Backoff_dB',  's_RfinTarget_dBmPeak']
           }

col_data = { 
            'filter': {}
#            'filter': {'s_RfinTarget_dBmPeak': 0, 's_Waveform': 0,}
            
             }

oData = rd.MyData(settings)
oData.retrieve()


oPages = autogen.ReportGen(oData, col_data)
oPages.generate_report()

web_report_name = 'test'
oReport = web.ReportGen()
oReport.web_report(oPages.data, content=oPages.content, name=web_report_name)
print 'Report Complete!\n'