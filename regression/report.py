'''
Created on May 15, 2014

@author: Rishi.Patel
'''

import pandas as pd
import regression.analysis as pars
import time
import os

class ReportGen(object):
    '''
    classdocs
    '''


    def __init__(self, oData, settings={}):
        '''
        Constructor
        '''
        
        print 'Generating Report...'
        
        self.oData = oData
        self._load_constants(settings)
        
    def _load_constants(self, settings):
        
        # GENERAL SETTINGS
        self.PAGE_COL_NAMES = ['name', 'type', 'title', 'data']
        
        default = {
                   'filter': ['s_Fw', 'EVBNICK'],
                   }
         
        self.settings = {}
        for key in default.keys():
            if key in settings:
                self.settings[key] = settings[key]
            else:
                self.settings[key] = default[key]
        
    def generate_report(self):
        
        self.oParse = pars.Analyze(self.oData.CONFIG['sweep'])
        figs = self.oParse.filter_data(self.oData.df)
        self.create_pages(figs)
        
    def add_setup_pages(self, line_up, p_dict):
        'Very Hackish - re-edit'
        
        path = r'\\lightspeed1\workspace\work_rpatel\database\dohrety\setup\\'
        datasheet_path = '//lightspeed1/home/public/MARKETING_AND_SALES/RFPAL2_Hardware/PAM_inventory/TestSetups/PAMTestSetups/'
        image_path = path + 'CharBenchSetupPAM114.png'
        body = 'Overview of PAM114 CHAR BENCH Setup for Antares'
        #body += 'Link to PA DataSheet:' + datasheet_path
        
        if line_up == 'Performance':
            line_up_path = path + 'Performance_Line_Up.png'
        elif line_up == '':
            line_up_path = path + 'Driver_Line_Up.png'
        else:
            line_up_path = ''

        pa_df = pd.read_csv(path + 'SetupPA.csv')
        ps_df = pd.read_csv(path + 'SetupPowerSupply.csv')
        data_url = open(image_path, 'rb').read().encode('base64').replace('\n', '')
        lineup_url = open(line_up_path, 'rb').read().encode('base64').replace('\n', '')
        
        i = len(p_dict)
        p_dict[i+1] = ['Setup', 'TEXT', 'Analysis', body]
        p_dict[i+2] = ['Setup', 'DATA', 'PA SETUP', pa_df]
        p_dict[i+3] = ['Setup', 'DATA', 'POWER SUPPLY SETUP', ps_df]
        p_dict[i+4] = ['Setup', 'IMG', line_up + ' PA Line Up', lineup_url]
        p_dict[i+5] = ['Setup', 'IMG', 'BENCH SETUP', data_url]
        
    def add_overview_page(self, p_dict):
        
        OVERVIEW_BODY = (
        'Below is a list of all the permutations that are being compared in ' 
        'this report')

        PERMUTATION_BODY = (
        'This is a list of all the permutations that are being processed. ')

        files_df = pd.DataFrame(self.oData.file_names, columns=['File Name'])

        i = len(p_dict)
        p_dict[i+1] = ['Overview', 'TEXT', 'Overview', OVERVIEW_BODY]
        p_dict[i+2] = ['Overview', 'TEXT', 'Permutations', PERMUTATION_BODY]
        p_dict[i+3] = ['Overview', 'DATA', '', self.oData.permutations]
        p_dict[i+4] = ['Overview', 'DATA', 'File Names', files_df]
        p_dict[i+5] = ['Overview', 'TEXT', 'Database Path', self.oData.CONFIG['path_db']] 
 
    def add_analysis_page(self, figs, p_dict):       
        ANALYSIS_BODY = (
        'Plots comparing the regression sweeps by permutations can be found '
        'below.')

        i = len(p_dict)
        p_dict[i+1] = ['Analysis', 'TEXT', 'Analysis', ANALYSIS_BODY]
        p_dict[i+2] = ['Analysis', 'FIG', 'Comparing Means', figs['aclr_mean']]
        p_dict[i+3] = ['Analysis', 'FIG', 'Comparing ACLR Variance', figs['aclr_var']]
        p_dict[i+4] = ['Analysis', 'FIG', 'Comparing PA OUT Variance', figs['paout_var']]
        
            
        i = len(p_dict)
        
        if 'pdet' not in figs:
            return 
        for fig in figs['pdet']:
            i += 1
            p_dict[i] = [ 'PDET_ANALYSIS', 'FIG', 'PDET'+str(i), fig]

    def add_result_page(self, fig_list, p_dict):
        
        RESULTS_BODY = (
        'Below are the results for each permutation.  Results are plotted vs '
        'time to view convergence rate and adaptation over time.')
    
        i = len(p_dict) + 1
        p_dict[i] = ['Analysis', 'TEXT', 'Results', RESULTS_BODY]
 
        start = i       
        for fig in fig_list:
            i += 1
            p_dict[i] = ['Analysis', 'FIG', 'Figure ' + str(i-start), fig]

    def add_individual_result_page(self, sweep, item, figs, p_dict, ext):
        
        i = len(p_dict) + 1
        fig_name = str(i) + '_' + sweep  + '_'
        fig_name += str(item).replace('-','_').replace('#','_')
        
        page_name = str(i) + '_' + sweep + ' ' + ext
        
        POW_PAGE_NAME = 'PA OUTPUT POWER'
        page_title  = 'Individual Filtered'
        
        p_dict[i+0] = ['Summary PA Power', 'FIG', 'Power ' + fig_name, figs['paout_var']]
        p_dict[i+1] = ['Summary ACLR', 'FIG', 'Variance' + fig_name, figs['aclr_var']]
        p_dict[i+2] = [page_name, 'TEXT', page_title, ext]
        p_dict[i+3] = [page_name, 'FIG', 'Variance ' + fig_name,  figs['aclr_var']]
        p_dict[i+4] = [page_name, 'FIG', 'Mean ' + fig_name, figs['aclr_mean']]
        p_dict[i+5] = [page_name, 'FIG', 'Power ' + fig_name, figs['paout_var']]
                    
    def break_out_results(self, df, p_dict, ext=''):
        for sweep in self.oData.CONFIG['sweep']:
            settings = df[sweep].unique()
            
            # Use as a threshold to decide # of settings required to save plots
            if len(settings) > 2:
                print settings
                for item in settings:
                    item_df = df[df[sweep] == item]
                    figs = self.oParse.filter_data(item_df)
                    self.add_individual_result_page(sweep, item, figs, p_dict, ext)
    
    def set_header_content(self):
        
        content = {}
        
        content['SETUP'] = 'Setup.html'
        content['ABOUT'] = 'http://www.maximintegrated.com/'
        content['HOME'] = self.oData.CONFIG['path_db'] + r'..\reports\\'
        content['DATABASE'] = self.oData.CONFIG['path_db']
        content['RESOURCES'] = 'http://intranet.scinteranetworks.com/default.aspx'
        content['SBAR2_BODY'] = self.set_test_summary()
        
        self.content = content
        
    def set_test_summary(self):
        
        info = []
        
        info.append('Bench: CHAR')
        info.append('Test Type: Regression')
        info.append('Report Made on: ' + time.strftime("%x"))
        info.append('Report Made by: ' + os.environ.get( "USERNAME" ).replace('.', ' '))
    
        return info
    
    def create_pages(self, figs):
        'Create pages for report'
        
        line_up = 'Performance'

        p_dict = {}
        
        self.add_overview_page(p_dict)
        self.add_setup_pages(line_up, p_dict) 
        self.add_analysis_page(figs, p_dict)
        self.add_result_page(figs['aclr_plots'], p_dict)
        self.break_out_results(self.oData.df, p_dict, 'all')

        for key in self.settings['filter'].keys():
            df = self.oData.df
            if  self.settings['filter'][key]:
                df = df[df[key] == self.settings['filter'][key]]
            for val in self.oData.df[key].unique():
                df =  self.oData.df[self.oData.df[key] == val]
                self.break_out_results(df, p_dict, key)
        
        self.set_header_content()
        
        # Convert dict of pages to dataframe
        self.data = pd.DataFrame.from_dict(p_dict, orient='index')
        self.data.columns = self.PAGE_COL_NAMES 