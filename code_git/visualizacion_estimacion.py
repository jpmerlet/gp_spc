import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp


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
    # con los datos ordenados por f1 (que es )
    # lo mismo que ordenar por fecha
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


def plotear_f1_gp(path_est):
    estimacion_sorted = add_year_month_sorted(path_est)
    YEARS = get_years(path_est)
    dicc_anual = dict()
    for year in YEARS:
        df_by_year = estimacion_sorted.loc[estimacion_sorted['year'] == year]
        meses = df_by_year['mes']
        seen = set()
        MESES = []  # se eliminan los meses repetidos
        for mes in meses:
            if mes not in seen:
                seen.add(mes)
                MESES.append(mes)
        dicc_cuociente_mensual = dict()  # mes: cut_poz.mean()/cut.mean()
        for mes in MESES:
            cut_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut']
            cut_poz_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut_poz']
            cuociente = np.divide(cut_poz_mes.mean(), cut_mes.mean())
            dicc_cuociente_mensual[mes] = cuociente
        dicc_anual[year] = dicc_cuociente_mensual

    _plot_f1(dicc_anual, YEARS)
    return dicc_anual


def add_year_month_sorted_ok(path_est):
    estimacion_original = pd.read_csv(path_est)
    estimacion_filtrada = estimacion_original.loc[(estimacion_original['f1'] > 0) &
                                                  (estimacion_original['cut_ok'] > 0)]
    f1 = estimacion_filtrada['f1'].as_matrix()
    estimacion = cp.copy(estimacion_filtrada)
    estimacion = estimacion.assign(year=((f1 - 1) / 12).astype(int) + 2014)
    estimacion = estimacion.assign(mes=((f1 - 1) % 12 + 1).astype(int))
    estimacion_sorted = estimacion.sort_values('f1', ascending=True)
    return estimacion_sorted


def plotear_f1_ok(path_est):
    estimacion_sorted = add_year_month_sorted_ok(path_est)
    years_rep = estimacion_sorted['year']
    years = sacar_repeticiones(years_rep)
    dicc_anual = dict()
    for year in years:
        df_by_year = estimacion_sorted.loc[estimacion_sorted['year'] == year]
        meses = df_by_year['mes']
        MESES = sacar_repeticiones(meses)
        dicc_cuociente_mensual = dict()  # mes: cut_poz.mean()/cut.mean()
        for mes in MESES:
            cut_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut_ok']
            cut_poz_mes = df_by_year.loc[df_by_year['mes'] == mes]['cut_poz']
            cuociente = np.divide(cut_poz_mes.mean(), cut_mes.mean())
            dicc_cuociente_mensual[mes] = cuociente
        dicc_anual[year] = dicc_cuociente_mensual

    _plot_f1(dicc_anual, years)
    return dicc_anual


def _plot_f1(dicc, years):
    df_dicc = pd.DataFrame.from_dict(dicc)
    f1 = df_dicc[years[0]]
    for year in years[1:]:
        f1 = pd.concat([f1, df_dicc[year]], names=['f1'])

    f1 = f1.dropna()  # elimina todas las filas con Nan
    f1_df = pd.DataFrame(f1.as_matrix(), index=pd.date_range('1/1/' + str(years[0]),
                                                             periods=f1.shape[0], freq='MS'))
    f1_df.columns = ['f1']
    f1_df.plot(style='bo-')
    plt.axhline(y=1.1, color='g', linestyle='-')
    plt.axhline(y=0.9, color='g', linestyle='-')
    return f1_df


if __name__ == '__main__':

    path_estimacion = 'estimaciones/'
    # # ker: Matern32(3, ARD=True)
    # path_estimacion_5 = 'mp_test_all_5.csv'
    # dicc_5 = dicc_error_volumen(path_estimacion_5)

    # ker: RBF(3, ARD=True)
    est_2 = 'mp_test_all_2.csv'
    dicc_2 = plotear_f1_gp(path_estimacion+est_2)
    #
    # # ker: sum_{i = 1}^3 RBF(x_i)
    # path_estimacion_4 = 'mp_test_all_4.csv'
    # dicc_4 = dicc_error_volumen(path_estimacion_4)

    # ker: RBF(3, ARD=True)
    # est_6 = 'mp_test_all_2_transformed.csv'
    # dicc_6 = plotear_f1_gp(path_estimacion+est_6)

    # se grafican los resultados de kriging
    est_ok = '../kriging/modelo_estimado_sondaje_20.csv'
    plotear_f1_ok(est_ok)
    plt.show()
