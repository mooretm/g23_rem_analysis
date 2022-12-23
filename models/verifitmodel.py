""" Verifit data class

    Extract and organze Verifit session .xml files.

    Extracts:
        1. Aided SII (NOTE: unaided SII not available from session file!)
        2. REM measured SPL values
        3. REM target SPL values

    Written by: Travis M. Moore
    Created: Nov. 17, 2022
    Last edited: Dec. 23, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import system packages
import os
from pathlib import Path

# Import GUI packages
import tkinter as tk
from tkinter import filedialog


class VerifitModel:
    def __init__(self, path=None, test_type=None, num_curves=None, freqs=None):
        """ Parse verifit session file data.
        
            Parameters:
                path: Path to directory of session files
                test_type: Either 'on-ear' or 'test-box'
                num_curves: The number of curves run (1 - 4)
                freqs: The desired freqs, if different from audiometric
        """
        # Get list of file paths
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(path)
        # Get list of file paths
        files = Path(path).glob('*.xml')
        self.files = list(files)

        # Type of test: on-ear or testbox
        if test_type:
            if test_type == 'on-ear':
                self.test_type = 'rear'
            elif test_type == 'test-box':
                self.test_type = 'sar'
        else:
            self.test_type = 'rear'

        # Number of curves run
        if num_curves:
            self.num_curves = num_curves
        else:
            self.num_curves = 3

        # Desired frequencies for index
        if freqs:
            self.desired_freqs = freqs
        else:
            self.desired_freqs = [250, 500, 750, 1000, 1500, 2000, 
                3000, 4000, 6000, 8000]


        # Automatically import all data upon instantiation
        #self.get_all()
            

    def get_all(self):
        print('')
        print('-' * 50)
        print("Verifit Data")
        print('-' * 50)
        self.get_aided_sii()
        self.get_measured_spls()
        self.get_target_spls()
        print('-' * 50)
        print('')


    def write_to_csv(self):
        #self.all_data.sort_values(by='filename')
        self.aided_sii.to_csv('aided_sii.csv', index=False)
        self.target_spls.to_csv('target_spls.csv', index=False)
        self.measured_spls.to_csv('measured_spls.csv', index=False)
        print("verifitmodel: .csv files created successfully!\n")


    def _get_root(self, file):
        # Get XML tree structure and root
        tree = ET.parse(file)
        self.root = tree.getroot()
        
        # Get tag with 12th-octave frequency list
        freqs = self.root.find("./test[@name='frequencies']/data[@name='12ths']").text
        freqs = freqs.split()
        self.twelfth_oct_freqs = [int(float(freq)) for freq in freqs]

        # Get tag with audiometric frequency list
        freqs = self.root.find("./test[@name='frequencies']/data[@name='audiometric']").text
        freqs = freqs.split()
        audiometric_freqs = [int(float(freq)) for freq in freqs]
        self.audiometric_freqs = audiometric_freqs[:-2]

        # Get file name
        filename = os.path.basename(file)
        self.filename = filename[:-4]


    ####################
    # AIDED SII VALUES #
    ####################
    # NOTE: Verifit session file does not include unaided SII!
    def get_aided_sii(self):
        print("verifitmodel: Fetching aided SII data...")
        sii_list = []
        sii_dict = {}

        for file in self.files:
            self._get_root(file)

            try:
                for num in range(1, self.num_curves+1):
                    # Left
                    sii_dict['sii_L' + str(num)] = self.root.find(f"./test[@side='left']/data[@internal='map_{self.test_type}_sii{str(num)}']").text
                    #sii_dict['sii_L1'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii1']").text)
                    #sii_dict['sii_L2'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii2']").text)
                    #sii_dict['sii_L3'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii3']").text)
                    #sii_dict['sii_L4'] = float(self.root.find("./test[@side='left']/data[@internal='map_rear_sii4']").text)
                    # Right
                    sii_dict['sii_L' + str(num)] = self.root.find(f"./test[@side='right']/data[@internal='map_{self.test_type}_sii{str(num)}']").text
                    #sii_dict['sii_R1'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii1']").text)
                    #sii_dict['sii_R2'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii2']").text)
                    #sii_dict['sii_R3'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii3']").text)
                    #sii_dict['sii_R4'] = float(self.root.find("./test[@side='right']/data[@internal='map_rear_sii4']").text)
            except AttributeError as e:
                print(e)
                print(f"\nverifitmodel: {self.filename} is missing SII data!\n")
                #exit()

            sii_list.append(pd.DataFrame(sii_dict, index=[str(self.filename)]))

        aided_sii = pd.concat(sii_list)
        aided_sii.reset_index(inplace=True)
        self.aided_sii = aided_sii.rename(columns={'index':'filename'})

        print("verifitmodel: Completed!\n")


    #######################
    # MEASURED SPL VALUES #
    #######################
    def get_measured_spls(self):
        print("verifitmodel: Fetching measured SPL data...")
        spls_list = []

        for file in self.files:
            self._get_root(file)

            spls_dict = {}

            # Measured SPL REM values
            try:
                for num in range(1, self.num_curves+1):
                    # Left MEASURED spls
                    spls_dict['spl_L' + str(num)] = self.root.find(f"./test[@side='left']/data[@internal='map_{self.test_type}spl{str(num)}']").text
                    #spls_dict['spl_L2'] = self.root.find("./test[@side='left']/data[@internal='map_rearspl2']").text
                    #spls_dict['spl_L3'] = self.root.find("./test[@side='left']/data[@internal='map_rearspl3']").text
                    
                    # Right MEASURED spls
                    spls_dict['spl_R' + str(num)] = self.root.find(f"./test[@side='right']/data[@internal='map_{self.test_type}spl{str(num)}']").text
                    #spls_dict['spl_R2'] = self.root.find("./test[@side='right']/data[@internal='map_rearspl2']").text
                    #spls_dict['spl_R3'] = self.root.find("./test[@side='right']/data[@internal='map_rearspl3']").text
            except AttributeError:
                print(f"\nverifitmodel: {self.filename} is missing MEASURED REM data!\n")
                #exit()

            # Split numbers into list
            for key in spls_dict:
                spls_dict[key] = spls_dict[key].split()
                spls_dict[key] = [float(x) for x in spls_dict[key]]

            df = pd.DataFrame(spls_dict, index=self.twelfth_oct_freqs)
            # Get only specified frequencies
            df = df.loc[self.desired_freqs]
            df.reset_index(inplace=True)
            df = df.rename(columns={'index':'freq'})
            df.insert(loc=0, column='filename', value=self.filename)

            spls_list.append(df)
        
        self.measured_spls = pd.concat(spls_list)
        
        print("verifitmodel: Completed!\n")


    #####################
    # TARGET SPL VALUES #
    #####################
    def get_target_spls(self):
        print("verifitmodel: Fetching target SPL data...")
        target_list = []

        for file in self.files:
            self._get_root(file)
            
            target_dict = {}

            # TARGET spl values
            try:
                for num in range(1, self.num_curves+1):
                    # Left TARGET spls
                    target_dict['target_L' + str(num)] = self.root.find(f"./test[@side='left']/data[@internal='map_{self.test_type}_targetspl{str(num)}']").text
                    #target_dict['target_L2'] = self.root.find("./test[@side='left']/data[@internal='map_rear_targetspl2']").text
                    #target_dict['target_L3'] = self.root.find("./test[@side='left']/data[@internal='map_rear_targetspl3']").text
                    # Right TARGET spls
                    target_dict['target_R' + str(num)] = self.root.find(f"./test[@side='right']/data[@internal='map_{self.test_type}_targetspl{str(num)}']").text
                    #target_dict['target_R2'] = self.root.find("./test[@side='right']/data[@internal='map_rear_targetspl2']").text
                    #target_dict['target_R3'] = self.root.find("./test[@side='right']/data[@internal='map_rear_targetspl3']").text
            except AttributeError:
                print(f"\nverifitmodel: {self.filename} is missing TARGET REM data!\n")
                #exit()

            # Split numbers into list
            for key in target_dict:
                target_dict[key] = target_dict[key].split()
                # There aren't targets above 8 kHz, just an underscore
                target_dict[key] = [x for x in target_dict[key] if x != '_']
                target_dict[key] = [float(x) for x in target_dict[key]]

            # Targets are only provided at audiometric frequencies,
            # not the full 12th octave list. Here we are just labeling
            # the frequencies, not selecting like with measured SPLs
            df = pd.DataFrame(target_dict, index=self.audiometric_freqs)
            df.reset_index(inplace=True)
            df = df.rename(columns={'index':'freq'})
            df.insert(loc=0, column='filename', value = self.filename)
            
            target_list.append(df)
        
        self.target_spls = pd.concat(target_list)

        print("verifitmodel: Completed!\n")


    ###############################
    # Data Organization Functions #
    ###############################
    def _to_long_format(self):
        """ Create a long format dataframe for each measure
        """
        try:
            # Aided SII
            self.aided_sii_long = pd.melt(
                self.aided_sii,
                id_vars=['filename'],
                value_vars=list(self.aided_sii.columns[1:])
            )

            self.aided_sii_long.rename(columns={'variable': 'unit'}, inplace=True)
            self.aided_sii_long[['unit', 'level']] = self.aided_sii_long['unit'].str.split('_', expand=True)
            column_to_move = self.aided_sii_long.pop('value')
            self.aided_sii_long.insert(len(self.aided_sii_long.columns), 'value', column_to_move)
            self.sii_flag = 1
        except ValueError as e:
            #print(e)
            print("verifitmodel: No aided SII data found\n")
            self.sii_flag = 0

        # Measured
        self.measured_spls_long = pd.melt(
            self.measured_spls,
            id_vars=['filename', 'freq'], 
            value_vars=list(self.measured_spls.columns[1:])
        )
        try:
            self.measured_spls_long.rename(columns={'variable': 'unit'}, inplace=True)
            self.measured_spls_long[['unit', 'level']] = self.measured_spls_long['unit'].str.split('_', expand=True)
            column_to_move = self.measured_spls_long.pop('value')
            self.measured_spls_long.insert(len(self.measured_spls_long.columns), 'value', column_to_move)
            self.measured_flag = 1
        except ValueError as e:
            #print(e)
            print("verifitmodel: No measured SPL data found\n")
            self.measured_flag = 0

        # Targets
        self.target_spls_long = pd.melt(
            self.target_spls,
            id_vars=['filename', 'freq'], 
            value_vars=list(self.target_spls.columns[1:])
        )
        try:
            self.target_spls_long.rename(columns={'variable': 'unit'}, inplace=True)
            self.target_spls_long[['unit', 'level']] = self.target_spls_long['unit'].str.split('_', expand=True)
            column_to_move = self.target_spls_long.pop('value')
            self.target_spls_long.insert(len(self.target_spls_long.columns), 'value', column_to_move)
            self.target_flag = 1
        except ValueError as e:
            #print(e)
            print("verifitmodel: No target SPL data found\n")
            self.target_flag = 0
    

    def get_diffs(self):
        """ Create a new dataframe with target and measured spls as 
            columns. Include a columns of differences.
        """
        self._to_long_format()

        # Check for target AND measured values
        if (self.measured_spls_long.shape[0] == 0) \
            or (self.target_spls_long.shape[0] == 0):
            print("verifitmodel: Calculating the difference requires " +
                "both target and measured data! Aborting!\n")
            exit()

        # Create new dataframe of diffs
        y = pd.DataFrame(self.measured_spls_long[['filename', 'freq', 'unit', 'level']])
        y['targets'] = self.target_spls_long[['value']]
        y['measured'] = self.measured_spls_long[['value']]
        y['measured-target'] = y['measured'] - y['targets']
        self.diffs = y.copy()


    ######################
    # Plotting Functions #
    ######################
    def _set_up_plot(self, **kwargs):
        """ Create empty plotting space for measured-target diffs
        """
        # Check for dict of custom labels
        # Titles
        titles_default = [
            'Soft (50 dB SPL):',
            'Average (60 dB SPL):',
            'Loud (80 dB SPL):',
            'MPO:'
        ]
        titles = kwargs.get('titles', titles_default)

        # Y labels
        ylabs_default = list(np.repeat('measured-target',3))
        ylabs_default.append('measured')
        ylabs = kwargs.get('ylabs', ylabs_default)

        if (len(titles) < self.num_curves) or (len(ylabs) < self.num_curves):
            print("verifitmodel: Insufficient number of labels! Aborting!\n")
            exit()

        # Define sides
        sides = [' Left', ' Right']

        # Set style
        plt.style.use('seaborn-v0_8')

        # Create figure and axes
        self.fig, self.axs = plt.subplots(nrows=self.num_curves, ncols=2)

        # Create ticks and labels
        kHz = [x/1000 for x in self.desired_freqs]
        for ii in [0, 2, 4, 6, 8]:
            kHz[ii] = ""

        # Create each empty plot
        for col, side in enumerate(sides):
            for row in range(0, self.num_curves):
                if self.num_curves > 1:
                    self.axs[row, col].set(
                        title=titles[row] + side,
                        ylabel=ylabs[row],
                        xticks=self.desired_freqs,
                        xticklabels=kHz
                    )
                elif self.num_curves == 1:
                    self.axs[col].set(
                        title=titles[row] + side,
                        ylabel=ylabs[row],
                        xticks=self.desired_freqs,
                        xticklabels=kHz
                        )

        # Set x label for bottom plots
        if self.num_curves > 1:
            for ii in range(0,2):
                if self.num_curves > 1:
                    self.axs[self.num_curves-1, ii].set_xlabel('Frequency (kHz)')
                elif self.num_curves == 1:
                    self.axs[ii].set_xlabel('Frequency (kHz)')


    def plot_ind_measured_spls(self, title=None, **kwargs):
        labels = kwargs
        self._to_long_format()
        self._set_up_plot(**labels)

        if not title:
            self.fig.suptitle('Measured SPLs')
        else:
            self.fig.suptitle(title)

        # Plot the individual data
        for file in self.measured_spls_long['filename'].unique():
            for ii in range(1, self.num_curves+1):
                temp = self.measured_spls_long[(self.measured_spls_long['filename']==file) & (self.measured_spls_long['level']=='L' + str(ii))]
                print(temp)
                self.axs[ii-1,0].plot(temp['freq'], temp['value'])
                self.axs[ii-1,0].axhline(y=0, color='k')
                self.axs[ii-1,0].set_ylim(
                    np.min(self.measured_spls_long['value']+(-5)),
                    np.max(self.measured_spls_long['value']+5)
                ) 

                temp = self.measured_spls_long[(self.measured_spls_long['filename']==file) & (self.measured_spls_long['level']=='R' + str(ii))]
                self.axs[ii-1,1].plot(temp['freq'], temp['value'])
                self.axs[ii-1,1].axhline(y=0, color='k')
                self.axs[ii-1,1].set_ylim(
                    np.min(self.measured_spls_long['value']+(-5)),
                    np.max(self.measured_spls_long['value']+5)
                )
            
        # Calculate and plot grand average curve for each level
        # Get values at all freqs for a single level
        for ii in range(1, self.num_curves+1):
                # Filter diffs by level
                temp = self.measured_spls_long[self.measured_spls_long['level']=='L' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['value'].apply(np.mean)
                self.axs[ii-1,0].plot(temp['freq'].unique(), vals_by_freq, 'ko')

                temp = self.measured_spls_long[self.measured_spls_long['level']=='R' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['value'].apply(np.mean)
                self.axs[ii-1,1].plot(temp['freq'].unique(), vals_by_freq, 'ko')

        plt.show()


    def plot_diffs(self, data, title=None, show=None, save=None, **kwargs):
        """ Plot the individual differences between measured and 
            target SPLs
        """
        labels = kwargs
        self._set_up_plot(**labels)
        if not title:
            self.fig.suptitle('Measured SPLs - NAL-NL2 Target SPLs')
        else:
            self.fig.suptitle(title)

        # Plot the individual data
        for file in data['filename'].unique():
            for ii in range(1,self.num_curves+1):
                if self.num_curves > 1:
                    temp = data[(data['filename']==file) & (data['level']=='L' + str(ii))]
                    self.axs[ii-1,0].plot(temp['freq'].unique(), temp['measured-target'])
                    self.axs[ii-1,0].axhline(y=0, color='k')
                    self.axs[ii-1,0].set_ylim(
                        np.min(data['measured-target']+(-5)),
                        np.max(data['measured-target']+5)
                    ) 

                    temp = data[(data['filename']==file) & (data['level']=='R' + str(ii))]
                    self.axs[ii-1,1].plot(temp['freq'].unique(), temp['measured-target'])
                    self.axs[ii-1,1].axhline(y=0, color='k')
                    self.axs[ii-1,1].set_ylim(
                        np.min(data['measured-target']+(-5)),
                        np.max(data['measured-target']+5)
                    )


                elif self.num_curves == 1:
                    temp = data[(data['filename']==file) & (data['level']=='L' + str(ii))]
                    self.axs[0].plot(temp['freq'], temp['measured-target'])
                    self.axs[0].axhline(y=0, color='k')
                    self.axs[0].set_ylim(
                        np.min(data['measured-target']+(-5)),
                        np.max(data['measured-target']+5)
                    ) 

                    temp = data[(data['filename']==file) & (data['level']=='R' + str(ii))]
                    self.axs[1].plot(temp['freq'].unique(), temp['measured-target'])
                    self.axs[1].axhline(y=0, color='k')
                    self.axs[1].set_ylim(
                        np.min(data['measured-target']+(-5)),
                        np.max(data['measured-target']+5)
                    )
            
        # Calculate and plot grand average curve for each level
        # Get values at all freqs for a single level
        for ii in range(1,self.num_curves+1):
            # Filter diffs by level
            if self.num_curves > 1:
                temp = data[data['level']=='L' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[ii-1,0].plot(temp['freq'].unique(), vals_by_freq, 'ko')

                temp = data[data['level']=='R' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[ii-1,1].plot(temp['freq'].unique(), vals_by_freq, 'ko')

            elif self.num_curves == 1:
                temp = data[data['level']=='L' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[0].plot(temp['freq'].unique(), vals_by_freq, 'ko')

                temp = data[data['level']=='R' + str(ii)]
                vals_by_freq = temp.groupby(['freq'])['measured-target'].mean()
                self.axs[1].plot(temp['freq'].unique(), vals_by_freq, 'ko')

        if save:
            plt.savefig(labels['save_title'])
        
        if show:
            plt.show()
