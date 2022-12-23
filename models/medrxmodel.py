""" Class to hold and organzie MedRX data pulled from tech toolbox

    Written by: Travis M. Moore
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import filedialog

# Import system packages
import os
from pathlib import Path

# Import data science packages
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


#########
# BEGIN #
#########
class MedRXModel:
    def __init__(self, path=None):
        """ Import all data files as single dataframe
        """
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(f"Path of selected folder: {path}")

        # Get list of file paths
        files = Path(path).glob('*.csv')
        self.files = list(files)

        # Create list of frequencies for indexing
        #self.freqs = [200, 500, 800, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        #self.freqs = [str(val) for val in self.freqs]

        self._organize_data()


    def _organize_data(self):
        df_list = []
        for file in self.files:
            df = pd.read_csv(file)
            df.insert(loc=0, column='filename', value=os.path.basename(file)[:-4])
            # Set frequencies as index
            #df = df.set_index(['Frequency'])
            # Subset by desired frequencies
            #df = df.loc[self.freqs, :]
            df_list.append(df)

        self.data = pd.concat(df_list)
        self.data[['sub', 'brand', 'side', 'style']] = self.data['filename'].str.split('_', expand=True)
        self.data.drop(['filename', 'brand', 'Real ear unaided gain', 'Model Error'], axis=1, inplace=True)
        
        # Rename columns
        self.data.columns = ['freq', 'target_2', 'p_2', 'p_1', 'p_3', 'end_2', 'end_1', 'end_3', 'filename', 'side', 'style']
        
        #Create two dfs: one for 'bestfit' and one for 'endstudy'
        # BESTFIT
        self.bestfit = self.data[['filename', 'style', 'freq', 'side', 'target_2', 'p_1', 'p_2', 'p_3']]
        self.bestfit = pd.pivot(self.bestfit, index=['filename', 'style', 'freq'], columns='side', values=['target_2', 'p_1', 'p_2', 'p_3'])
        self.bestfit.columns = ['_'.join(col) for col in self.bestfit.columns.values]
        self.bestfit.columns = ['target_L2', 'target_R2', 'L1', 'R1', 'L2', 'R2', 'L3', 'R3']
        self.bestfit['L2-Target'] = self.bestfit['L2'] - self.bestfit['target_L2']
        self.bestfit['R2-Target'] = self.bestfit['R2'] - self.bestfit['target_R2']
        self.bestfit.reset_index(inplace=True)
        self.bestfit.to_csv('./G23 REM Data/medrx_bestfit.csv', index=False)
        
        # ENDSTUDY
        self.endstudy = self.data[['filename', 'style', 'freq', 'side', 'target_2', 'end_1', 'end_2', 'end_3']]
        self.endstudy = pd.pivot(self.endstudy, index=['filename', 'style', 'freq'], columns='side', values=['target_2', 'end_1', 'end_2', 'end_3'])
        self.endstudy.columns = ['_'.join(col) for col in self.endstudy.columns.values]
        self.endstudy.columns = ['target_L2', 'target_R2', 'L1', 'R1', 'L2', 'R2', 'L3', 'R3']
        self.endstudy['L2-Target'] = self.endstudy['L2'] - self.endstudy['target_L2']
        self.endstudy['R2-Target'] = self.endstudy['R2'] - self.endstudy['target_R2']
        self.endstudy.reset_index(inplace=True)
        self.endstudy.to_csv('./G23 REM Data/medrx_endstudy.csv', index=False)


    def _to_long_format(self, df):
        """ Convert both dfs to long format
        """
        x = df.copy()
        long = pd.melt(x, id_vars=['filename', 'style', 'freq'], value_vars=list(x[3:]))
        # Convert values to floats and round to one decimal place
        long['value'] = np.round(long['value'].astype(float), 1)
        return long
