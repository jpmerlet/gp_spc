import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp

# se cargan los datos de entrenamiento
train_data = pd.read_csv('../../GP_Data/cy17_spc_assays_rl6_entry.csv')
train_cols = ['midx', 'midy', 'midz', 'cut']

test_data = pd.read_csv('../../GP_Data/12_BLASTHOLE_ASS_ENTRY.csv')
test_cols = ['POINTEAST', 'POINTNORTH', 'POINTRL']


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
    # al archivo dque contiene las estimacines
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


def dicc_error_volumen(path_est):
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


path_estimacion = 'estimaciones/'
# # ker: Matern32(3, ARD=True)
# path_estimacion_5 = 'mp_test_all_5.csv'
# dicc_5 = dicc_error_volumen(path_estimacion_5)

# ker: RBF(3, ARD=True)
# est_2 = 'mp_test_all_2.csv'
# dicc_2 = dicc_error_volumen(path_estimacion+est_2)
#
# # ker: sum_{i = 1}^3 RBF(x_i)
# path_estimacion_4 = 'mp_test_all_4.csv'
# dicc_4 = dicc_error_volumen(path_estimacion_4)

# ker: RBF(3, ARD=True)
est_6 = 'mp_test_all_2_transformed.csv'
dicc_6 = dicc_error_volumen(path_estimacion+est_6)
plt.show()
