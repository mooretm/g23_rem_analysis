""" Controller script for analyzing REM data from MedRX

    Written by: Travis M. Moore
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import data science packages
import numpy as np

# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import medrxmodel
from models import g23model


##########################
# Fetch Data from Models #
##########################
""" Instantiate class objects and load data
"""
# Verfit data
_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
#_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
v = verifitmodel.VerifitModel(path=_verifit_path, test_type='on-ear', num_curves=1, freqs=None)

# MedRX Data
_medrx_path = '//starfile/Dept/Research and Development/HRT/Users/CR Studies/G23 Validation/REM Target Match'
#_medrx_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/REM Target Match'
mx = medrxmodel.MedRXModel(_medrx_path)


#################
# Organize Data #
#################
""" Shape data to work with verifitmodel plotting
    functions
"""
# BESTFIT
spls = mx.bestfit.iloc[:, [0,1,2,7,8]].copy()
spls.rename(columns={'L2':'L1', 'R2':'R1'}, inplace=True)
targets = mx.bestfit.iloc[:, [0,1,2,3,4]].copy()
#targets.rename(columns={'target_L2':'L1', 'target_R2':'R1'}, inplace=True)

spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
spls['session'] = 'bestfit'
bestfit = spls.copy()

# ENDSTUDY
spls = mx.endstudy.iloc[:, [0,1,2,7,8]].copy()
spls.rename(columns={'L2':'L1', 'R2':'R1'}, inplace=True)
targets = mx.endstudy.iloc[:, [0,1,2,3,4]].copy()
spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
spls['session'] = 'endstudy'
endstudy = spls.copy()


#############
# Plot Data #
#############
""" Plot using verifitmodel funcs
"""
# Create labels to pass to plot
plot_labels = {
    'titles': ['Average (60 dB SPL):'],
    'ylabs': ['Deviation from Target'],
}

# Plot all form factors on separate plots
dfs = [bestfit, endstudy]
labels = ['bestfit', 'endstudy']

for ii, df in enumerate(dfs):
    form_factors = df['style'].unique()
    for form in form_factors:
        plot_labels['save_title'] = f"./G23 REM Data/MedRX_{labels[ii]}_{form}.png"
        vals = df[df['style']==form]
        v.plot_diffs(
            data=vals, 
            title=f"MedRX: Measured minus Target ({form}: {labels[ii]})",
            show=1,
            save=1,
            **plot_labels
        )
