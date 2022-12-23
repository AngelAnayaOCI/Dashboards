
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
	options=["Campañas e iniciativas", "MiTEC", "Correos de HubSpot"],
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


    st.title("Gráficos")
    st.write("---")

    #-------------------------------------------------------------------------------------
    ### Gráfico para el análisis de MiTec
    #st.markdown("## Análisis de MiTEC")
    #st.markdown('')
    tipo_analisis_mitec = st.radio("Seleccione el nivel de análisis que desea visualizar en los gráficos:",
                                ('Nivel campaña', 'Nivel iniciativa'), key = "Mitec", index = 0)
    st.markdown('')
    df_campañas["2do prefijo (pilar)"].fillna('-', inplace = True)
    df_mitec_final = pd.merge(df_mitec,df_campañas, on = "Iniciativa", how = "left")
    df_mitec_nulos = df_mitec_final.isnull().sum(axis=1)
    df_mitec_final["Estatus"] = ["No encontrado" if num_nulos>2 else "Encontrado" for num_nulos in df_mitec_nulos]
    df_mitec_final = df_mitec_final[['1er prefijo (TyE)',
            '2do prefijo (pilar)', '3er prefijo (area o VP)','Nombre de campaña','Iniciativa','Estatus','Mes',
            'Mes [Fecha]','Número de clics']]
    
    if tipo_analisis_mitec == "Nivel campaña":
        st.markdown('#### Número de clicks recibidos por campaña a través del tiempo')
        st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido las recursos publicados en Mitec por campaña a través del tiempo.</div>', unsafe_allow_html=True)
        st.markdown('')
    
        # LISTA DESPLEGABLES || MITEC
        filtro1_mitec_1, filtro2_mitec_1, filtro3_mitec_1 = st.columns(3)
        # Filtro 1
        df_1_mitec_1 = df_mitec_final.copy()
        PrimerPrefijo_mitec_options_1 = df_1_mitec_1["1er prefijo (TyE)"].unique().tolist()
        PrimerPrefijo_mitec_1 = filtro1_mitec_1.selectbox("1er prefijo:", PrimerPrefijo_mitec_options_1, 0, key = "Mitec_campaña_1")
        # Filtro 2
        df_2_mitec_1 = df_1_mitec_1[df_1_mitec_1["1er prefijo (TyE)"] == PrimerPrefijo_mitec_1]
        SegundoPrefijo_mitec_options_1 = df_2_mitec_1["2do prefijo (pilar)"].unique().tolist()
        SegundoPrefijo_mitec_1 = filtro2_mitec_1.selectbox("2do prefijo:", SegundoPrefijo_mitec_options_1, 0, key = "Mitec_campaña_2")
        # Filtro 3
        df_3_mitec_1 = df_2_mitec_1[df_2_mitec_1["2do prefijo (pilar)"] == SegundoPrefijo_mitec_1]
        TercerPrefijo_mitec_options_1 = df_3_mitec_1["3er prefijo (area o VP)"].unique().tolist()
        TercerPrefijo_mitec_1 = filtro3_mitec_1.selectbox("3er prefijo:", TercerPrefijo_mitec_options_1, 0, key = "Mitec_campaña_3")
        st.write("---")
        df_mitec_campañas_final_1 = df_3_mitec_1[df_3_mitec_1["3er prefijo (area o VP)"] == TercerPrefijo_mitec_1]

        mitec_analisis_mes_1 = df_mitec_campañas_final_1.groupby(["Mes","Mes [Fecha]"], as_index=False)["Número de clics"].sum()
        mitec_analisis_mes_1.rename(columns = {"Número de clics":"Total de clics recibidos"}, inplace=True)
        mitec_analisis_mes_1 = mitec_analisis_mes_1.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

        fig_mitec_1 = go.Figure([go.Scatter(x=mitec_analisis_mes_1['Mes'], y=mitec_analisis_mes_1['Total de clics recibidos'])])
        fig_mitec_1.update_layout(
            xaxis_title="Mes",
            yaxis_title="Total de clics recibidos",
            font=dict(family="Courier New, monospace",size=12,color="Black"))
        
        left_column_mitec_1, right_column_mitec_1 = st.columns([1, 3])
        with left_column_mitec_1:
            st.write(mitec_analisis_mes_1[['Mes','Total de clics recibidos']])
        with right_column_mitec_1:
            st.write(fig_mitec_1)
    else:
        st.markdown('#### Número de clicks recibidos por iniciativa a través del tiempo')
        st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido las recursos publicados en Mitec por iniciativa a través del tiempo.</div>', unsafe_allow_html=True)
        st.markdown('')
    
        # LISTA DESPLEGABLES || MITEC
        filtro1_mitec_2, filtro2_mitec_2, filtro3_mitec_2, filtro4_mitec_2 = st.columns(4)
        # Filtro 1
        df_1_mitec_2 = df_mitec_final.copy()
        PrimerPrefijo_mitec_options_2 = df_1_mitec_2["1er prefijo (TyE)"].unique().tolist()
        PrimerPrefijo_mitec_2 = filtro1_mitec_2.selectbox("1er prefijo:", PrimerPrefijo_mitec_options_2, 0, key = "Mitec_iniciativa_1")
        # Filtro 2
        df_2_mitec_2 = df_1_mitec_2[df_1_mitec_2["1er prefijo (TyE)"] == PrimerPrefijo_mitec_2]
        SegundoPrefijo_mitec_options_2 = df_2_mitec_2["2do prefijo (pilar)"].unique().tolist()
        SegundoPrefijo_mitec_2 = filtro2_mitec_2.selectbox("2do prefijo:", SegundoPrefijo_mitec_options_2, 0, key = "Mitec_iniciativa_2")
        # Filtro 3
        df_3_mitec_2 = df_2_mitec_2[df_2_mitec_2["2do prefijo (pilar)"] == SegundoPrefijo_mitec_2]
        TercerPrefijo_mitec_options_2 = df_3_mitec_2["3er prefijo (area o VP)"].unique().tolist()
        TercerPrefijo_mitec_2 = filtro3_mitec_2.selectbox("3er prefijo:", TercerPrefijo_mitec_options_2, 0, key = "Mitec_iniciativa_3")
        # Filtro 4
        df_4_mitec_2 = df_3_mitec_2[df_3_mitec_2["3er prefijo (area o VP)"] == TercerPrefijo_mitec_2]
        Iniciativa_mitec_options_2 = df_4_mitec_2["Iniciativa"].unique().tolist()
        Iniciativa_mitec_2 = filtro4_mitec_2.selectbox("Iniciativa:", Iniciativa_mitec_options_2, 0, key = "Mitec_iniciativa_4")
        
        st.write("---")
        df_mitec_campañas_final_2 = df_4_mitec_2[df_4_mitec_2["Iniciativa"] == Iniciativa_mitec_2]

        mitec_analisis_mes_2 = df_mitec_campañas_final_2.groupby(["Mes","Mes [Fecha]"], as_index=False)["Número de clics"].sum()
        mitec_analisis_mes_2.rename(columns = {"Número de clics":"Total de clics recibidos"}, inplace=True)
        mitec_analisis_mes_2 = mitec_analisis_mes_2.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

        fig_mitec_2 = go.Figure([go.Scatter(x=mitec_analisis_mes_2['Mes'], y=mitec_analisis_mes_2['Total de clics recibidos'])])
        fig_mitec_2.update_layout(
            xaxis_title="Mes",
            yaxis_title="Total de clics recibidos",
            font=dict(family="Courier New, monospace",size=12,color="Black"))
        
        left_column_mitec_2, right_column_mitec_2 = st.columns([1, 3])
        with left_column_mitec_2:
            st.write(mitec_analisis_mes_2[['Mes','Total de clics recibidos']])
        with right_column_mitec_2:
            st.write(fig_mitec_2)


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

    #-------------------------------------------------------------------------------------
    ### Gráfico para el análisis de los correos de Hubspot
    st.markdown("## Gráficos")
    st.markdown('----------------------')
    tipo_analisis_correos = st.radio("Seleccione el nivel de análisis que desea visualizar en los gráficos:",
                                ('Nivel general','Nivel campaña', 'Nivel iniciativa'), key = "Correos", index = 0)
    st.markdown('')
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
    df_correos_final = df_correos_final[df_correos_final["Enviado"] != "-"]
    
    metric_options_graphic = ["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                        "Recibió clics","Tasa de clics","Tasa de click-through"]
    metric_selected_graphic = st.selectbox("Métricas a analizar de los correos de HubSpot:", metric_options_graphic, 7)
    
    st.markdown('----------------------')
    with st.expander("Ver gráficos"):
        if tipo_analisis_correos == 'Nivel general':
            titulo_1_0 = str(metric_selected_graphic) + ' por campaña a través del tiempo'
            st.markdown('### Total de '+ titulo_1_0)
            st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido los correos enviados por Hubspot a través del tiempo, considerando la métrica de su preferencia.</div>', unsafe_allow_html=True)
            st.markdown('')

            fig_correos_0 = go.Figure([go.Scatter(x = correos_analisis_mes['Mes'], 
                                        y = correos_analisis_mes[metric_selected_graphic])])
            fig_correos_0.update_layout(
                xaxis_title="Mes",
                yaxis_title="Promedio de " + metric_selected_graphic,
                font=dict(family="Courier New, monospace",size=12,color="Black"))
            
            left_column_correos_0, right_column_correos_0 = st.columns([1, 3])
            with left_column_correos_0:
                list_with_metric_output_0 = ['Mes']
                list_with_metric_output_0.append(metric_selected_graphic)
                st.write(correos_analisis_mes[list_with_metric_output_0])
            with right_column_correos_0:
                st.write(fig_correos_0)

        elif tipo_analisis_correos == 'Nivel campaña':
            titulo_1 = str(metric_selected_graphic) + ' por campaña a través del tiempo'
            st.markdown('### Total de '+ titulo_1)
            st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido los correos enviados por Hubspot para la campaña seleccionada a través del tiempo, considerando la métrica de su preferencia.</div>', unsafe_allow_html=True)
            st.markdown('')

            # LISTA DESPLEGABLES
            filtro1_correos_1, filtro2_correos_1, filtro3_correos_1 = st.columns(3)
            # Filtro 1
            df_1_correos_1 = df_correos_final.copy()
            PrimerPrefijo_correos_options_1 = df_1_correos_1["1er prefijo (TyE)"].unique().tolist()
            PrimerPrefijo_correos_1 = filtro1_correos_1.selectbox("1er prefijo:", PrimerPrefijo_correos_options_1, 0, key = "Correos_campañas_1")
            # Filtro 2
            df_2_correos_1 = df_1_correos_1[df_1_correos_1["1er prefijo (TyE)"] == PrimerPrefijo_correos_1]
            SegundoPrefijo_correos_options_1 = df_2_correos_1["2do prefijo (pilar)"].unique().tolist()
            SegundoPrefijo_correos_1 = filtro2_correos_1.selectbox("2do prefijo:", SegundoPrefijo_correos_options_1, 0, key = "Correos_campañas_2")
            # Filtro 3
            df_3_correos_1 = df_2_correos_1[df_2_correos_1["2do prefijo (pilar)"] == SegundoPrefijo_correos_1]
            TercerPrefijo_correos_options_1 = df_3_correos_1["3er prefijo (area o VP)"].unique().tolist()
            TercerPrefijo_correos_1 = filtro3_correos_1.selectbox("3er prefijo:", TercerPrefijo_correos_options_1, 0, key = "Correos_campañas_3")
            st.write("---")

            df_correos_final_otro_1 = df_3_correos_1[df_3_correos_1["3er prefijo (area o VP)"] == TercerPrefijo_correos_1]
            correos_analisis_mes_1 = df_correos_final_otro_1.groupby(['Mes',"Mes [Fecha]"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                                "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
            list_with_metric_1 = ['Mes',"Mes [Fecha]"]
            list_with_metric_1.append(metric_selected_graphic)
            #st.write(list_with_metric)
            correos_analisis_mes_with_metric_1 = correos_analisis_mes_1[list_with_metric_1]
            correos_analisis_mes_with_metric_1 = correos_analisis_mes_with_metric_1.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

            
            fig_correos_1 = go.Figure([go.Scatter(x = correos_analisis_mes_with_metric_1['Mes'], 
                                        y = correos_analisis_mes_with_metric_1[metric_selected_graphic])])
            fig_correos_1.update_layout(
                xaxis_title="Mes",
                yaxis_title="Promedio de " + metric_selected_graphic,
                font=dict(family="Courier New, monospace",size=12,color="Black"))
            
            left_column_correos_1, right_column_correos_1 = st.columns([1, 3])
            with left_column_correos_1:
                list_with_metric_output_1 = ['Mes']
                list_with_metric_output_1.append(metric_selected_graphic)
                st.write(correos_analisis_mes_with_metric_1[list_with_metric_output_1])
            with right_column_correos_1:
                st.write(fig_correos_1)
        else:
            titulo_2 = str(metric_selected_graphic) + ' por iniciativa a través del tiempo'
            st.markdown('### Total de '+ titulo_2)
            st.markdown('<div style="text-align: justify;">En el siguiente gráfico podrá visualizar el impacto que han tenido los correos enviados por Hubspot para la iniciativa seleccionada a través del tiempo, considerando la métrica de su preferencia.</div>', unsafe_allow_html=True)
            st.markdown('')

            # LISTA DESPLEGABLES
            filtro1_correos_2, filtro2_correos_2, filtro3_correos_2, filtro4_correos_2 = st.columns(4)
            # Filtro 1
            df_1_correos_2 = df_correos_final.copy()
            PrimerPrefijo_correos_options_2 = df_1_correos_2["1er prefijo (TyE)"].unique().tolist()
            PrimerPrefijo_correos_2 = filtro1_correos_2.selectbox("1er prefijo:", PrimerPrefijo_correos_options_2, 0, key = "Correos_iniciativas_1")
            # Filtro 2
            df_2_correos_2 = df_1_correos_2[df_1_correos_2["1er prefijo (TyE)"] == PrimerPrefijo_correos_2]
            SegundoPrefijo_correos_options_2 = df_2_correos_2["2do prefijo (pilar)"].unique().tolist()
            SegundoPrefijo_correos_2 = filtro2_correos_2.selectbox("2do prefijo:", SegundoPrefijo_correos_options_2, 0, key = "Correos_iniciativas_2")
            # Filtro 3
            df_3_correos_2 = df_2_correos_2[df_2_correos_2["2do prefijo (pilar)"] == SegundoPrefijo_correos_2]
            TercerPrefijo_correos_options_2 = df_3_correos_2["3er prefijo (area o VP)"].unique().tolist()
            TercerPrefijo_correos_2 = filtro3_correos_2.selectbox("3er prefijo:", TercerPrefijo_correos_options_2, 0, key = "Correos_iniciativas_3")
            # Filtro 4
            df_4_correos_2 = df_3_correos_2[df_3_correos_2["3er prefijo (area o VP)"] == TercerPrefijo_correos_2]
            Iniciativas_correos_options_2 = df_4_correos_2["Iniciativa"].unique().tolist()
            Iniciativa_correos_2 = filtro4_correos_2.selectbox("Iniciativa:", Iniciativas_correos_options_2, 0, key = "Correos_iniciativas_4")

            st.write("---")
            df_correos_final_otro_2 = df_4_correos_2[df_4_correos_2["Iniciativa"] == Iniciativa_correos_2]
            correos_analisis_mes_2 = df_correos_final_otro_2.groupby(['Mes',"Mes [Fecha]"], as_index=False)[["Enviado","Entregado","Tasa de entregas","Abierto","Tasa de aperturas",
                                "Recibió clics","Tasa de clics","Tasa de click-through"]].mean()
            
            list_with_metric_2 = ['Mes',"Mes [Fecha]"]
            list_with_metric_2.append(metric_selected_graphic)

            correos_analisis_mes_with_metric_2 = correos_analisis_mes_2[list_with_metric_2]
            correos_analisis_mes_with_metric_2 = correos_analisis_mes_with_metric_2.sort_values(by=["Mes [Fecha]"], ascending=True).reset_index(drop=True)

            
            fig_correos_2 = go.Figure([go.Scatter(x = correos_analisis_mes_with_metric_2['Mes'], 
                                        y = correos_analisis_mes_with_metric_2[metric_selected_graphic])])
            fig_correos_2.update_layout(
                xaxis_title="Mes",
                yaxis_title="Promedio de " + metric_selected_graphic,
                font=dict(family="Courier New, monospace",size=12,color="Black"))
            
            left_column_correos_2, right_column_correos_2 = st.columns([1, 3])
            with left_column_correos_2:
                list_with_metric_output_2 = ['Mes']
                list_with_metric_output_2.append(metric_selected_graphic)
                st.write(correos_analisis_mes_with_metric_2[list_with_metric_output_2])
            with right_column_correos_2:
                st.write(fig_correos_2)


   
