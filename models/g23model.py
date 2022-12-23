""" Class that does all the G23-specific juggling of 
    verifit and estat data files

    Written by: Travis M. Moore
    Created: Dec 07, 2022
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd

class G23Model:
    """ Class that does all the G23-specific juggling of 
        verifit and estat data files.

        Returns:
            final_data: a dataframe of verifit and estat
                data, including measured minus target
                differences
    """
    def __init__(self, verifit, estat, form_key, session):
        self.verifit = verifit.copy()
        self.estat = estat.copy()
        self.form_key = form_key
        self.session = session


    def get_data(self):
        """ Main function 
        """
        self._add_sub_and_form_cols()
        self._filter_by_session()
        self._match_subs()
        self._get_diffs()


    ##################################
    # Dataframe Reorganization Funcs #
    ##################################
    def _add_sub_and_form_cols(self):
        """ Create subject column from file name
        """
        # Verifit
        self.verifit.insert(loc=0, column='sub', value= '')
        self.verifit.insert(loc=1, column='form_factor', value='')
        self.verifit.reset_index(inplace=True, drop=True)
        for ii in range(0,len(self.verifit)):
            # Add subject ID
            sub = self.verifit.iloc[ii, 2].split('_')[0]
            self.verifit.iloc[ii, 0] = sub
            self.verifit.iloc[ii, 1] = self.form_key[sub]['Form_Factor']
        self.verifit.sort_values(by='sub')

        # Estat
        self.estat.insert(loc=0, column='sub', value= '')
        self.estat.reset_index(inplace=True, drop=True)
        for ii in range(0,len(self.estat)):
            self.estat.loc[ii, 'sub'] = self.estat.loc[ii, 'filename'].split('_')[0]
        self.estat.sort_values(by='sub')
    

    def _filter_by_session(self):
        # Only verifit files contain the session (BestFit/EndStudy)
        self.verifit = self.verifit[
            self.verifit['filename'].str.contains(self.session)]


    def _match_subs(self):
        """ Identify common subjects across verifit and 
            estat dfs after filtering
        """
        vsubs = self.verifit['sub'].unique()
        esubs = self.estat['sub'].unique()
        common_subs = list(set(vsubs) & set(esubs))

        # Create new dataframe of common subjects with all data
        self.verifit = self.verifit[self.verifit['sub'].isin(common_subs)].copy()
        self.estat = self.estat[self.estat['sub'].isin(common_subs)].copy()
        self.verifit.sort_values(by=['sub', 'level', 'form_factor'], inplace=True)
        self.estat.sort_values(by=['sub', 'level', 'form_factor'], inplace=True)


    def _get_diffs(self):
        """ Find measured SPL - e-STAT target and add a difference column
        """
        # Add estat values to verifit dataframe
        self.verifit['estat_target'] = list(self.estat['estat_target'])

        self.final_data = self.verifit.copy()
        # Subtract
        self.final_data['measured-estat'] = self.final_data['measured'] - self.final_data['estat_target']
        
        # Assign column names to use with verifitmodel plotting function
        self.final_data.rename(columns={
            'filename': 'file',
            'sub': 'filename',
            'measured-target': 'measured-NAL',
            'measured-estat': 'measured-target'
            }, inplace=True
        )
