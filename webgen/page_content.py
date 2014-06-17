'''
Created on Mar 22, 2014

@author: rpatel
'''

import webgen.text_to_html

class WebContent(object):
    'Add Data in sections here to make a page'
    
    def __init__(self):
        pass
    
class WebPage(object):
    'Base WebPage Class'
    
    def __init__(self, path, oContent):
        
        self.SAVE_PATH = path
        self.oContent = oContent
        
        self.load_defaults()
        
    def write_page(self):
        
        PAGE = open(self.content.PAGE_NAME, 'w')
        PAGE.write(self.content.html_raw)
        PAGE.close()
        
class Maxim(WebPage):
    '''
    '''
    
    def _load_settings(self):
        'Set Page Depdendencies'
        
        self.DEBUG = True
        
        self.PATH = r'../WebReports/webTemplate/templates/Maxim/'
        self.TEMPLATE = 'standard.html'
        self.FILES = self.PATH + 'standard'
        
        self.frame = {
                      'TITLE': 'FFA',
                      'NAME': 'Doherty PA and Antares',
                      'MAIN_BODY': '',
                      'SBAR1_TITLE': 'Main Menu',
                      'SBAR1_BODY': 'TOC - Fill in with page links',
                      'SBAR2_TITLE': 'WebReport',
                      'SBAR2_BODY': 'Results taken on CHAR Bench',
                      'HOME': 'overview.html',
                      'BLOG': 'overview.html',
                      'SERVICES': 'overview.html',
                      'CONTACT': 'overview.html',
                      'RESOURCES': 'overview.html',
                      'PARTNERS': 'overview.html',
                      'ABOUT': 'overview.html',
                      }