
# IMPORTACIÓN DE LAS LIBRERÍAS
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu


#------------------------------------------------------------------------------------------------#
# IMPORTACIÓN DE LA BASE DE DATOS
df_campañas = pd.read_excel("Indicadores de anuncios de colaboradores.xlsx", sheet_name='Campañas y correos')
df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
df_mitec = pd.read_excel("Indicadores de anuncios de colaboradores.xlsx", sheet_name='AnálisisMITEC', parse_dates=['Mes [Fecha]'])
df_correos = pd.read_excel("Indicadores de anuncios de colaboradores.xlsx", sheet_name='AnálisisCorreos', parse_dates=['Mes [Fecha]'])
df_comparativo = pd.read_excel("Indicadores de anuncios de colaboradores.xlsx", sheet_name='AnálisisComparativo')

#------------------------------------------------------------------------------------------------#
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
#This code helps to hide the main menu of Streamlit
hide_st_style = """
			<style>
			#MainMenu {visibility: hidden;}
			footer {visibility: hidden;}
			header {visibility: hidden;}
			</style>
			"""
st.markdown(hide_st_style, unsafe_allow_html=True)

#------------------------------------------------------------------------------------------------#
#------- Navigation Menu ----------

option_selected = option_menu(
	menu_title=None,
	options=["Campañas e iniciativas", "MiTEC", "Correos de HubSpot", "Análisis comparativo"],
    orientation="horizontal"
)
#------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------#
# SIDEBAR
sidebar = st.sidebar
#------------------------------------------------------------------------------------------------#
#------- Campañas e iniciativas ----------
if option_selected == "Campañas e iniciativas":
    # CONFIGURACIÓN DE LA PÁGINA Y EL SIDEBAR
    
    #sidebar.header('Dashboard \n `Indicadores`')

    st.title("Indicadores de rendimiento de campañas: MiTec y HubSpot")
    st.write("---")

    st.markdown('### Análisis general de camapañas e iniciativas')
    st.write("---")

    campañas_general = df_campañas.groupby(["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"])["3er prefijo (area o VP)"].count().to_dict()
    df_campañas_general = pd.DataFrame([key for key in campañas_general.keys()], columns=["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"])
    df_campañas_general['Número de inicativas'] = [value for value in campañas_general.values()]
    df_campañas_general = df_campañas_general.sort_values(by=["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"], ascending=True)
    st.dataframe(df_campañas_general)
    
    st.markdown('### Visualización de iniciativas por campaña')

    # LISTA DESPLEGABLES
    filtro1, filtro2, filtro3 = st.columns(3)

    # Filtro 1
    df_1 = df_campañas.copy()
    PrimerPrefijo_options = df_1["1er prefijo (TyE)"].unique().tolist()
    PrimerPrefijo = filtro1.selectbox("1er prefijo:", PrimerPrefijo_options, 0)

    # Filtro 2
    df_2 = df_1[df_1["1er prefijo (TyE)"] == PrimerPrefijo]
    SegundoPrefijo_options = df_2["2do prefijo (pilar)"].unique().tolist()
    SegundoPrefijo = filtro2.selectbox("2do prefijo:", SegundoPrefijo_options, 0)

    # Filtro 3
    df_3 = df_2[df_2["2do prefijo (pilar)"] == SegundoPrefijo]
    TercerPrefijo_options = df_3["3er prefijo (area o VP)"].unique().tolist()
    TercerPrefijo = filtro3.selectbox("3er prefijo:", TercerPrefijo_options, 0)

    st.write("---")

    df_iniciativas = df_3[df_3["3er prefijo (area o VP)"] == TercerPrefijo]
    df_iniciativas = df_iniciativas.reset_index(drop=True)
    df_iniciativas = df_iniciativas[["1er prefijo (TyE)", "2do prefijo (pilar)", "3er prefijo (area o VP)", "Nombre de campaña","Iniciativa"]]

    st.dataframe(df_iniciativas)

#------------------------------------------------------------------------------------------------#
#------- MiTEC ----------
elif option_selected == "MiTEC":
    
    sidebar.header('Dashboard \n `Indicadores de MITEC`')

    st.title("Indicadores de rendimiento de campañas: MITEC")
    st.write("---")

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_mitec_final = pd.merge(df_mitec,df_campañas, how = "left")
    df_mitec_nulos = df_mitec_final.isnull().sum(axis=1)
    df_mitec_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_mitec_nulos]
    # Solo incluirá información de las iniciativas encontradas
    df_mitec_final = df_mitec_final[df_mitec_final["Estatus"] == "Encontrado"]
    df_mitec_final["Num_prefijos"] = np.where(df_mitec_final["2do prefijo (pilar)"] == "-",2,3)
    df_mitec_final_1 = df_mitec_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes','Número de clics']]
    df_mitec_final_2 = df_mitec_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa',"Num_prefijos",
        'Estatus','Mes','Número de clics']]
    #df_mitec_final_1.head(3)

    month_options = df_mitec_final_1["Mes"].unique().tolist()
    month_options.append("Todos los meses")
    months_selected = sidebar.multiselect("Meses:", month_options, default=["Todos los meses"])

    if "Todos los meses" in months_selected:
        df_mitec_2 = df_mitec_final_1.copy()
    else:
        df_mitec_2 = df_mitec_final_1[df_mitec_final_1["Mes"].isin(months_selected)]
    # Análisis por iniciativa y mes
    st.markdown('### Análisis por iniciativas y mes')
    with st.expander("Ver análisis"):
        mitec_analisis_iniciativa_mes = df_mitec_2.groupby(['1er prefijo (TyE)','2do prefijo (pilar)','3er prefijo (area o VP)','Nombre de campaña',"Iniciativa","Mes"], as_index=False)["Número de clics"].mean()
        mitec_analisis_iniciativa_mes.rename(columns = {"Número de clics":"Número de clics promedio mensual"}, inplace=True)
        mitec_analisis_iniciativa_mes["Número de clics promedio diario"] = mitec_analisis_iniciativa_mes["Número de clics promedio mensual"]/30
        mitec_analisis_iniciativa_mes = mitec_analisis_iniciativa_mes.sort_values(by=["Mes"], ascending=True).reset_index(drop=True)
        st.dataframe(mitec_analisis_iniciativa_mes)

    # Análisis por campaña y mes
    st.markdown('### Análisis por campaña y mes')
    with st.expander("Ver análisis"):
        mitec_analisis_campaña_mes = df_mitec_2.groupby(['Nombre de campaña',"Mes"], as_index=False)["Número de clics"].mean()
        mitec_analisis_campaña_mes.rename(columns = {"Número de clics":"Número de clics promedio mensual"}, inplace=True)
        mitec_analisis_campaña_mes["Número de clics promedio diario"] = mitec_analisis_campaña_mes["Número de clics promedio mensual"]/30
        mitec_analisis_campaña_mes = mitec_analisis_campaña_mes.sort_values(by=["Mes"], ascending=True).reset_index(drop=True)
        st.dataframe(mitec_analisis_campaña_mes)

    # Análisis por iniciativa y mes
    st.markdown('### Análisis general por mes')
    with st.expander("Ver análisis"):
        mitec_analisis_mes = df_mitec.groupby(["Mes"], as_index=False)["Número de clics"].mean()
        mitec_analisis_mes.rename(columns = {"Número de clics":"Número de clics promedio mensual"}, inplace=True)
        mitec_analisis_mes["Número de clics promedio diario"] = mitec_analisis_mes["Número de clics promedio mensual"]/30
        mitec_analisis_mes = mitec_analisis_mes.sort_values(by=["Mes"], ascending=True).reset_index(drop=True)
        st.dataframe(mitec_analisis_mes)

    # Construcción del gráfico de Sankey
    st.markdown('### Gráficas')
    st.radio("Seleccione el número de prefijos de las campañas a analizar:",[2, 3], index=1)
    st.write(df_mitec_final_2)

#------------------------------------------------------------------------------------------------#
#------- Correos de HubSpot ----------
elif option_selected == "Correos de HubSpot":
    
    sidebar.header('Dashboard \n `Indicadores de correos de HubSpot`')

    st.title("Indicadores de rendimiento de campañas: Correos de HubSpot")
    st.write("---")

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_correos_final = pd.merge(df_correos,df_campañas, how = "left")
    df_nulos = df_correos_final.isnull().sum(axis=1)
    df_correos_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_nulos]
    df_correos_final = df_correos_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes', 'Mes [Fecha]', 'Correo en HubSpot', 'Responsable',
        'Enviado', 'Entregado', 'Tasa de entregas', 'Abierto',
        'Tasa de aperturas', 'Recibió clics', 'Tasa de clics',
        'Tasa de click-through']]
    df_correos_final.head(3)

    metric_options = ["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                    "Recibió clics","Tasa de clics","Tasa de click-through"]
    metrics_selected = st.sidebar.multiselect("Métricas a analizar:", metric_options, default=["Tasa de click-through"])

    month_options = df_correos_final["Mes"].unique().tolist()
    month_options.append("Todos los meses")
    months_selected = sidebar.multiselect("Meses:", month_options, default=["Todos los meses"])

    if "Todos los meses" in months_selected:
        df_correos_2 = df_correos_final.copy()
    else:
        df_correos_2 = df_correos_final[df_correos_final["Mes"].isin(months_selected)]
    # Análisis por iniciativa y mes
    st.markdown('### Análisis por iniciativas y mes')
    with st.expander("Ver análisis"):
        df_correos_2 = df_correos_2[df_correos_2["Enviado"] != "-"]
        correos_analisis_iniciativa_mes = df_correos_2.groupby(['1er prefijo (TyE)','2do prefijo (pilar)','3er prefijo (area o VP)','Nombre de campaña',"Iniciativa","Mes"], as_index=False)["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"].mean()
        list_metrics = ['1er prefijo (TyE)','2do prefijo (pilar)','3er prefijo (area o VP)','Nombre de campaña',"Iniciativa","Mes"]
        for i in range(len(metrics_selected)):
            list_metrics.append(metrics_selected[i])
        correos_analisis_iniciativa_mes = correos_analisis_iniciativa_mes[list_metrics]
        st.dataframe(correos_analisis_iniciativa_mes)

    # Análisis por campaña y mes
    st.markdown('### Análisis por campaña y mes')
    with st.expander("Ver análisis"):
        df_correos_2 = df_correos_2[df_correos_2["Enviado"] != "-"]
        correos_analisis_iniciativa_mes = df_correos_2.groupby(['Nombre de campaña',"Mes"], as_index=False)["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"].mean()
        list_metrics = ['Nombre de campaña',"Mes"]
        for i in range(len(metrics_selected)):
            list_metrics.append(metrics_selected[i])
        correos_analisis_iniciativa_mes = correos_analisis_iniciativa_mes[list_metrics]
        st.dataframe(correos_analisis_iniciativa_mes)

    # Análisis por iniciativa y mes
    st.markdown('### Análisis general por mes')
    with st.expander("Ver análisis"):
        df_correos = df_correos[df_correos["Enviado"] != "-"]
        correos_analisis_mes = df_correos.groupby(["Mes"], as_index=False)["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"].mean()
        list_metrics_2 = ["Mes"]
        for i in range(len(metrics_selected)):
            list_metrics_2.append(metrics_selected[i])
        correos_analisis_mes = correos_analisis_mes[list_metrics_2]
        st.dataframe(correos_analisis_mes)

#------------------------------------------------------------------------------------------------#
#------- Gráficos ----------
elif option_selected == "Análisis comparativo":

    sidebar.header('Dashboard \n `Visualización de los datos`')

    st.title("Gráficos")
    st.write("---")

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_mitec_final = pd.merge(df_mitec,df_campañas, how = "left")
    df_mitec_nulos = df_mitec_final.isnull().sum(axis=1)
    df_mitec_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_mitec_nulos]
    df_mitec_final = df_mitec_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes [Fecha]','Número de clics']]
    
    mitec_analisis_mes = df_mitec.groupby(["Mes [Fecha]"], as_index=False)["Número de clics"].mean()
    mitec_analisis_mes.rename(columns = {"Número de clics":"Número de clics promedio mensual"}, inplace=True)
    mitec_analisis_mes["Número de clics promedio diario"] = mitec_analisis_mes["Número de clics promedio mensual"]/30
    mitec_analisis_mes = mitec_analisis_mes.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

    fig = go.Figure([go.Scatter(x=mitec_analisis_mes['Mes [Fecha]'], y=mitec_analisis_mes['Número de clics promedio mensual'])])
    st.markdown('### Número de clicks a través del tiempo')
    st.write(fig)