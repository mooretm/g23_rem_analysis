""" Control script for pulling Verifit and e-STAT data.

    Conditions to test:
        Official:
        1. e-STAT targets vs. BestFit spls
        2. e-STAT targets vs. EndStudy spls
        3. BestFit spls vs. EndStudy spls

        Interesting:
        4. NAL-NL2 targets vs. BestFit spls
        5. NAL-NL2 targets vs. EndStudy spls

    Written by: Travis M. Moore
    Created: Nov 17, 2022
    Last edited: Dec 23, 2022
"""

###########
# Imports #
###########
# Import plotting packages
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

# Import data science packages
import pandas as pd

# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import g23model


##########################
# Fetch Data from Models #
##########################
# Verfit data
#_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
v = verifitmodel.VerifitModel(path=_verifit_path, test_type='on-ear', num_curves=3)
v.get_all()
v.get_diffs()

# Estat data
#_estat_path = r'\\starfile\Public\Temp\CAR Group\G23 Validation\Estat'
_estat_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Estat'
e = estatmodel.Estatmodel(_estat_path)
e._to_long_format()

# Form factor by subject key
x = pd.read_csv(_verifit_path + '/form_key.csv')
form_key = x.set_index('PID').transpose().to_dict()

# Provide some feedback to console 
print(f"Length of Verifit dataframe: {len(v.diffs)}")
print(f"Length of Verifit BestFit: {len(v.diffs[v.diffs['filename'].str.contains('BestFit')])}")
print(f"Length of Verifit EndStudy: {len(v.diffs[v.diffs['filename'].str.contains('EndStudy')])}")
print(f"Length of eSTAT dataframe: {len(e.estat_targets_long)}")


#####################
# Plot Verifit Data #
#####################
# Plot each form factor on separate plot
# data, title=None, show=None, save=None, **kwargs

# v_best = v.diffs[v.diffs['filename']]
# labels = ['bestfit', 'endstudy']

# for ii, df in enumerate(dfs):
#     form_factors = df['style'].unique()
#     for form in form_factors:
#         plot_labels['save_title'] = f"./G23 REM Data/MedRX_{labels[ii]}_{form}.png"
#         vals = df[df['style']==form]
#         v.plot_diffs(
#             data=vals, 
#             title=f"Measured eSTAT minus NAL-NL2 ({form}: {labels[ii]})",
#             show=1,
#             save=None,
#         )


######################
# Specify Conditions #
######################
bestfit = g23model.G23Model(v.diffs, e.estat_targets_long, form_key, "BestFit")
bestfit.get_data()
bestfit.final_data.to_csv('./G23 REM Data/estat_bestfit.csv', index=False)

endstudy = g23model.G23Model(v.diffs, e.estat_targets_long, form_key, "EndStudy")
endstudy.get_data()
endstudy.final_data.to_csv('./G23 REM Data/estat_endstudy.csv', index=False)

plot_labels = {'save_title': ''}

dfs = [bestfit, endstudy]
labels = ['BestFit', 'EndStudy']
forms = ['RIC', 'MRIC', 'ITE', 'ITC', 'CIC', 'IIC']
for ii, df in enumerate(dfs):
    for form in forms:
        temp = df.final_data[df.final_data['form_factor']==form]
        plot_labels['save_title'] = f"./G23 REM Data/eSTAT_{labels[ii]}_{form}.png"
        v.plot_diffs(
            data=temp, 
            title=f"Measured SPL minus e-STAT Target ({form}: {labels[ii]})",
            show=None,
            save=1,
            **plot_labels
            )
