'''
Created on May 15, 2014

@author: Rishi.Patel
'''

import pandas as pd
import seaborn as sns
import numpy as np

class Analyze(object):
    '''
    classdocs
    '''


    def __init__(self, sweepVar, result_var='correctedmxaAclr1Max'):
        '''
        Constructor
        '''
        
        self.sweepVar = sweepVar
        self._load_constants(result_var)
        
    def _load_constants(self, result_var):
        
        #self.df = oData.df
        #self.permuations = oData.
        self.RESULT_VAR = result_var 
        self.X_KEEP_PERCENT = .7
        self.benchmark_lut = {
                              'correctedmxaAclr1Max': -47,
                               }
        
    def filter_data(self, df):
        
        figs = {}
        fig_list = []
        violin_labels = []
        aclr_var_perm = []
        pout_var_perm = []
        aclr_mean_df = pd.DataFrame()
        
        permutations = df[self.sweepVar].drop_duplicates()
        for ith_perm in range(permutations.index.size):
            
            settings = permutations.iloc[ith_perm]
            data = df.copy()
            
            # Filter Data for Current Permutation
            for perm_idx in settings.index:
                data = data[data[perm_idx] == settings[perm_idx]]
                
            # Create a Pivot Table
            pivot = data.pivot_table(
                                     rows=['r_RepeatNumWithoutReset'],
                                     cols=['r_RepeatNumWithReset'],
                                     values=[self.RESULT_VAR],
                                     aggfunc='mean'   # Other options?
                                     )
            
            # Gather Data
            x_data_max = data['r_RepeatNumWithoutReset'].max()
            aclr_mean = pivot[self.RESULT_VAR].mean(axis='columns')
            aclr_var = data[self.RESULT_VAR][data['r_RepeatNumWithoutReset'] >
                                             x_data_max * self.X_KEEP_PERCENT]
            
            # Save Data
            violin_labels.append(settings)
            aclr_var_perm.append(aclr_var)
            pout_var_perm.append(data['pmPaOutDBm'])
            
            aclr_mean.name = aclr_mean_df.columns.size
            aclr_mean_df = aclr_mean_df.join(aclr_mean, how='outer')
            
            fig = sns.plt.figure()
            ax = fig.add_subplot(1,1,1)
            pivot.plot(y=self.RESULT_VAR)
            ax.plot(aclr_mean, lw=3, color='orchid')
            ax.plot(aclr_mean + pivot[self.RESULT_VAR].std(axis='columns'),
                         'lightskyblue', lw=2)
            ax.plot(aclr_mean - pivot[self.RESULT_VAR].std(axis='columns'),
                         'lightskyblue', lw=2)
            
            # Plot a baseline if baseline exists in LUT
            if self.RESULT_VAR in self.benchmark_lut:
                base_line = self.benchmark_lut[self.RESULT_VAR]
            else:
                base_line = aclr_mean.mean()
            ax.plot(base_line * np.ones(aclr_mean.size), lw=2, color='red')

            # Super Impose Temperature
            if 'currentTemp_degrees' in data.columns and 1:
                ax2 = ax.twinx()
                ax2.plot(data['r_RepeatNumWithoutReset'], data['currentTemp_degrees'], 'Maroon', lw=2)
                #ax2.set_ylabel('Temp (degC)', color='Maroon', fontsize=16)
                ax2.tick_params(axis='both', which='major', labelsize=10)
                ax2.tick_params(axis='both', which='minor', labelsize=8)

            # Super Impose Temperature
            if 'PdetIndexAFine' in data.columns and 1:
                ax3 = ax.twinx()
                ax3.plot(data['r_RepeatNumWithoutReset'], data['PdetIndexAFine'], 'RoyalBlue', lw=2)
                ax3.set_ylabel('PdetIndexAFine', color='RoyalBlue', fontsize=16)
                #ax4 = ax.twinx()
                #ax4.plot(data['r_RepeatNumWithoutReset'], data['PdetIndexA'], 'green', lw=2)
                #ax4.set_ylabel('PdetIndexA', color='green', fontsize=16)                                
                # Super Impose Temperature

            if 'Temp' in data.columns and 0:
                ax4 = ax.twinx()
                ax4.plot(data['r_RepeatNumWithoutReset'], data['Temp'], 'g--', lw=2)
                
            # Plot Dressing
            sns.plt.title(settings.values, fontsize=10)
            sns.plt.suptitle('{y_axis} Time Variance'.format
                             (y_axis=self.RESULT_VAR), fontsize=20
                             )
            sns.plt.xlabel('Run Number', fontsize=16)
            ax.set_ylabel('{name} Max [dB]'.format(name=self.RESULT_VAR), fontsize=16, color='orchid')
            fig_list.append(fig)
            
        
        # Setup figs Info
        figs['aclr_plots'] = fig_list    
        figs['aclr_mean'] = self.mean_plot(self.RESULT_VAR, violin_labels, aclr_mean_df)
        figs['aclr_var'] = self.violin_plot(self.RESULT_VAR, violin_labels, aclr_var_perm)
        figs['paout_var'] = self.violin_plot('pmPaOutDBm', violin_labels, pout_var_perm)
        figs['pdet'] = self.pdet_plot(self.RESULT_VAR, violin_labels, data)
        
        return figs
    
    def generate_figure(self, df, param, fig=False):

        if param['y'] not in df.columns or param['x'] not in df.columns:
            return
        
        if not fig:            
            fig = sns.plt.figure()
        ax = fig.add_subplot(1,1,1)

        # Plot the Main Figure
        ax.plot(df[param['x']], df[param['y']], lw=2, color='b') 
        ax.set_ylabel(param['y'], fontsize=16, color='b')

        if param['y'] in self.benchmark_lut:
            ax.plot(self.benchmark_lut[param['y']] * 
                    np.ones(len(df[param['x']])), lw=4, color='r')
        
        # Plot Second Axis if exist
        if param['y2'] in df.columns:
            ax2 = ax.twinx()
            ax2.plot(df[param['x']], df[param['y2']], 'Maroon', lw=2)
            ax2.set_ylabel(param['y2'], color='Maroon', fontsize=16)
        # Plot Dressing
        sns.plt.xlabel(param['x'], fontsize=16)
        sns.plt.title(param['title'], fontsize=20)
        #sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()      
    
        return fig
    
    def pdet_plot(self, resultVar, labels, df, chan='B'):
        
        figs = []
 
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'correctedmxaAclr1Max',
                 'y2': 'currentTemp_degrees',
                 'title': 'ACLR vs Temp NEW!',
                 }
        figs.append(self.generate_figure(df, param))
         
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'correctedmxaAclr1Max',
                 'y2': 'EdetIndex' + chan + 'Fine',
                 'title': 'EDET vs ACLR',
                 }
        figs.append(self.generate_figure(df, param))                                 
        
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'correctedmxaAclr1Max',
                 'y2': 'PdetIndex' + chan + 'Fine',
                 'title': 'ACLR vs PDET',
                 }
        figs.append(self.generate_figure(df, param)) 
        
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'PdetIndex' + chan + 'Fine',
                 'y2': 'EdetIndex' + chan + 'Fine',
                 'title': 'PDET vs EDET',
                 }
        figs.append(self.generate_figure(df, param))  
          
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'PdetIndex' + chan + 'Fine',
                 'y2': 'currentTemp_degrees',
                 'title': 'PDET vs Case Temp',
                 }
        figs.append(self.generate_figure(df, param))
        
        df['RFFB-RFIN'] =  df['PmuRffb' + chan] -  df['PmuRfin' + chan]
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'PdetIndex' + chan + 'Fine',
                 'y2': 'RFFB-RFIN',
                 'title': 'PDET vs RFPAL Gain',
                 }
        figs.append(self.generate_figure(df, param))
               
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'currentTemp_degrees',
                 'y2': 'RFFB-RFIN',
                 'title': 'Case Temp vs RFPAL Gain',
                 }
        figs.append(self.generate_figure(df, param))
        
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'pmPaGainDB',
                 'y2': 'RFFB-RFIN',
                 'title': 'PA Gain: Measured vs RFPAL',
                 }
        figs.append(self.generate_figure(df, param)) 
           
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'correctedmxaAclr1Max',
                 'y2': 'pmPaOutDBm',
                 'title': 'ACLR vs PA Out',
                 }
        figs.append(self.generate_figure(df, param))
        
        param = {
                 'x': 'r_RepeatNumWithoutReset',
                 'y': 'PdetIndex' + chan + 'Fine',
                 'y2': 'PmuRfin' + chan,
                 'title': 'PDET vs RFIN'
                 }
        figs.append(self.generate_figure(df, param))
          
        return figs
                 
        # ACLR and Temp
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        ax.plot(df['r_RepeatNumWithoutReset'], df[resultVar], lw=2, color='orchid') 
        ax.set_ylabel('{name} Max [dB]'.format(name=self.RESULT_VAR), fontsize=16, color='orchid')
        base_line = self.benchmark_lut[resultVar]
        ax.plot(base_line * np.ones(len(df['r_RepeatNumWithoutReset'])), lw=4, color='r')
        if 'currentTemp_degrees' in df.columns and 1:
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['currentTemp_degrees'], 'Maroon', lw=2)
            ax2.set_ylabel('Current Case Temp', color='Maroon', fontsize=16)
        # Plot Dressing
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.title('ACLR and Case Temp', fontsize=20)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()  
                             
        # ACLR vs. PDET
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        ax.plot(df['r_RepeatNumWithoutReset'], df[resultVar], lw=2, color='orchid') 
        ax.set_ylabel('{name} Max [dB]'.format(name=self.RESULT_VAR), fontsize=16, color='orchid')
        base_line = self.benchmark_lut[resultVar]
        ax.plot(base_line * np.ones(len(df['r_RepeatNumWithoutReset'])), lw=4, color='r')
        if 'PdetIndexAFine' in df.columns and 'EdetIndexAFine' in df.columns:
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['PdetIndexAFine'], 'RoyalBlue', lw=2)
            ax2.set_ylabel('E/PdetIndexAFine', color='RoyalBlue', fontsize=16)
            ax2.plot(df['r_RepeatNumWithoutReset'], df['EdetIndexAFine'], 'g', lw=2)
        # Plot Dressing
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.title('ACLR and Case Temp', fontsize=20)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()
        
        # PDET vs Temp
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        # Super Impose PDET
        if 'PdetIndexAFine' in df.columns and 'EdetIndexAFine' in df.columns and 'currentTemp_degrees' : 
            ax.plot(df['r_RepeatNumWithoutReset'], df['PdetIndexAFine'], 'RoyalBlue', lw=2)
            ax.set_ylabel('E/PdetIndexAFine', color='RoyalBlue', fontsize=16)
            ax.plot(df['r_RepeatNumWithoutReset'], df['EdetIndexAFine'], 'g', lw=2)
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['currentTemp_degrees'], 'Maroon', lw=2)
            ax2.set_ylabel('Current Case Temp', color='Maroon', fontsize=16)
        # Plot Dressing
        sns.plt.title('PDET Index and Case Temp', fontsize=20)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend(['resultVar', 'PDET', 'EDET'], fontsize=10)
        sns.plt.tight_layout() 
                
        # RFPAL Measured Gain vs. PDET/EDET
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        if 'PmuRffbA' in df.columns and 'PdetIndexAFine' in df.columns and 1:
            ax.plot(df['r_RepeatNumWithoutReset'], df['PdetIndexAFine'], 'RoyalBlue', lw=2)
            ax.set_ylabel('E/PdetIndexAFine', color='RoyalBlue', fontsize=16)
            ax.plot(df['r_RepeatNumWithoutReset'], df['EdetIndexAFine'], 'green', lw=2)  
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['PmuRffbA'] -  df['PmuRfinA'], 'Maroon', lw=2)
            ax2.set_ylabel('PA Gain: RFFB - RFIN', color='Maroon', fontsize=16)
        # Plot Dressing
        sns.plt.title('PA Gain vs PDET', fontsize=20)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()  
        
        # RFPAL Measured Gain vs. Temp
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        if 'PmuRffbA' in df.columns and 'currentTemp_degrees' in df.columns and 1:
            ax.plot(df['r_RepeatNumWithoutReset'], df['currentTemp_degrees'], 'red', lw=2)
            ax.set_ylabel('Current Case Temp', color='red', fontsize=16)
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['PmuRffbA'] -  df['PmuRfinA'], 'RoyalBlue', lw=2)
            ax2.set_ylabel('PA Gain: RFFB - RFIN', color='RoyalBlue', fontsize=16)
        # Plot Dressing
        sns.plt.title('PA Gain vs PDET', fontsize=20)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout() 
        
        
        # RFPAL Measured Gain vs. PM Gain
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        if 'PmuRffbA' in df.columns and 'PmuRfinA' in df.columns and 1:
            ax.plot(df['r_RepeatNumWithoutReset'], df['PmuRffbA'], 'RoyalBlue', lw=2)
            ax.set_ylabel('RFPAL PMU - RFFB', color='RoyalBlue', fontsize=16)
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'],df['pmPaOutDBm'], 'Maroon', lw=2)
            ax2.set_ylabel('Power Meter - PA OUT', color='Maroon', fontsize=16)
        # Plot Dressing
        sns.plt.title('Output Power: Power Meter vs RFPAL', fontsize=20)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()  
                         
        # IC Temp vs Case Temp
        fig = sns.plt.figure()
        figs.append(fig)
        ax = fig.add_subplot(1,1,1)
        
        # Super Impose Temperature and IC Temp
        if 'Temp' in df.columns and 'currentTemp_degrees' in df.columns and 1:
            ax.plot(df['r_RepeatNumWithoutReset'], df['Temp'], 'g', lw=2)
            ax.set_ylabel('IC Temp', color='g', fontsize=16)    
            ax2 = ax.twinx()
            ax2.plot(df['r_RepeatNumWithoutReset'], df['currentTemp_degrees'], 'Maroon', lw=2)
            ax2.set_ylabel('Current Case Temp', color='Maroon', fontsize=16)    
        # Plot Dressing
        sns.plt.title('IC Temp and Case Temp', fontsize=20)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout() 
                          
        return figs
        
    def mean_plot(self, resultVar, labels, df):
        
        if resultVar in self.benchmark_lut:
            base_line = self.benchmark_lut[resultVar]
        else:
            base_line = df.mean()
        
        df.plot(lw=4)
        sns.plt.plot(base_line * np.ones(df.index.size), lw=2, color='red')
         
        fig = sns.plt.gcf()
        
        sns.plt.title('Comparing Permutations', fontsize=12)
        sns.plt.ylabel('{y_axis} Means'.format(y_axis=resultVar), fontsize=16)
        sns.plt.xlabel('Run Number', fontsize=16)
        sns.plt.legend([name.values for name in labels], fontsize=10)
        sns.plt.tight_layout()
        
        return fig
    
    def violin_plot(self, resultVar, labels, var_data):
        
        if resultVar in self.benchmark_lut:
            base_line = self.benchmark_lut[resultVar]
        else:
            base_line = pd.DataFrame(var_data).mean().mean()
 
        fig = sns.plt.figure()
        fig.set_size_inches(10,10)
        sns.violinplot(var_data, names=labels, cut=0, rot=90)
        sns.plt.plot(base_line * np.ones(len(var_data)+2), 'red', lw=2)
        
        sns.plt.title('Parameter Variance After Convergence', fontsize=20)
        sns.plt.xlabel('Permutation Settings', fontsize=16)
        sns.plt.ylabel('{y_axis} (dBc)'.format(y_axis=resultVar), fontsize=16)
        locs, labels = sns.plt.xticks()
        sns.plt.setp(labels, rotation=90)
        sns.plt.tight_layout()
        
        return fig
        