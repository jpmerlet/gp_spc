from utilidades import *


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


def estimation_by_point_mp(IDHOLEs, out_q, modelo, ker, distancia, transform, std, lik, inf):
    # distancia a la que se buscan muestras (quizas es mejor tomar la minima necesaria?)
    global lmbda
    n = len(IDHOLEs)
    dicc_preds = {}
    for idx, idhole in enumerate(IDHOLEs):
        y_preds = list()
        num_muestras = list()
        test_points = get_test_points_holeid(idhole)
        for test_point in test_points:
            X_df, y_df = get_trainingSet_by_point(test_point, distancia)

            if X_df.shape[0] < 10:
                y_preds.extend(list(np.array([-99])))
                num_muestras.append(0)
                continue
            num_muestras.append(X_df.shape[0])  # guardar nro muestras por test_point

            X = X_df[['midx', 'midy', 'midz']].as_matrix()
            y = y_df[['cut']].as_matrix()

            X_std = (X - X.mean()) / X.std()
            y_std = (y - y.mean()) / y.std()

            if std == 1:
                test_point_std = (test_point - X.mean()) / X.std()
            else:
                print('std debe ser 0 o 1.')

            if modelo == 'sgpr':
                if transform:
                    y_cox, lmbda = stats.boxcox(y)  # transformamos el dato sin estandarizar
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
                if transform:
                    y_predicc, _ = modelo.predict(np.array([[test_point[0],
                                                             test_point[1],
                                                             test_point[2]]]))
                else:
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
            if transform:  # si transformamos no se esta estandarizando!!!
                y_predicc_inv = inv_boxcox(y_predicc, lmbda)
                y_preds.extend(list(y_predicc_inv))
            else:
                y_preds.extend(list(y_predicc * y.std() + y.mean()))

        # transformar restricciones en ndarray, just in case
        y_preds_ndarray = np.array(y_preds.copy())
        dicc_preds[idhole] = (y_preds_ndarray, num_muestras)
        # printProgressBar(idx + 1, n,
        #                  prefix='Current process: {}. Total Progress:'.format(getpid()),
        #                  suffix='Complete', length=50)
    out_q.put(dicc_preds)


def mp_gaussian_process_by_test_point(IDHOLEs, nprocs, modelo, ker, distancia=50, transform=False, std=1,
                                      lik=GPy.likelihoods.Gaussian(),
                                      inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    out_q = multiprocessing.Queue()
    chuncksize = int(math.ceil(len(IDHOLEs) / float(nprocs)))
    procs = []
    for idx in range(nprocs):
        p = multiprocessing.Process(target=estimation_by_point_mp,
                                    args=(IDHOLEs[chuncksize * idx:chuncksize * (idx + 1)],
                                          out_q, modelo, ker, distancia, transform, std,
                                          lik, inf))
        procs.append(p)
        p.start()

    resultdict = {}

    for idx in range(nprocs):
        resultdict.update(out_q.get())
    for p in procs:
        p.join()
    return resultdict


if __name__ == '__main__':
    print('Se realiza estimacion con kernel RBF(3, ARD), parametros: default')
    HOLEIDs = get_holeids()
    kernel = GPy.kern.RBF(3, ARD=True)
    dist = 33
    print('distancia de busqueda para entrenar: {}'.format(dist))
    t0 = time.time()
    diccionario = mp_gaussian_process_by_test_point(HOLEIDs[:1], 2, 'sgpr', kernel, distancia=dist)
    # print('Tiempo para gp en paralelo: {}'.format(time.time() - t0))

    # exportar los datos
    path_estimacion = 'estimaciones/'
    outfile_name = 'matlab_mp_test_' + 'all_2_' + str(dist) + '.csv'
    outfile = open(path_estimacion + outfile_name, 'w')
    outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1,muestras\n')
    for holeid in HOLEIDs[:1]:
        pozo = get_pozo_holeid(holeid)
        for i, fila in enumerate(pozo):
            muestras = diccionario[holeid][1]
            line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][0][i, ], fila[5], muestras[i]
            outfile.write('%f,%f,%f,%f,%f,%f,%f,%f\n' % line)
    outfile.close()
