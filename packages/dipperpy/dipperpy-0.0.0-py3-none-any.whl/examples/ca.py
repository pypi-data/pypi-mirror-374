import matplotlib.pyplot as plt
import numpy as np
import scipy.special as sp
import math
import dipperpy as dp


wm = 3933.e-8
print(wm, dp.dipall.planck(wm,4000.), dp.dipall.planck(wm,7000.)/dp.dipall.planck(wm,4000))
wm = 8542.e-8
print(wm, dp.dipall.planck(wm,4000.), dp.dipall.planck(wm,7000.)/dp.dipall.planck(wm,4000))
       
