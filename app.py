# -*- coding: utf-8 -*-
"""Deploy_Streamlit — Predicción Precio Energía"""

# =========================
# LIBRARIES
# =========================

import io
import pickle

import numpy as np
import pandas as pd
import streamlit as st

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title='Predicción Precio Energía',
    layout='wide'
)

# =========================
# TITLE
# =========================

st.title('Predicción del precio de energía d+1')

# =========================
# LOAD MODEL
# =========================

MODEL_FILE = 'modelo_final.pkl'

modelo = None
scaler = None
variables = None
numeric_cols = None

# Try loading from disk first (works when file is deployed alongside the app)
try:
    with open(MODEL_FILE, 'rb') as f:
        modelo, scaler, variables = pickle.load(f)
    st.sidebar.success('✅ Modelo cargado desde disco')
except FileNotFoundError:
    st.sidebar.warning('⚠️ Archivo de modelo no encontrado en disco.')
    uploaded_model = st.sidebar.file_uploader(
        'Sube el archivo del modelo (.pkl)',
        type=['pkl'],
        key='model_uploader'
    )
    if uploaded_model is not None:
        try:
            modelo, scaler, variables = pickle.load(uploaded_model)
            st.sidebar.success('✅ Modelo cargado correctamente')
        except Exception as e:
            st.sidebar.error(f'Error al cargar el modelo: {e}')

# =========================
# MAIN CONTENT
# =========================

st.write(
    'Cargue un archivo CSV con la estructura requerida para realizar las predicciones.'
)

# =========================
# EXPECTED STRUCTURE
# =========================

st.subheader('Estructura requerida del archivo CSV')

estructura = pd.DataFrame({
    'Variable': [
        'periodo', 'mes', 'Generación_kWh', 'Demanda_No_Atendida_kWh',
        'Exportaciones_kWh', 'Importaciones_kWh', 'Volumen_Mm³',
        'Aportes_Caudal_m3/s', 'Mínimo_Generación_Hidraulica_kWh',
        'delta_reservas_7d', 'regimen_enso'
    ],
    'Tipo': [
        'float', 'float', 'float', 'float', 'float', 'float',
        'float', 'float', 'float', 'float', 'categoria'
    ],
    'Ejemplo': [
        2024, 5, 1500000, 0, 12000, 3000, 500, 700, 200000, -5, 'Niño'
    ]
})

st.dataframe(estructura, use_container_width=True)

# =========================
# FILE UPLOADER
# =========================

uploaded_file = st.file_uploader(
    'Cargue el archivo CSV con datos futuros',
    type=['csv']
)

# =========================
# PREDICTION PROCESS
# =========================

if uploaded_file is not None:

    if modelo is None:
        st.error('❌ Primero debes cargar el modelo desde la barra lateral antes de realizar predicciones.')
        st.stop()

    # READ CSV
    data = pd.read_csv(uploaded_file)

    st.subheader('Datos cargados')
    st.dataframe(data.head(), use_container_width=True)

    # PREPROCESSING
    data_preparada = data.copy()
    
    # CLEAN COLUMN NAMES
    data_preparada.columns = (
        data_preparada.columns
        .str.replace("'", "", regex=False)
        .str.strip()
        .str.replace(" ", "_")
    )
    
    # NUMERIC COLUMNS
    numeric_cols = [
        'periodo',
        'mes',
        'Generación_kWh',
        'Demanda_No_Atendida_kWh',
        'Exportaciones_kWh',
        'Importaciones_kWh',
        'Volumen_Mm³',
        'Aportes_Caudal_m3/s',
        'Mínimo_Generación_Hidraulica_kWh',
        'delta_reservas_7d'
    ]
    
    # VALIDATE REQUIRED COLUMNS
    missing_cols = [
        col for col in numeric_cols + ['regimen_enso']
        if col not in data_preparada.columns
    ]
    
    if missing_cols:
        st.error(f'❌ Faltan columnas requeridas: {missing_cols}')
        st.stop()
    
    # FORCE NUMERIC TYPES
    data_preparada[numeric_cols] = (
        data_preparada[numeric_cols]
        .apply(pd.to_numeric, errors='coerce')
    )
    
    # CHECK NULLS AFTER CONVERSION
    if data_preparada[numeric_cols].isnull().sum().sum() > 0:
        st.error('❌ Existen valores vacíos o no numéricos en las columnas numéricas.')
        st.stop()
    
    # SCALE FIRST
    data_preparada[numeric_cols] = scaler.transform(
        data_preparada[numeric_cols]
    )
    
    # CREATE DUMMIES
    data_preparada = pd.get_dummies(
        data_preparada,
        columns=['regimen_enso'],
        drop_first=True,
        dtype=int
    )
    
    # ALIGN COLUMNS WITH TRAINING
    data_preparada = data_preparada.reindex(
        columns=variables,
        fill_value=0
    )
    
    # FINAL VALIDATION
    missing_model_cols = [
        col for col in variables
        if col not in data_preparada.columns
    ]
    
    if missing_model_cols:
        st.error(f'❌ Faltan columnas para el modelo: {missing_model_cols}')
        st.stop()
    
    # PREDICTIONS
    predicciones = modelo.predict(data_preparada)

    # RESULTS
    data['Prediccion_precio_d+1'] = predicciones

    st.subheader('Predicciones realizadas')
    st.dataframe(data, use_container_width=True)

    # DOWNLOAD CSV
    csv = data.to_csv(index=False).encode('utf-8')

    st.download_button(
        label='Descargar predicciones CSV',
        data=csv,
        file_name='predicciones_energia.csv',
        mime='text/csv'
    )

    st.success('✅ Predicciones generadas correctamente')

# =========================
# MODEL PERFORMANCE
# =========================

st.subheader('Desempeño del modelo')

st.info('Error promedio del modelo (MAPE): 1.07%')

st.write(
    'El MAPE representa el porcentaje promedio de error de las predicciones del modelo.'
)
