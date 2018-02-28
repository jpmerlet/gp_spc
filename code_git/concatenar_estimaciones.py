from code_git.visualizacion_estimacion import *

if __name__ == '__main__':
    path_est_gp = 'estimaciones/mp_GP_rbf_33.csv'
    path_est_ok = '../kriging/modelo_estimado_sondaje_20.csv'

    # se generan los dataFrame con las dos estimaciones ordenadas por f1
    # df_est_gp = add_year_month_sorted(path_est_gp)
    # df_est_ok = add_year_month_sorted(path_est_ok)
    df_est_gp = pd.read_csv(path_est_gp)
    df_est_ok = pd.read_csv(path_est_ok)

    # solo considerar los valores estimados en ambos modelos
    df_est_gp = df_est_gp.loc[df_est_gp['cut'] > 0]
    df_est_ok = df_est_ok.loc[df_est_ok['cut'] > 0]
    df_est_gp.rename(columns={'cut': 'cut_gp'}, inplace=True)
    df_est_ok.rename(columns={'cut': 'cut_ok'}, inplace=True)
    print('cantidad de filas en ok:{}\ncantidad de filas en gp:{}'.format(df_est_ok.shape[0], df_est_gp.shape[0]))

    # se adjuntan una columna con las estimaciones de gp a el dataframe de ok

    # print(df_est_gp.head())
    # print(df_est_ok.head())

    df_concatenated = pd.merge(df_est_ok, df_est_gp, on=['xcentre', 'ycentre', 'zcentre'])
    # print(df_concatenated.head())
    df_concatenated.rename(columns={'cut_poz_x': 'cut_poz'}, inplace=True)
    # df_concatenated.rename(columns={'cut_x': 'cut_gp'}, inplace=True)
    # df_concatenated.rename(columns={'cut_y': 'cut_ok'}, inplace=True)
    df_final = df_concatenated[['xcentre', 'ycentre', 'zcentre', 'cut_ok', 'cut_gp', 'cut_poz', 'f1_x']]
    df_final.rename(columns={'f1_x': 'f1'}, inplace=True)
    df_final.to_csv('estimaciones/estimaciones_gp_ok_all')
    print(df_final.shape)
    # print(df_final.head())
