from code_git.visualizacion_estimacion import *

if __name__ == '__main__':
    path_est_gp = 'estimaciones/mp_test_all_2.csv'
    path_est_ok = '../kriging/modelo_estimado_sondaje_20.csv'

    # se generan los dataFrame con las dos estimaciones ordenadas por f1
    df_est_gp = add_year_month_sorted(path_est_gp)
    df_est_ok = add_year_month_sorted(path_est_ok)

    print('cantidad de filas en ok:{}\ncantidad de filas en gp:{}'.format(df_est_ok.shape[0], df_est_gp.shape[0]))

    # se adjuntan una columna con las estimaciones de gp a el dataframe de ok

    # print(df_est_gp.head())
    # print(df_est_ok.head())

    df_concatenated = pd.merge(df_est_ok, df_est_gp, on=['xcentre', 'ycentre', 'zcentre'])
    # print(df_concatenated.head())
    df_concatenated.rename(columns={'cut_poz_x': 'cut_poz'}, inplace=True)
    df_concatenated.rename(columns={'cut': 'cut_gp'}, inplace=True)
    df_final = df_concatenated[['xcentre', 'ycentre', 'zcentre', 'cut_ok', 'cut_gp']]
    df_final.to_csv('estimaciones_gp_ok')
    print(df_final.shape)
    # print(df_final.head())
