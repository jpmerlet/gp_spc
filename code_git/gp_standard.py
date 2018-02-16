from mp_gp_test import *


def estimacion_by_point(modelo, ker, distancia=30, transform=False, std=1,
                        lik=GPy.likelihoods.Gaussian(),
                        inf=GPy.inference.latent_function_inference.ExactGaussianInference()):
    # diccionario que guardara las predicciones por dhid
    global lmb
    dicc_preds = dict()
    IDHOLEs = get_holeids()
    n = len(IDHOLEs)
    for idx, idhole in enumerate(IDHOLEs):
        y_preds = list()
        num_muestras = list()
        test_points = get_test_points_holeid(idhole)
        for idx_muetra, test_point in enumerate(test_points):
            X_df, y_df = get_trainingSet_by_point(test_point, distancia)

            if X_df.shape[0] < 10:
                y_preds.extend(list(np.array([-99])))
                continue

            X = X_df[['midx', 'midy', 'midz']].as_matrix()
            y = y_df[['cut']].as_matrix()
            num_muestras[idx_muetra] = X.shape[0]  # guardar nro muestras por test_point
            X_std = (X - X.mean()) / X.std()
            y_std = (y - y.mean()) / y.std()

            if std == 1:
                test_point_std = (test_point - X.mean()) / X.std()
            else:
                print('std debe ser 0 o 1.')

            if modelo == 'sgpr':
                if transform:
                    y_cox, lmb = stats.boxcox(y)  # transformamos el dato sin estandarizar
                    model = GPy.core.GP(X, y_cox, kernel=ker, likelihood=lik, inference_method=inf)
                else:
                    model = GPy.core.GP(X_std, y_std, kernel=ker,
                                        likelihood=lik,
                                        inference_method=inf)
            else:
                model = GPy.models.GPRegression(X, y, ker)
            y_predicc = -99
            try:
                model.optimize(messages=False, max_f_eval=1000)
                y_predicc, _ = model.predict(np.array([[test_point_std[0],
                                                        test_point_std[1],
                                                        test_point_std[2]]]))
                pass
            except GPy.util.linalg.linalg.LinAlgError as err:
                if 'not positive definite' in err.message:
                    print('not positive definite, even with jitter.')
                    pass
            except np.linalg.LinAlgError:
                print('La matriz definida por el kernel no es definida positiva')
                pass
            y_preds.extend(list(y_predicc * y.std() + y.mean()))

            if transform:
                y_predicc_inv = inv_boxcox(y_predicc, lmb)
                y_preds.extend(list(y_predicc_inv))
            else:
                y_preds.extend(list(y_predicc * y.std() + y.mean()))

        # transformar restricciones en ndarray, por si acaso
        y_preds_ndarray = np.array(y_preds.copy())
        dicc_preds[idhole] = (y_preds_ndarray, num_muestras)

        # se imprime
        printProgressBar(idx + 1, n, prefix='Progress:', suffix='Complete', length=50)

    return dicc_preds


if __name__ == '__main__':

    HOLEIDs = get_holeids()
    kernel = GPy.kern.RBF(3, ARD=True)
    dist = 20
    diccionario = estimacion_by_point('sgpr', kernel, distancia=dist)

    # exportar los datos
    path_estimacion = 'estimaciones/'
    outfile_name = 'gp_test_' + 'all_2_' + str(dist) + '.csv'
    outfile = open(path_estimacion + outfile_name, 'w')
    outfile.write('xcentre,ycentre,zcentre,minty,cut_poz,cut,f1,muestras\n')
    for holeid in HOLEIDs:
        pozo = get_pozo_holeid(holeid)
        for i, fila in enumerate(pozo):
            muestras = diccionario[holeid][1][i]
            line = fila[0], fila[1], fila[2], fila[3], fila[4], diccionario[holeid][0][i, ], fila[5], muestras
            outfile.write('%f,%f,%f,%f,%f,%f,%f,%f\n' % line)
    outfile.close()
