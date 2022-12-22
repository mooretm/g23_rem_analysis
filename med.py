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
#_verifit_path = '//starfile/Public/Temp/CAR Group/G23 Validation/Verifit'
_verifit_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/Verifit'
v = verifitmodel.VerifitModel(_verifit_path)

_path = 'C:/Users/MooTra/OneDrive - Starkey/Desktop/REM Target Match'
mx = medrxmodel.MedRXModel(_path)

# BESTFIT
spls = mx.bestfit.iloc[:, [0,1,2,7,8]].copy()
targets = mx.bestfit.iloc[:, [0,1,2,3,4]].copy()
spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
bestfit = spls.copy()

# ENDSTUDY
spls = mx.endstudy.iloc[:, [0,1,2,7,8]].copy()
targets = mx.endstudy.iloc[:, [0,1,2,3,4]].copy()
spls = mx._to_long_format(spls)
targets = mx._to_long_format(targets)
spls.rename(columns={'variable':'level', 'value':'measured'}, inplace=True)
spls['targets'] = targets['value']
spls['measured-target'] = spls['measured'] - spls['targets']
endstudy = spls.copy()

form_factors = bestfit['style'].unique()

for form in form_factors:
    v.diffs = bestfit[bestfit['style']==form]
    v.plot_diffs(title=f"Measured MedRX SPL minus MedRX Target ({form})")
