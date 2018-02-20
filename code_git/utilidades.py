import GPy
import matlab.engine
import numpy as np
import time
from os import getpid
import pandas as pd
import scipy.spatial as spatial
from scipy import stats
import multiprocessing
import math


# se cargan los datos de entrenamiento
train_data = pd.read_csv('../GP_Data/cy17_spc_assays_rl6_entry.csv')
train_cols = ['midx', 'midy', 'midz', 'cut']

test_data = pd.read_csv('../GP_Data/cy17_spc_assays_pvo_entry.csv')
test_cols = ['midx', 'midy', 'midz']

# se incializa el toolbox gpml de matlab
eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\Equipo\Desktop\gpml', nargout=0)
eng.startup(nargout=0)
# print('esto es jackass')
# eng.ejemplo_gp(nargout=0)  # prueba para ver que matlab funciona