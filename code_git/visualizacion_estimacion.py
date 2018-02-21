import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp
from sklearn.metrics import r2_score


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

    # solamente se consideran las estimaciones
    # que tienen f1 dado (i.e. no -99) y cut
    # mayor que cero
    estimacion_filtrada = estimacion_original.loc[(estimacion_original['f1'] > 0) &
                                                  (estimacion_original['cut'] > 0)]
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


def plotear_f1(list_paths):
    n = len(list_paths)
    fig, axes = plt.subplots(nrows=n, ncols=1)
    for i in range(n):
        estimacion_sorted = add_year_month_sorted(list_paths[i])
        YEARS = get_years(list_paths[i])
        dicc_anual = dict()
        for year in YEARS:
            df_by_year = estimacion_sorted.loc[estimacion_sorted['year'] == year]
            meses = df_by_year['mes']
            MESES = sacar_repeticiones(meses)
            dicc_cuociente_mensual = dict()  # mes: cut_poz.mean()/cut.mean()
            for mes in MESES:
                cut_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut']
                cut_poz_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut_poz']
                cuociente = np.divide(cut_poz_mes.mean(), cut_mes.mean())
                dicc_cuociente_mensual[mes] = cuociente
            dicc_anual[year] = dicc_cuociente_mensual

        _plot_f1(dicc_anual, YEARS, i, axes)


def _plot_f1(dicc, years, i, ejes):
    df_dicc = pd.DataFrame.from_dict(dicc)
    f1 = df_dicc[years[0]]
    for year in years[1:]:
        f1 = pd.concat([f1, df_dicc[year]], names=['f1'])

    f1 = f1.dropna()  # elimina todas las filas con Nan
    f1_df = pd.DataFrame(f1.as_matrix(), index=pd.date_range('1/1/' + str(years[0]),
                                                             periods=f1.shape[0], freq='MS'))
    f1_df.columns = ['f1']
    axis = ejes[i, ]
    f1_df.plot(style='bo-', ax=axis)
    axis.axhline(y=1.1, color='g', linestyle='-')
    axis.axhline(y=0.9, color='g', linestyle='-')
    return f1_df


def plot_errores_lista(lists_path, plot_reg=False):
    n = len(lists_path)
    for i in range(n):
        df_est = pd.read_csv(lists_path[i])
        print('####################')
        print(lists_path[i])
        errores = plot_errores(df_est, plot_reg)
        plt.plot(range(len(errores)), errores)

def plot_errores(df_estimaciones, plot):

    # se filtra por puntos donde se realizó estimacion y donde existe f1
    estimacion_filtrada = df_estimaciones.loc[(df_estimaciones['f1'] > 0) &
                                              (df_estimaciones['cut'] > 0)]

    cut_poz = estimacion_filtrada['cut_poz'].as_matrix()
    cut_est = estimacion_filtrada['cut'].as_matrix()
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


# def analisis_num_muestras(path_est):


if __name__ == '__main__':
    path_estimacion = 'estimaciones/'

    # ker: RBF(3, ARD=True)
    # dist:20
    est_2 = path_estimacion + 'mp_test_all_2.csv'

    # ker: Matern52(3, ARD=True)
    # dist:20
    est_6_20 = path_estimacion + 'mp_test_all_6_20.csv'

    # ker: Matern52(3, ARD=True)
    # dist:20
    est_Mat52_20 = path_estimacion + 'mp_gp_MAt52_20.csv'

    # ker: Matern52(3, ARD=True)
    # dist:15
    est_Mat52_15 = path_estimacion + 'mp_gp_MAt52_15.csv'

    # ker: Matern52(3, ARD=True)
    # dist:25
    est_Mat52_25 = path_estimacion + 'mp_gp_MAt52_25.csv'

    # ker: Matern52(3, ARD=True)
    # dist:33
    est_6_33 = path_estimacion + 'mp_test_all_6_33.csv'

    # se grafican los resultados de kriging
    est_ok = '../kriging/modelo_estimado_sondaje_20.csv'

    paths_list = [est_2, est_Mat52_20, est_Mat52_20, est_Mat52_15, est_ok]
    plotear_f1(paths_list)
    plt.figure()
    plot_errores_lista(paths_list[:4])

    r2_gp_by_f1(est_2)
    plt.show()
