'''
Created on May 14, 2014

@author: Rishi.Patel
'''

import pandas as pd

class MyData(object):
    '''
    classdocs
    '''


    def __init__(self, config={}):
        '''
        Constructor
        '''
        
        self._load_defaults(config)
        
    def _load_defaults(self, config):
        
        default = {}
        self.file_names = config['files']
        
        # Columns to Keep
        default['sweep'] = ['PROCESS','EVBNICK', 's_RfinTarget_dBmPeak',  's_Backoff_dB',  's_Waveform']
        default['result'] = ['correctedmxaAclr1Max','correctedmxaAclr2Max', 'pmPaOutDBm']
        default['repeat'] = ['r_RepeatNumWithReset','r_RepeatNumWithoutReset']
        default['path_db'] = r'../../../../../iDocuments/Maxim/projects/dortey/data/baseline/'
        
        for key in default.keys():
            if key not in config:
                config[key] = default[key]
        
        self.CONFIG = config
        self.EVB_LUT = {
                        110: 'ANTDEL',
                        109: 'ANTNOD',
                        'GLD': 'KOLDEL',
                        21127: 'KOLNOD',
                        }
        self.shorthand = {
                          's_RfinTarget_dBmPeak':'RfinTarg',
                          's_Backoff_dB':'BackOff',
                          'EVBNUM':'EVB#',
                          }
    
    def retrieve(self):
        
        data = self.read()
        self.clean(data)
        self.remove(data)
        
    def read(self):
        
        data_raw = pd.DataFrame()
        for name in self.file_names:
            print 'adding file: ' + name
            file_path = self.CONFIG['path_db'] + name
            
            try:
                data_raw = data_raw.append(pd.read_csv(file_path)) 
            except IOError:
                raise
        
        print data_raw.columns    
        return data_raw
    
    def clean(self, data):   
        # Convert FW to Short Form if path is included
        
        MAX_LENGTH = 20

        for fw in  data.s_Fw.unique():
            out_fw =  data.s_Fw[data.s_Fw == fw]
            check = out_fw.iloc[0].split('\\')
            
            # Only convert if name is long...
            if len(check) > 1:
                data.s_Fw[ data.s_Fw == fw] = check[-1]
                fw = check[-1]
                
            if len(fw) > MAX_LENGTH:
                data.s_Fw[data.s_Fw == fw] = fw[-MAX_LENGTH:]
                fw = fw[-MAX_LENGTH:]

        EVBNICK = []
        if 'EVBNICK' in self.CONFIG['sweep']:
            for name in data['EVBNUM']:
                if type(name) == float:
                    name = int(name)
                if name in self.EVB_LUT:
                    nickname = self.EVB_LUT[name]
                else:
                    nickname = 'NA'
                EVBNICK.append(nickname + str(name))
            
            data['EVBNICK'] = EVBNICK

    def remove(self, data):
        # Filters

        self.df = data[self.CONFIG['result'] + 
                       self.CONFIG['sweep'] + 
                       self.CONFIG['repeat']]  
        self.permutations = data[self.CONFIG['sweep']].drop_duplicates()

        #self.df = self.df.rename(columns = self.shorthand)
        #self.permutations = self.permutations.rename(columns = self.shorthand)
        
        print self.permutations