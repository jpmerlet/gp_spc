import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp
from sklearn.metrics import r2_score
import matplotlib.dates as mdates
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')

##############################################
# To DO LIST

# * QQPLOT (pozo contar gp y ok)


def get_years(path_est):

    estimacion_sorted = add_year_month_sorted(path_est)
    df_years = estimacion_sorted['year']
    seen = set()
    YEARS = []
    for item in df_years:
        if item not in seen:
            seen.add(item)
            YEARS.append(item)
    return YEARS


def add_year_month_sorted(path_est):
    # se agregan las columans year y month a
    # al archivo que contienen las estimaciones
    # hechas por gp, y retorna un dataframe
    # con los datos ordenados por f1 (que es
    # lo mismo que ordenar por fecha)
    estimacion_original = pd.read_csv(path_est)
    cols_names = list(estimacion_original.columns.values)
    if 'cut_gp' in cols_names:
        var_est = 'cut_gp'
    elif 'cut_ok' in cols_names:
        var_est = 'cut_ok'

    elif 'cut' in cols_names:
        var_est = 'cut'
    elif 'cut_est' in cols_names:
        var_est = 'cut_est'
    else:
        var_est = 'cut_vulcan'
    # solamente se consideran las estimaciones
    # que tienen f1 dado (i.e. no -99) y cut
    # mayor que cero
    estimacion_filtrada = estimacion_original.loc[(estimacion_original['f1'] > 0) &
                                                  (estimacion_original[var_est] > 0)]
    f1 = estimacion_filtrada['f1'].as_matrix()
    estimacion = cp.copy(estimacion_filtrada)
    estimacion = estimacion.assign(year=((f1 - 1) / 12).astype(int) + 2014)
    estimacion = estimacion.assign(mes=((f1 - 1) % 12 + 1).astype(int))
    estimacion_sorted = estimacion.sort_values('f1', ascending=True)
    return estimacion_sorted


def dicc_error_bloque(path_est):
    estimacion_sorted = add_year_month_sorted(path_est)
    YEARS = get_years(path_est)
    dicc_anual = dict()
    for year in YEARS:
        plt.figure()
        df_by_year = estimacion_sorted.loc[estimacion_sorted['year'] == year]
        meses = df_by_year['mes']
        dicc_promedios_mensual = dict()
        for mes in meses:
            cut_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut']
            cut_poz_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut_poz']
            cuociente = np.divide(cut_poz_mes, cut_mes)
            promedio_mensual = cuociente.mean()
            dicc_promedios_mensual[mes] = promedio_mensual
        dicc_anual[year] = dicc_promedios_mensual
    return dicc_anual
    # for year,dicc in dicc_anual:
    #    plt.figure()
    #    for mes, promedio in dicc:
    #        plt.plot(mes,promedio)


def sacar_repeticiones(iterable):
    seen = set()
    lista_sin_rep = []
    for item in iterable:
        if item not in seen:
            seen.add(item)
            lista_sin_rep.append(item)
    return lista_sin_rep


def concatenar_estimaciones(list_path, sinLixCob=False):
    global df_concatenated
    path_est_gp = 'estimaciones/mp_GPConcat_rbf_33.csv'
    # path_est_ok = '../kriging/modeloConcant_estimado_sondaje_20.csv'
    path_est_vulcan = 'estimaciones/vulcan.csv'

    path_0 = list_path[0]
    df_est_0 = pd.read_csv(path_0)
    if 'sondaje' in path_0:
        var_est = 'cut_ok'
        df_est_0.rename(columns={'cut': 'cut_ok'}, inplace=True)

    elif 'GP' in path_0:
        var_est = 'cut_gp'
        df_est_0.rename(columns={'cut': 'cut_gp'}, inplace=True)
    else:
        var_est = 'cut_est'
        df_est_0.rename(columns={'cut_est': 'cut_vulcan'}, inplace=True)
        df_est_0.rename(columns={'midx': 'xcentre', 'midy': 'ycentre', 'midz': 'zcentre'}, inplace=True)

    df_est_0 = df_est_0.loc[df_est_0[var_est] > 0]

    # se concatenan con los que vienen
    for ruta_i in list_path[1:]:
        df_est_i = pd.read_csv(ruta_i)
        if 'sondaje' in ruta_i:
            var_est = 'cut_ok'
            df_est_i.rename(columns={'cut': 'cut_ok'}, inplace=True)

        elif 'GP' in ruta_i:
            var_est = 'cut_gp'
            df_est_i.rename(columns={'cut': 'cut_gp'}, inplace=True)
        else:
            var_est = 'cut_vulcan'
            df_est_i.rename(columns={'cut_est': 'cut_vulcan'}, inplace=True)
            df_est_i.rename(columns={'midx': 'xcentre', 'midy': 'ycentre', 'midz': 'zcentre'}, inplace=True)

        df_est_i = df_est_i.loc[df_est_i[var_est] > 0]
        df_concatenated = pd.merge(df_est_0, df_est_i, on=['xcentre', 'ycentre', 'zcentre'])
        df_est_0 = df_concatenated
    df_concatenated.rename(columns={'cut_poz_x': 'cut_poz'}, inplace=True)
    if sinLixCob:
        df_concatenated = df_concatenated.loc[df_concatenated['minty'] > 10]

    df_gp = df_concatenated[['xcentre', 'ycentre', 'zcentre', 'cut_gp', 'cut_poz', 'f1']]
    # df_ok = df_concatenated[['xcentre', 'ycentre', 'zcentre', 'cut_ok', 'cut_poz', 'f1']]
    df_vulcan = df_concatenated[['xcentre', 'ycentre', 'zcentre', 'cut_vulcan', 'cut_poz', 'f1']]

    df_gp.to_csv(path_est_gp)
    # df_ok.to_csv(path_est_ok)
    df_vulcan.to_csv(path_est_vulcan)


def plotear_f1(list_paths):
    n = len(list_paths)
    fig, axes = plt.subplots(nrows=n, ncols=1, sharey=True)
    plt.suptitle('F1 de OK & GP', fontsize=15)
    for i in range(n):
        estimacion_sorted = add_year_month_sorted(list_paths[i])

        # se recupera el nombre de la variable estimada y real en el .csv, si no la reconoce para y avisa
        cols_names = list(estimacion_sorted.columns.values)

        if 'cut_gp' in cols_names:
            var_est = 'cut_gp'
            var_real = 'cut_poz'
        elif 'cut_ok' in cols_names:
            var_est = 'cut_ok'
            var_real = 'cut_poz'
        elif 'cut' in cols_names:
            var_est = 'cut'
            var_real = 'cut_poz'
        elif 'cut_est' in cols_names:
            var_est = 'cut_est'
            var_real = 'cut_real'
        else:
            var_est = 'cut_vulcan'
            var_real = 'cut_poz'
        YEARS = get_years(list_paths[i])
        dicc_anual_f1 = dict()
        dicc_anual_muestras = dict()
        columnas = []
        for year in YEARS:
            df_by_year = estimacion_sorted.loc[estimacion_sorted['year'] == year]
            columnas = list(df_by_year.columns)
            meses = df_by_year['mes']
            seen = set()
            MESES = []  # se eliminan los meses repetidos
            for mes in meses:
                if mes not in seen:
                    seen.add(mes)
                    MESES.append(mes)
            dicc_cuociente_mensual = dict()  # mes: cut_poz.mean()/cut.mean()
            dicc_promedio_mensual = dict()  # mes: muestras.mean()
            for mes in MESES:
                cut_mes = df_by_year.loc[df_by_year['mes'] == mes][var_est]
                cut_poz_mes = df_by_year.loc[df_by_year['mes'] == mes][var_real]
                cuociente = np.divide(cut_poz_mes.mean(), cut_mes.mean())
                dicc_cuociente_mensual[mes] = cuociente
                if 'muestras' in list(df_by_year.columns):  # solo funcionara en gp
                    num_muestras_mes = df_by_year.loc[df_by_year['mes'] == mes]['muestras']
                    mean_muestras_mes = num_muestras_mes.mean()
                    dicc_promedio_mensual[mes] = mean_muestras_mes

            dicc_anual_f1[year] = dicc_cuociente_mensual
            dicc_anual_muestras[year] = dicc_promedio_mensual
        if 'muestras' in columnas:
            _plot_f1(list_paths[i], dicc_anual_f1, YEARS, i, axes, dicc_anual_muestras)
        else:
            _plot_f1(list_paths[i], dicc_anual_f1, YEARS, i, axes)


def _plot_f1(path_name, dicc_f1, YEARS, i, ejes, dicc_muestras=None):
    if dicc_muestras is not None:
        axis = ejes[i, ]
        df_dicc_f1 = pd.DataFrame.from_dict(dicc_f1)
        df_dicc_muestras = pd.DataFrame.from_dict(dicc_muestras)
        f1 = df_dicc_f1[YEARS[0]]
        muestras = df_dicc_muestras[YEARS[0]]
        for year in YEARS[1:]:
            f1 = pd.concat([f1, df_dicc_f1[year]], names=['f1'])
            muestras = pd.concat([muestras, df_dicc_muestras[year]], names=['f1'])
        # return f1, muestras
        f1 = f1.dropna()  # elimina todas las filas con Nan
        # muestras = muestras.dropna()
        f1_df = pd.DataFrame(f1.as_matrix(), index=pd.date_range('1/1/' + str(YEARS[0]),
                                                                 periods=f1.shape[0], freq='MS'))
        # muestras_df = pd.DataFrame(muestras.as_matrix(), index=pd.date_range('1/1/' + str(YEARS[0]),
        #                                                                      periods=muestras.shape[0], freq='MS'))
        # agregar cantidad de muestras en pomedio utilizadas por mes
        # axis_muestras = axis.twinx()
        # muestras_df.plot.bar(ax=axis_muestras, legend=False, width=0.1)
        # axis_muestras.set_ylim(10, 25)

        # graficar f1 en meses
        f1_df.columns = ['f1']
        f1_df.plot(style='bo-', ax=axis, legend=False)
        # axis.plot(f1_df['f1'].as_matrix(), 'bo-')

        # agregar cantidad de muestras en pomedio utilizadas por mes
        # axis_muestras = axis.twinx()
        # muestras_df.plot.bar(ax=axis_muestras, legend=False, width=0.1)
        # axis_muestras.set_ylim(10, 25)

        # se agregan los margenes para el f1
        axis.axhline(y=1.1, color='g', linestyle='-')
        axis.axhline(y=0.9, color='g', linestyle='-')
        axis.axhline(y=1, color='k', linestyle='--')

        # a partir del nombre del archivo se recupera el nombre del kernel y la distancia de busqueda
        # groups = path_name.split('_')
        # ker_name = groups[2]
        # distancia = groups[3].split('.')[0]
        if 'sondaje' in path_name:
            title = 'OK outlier'

        elif 'GP' in path_name:
            title = 'GP'
        else:
            title = 'OK vulvan'
        axis.set_title(title)

    else:
        try:
            axis = ejes[i, ]
        except TypeError:
            axis = ejes
            pass
        df_dicc_f1 = pd.DataFrame.from_dict(dicc_f1)
        f1 = df_dicc_f1[YEARS[0]]
        for year in YEARS[1:]:
            f1 = pd.concat([f1, df_dicc_f1[year]], names=['f1'])
        # return f1, muestras
        f1 = f1.dropna()  # elimina todas las filas con Nan
        f1_df = pd.DataFrame(f1.as_matrix(), index=pd.date_range('1/1/' + str(YEARS[0]),
                                                                 periods=f1.shape[0], freq='MS'))

        f1_df.columns = ['f1']
        f1_df.plot(style='bo-', ax=axis)
        axis.axhline(y=1.1, color='g', linestyle='-')
        axis.axhline(y=0.9, color='g', linestyle='-')
        axis.axhline(y=1, color='k', linestyle='--')
        if 'sondaje' in path_name:
            title = 'OK outlier'

        elif 'GP' in path_name:
            title = 'GP'
        else:
            title = 'OK vulcan'
        axis.set_title(title)


def plot_errores_lista(lists_path, plot_reg=False):
    fig = plt.figure()
    fig.suptitle('AMPRD90 de GP & OK', fontsize=15)
    n = len(lists_path)
    for i in range(n):
        df_est = pd.read_csv(lists_path[i])
        print('####################')
        print(lists_path[i])
        errors = plot_errores(df_est, plot_reg)

        # grafico de la curva de errores
        if 'GP' in lists_path[i]:
            # path_name = lists_path[i]
            # groups = path_name.split('_')
            # ker_name = groups[2]
            # distancia = groups[3].split('.')[0]
            plt.plot(range(len(errors)), errors, label='GP')

        elif 'point' in lists_path[i]:
            plt.plot(range(len(errors)), errors, label='Vulcan')
        else:
            plt.plot(range(len(errors)), errors, label='OK outlier')
        AMPRD90 = np.percentile(errors, 90)

        # grafico del punto donde se encuentra el AMPRD90
        posicion = 0
        for error in errors:
            if error < AMPRD90:
                posicion += 1
        print(posicion)
        plt.plot([posicion, posicion], [0, AMPRD90], 'k-')
        plt.plot([0, posicion], [AMPRD90, AMPRD90], 'k-')
        plt.text(0, AMPRD90, 'AMPRD90: {0:.2f}'.format(AMPRD90))
        plt.plot([posicion], [AMPRD90], 'ro')
        plt.legend()


def plot_errores(df_estimaciones, plot):

    # se filtra por puntos donde se realizó estimacion y donde existe f1
    cols_names = list(df_estimaciones.columns.values)
    if 'cut_gp' in cols_names:
        var_est = 'cut_gp'
        var_real = 'cut_poz'
    elif 'cut_ok' in cols_names:
        var_est = 'cut_ok'
        var_real = 'cut_poz'
    elif 'cut' in cols_names:
        var_est = 'cut'
        var_real = 'cut_poz'
    elif 'cut_est' in cols_names:
        var_est = 'cut_est'
        var_real = 'cut_real'
    else:
        var_est = 'cut_vulcan'
        var_real = 'cut_poz'
    estimacion_filtrada = df_estimaciones.loc[(df_estimaciones['f1'] > 0) &
                                              (df_estimaciones[var_est] > 0)]

    cut_poz = estimacion_filtrada[var_real].as_matrix()
    cut_est = estimacion_filtrada[var_est].as_matrix()
    error = 2*np.divide(np.absolute(cut_poz-cut_est), cut_poz + cut_est)
    AMPRD90 = np.percentile(error, 90)
    r2 = r2_score(cut_poz, cut_est)
    print('r2_score: {}'.format(r2))
    print('AMPRD90: {}'.format(AMPRD90))

    if plot:
        plt.figure()
        plt.scatter(cut_est, cut_poz)
        plt.xlabel('Estimacion')
        plt.ylabel('Valor de pozo')
        plt.title('Estimaciones gp vs Valor de pozo')

    error.sort()
    return error


def r2_gp_by_f1(path_est):
    est_original_gp = pd.read_csv(path_est)
    est_filt_gp = est_original_gp.loc[(est_original_gp['f1'] > 0) & (est_original_gp['cut'] > 0)]
    f1s = sacar_repeticiones(est_filt_gp['f1'])
    f1s.sort()
    for f1 in f1s:
        est_filt_gp_f1 = est_filt_gp.loc[est_filt_gp['f1'] == f1]
        cut_poz = est_filt_gp_f1['cut_poz'].as_matrix()
        cut_est = est_filt_gp_f1['cut'].as_matrix()
        r2 = r2_score(cut_poz, cut_est)
        print('El r2 para f1={} es:{}'.format(f1, r2))

    return


if __name__ == '__main__':
    plt.style.use('classic')
    path_estimacion = 'estimaciones/'

    # ker: RBF(3, ARD=True)
    # dist:20
    est_2 = path_estimacion + 'mp_test_all_2_35.csv'

    # ker: RBF(3, ARD=True)
    # dist:33
    est_rbf_GP_33 = path_estimacion + 'mp_GP_rbf_33.csv'

    # se grafican los resultados de kriging
    est_ok = '../kriging/modelo_estimado_sondaje_20.csv'
    # est_ok = '../kriging/modelo_estimado_ok.csv'

    # se imprimen los errores de las estimaciones
    #paths_list = [est_rbf_GP_33, 'SPC_point_f1_correg.csv', est_ok]
    paths_list = [est_rbf_GP_33, 'SPC_point_f1_correg.csv']  # solo se concatenan las de vulcan con las del gp
    concatenar_estimaciones(paths_list, sinLixCob=True)  # este  comando genera los .csv tales que se estan considerando los mismos pts
    # plotear_f1(paths_list)
    # plot_errores_lista(paths_list)

    # figura, ejess = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
    # figura.suptitle('Distribución de los errores', fontsize=15)
    # for i_err, ax_err in enumerate(ejess):
    #     eje_i = ax_err
    #     path_i = paths_list[i_err]
    #     df_esti = add_year_month_sorted(path_i)
    #     errores = plot_errores(df_esti, False)
    #     etiqueta_modelo = ''
    #     if 'sondaje' in path_i:
    #         etiqueta_modelo = 'ok'
    #     else:
    #         etiqueta_modelo = 'gp'
    #     df_errores = pd.DataFrame({etiqueta_modelo: errores})
    #     df_errores.plot.hist(bins=100, ax=eje_i, sharey=True)

    # figura = plt.figure()
    # figura.suptitle('Distribución de los errores', fontsize=15)
    # error_gp = plot_errores(add_year_month_sorted(paths_list[0]), False)
    # error_ok = plot_errores(add_year_month_sorted(paths_list[1]), False)
    # plt.hist([error_ok, error_gp], bins=10, stacked=True, label=['ok','gp'])
    # plt.legend()
    # r2_gp_by_f1(est_2)
    paths_list = ['estimaciones/mp_GPConcat_rbf_33.csv', 'estimaciones/vulcan.csv']
    plotear_f1(paths_list)

    plot_errores_lista(paths_list)

    # histogramas de las predicciones
    figura, ejess = plt.subplots(nrows=len(paths_list), ncols=1, sharey=True)
    figura.suptitle('Distribución de las estimaciones', fontsize=15)
    for indice, ax in enumerate(ejess):
        eje_i = ejess[indice, ]
        path_i = paths_list[indice]
        df_esti = add_year_month_sorted(path_i)
        names = list(df_esti.columns.values)
        if 'cut_gp' in names:
            variable_est = 'cut_gp'
            variable_real = 'cut_poz'
        elif 'cut_ok' in names:
            variable_est = 'cut_ok'
            variable_real = 'cut_poz'
        elif 'cut' in names:
            variable_est = 'cut'
            variable_real = 'cut_poz'
        elif 'cut_est' in names:
            variable_est = 'cut_est'
            variable_real = 'cut_real'
        else:
            variable_est = 'cut_vulcan'
            variable_real = 'cut_poz'
        df_esti = df_esti[[variable_est, variable_real]]
        df_esti.plot.hist(bins=100, ax=eje_i, alpha=0.5, sharey=True)
    plt.show()
