
# IMPORTACIÓN DE LAS LIBRERÍAS
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime

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
#------- Caché to download DataFrame as CSV ----------
@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')
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

    st.markdown('### Análisis general de campañas e iniciativas')
    st.write("---")
    st.markdown('En la siguiente tabla se puede visualizar las campañas registradas, teniendo en consideración la nomenclatura de los prefijos para identificar la vicepresidencia, los pilares del modelos work@tec y las diferentes vicepresidencias, así como también el número de iniciativas que conforman cada campaña.')

    campañas_general = df_campañas.groupby(["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"])["3er prefijo (area o VP)"].count().to_dict()
    df_campañas_general = pd.DataFrame([key for key in campañas_general.keys()], columns=["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"])
    df_campañas_general['Número de inicativas'] = [value for value in campañas_general.values()]
    df_campañas_general = df_campañas_general.sort_values(by=["1er prefijo (TyE)","2do prefijo (pilar)","3er prefijo (area o VP)"], ascending=True)
    st.dataframe(df_campañas_general)
    
    st.markdown('### Visualización de iniciativas por campaña')
    st.markdown('Con la campaña seleccionada a través de los filtros, podrá visualizar las iniciativas que conforman cada una de ellas.')
    st.write("---")
    
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
    df_mitec_final = pd.merge(df_mitec,df_campañas, on = "Iniciativa", how = "left")
    df_mitec_nulos = df_mitec_final.isnull().sum(axis=1)
    df_mitec_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_mitec_nulos]
    # Solo incluirá información de las iniciativas encontradas
    df_mitec_final = df_mitec_final[df_mitec_final["Estatus"] == "Encontrado"]
    #df_mitec_final["Num_prefijos"] = np.where(df_mitec_final["2do prefijo (pilar)"] == "-",2,3)
    df_mitec_final_1 = df_mitec_final[['1er prefijo (TyE)',"MITEC",
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes [Fecha]','Mes','Número de clics']]

    month_options = df_mitec_final_1["Mes"].unique().tolist()
    month_options.append("Todos los meses")
    months_selected = sidebar.multiselect("Meses:", month_options, default=["Todos los meses"])

    if "Todos los meses" in months_selected:
        df_mitec_2 = df_mitec_final_1.copy()
    else:
        df_mitec_2 = df_mitec_final_1[df_mitec_final_1["Mes"].isin(months_selected)]
    #st.write(df_mitec_2)
    #*****************************************************************************************#
    # Análisis general por mes
    st.markdown('### Análisis general por mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">El presente análisis muestra una perspectiva general del impacto de los recursos publicados en el carrusel de Mitec por mes.</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: justify;"><b>- Total de clics al mes.</b> Es la suma de los clics recibidos por todos los recursos publicados durante el mes.</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: justify;"><b>- Total de campañas al mes.</b> Corresponde a la cantidad de campañas sobre las cuales se publicaron al menos un recurso durante el mes.</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align: justify;"><b>- Número de clics promedio por campaña.</b> Es una métrica que representa el promedio de clics que recibieron cada una de las campañas sobre las que se publicaron recursos en el carrusel de MiTec.</div>', unsafe_allow_html=True)
        st.markdown('')
        # Total de clics por mes
        mitec_analisis_mes = df_mitec_final_1.groupby(["Mes [Fecha]", "Mes"], as_index=False)["Número de clics"].sum()
        mitec_analisis_mes.rename(columns = {"Número de clics":"Total de clics al mes"}, inplace=True)

        # Número de campañas por mes
        numero_campañas = []
        for mes in mitec_analisis_mes["Mes"]:
            numero_campañas.append(len(df_mitec_final_1['Nombre de campaña'][df_mitec_final_1["Mes"] == mes].unique()))
        mitec_analisis_mes["Total de campañas al mes"] = numero_campañas
        
        # Número de clics promedio por campaña
        mitec_analisis_mes.loc[:,"Número de clics promedio por campaña"] = mitec_analisis_mes.loc[:,"Total de clics al mes"]/mitec_analisis_mes.loc[:,"Total de campañas al mes"]
        mitec_analisis_mes["Total de clics al mes"] = mitec_analisis_mes["Total de clics al mes"].apply('{:,}'.format)
        mitec_analisis_mes["Número de clics promedio por campaña"] = mitec_analisis_mes["Número de clics promedio por campaña"].apply('{:.2f}'.format)
        mitec_analisis_mes = mitec_analisis_mes.iloc[:,1:]
        #------------------------------ Download button ----------------------------------
        mitec_analisis_mes_csv = convert_df(mitec_analisis_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis general por mes_Mitec_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = mitec_analisis_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.write(mitec_analisis_mes)
    
    #*****************************************************************************************#
    # Análisis por campaña y mes
    st.markdown('### Análisis por campaña y mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">El presente análisis muestra un análisis sobre el número de clics recibidos por campaña, en los meses seleccionados.</div>', unsafe_allow_html=True)
        st.markdown('')
        mitec_analisis_campaña_mes = df_mitec_2.groupby(['Nombre de campaña',"Mes [Fecha]","Mes"], as_index=False)["Número de clics"].sum()
        mitec_analisis_campaña_mes.rename(columns = {"Número de clics":"Total de clics mensuales por campaña"}, inplace=True)
        #mitec_analisis_campaña_mes["Número de clics promedio diario"] = mitec_analisis_campaña_mes["Número de clics promedio mensual"]/30
        mitec_analisis_campaña_mes = mitec_analisis_campaña_mes.sort_values(by=["Mes [Fecha]",'Nombre de campaña'], ascending=True).reset_index(drop=True)
        mitec_analisis_campaña_mes = mitec_analisis_campaña_mes[['Nombre de campaña',"Mes","Total de clics mensuales por campaña"]]
        #------------------------------ Download button ----------------------------------
        mitec_analisis_campaña_mes_csv = convert_df(mitec_analisis_campaña_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis por campaña y mes_Mitec_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = mitec_analisis_campaña_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.dataframe(mitec_analisis_campaña_mes)

    #*****************************************************************************************#
    # Análisis por iniciativa y mes
    st.markdown('### Análisis por iniciativas y mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">El presente análisis muestra un análisis sobre el número de clics recibidos por iniciativa, en los meses seleccionados.</div>', unsafe_allow_html=True)
        st.markdown('')
        mitec_analisis_iniciativa_mes = df_mitec_2.groupby(['1er prefijo (TyE)','2do prefijo (pilar)','3er prefijo (area o VP)','Nombre de campaña',"Iniciativa","Mes","Mes [Fecha]"], as_index=False)["Número de clics"].sum()
        mitec_analisis_iniciativa_mes.rename(columns = {"Número de clics":"Total de clics mensuales por iniciativa"}, inplace=True)
        #mitec_analisis_iniciativa_mes["Número de clics promedio diario"] = mitec_analisis_iniciativa_mes["Número de clics promedio mensual"]/30
        mitec_analisis_iniciativa_mes["Identificación de la iniciativa"] = mitec_analisis_iniciativa_mes['Nombre de campaña'] + "_" + mitec_analisis_iniciativa_mes["Iniciativa"]
        mitec_analisis_iniciativa_mes = mitec_analisis_iniciativa_mes.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)
        mitec_analisis_iniciativa_mes = mitec_analisis_iniciativa_mes[["Identificación de la iniciativa", "Mes", "Total de clics mensuales por iniciativa"]]
        #------------------------------ Download button ----------------------------------
        mitec_analisis_iniciativa_mes_csv = convert_df(mitec_analisis_iniciativa_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis por iniciativa y mes_Mitec_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = mitec_analisis_iniciativa_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.dataframe(mitec_analisis_iniciativa_mes)

    st.markdown('### Análisis de los refuerzos por campaña')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">En el siguiente análisis es posible visualizar el número de clics recibidos por cada refuerzo publicado para cada iniciativa, con el apoyo de los filtros de los prefijos que estructuran las campañas.</div>', unsafe_allow_html=True)
        st.markdown('')
        # LISTA DESPLEGABLES
        filtro1, filtro2, filtro3 = st.columns(3)
        # Filtro 1
        df_1 = df_mitec_2.copy()
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
        df_refuerzos = df_3[df_3["3er prefijo (area o VP)"] == TercerPrefijo]
        df_refuerzos = df_refuerzos.reset_index(drop=True)
        df_refuerzos = df_refuerzos[["MITEC", "Número de clics"]]
        st.dataframe(df_refuerzos)

#------------------------------------------------------------------------------------------------#
#------- Correos de HubSpot ----------
elif option_selected == "Correos de HubSpot":
    
    sidebar.header('Dashboard \n `Indicadores de correos de HubSpot`')

    st.title("Indicadores de rendimiento de campañas: Correos de HubSpot")
    st.write("---")

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_correos_final = pd.merge(df_correos,df_campañas, on = "Iniciativa", how = "left")
    df_nulos = df_correos_final.isnull().sum(axis=1)
    df_correos_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_nulos]
    df_correos_final = df_correos_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes', 'Mes [Fecha]', 'Correo en HubSpot', 'Responsable',
        'Enviado', 'Entregado', 'Tasa de entregas', 'Abierto',
        'Tasa de aperturas', 'Recibió clics', 'Tasa de clics',
        'Tasa de click-through']]

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

    #*****************************************************************************************#
    # Análisis general por mes
    st.markdown('### Análisis general por mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">En el siguiente apartado podrá visualizar las métricas de manera mensual.</div>', unsafe_allow_html=True)
        st.markdown('')
        df_correos = df_correos[df_correos["Enviado"] != "-"]
        correos_analisis_mes = df_correos.groupby(["Mes"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
        list_metrics_2 = ["Mes"]
        for i in range(len(metrics_selected)):
            list_metrics_2.append(metrics_selected[i])
        correos_analisis_mes = correos_analisis_mes[list_metrics_2]
        
        #------------------------------ Download button ----------------------------------
        correos_analisis_mes_csv = convert_df(correos_analisis_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis general por mes_Hubspot_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = correos_analisis_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.dataframe(correos_analisis_mes)

    #*****************************************************************************************#
    # Análisis por campaña y mes
    st.markdown('### Análisis por campaña y mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">En el siguiente apartado podrá visualizar las métricas de su preferencia por campaña.</div>', unsafe_allow_html=True)
        st.markdown('')
        df_correos_2 = df_correos_2[df_correos_2["Enviado"] != "-"]
        correos_analisis_iniciativa_mes = df_correos_2.groupby(['Nombre de campaña',"Mes"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
        list_metrics = ['Nombre de campaña',"Mes"]
        for i in range(len(metrics_selected)):
            list_metrics.append(metrics_selected[i])
        correos_analisis_iniciativa_mes = correos_analisis_iniciativa_mes[list_metrics]
        
        #------------------------------ Download button ----------------------------------
        correos_analisis_iniciativa_mes_csv = convert_df(correos_analisis_iniciativa_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis por campaña y mes_Hubspot_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = correos_analisis_iniciativa_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.dataframe(correos_analisis_iniciativa_mes)

    #*****************************************************************************************#
    # Análisis por iniciativa y mes
    st.markdown('### Análisis por iniciativas y mes')
    with st.expander("Ver análisis"):
        st.markdown('<div style="text-align: justify;">En el siguiente apartado podrá visualizar las métricas de su preferencia por iniciativa.</div>', unsafe_allow_html=True)
        st.markdown('')
        df_correos_2 = df_correos_2[df_correos_2["Enviado"] != "-"]
        correos_analisis_iniciativa_mes = df_correos_2.groupby(['1er prefijo (TyE)','2do prefijo (pilar)','3er prefijo (area o VP)','Nombre de campaña',"Iniciativa","Mes"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
        correos_analisis_iniciativa_mes["Identificación de la iniciativa"] = correos_analisis_iniciativa_mes['Nombre de campaña'] + "_" + correos_analisis_iniciativa_mes["Iniciativa"]
        list_metrics = ["Identificación de la iniciativa","Mes"]
        for i in range(len(metrics_selected)):
            list_metrics.append(metrics_selected[i])
        correos_analisis_iniciativa_mes = correos_analisis_iniciativa_mes[list_metrics]
        
        #------------------------------ Download button ----------------------------------
        correos_analisis_iniciativa_mes_csv = convert_df(correos_analisis_iniciativa_mes)
        fecha_hoy = datetime.now()
        nombre_csv = 'Analisis por iniciativa y mes_Hubspot_' + str(fecha_hoy.date()) + '.csv'
        st.download_button(label = "Descargar datos como CSV",data = correos_analisis_iniciativa_mes_csv, file_name = nombre_csv, mime = 'text/csv')
        #--------------------------------------------------------------------------------
        st.dataframe(correos_analisis_iniciativa_mes)

#------------------------------------------------------------------------------------------------#
#------- Gráficos ----------
elif option_selected == "Análisis comparativo":

    sidebar.header('Dashboard \n `Visualización de los datos`')

    st.title("Gráficos")
    st.write("---")

    ### Gráfico para el análisis de MiTec

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_mitec_final = pd.merge(df_mitec,df_campañas, on = "Iniciativa", how = "left")
    df_mitec_nulos = df_mitec_final.isnull().sum(axis=1)
    df_mitec_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_mitec_nulos]
    df_mitec_final = df_mitec_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes [Fecha]','Número de clics']]

    st.markdown('### Número de clicks recibidos por campaña a través del tiempo')
    st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido las recursos publicados en Mitec por campaña a través del tiempo.</div>', unsafe_allow_html=True)
    st.markdown('')
    # LISTA DESPLEGABLES
    filtro1, filtro2, filtro3 = st.columns(3)
    # Filtro 1
    df_1 = df_mitec_final.copy()
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
    df_mitec_campañas_final = df_3[df_3["3er prefijo (area o VP)"] == TercerPrefijo]

    
    mitec_analisis_mes = df_mitec_campañas_final.groupby(["Mes [Fecha]"], as_index=False)["Número de clics"].sum()
    mitec_analisis_mes.rename(columns = {"Número de clics":"Total de clics recibidos"}, inplace=True)
    #mitec_analisis_mes["Número de clics promedio diario"] = mitec_analisis_mes["Número de clics promedio mensual"]/30
    mitec_analisis_mes = mitec_analisis_mes.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

    fig = go.Figure([go.Scatter(x=mitec_analisis_mes['Mes [Fecha]'], y=mitec_analisis_mes['Total de clics recibidos'])])
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Total de clics recibidos",
        font=dict(family="Courier New, monospace",size=12,color="White"))
    st.write(fig)

    ### Gráfico para el análisis de los correos de Hubspot

    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_correos_final = pd.merge(df_correos,df_campañas, on = "Iniciativa", how = "left")
    df_nulos = df_correos_final.isnull().sum(axis=1)
    df_correos_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_nulos]
    df_correos_final = df_correos_final[['1er prefijo (TyE)',
        '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus',
        'Mes', 'Mes [Fecha]', 'Correo en HubSpot', 'Responsable',
        'Enviado', 'Entregado', 'Tasa de entregas', 'Abierto',
        'Tasa de aperturas', 'Recibió clics', 'Tasa de clics',
        'Tasa de click-through']]
    
    metric_options_g = ["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                    "Recibió clics","Tasa de clics","Tasa de click-through"]
    metric_selected = st.sidebar.selectbox("Métricas a analizar:", metric_options_g, 7)
    titulo = str(metric_selected) + ' por campaña a través del tiempo'
    st.markdown('### Total de '+ titulo)
    st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido los correos enviados por Hubspot para la campaña seleccionada a través del tiempo, considerando la métrica de su preferencia.</div>', unsafe_allow_html=True)
    st.markdown('')

    df_correos = df_correos[df_correos["Enviado"] != "-"]
    correos_analisis_mes = df_correos.groupby(['Mes',"Mes [Fecha]"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
    list_metrics_3 = ['Mes',"Mes [Fecha]"]
    list_metrics_3.append(metric_selected)
    correos_analisis_mes = correos_analisis_mes[list_metrics_3]
    correos_analisis_mes = correos_analisis_mes.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

    fig2 = go.Figure([go.Scatter(x=correos_analisis_mes['Mes'], y=correos_analisis_mes[metric_selected])])
    fig2.update_layout(
        xaxis_title="Mes",
        yaxis_title="Promedio de " + metric_selected,
        font=dict(family="Courier New, monospace",size=12,color="White"))
    st.write(fig2)