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
    Created: Nov. 17, 2022
    Last edited: Dec. 07, 2022
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import estatmodel
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
v = verifitmodel.VerifitModel(_verifit_path)
v.get_diffs()

# Estat data
_estat_path = r'\\starfile\Public\Temp\CAR Group\G23 Validation\Estat'
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
g = g23model.G23Model(v.diffs, e.estat_targets_long, 'BestFit', 'mRIC')
g.get_data()

# Assign verifitmodel public attribute to the e-STAT to SPL data
v.diffs = g.all_data
v.plot_diffs(title=f"Measured SPL minus e-STAT Target ({g.form_factor})")
