import GPy
import numpy as np
import time
from os import getpid
import pandas as pd
import scipy.spatial as spatial

import multiprocessing
import math

# se cargan los datos de entrenamiento
train_data = pd.read_csv('../GP_Data/cy17_spc_assays_rl6_entry.csv')

test_data = pd.read_csv('../GP_Data/cy17_spc_assays_pvo_entry_ug.csv')
test_cols = ['midx', 'midy', 'midz', 'ugcut']

# solo se entrena con los datos que tienen ug
train_data = train_data.loc[train_data['ugcut'] >= 10]
test_data = test_data.loc[test_data['ugcut'] >= 10]

ugs = [10, 20, 30, 40, 50, 51, 60, 61, 70, 71, 80]


# se definen los estilos de los graficos
# jtplot.style(theme='onedork',figsize = (16.5,12))


def get_holeids():
    df_holeid = test_data['dhid']
    seen = set()
    HOLEID = []
    for item in df_holeid:
        if item not in seen:
            seen.add(item)
            HOLEID.append(item)
    return HOLEID


def get_test_points_holeid(idhole):
    return test_data.loc[test_data['dhid'] == idhole][test_cols].as_matrix()


def get_pozo_holeid(idhole, cols_names=None):
    if cols_names is None:
        cols_names = ['midx', 'midy', 'midz', 'minty', 'cut', 'f1']

    hole = test_data.loc[test_data['dhid'] == idhole][cols_names].as_matrix()
    return hole


def get_trainingSet_by_point(test_point, distancia):
    X_train_df = train_data[['dhid', 'midx', 'midy', 'midz', 'ugcut']]  # Ahora se agrega la variable categorica ug
    y_df = train_data[['dhid', 'cut']]
    X_train = X_train_df[['midx', 'midy', 'midz']].as_matrix()
    train_tree = spatial.cKDTree(X_train)
    idx = train_tree.query_ball_point(list(test_point)[:3], distancia)  # 3:solo variables espaciales para busqueda
    return X_train_df.iloc[idx, :], y_df.iloc[idx, :]


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def estimation_by_point_mp(IDHOLEs, out_q, model, ker, distancia, lik=GPy.likelihoods.Gaussian(),
                           inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    # def estimation_by_point_mp(IDHOLEs, model, ker, distancia, lik=GPy.likelihoods.Gaussian(),
    #                            inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    n = len(IDHOLEs)
    dicc_preds = {}
    for idx, idhole in enumerate(IDHOLEs):
        y_preds = list()
        test_points = get_test_points_holeid(idhole)
        for test_point in test_points:
            X_df, y_df = get_trainingSet_by_point(test_point[:3], distancia)  # :3 para buscar sin considerar ug
            if X_df.shape[0] < 10:
                y_preds.extend(list(np.array([-99])))
                continue

            X = X_df[['midx', 'midy', 'midz']].as_matrix()
            y = y_df[['cut']].as_matrix()

            X_std = (X - X.mean()) / X.std()
            y_std = (y - y.mean()) / y.std()

            test_point_std = (test_point[:3] - X.mean()) / X.std()

            # one hot encoder para X
            ug_samples = X_df[['ugcut']].as_matrix()
            X_zeros = np.zeros(shape=(X_std.shape[0], 14))
            X_zeros[:, :3] = X_std[:, :3]
            for pos, row in enumerate(ug_samples):
                ug = row[0]
                index = ugs.index(ug)
                X_zeros[pos, 2 + index + 1] = 1

            X_std = X_zeros

            # one hot encoder para test
            ug_test = test_point[3]
            test_point_zeros = np.zeros(shape=(1, 14))
            test_point_zeros[0, :3] = test_point_std[:3]
            test_point_zeros[0, 2 + ugs.index(ug_test) + 1] = 1

            test_point_std = test_point_zeros

            if model == 'sgpr':
                modelo = GPy.core.GP(X_std, y_std, kernel=ker, likelihood=lik, inference_method=inf)

            else:
                modelo = GPy.models.GPRegression(X, y, ker)
            y_predicc = -99
            try:
                modelo.optimize(messages=False, max_f_eval=1000)
                y_predicc, _ = modelo.predict(test_point_std)

            except GPy.util.linalg.linalg.LinAlgError as err:
                if 'not positive definite' in err.message:
                    print('not positive definite, even with jitter.')
                    pass
            except np.linalg.LinAlgError:
                print('La matriz definida por el kernel no es definida positiva')
                pass
            y_preds.extend(list(y_predicc * y.std() + y.mean()))

        # transformar restricciones en ndarray, por sia caso
        y_preds_ndarray = np.array(y_preds.copy())
        dicc_preds[idhole] = y_preds_ndarray
        printProgressBar(idx + 1, n,
                         prefix='Current process: {}. Total Progress:'.format(getpid()),
                         suffix='Complete', length=50)

    # return dicc_preds
    return out_q.put(dicc_preds)


def mp_gaussian_process_by_test_point(IDHOLEs, nprocs, model, ker, distancia=35):
    out_q = multiprocessing.Queue()
    chuncksize = int(math.ceil(len(IDHOLEs) / float(nprocs)))
    procs = []
    for idx in range(nprocs):
        p = multiprocessing.Process(target=estimation_by_point_mp,
                                    args=(IDHOLEs[chuncksize * idx:chuncksize * (idx + 1)],
                                          out_q, model, ker, distancia))
        procs.append(p)
        p.start()

    resultdict = {}

    for idx in range(nprocs):
        resultdict.update(out_q.get())
    for p in procs:
        p.join()
    return resultdict


if __name__ == '__main__':
    HOLEIDs = get_holeids()
    kernel = GPy.kern.RBF(input_dim=3, active_dims=[0, 1, 2], ARD=True)
    dist = 35
    t0 = time.time()
    # diccionario = estimation_by_point_mp(HOLEIDs[:1], 'sgpr', kernel, dist)
    diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel, distancia=dist)
    print('Tiempo para gp en paralelo: {}'.format(time.time() - t0))

    # exportar los datos
    path_estimacion = '../code_git/estimaciones/'
    outfile_name = 'mp_gpUg_' + kernel.name + '_' + str(dist) + '.csv'
    outfile = open(path_estimacion + outfile_name, 'w')
    outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    for holeid in HOLEIDs:
        pozo = get_pozo_holeid(holeid)
        for i, fila in enumerate(pozo):
            line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i, ], fila[5]
            outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    outfile.close()
