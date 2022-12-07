""" Class that does all the G23-specific juggling of 
    verifit and estat data files

    Written by: Travis M. Moore
    Created: Dec 07, 2022
    Last edited: Dec 07, 2022
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
            all_data: a dataframe of verifit and estat
                data, including measured minus target
                differences
    """
    def __init__(self, verifit, estat, condition=None, form_factor=None):
        self.verifit = verifit
        self.estat = estat
        self.condition = condition
        self.form_factor = form_factor


    def get_data(self):
        """ Main function 
        """
        self._add_sub_column()
        self._filter_by_condition_and_form()
        self._match_subs()
        self._get_diffs()


    ##################################
    # Dataframe Reorganization Funcs #
    ##################################
    def _add_sub_column(self):
        """ Create subject column from file name
        """
        # Verifit
        self.verifit.insert(loc=0, column='sub', value= '')
        for ii in range(0,len(self.verifit)):
            self.verifit.loc[ii, 'sub'] = self.verifit.loc[ii, 'filename'].split('_')[0]

        # Estat
        self.estat.insert(loc=0, column='sub', value= '')
        for ii in range(0,len(self.estat)):
            self.estat.loc[ii, 'sub'] = self.estat.loc[ii, 'filename'].split('_')[0]


    def _filter_by_condition_and_form(self):
        #if (not self.condition) and (not self.form_factor):
        #    pass
        #else:
        # Only verifit files that have condition (BestFit/EndStudy)
        self.verifit = self.verifit[
            self.verifit['filename'].str.contains(self.condition)]

        # Only estat has form factor (could grab from verifit as well though?)
        self.estat = self.estat[
            self.estat['form_factor'].str.contains(self.form_factor)]


    def _match_subs(self):
        """ Identify common subjects across verifit and 
            estat dfs after filtering
        """
        vsubs = self.verifit['sub'].unique()
        esubs = self.estat['sub'].unique()
        common_subs = list(set(vsubs) & set(esubs))

        # Create new dataframe of common subjects with all data
        self.verifit = self.verifit[self.verifit['sub'].isin(common_subs)]
        self.estat = self.estat[self.estat['sub'].isin(common_subs)]
        self.verifit.sort_values(by=['sub', 'level'], inplace=True)
        self.estat.sort_values(by=['sub', 'level'], inplace=True)

        # Add estat values to verifit dataframe
        self.verifit['estat_target'] = list(self.estat['estat_target'])

        # Add estat form factors to verifit dataframe
        self.verifit['form_factor'] = list(self.estat['form_factor'])


    def _get_diffs(self):
        """ Find measured SPL - e-STAT target and add a difference column
        """
        self.all_data = self.verifit.copy()
        # Subtract
        self.all_data['measured-estat'] = self.all_data['measured'] - self.all_data['estat_target']
        
        # Assign column names to use with verifitmodel plotting function
        self.all_data.rename(columns={
            'filename': 'file',
            'sub': 'filename',
            'measured-target': 'measured-NAL',
            'measured-estat': 'measured-target'
            }, inplace=True
        )
