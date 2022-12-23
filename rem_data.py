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
    Last edited: Dec 08, 2022
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import medrxmodel
from models import g23model

# Import plotting modules
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})


##########################
# Fetch Data from Models #
##########################
# Verfit data
_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
#v = verifitmodel.VerifitModel(_verifit_path)
v = verifitmodel.VerifitModel(path=_verifit_path, test_type='on-ear', num_curves=1)
v.get_all()
v.get_diffs()
v.plot_diffs(data=v.diffs)

# Estat data
_estat_path = r'\\starfile\Public\Temp\CAR Group\G23 Validation\Estat'
_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Estat'
e = estatmodel.Estatmodel(_estat_path)
e._to_long_format()


######################
# Specify Conditions #
######################
# NOTE: Need to add a way to produce all plots at once, rather than 
# waiting for all the data to load each time. 

# NOTE: Need to make a plot for the average difference across all 
# form factors.

#forms = ['RIC', 'mRIC', 'ITE', 'IIC', 'CIC', 'IIC']
#for ii in forms:
g = g23model.G23Model(v.diffs, e.estat_targets_long, 'BestFit', 'ITE')
g.get_data()

# Assign verifitmodel public attribute to the e-STAT to SPL data
#v.diffs = g.all_data
v.plot_diffs(data=g.all_data, title=f"Measured SPL minus e-STAT Target ({g.form_factor})")


#print(g.all_data[g.all_data['filename']=='P0700'][['filename', 'freq', 'level', 'estat_target']])
