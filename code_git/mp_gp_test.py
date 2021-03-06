import GPy
import numpy as np
import time
from os import getpid
import pandas as pd
import matplotlib.pyplot as plt
import scipy.spatial as spatial
from scipy import stats
from scipy.special import inv_boxcox

import multiprocessing
import math

# se cargan los datos de entrenamiento
train_data = pd.read_csv('../../GP_Data/cy17_spc_assays_rl6_entry.csv')
train_cols = ['midx', 'midy', 'midz', 'cut']

test_data = pd.read_csv('../../GP_Data/cy17_spc_assays_pvo_entry.csv')
test_cols = ['midx', 'midy', 'midz']

# se definen los estilos de los graficos
# jtplot.style(theme='onedork',figsize = (16.5,12))


class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name, end=' ')
        print('Elapsed: %s' % (time.time() - self.tstart))


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


def get_y_holeid(idhole):
    return test_data.loc[test_data['dhid'] == idhole][['cut']].as_matrix()


def get_cut_xyz_by_holeid(idhole):
    xyz_cut = test_data.loc[test_data['dhid'] == idhole][['midx',
                                                          'midy',
                                                          'midz',
                                                          'cut']].as_matrix()
    return xyz_cut


def get_pozo_holeid(idhole, cols_names=None):
    if cols_names is None:
        cols_names = ['midx', 'midy', 'midz', 'minty', 'cut', 'f1']

    hole = test_data.loc[test_data['dhid'] == idhole][cols_names].as_matrix()
    return hole


def get_trainingSet_by_point(test_point, distancia):
    # distancia se podria calcular por caso,
    # segun la cantidad de pts. que se encuentren
    X_train_df = train_data[['dhid', 'midx', 'midy', 'midz']]
    y_df = train_data[['dhid', 'cut']]
    X_train = X_train_df[['midx', 'midy', 'midz']].as_matrix()
    train_tree = spatial.cKDTree(X_train)
    idx = train_tree.query_ball_point(list(test_point), distancia)
    return X_train_df.iloc[idx, :], y_df.iloc[idx, :]


def get_traningSet(idhole, distancia):
    # retorna X dataFrame con los puntos de
    # entrenamiento para todo el sondaje dhid
    X_train_df = train_data[['dhid', 'midx', 'midy', 'midz']]
    y_df = train_data[['dhid', 'cut']]
    X_train = X_train_df[['midx', 'midy', 'midz']].as_matrix()

    test_points = get_test_points_holeid(idhole)
    test_tree = spatial.cKDTree(test_points)
    train_tree = spatial.cKDTree(X_train)

    idx_rep = test_tree.query_ball_tree(train_tree, distancia)
    idx_sin_rep = list(set([indice for lista in idx_rep for indice in lista]))
    return X_train_df.iloc[idx_sin_rep, :], y_df.iloc[idx_sin_rep, :]


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


def estimacion_by_point(modelo, ker, transform=False, Plotear=False, std=1,
                        lik=GPy.likelihoods.Gaussian(),
                        inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    # diccionario que guardara las predicciones por dhid
    global m, y_pred, lmb
    dicc_preds = dict()

    # distancia a la que se buscan muestras (quizas es mejor tomar la minima necesaria?)
    distancia = 33
    IDHOLEs = get_holeids()
    n = len(IDHOLEs)
    # HOLEIDs.remove('F06-1580-016')
    # HOLEIDs.remove('F06-1610-004')
    # HOLEIDs.remove('F06-1625-021')
    # HOLEIDs.remove('F13-1595-005')
    # HOLEIDs.remove('F05-1565-009')
    for idx, idhole in enumerate(IDHOLEs):
        y_preds = list()
        test_points = get_test_points_holeid(idhole)
        for test_point in test_points:
            X_df, y_df = get_trainingSet_by_point(test_point, distancia)
            X = X_df[['midx', 'midy', 'midz']].as_matrix()
            y = y_df[['cut']].as_matrix()

            X_std = (X - X.mean()) / X.std()
            y_std = (y - y.mean()) / y.std()
            if std == 1:
                test_point_std = (test_point - X.mean()) / X.std()
            elif std == 0:
                (test_point - test_points.mean()) / test_points.std()
            else:
                print('std debe ser 0 o 1.')
            if X_df.shape[0] < 10:
                y_preds.extend(list(np.array([-99])))
                continue
            if modelo == 'sgpr':
                # m = GPy.models.SparseGPRegression(X,y,ker)
                if transform:
                    y_cox, lmb = stats.boxcox(y)
                    m = GPy.core.GP(X, y_cox, kernel=ker, likelihood=lik, inference_method=inf)
                else:
                    m = GPy.core.GP(X_std, y_std, kernel=ker,
                                    likelihood=lik,
                                    inference_method=inf)
            else:
                m = GPy.models.GPRegression(X, y, ker)
            try:
                m.optimize(messages=False, max_f_eval=1000)
                y_pred, _ = m.predict(np.array([[test_point_std[0],
                                                 test_point_std[1],
                                                 test_point_std[2]]]))
            except GPy.util.linalg.linalg.LinAlgError as err:
                if 'not positive definite' in err.message:
                    print('not positive definite, even with jitter.')
                    pass
            except np.linalg.LinAlgError:
                print('La matriz definida por el kernel no es definida positiva')
                pass
            y_preds.extend(list(y_pred * y.std() + y.mean()))

        if transform:
            y_preds = inv_boxcox(y_preds, lmb)
        # transformar restricciones en ndarray, por sia caso
        y_preds_ndarray = np.array(y_preds.copy())
        dicc_preds[idhole] = y_preds_ndarray

        # guardar valores reales de oro en los puntos test de dhid
        y_medido = get_y_holeid(idhole).reshape(y_preds_ndarray.shape)

        if Plotear:
            # se analizan los resultados por dhid
            fig, ax = plt.subplots()
            ax.scatter(y_medido, y_preds_ndarray, edgecolors=(0, 0, 0))
            ax.plot([y_medido.min(), y_medido.max()], [y_medido.min(), y_medido.max()], 'k--', lw=2)
            ax.set_xlabel('Medido')
            ax.set_ylabel('Prediccion')
            ax.set_title('Regresion para el sondaje %s' % idhole)
            # ax.set_title('DHID:%s, Kernel: %s' % (dhid,gp.kernel_))
        printProgressBar(idx + 1, n,
                         prefix='Current HOLEID: {}. Total Progress:'.format(IDHOLEs[(idx + 1) * (idx < n - 1)]),
                         suffix='Complete', length=50)
    if Plotear:
        plt.show()
    return m, dicc_preds


def estimation_by_point_mp(IDHOLEs, out_q, modelo, ker, distancia, transform, std=1, lik=GPy.likelihoods.Gaussian(),
                           inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    # distancia a la que se buscan muestras (quizas es mejor tomar la minima necesaria?)
    global lmbda
    n = len(IDHOLEs)
    dicc_preds = {}
    for idx, idhole in enumerate(IDHOLEs):
        y_preds = list()
        test_points = get_test_points_holeid(idhole)
        for test_point in test_points:
            X_df, y_df = get_trainingSet_by_point(test_point, distancia)

            # while X_df.shape[0] < 20:
            #     distancia_aumentada = 5 + distancia
            #     X_df, y_df = get_trainingSet_by_point(test_point, distancia_aumentada)
            if X_df.shape[0] < 10:
                y_preds.extend(list(np.array([-99])))
                continue

            X = X_df[['midx', 'midy', 'midz']].as_matrix()
            y = y_df[['cut']].as_matrix()

            X_std = (X - X.mean()) / X.std()
            y_std = (y - y.mean()) / y.std()

            if std == 1:
                test_point_std = (test_point - X.mean()) / X.std()
            elif std == 0:
                (test_point - test_points.mean()) / test_points.std()
            else:
                print('std debe ser 0 o 1.')
            if modelo == 'sgpr':
                # m = GPy.models.SparseGPRegression(X,y,ker)
                if transform:
                    y_cox, lmbda = stats.boxcox(y)
                    modelo = GPy.core.GP(X, y_cox, kernel=ker, likelihood=lik, inference_method=inf)
                else:
                    modelo = GPy.core.GP(X_std, y_std, kernel=ker,
                                         likelihood=lik,
                                         inference_method=inf)

            else:
                modelo = GPy.models.GPRegression(X, y, ker)
            y_predicc = -99
            try:
                modelo.optimize(messages=False, max_f_eval=1000)
                y_predicc, _ = modelo.predict(np.array([[test_point_std[0],
                                                         test_point_std[1],
                                                         test_point_std[2]]]))

            except GPy.util.linalg.linalg.LinAlgError as err:
                if 'not positive definite' in err.message:
                    print('not positive definite, even with jitter.')
                    pass
            except np.linalg.LinAlgError:
                print('La matriz definida por el kernel no es definida positiva')
                pass
            y_preds.extend(list(y_predicc * y.std() + y.mean()))

        if transform:
            y_preds = inv_boxcox(y_preds, lmbda)
        # transformar restricciones en ndarray, por sia caso
        y_preds_ndarray = np.array(y_preds.copy())
        dicc_preds[idhole] = y_preds_ndarray
        # printProgressBar(i + 1, n,
        #               prefix='Current HOLEID: {}. Total Progress:'.format(HOLEIDs[(i + 1) * (i < n - 1)]),
        #               suffix='Complete', length=50)
        printProgressBar(idx + 1, n,
                         prefix='Current process: {}. Total Progress:'.format(getpid()),
                         suffix='Complete', length=50)
    out_q.put(dicc_preds)

    return


def mp_gaussian_process_by_test_point(IDHOLEs, nprocs, modelo, ker, distancia=33, transform=False):
    out_q = multiprocessing.Queue()
    chuncksize = int(math.ceil(len(IDHOLEs) / float(nprocs)))
    procs = []
    for idx in range(nprocs):
        p = multiprocessing.Process(target=estimation_by_point_mp,
                                    args=(IDHOLEs[chuncksize * idx:chuncksize * (idx + 1)],
                                          out_q, modelo, ker, distancia, transform))
        procs.append(p)
        p.start()

    resultdict = {}

    for idx in range(nprocs):
        resultdict.update(out_q.get())
    for p in procs:
        p.join()
    return resultdict


if __name__ == '__main__':
    # modelo: sgpr
    # transform: True
    # lik: GPy.likelihoods.Gaussian()
    # ker: GPy.kern.Matern32(input_dim=2, active_dims=[0, 1]) + GPy.kern.Matern32(input_dim =1, active_dims = [2])
    # inf: GPy.inference.latent_function_inference.ExactGaussianInference()

    # HOLEIDs = get_holeids()
    # kernel = GPy.kern.Matern32(input_dim=2, active_dims=[0, 1]) + GPy.kern.Matern32(input_dim =1, active_dims = [2])
    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel)
    # print('Tiempo para gp en paralelo: {}'.format(time.time()-t0))

    # exportar los datos
    # outfile_name = 'mp_test_'+'all'+'.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    # for holeid in HOLEIDs:
    #     pozo = get_pozo_holeid(holeid)
    #     for i, fila in enumerate(pozo):
    #        line = fila[0], fila[1], fila[2], fila[3], fila[4],diccionario[holeid][i,], fila[5]
    #         outfile.write('%f,%f,%f,%s,%s,%s,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # transform: False
    # lik: GPy.likelihoods.Gaussian()
    # ker: GPy.kern.Matern32(input_dim=2, active_dims=[0, 1]) + GPy.kern.Bias(3)
    # inf: GPy.inference.latent_function_inference.ExactGaussianInference()

    # HOLEIDs = get_holeids()

    # kernel = GPy.kern.Matern32(input_dim=2, active_dims=[0, 1]) + GPy.kern.Bias(3)
    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel)
    # print('Tiempo para gp en paralelo: {}'.format(time.time()-t0))

    # exportar los datos
    # outfile_name = 'mp_test_'+'all_1'+'.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,lito,alt,cut,cut_poz\n')
    # for holeid in HOLEIDs:
        # pozo = get_pozo_holeid(holeid)
        # for i, fila in enumerate(pozo):
            # line = fila[0], fila[1], fila[2], fila[3], fila[4], fila[5], diccionario[holeid][i, ],fila[6]
            # outfile.write('%f,%f,%f,%s,%s,%s,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # transform: False
    # lik: GPy.likelihoods.Gaussian()
    # ker: GPy.kern.RBF(3,ARD = True)
    # inf: GPy.inference.latent_function_inference.ExactGaussianInference()

    # HOLEIDs = get_holeids()
    # kernel = GPy.kern.RBF(3,ARD=True)
    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel)
    # print('Tiempo para gp en paralelo: {}'.format(time.time()-t0))

    # exportar los datos
    # outfile_name = 'mp_test_'+'all_2'+'.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    # for holeid in HOLEIDs:
    #     pozo = get_pozo_holeid(holeid)
    #    for i, fila in enumerate(pozo):
    #         line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i,], fila[5]
    #         outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # transform: False
    # lik: GPy.likelihoods.Gaussian()
    # ker: GPy.kern.RBF(3) + GPy.kern.Linear(3)
    # inf: GPy.inference.latent_function_inference.ExactGaussianInference()
    # HOLEIDs = get_holeids()
    # kernel = GPy.kern.RBF(3) + GPy.kern.Linear(3)
    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel) # se prueba print en multiprocessing
    # print('Tiempo para gp en paralelo: {}'.format(time.time() - t0))

    # exportar los datos
    # outfile_name = 'mp_test_' + 'all_3' + '.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    # for holeid in HOLEIDs:
    #    pozo = get_pozo_holeid(holeid)
    #    for i, fila in enumerate(pozo):
    #        line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i,], fila[5]
    #        outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # transform: False
    # lik: GPy.likelihoods.Gaussian()
    # ker: GPy.kern.RBF(x)+ GPy.kern.RBF(y) + GPy.kern.RBF(z)
    # inf: GPy.inference.latent_function_inference.ExactGaussianInference()

    # HOLEIDs = get_holeids()
    # kernel = GPy.kern.RBF(input_dim=1, active_dims=[1]) + \
    #         GPy.kern.RBF(input_dim=1, active_dims=[2]) + GPy.kern.RBF(input_dim=1, active_dims=[0])

    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 5, 'sgpr', kernel)
    # print('Tiempo para gp en paralelo: {}'.format(time.time() - t0))

    # exportar los datos
    # outfile_name = 'mp_test_' + 'all_4' + '.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    # for holeid in HOLEIDs:
    #     pozo = get_pozo_holeid(holeid)
    #     for i, fila in enumerate(pozo):
    #         line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i,], fila[5]
    #         outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # ker: Matern32(3, ARD=True)

    # HOLEIDs = get_holeids()
    # kernel = GPy.kern.Matern32(3, ARD=True)
    # t0 = time.time()
    # diccionario = mp_gaussian_process_by_test_point(HOLEIDs, 8, 'sgpr', kernel)
    # print('Tiempo para gp con multiprocessing: {}'.format(time.time()-t0))

    # exportar los datos
    # outfile_name = 'mp_test_'+'all_5'+'.csv'
    # outfile = open(outfile_name, 'w')
    # outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    # for holeid in HOLEIDs:
    #     pozo = get_pozo_holeid(holeid)
    #     for i, fila in enumerate(pozo):
    #         line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i, ], fila[5]
    #         outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    # outfile.close()

    # Modelo sobre todos los pozos
    # modelo: sgpr (Sparse Gaussian process)
    # ker: Matern52(3, ARD=True)

    HOLEIDs = get_holeids()
    kernel = GPy.kern.Matern52(3, ARD=True)
    t0 = time.time()
    diccionario = mp_gaussian_process_by_test_point(HOLEIDs[:8], 8, 'sgpr', kernel)
    print('Tiempo para gp con multiprocessing: {}'.format(time.time()-t0))

    # exportar los datos
    outfile_name = 'mp_test_'+'all_6'+'.csv'
    path_estimacion = 'estimaciones/'
    outfile = open(path_estimacion + outfile_name, 'w')
    outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1\n')
    for holeid in HOLEIDs[:8]:
        pozo = get_pozo_holeid(holeid)
        for i, fila in enumerate(pozo):
            line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][i, ], fila[5]
            outfile.write('%f,%f,%f,%f,%f,%f,%f\n' % line)
    outfile.close()
