# ⚡ Predicción del Precio de Bolsa de Energía — SIN Colombia

> Modelo predictivo supervisado (XGBoost) para estimar el precio de bolsa de energía del día siguiente (D+1) en el Sistema Interconectado Nacional de Colombia, en función de las condiciones operativas e hídricas del sistema.

---

## 📋 Descripción del Proyecto

El Sistema Interconectado Nacional (SIN) de Colombia genera aproximadamente el **70 % de su energía desde centrales hidroeléctricas**, lo que convierte el nivel de los embalses en el principal determinante del precio de bolsa. Cuando los embalses bajan, los generadores hidráulicos incrementan sus ofertas para preservar el agua almacenada y XM debe despachar plantas termoeléctricas de mayor costo, elevando así el precio marginal del sistema.

Esta relación causal, aunque conocida, presenta retos de cuantificación: es no lineal (con umbrales críticos alrededor del 35–40 % de la capacidad útil), opera con rezagos de 7 a 15 días y se amplifica durante episodios ENSO (El Niño).

Este proyecto desarrolla un modelo predictivo que permite a generadores, comercializadores y grandes consumidores **anticipar movimientos de precio con un día de antelación**, apoyando decisiones de cobertura, contratación y gestión de portafolio.

---

## 🎯 Objetivos

- Desarrollar un modelo de **regresión supervisada** que estime `precio_bolsa[t+1]` a partir de las condiciones operativas observadas en el día `t`.
- Identificar las dimensiones latentes que explican la variabilidad conjunta de las variables operativas del SIN mediante **reducción de dimensionalidad (PCA)**.

---

## 📊 Resultados del Modelo

| Métrica | Resultado | Umbral de Éxito |
|---------|-----------|-----------------|
| MAPE    | **1.07 %** | < 12 %          |
| DA (Directional Accuracy) | — | > 65 % |

El modelo supera ampliamente el umbral de éxito definido para el MAPE.

---

## 🗂️ Estructura del Repositorio

```
├── data/
│   ├── raw/
│   │   ├── precios/                     # Archivos XM por año
│   │   ├── hidrologia/                  # Reservas y aportes
│   │   ├── demanda/                     # Demanda y generación
│   │   └── generacion_hidraulica/
│   └── processed/
│       └── sin_modelo_diario.csv        # Dataset consolidado final
├── notebooks/
│   └── CRISP_DM_preparacion.ipynb       # Análisis y preparación de datos
├── assets/
│   ├── screenshot_main.png              # Pantallazo interfaz principal
│   └── screenshot_results.png          # Pantallazo resultados predicción
├── modelo_final.pkl                     # Modelo entrenado (XGBoost + scaler + variables)
├── app.py                               # Aplicación Streamlit para predicciones
├── datos_prediccion_ejemplo.csv         # CSV de ejemplo listo para usar en la app
├── requirements.txt
└── README.md
```

---

## 🔄 Metodología CRISP-DM

El proyecto sigue la metodología **CRISP-DM** en las siguientes fases:

### 1. Entendimiento del Negocio
Análisis del mercado eléctrico colombiano y definición del problema predictivo.

### 2. Entendimiento de los Datos
Los datos provienen de **XM / Sinergox** con frecuencia diaria para el período 2023–2025 (~1.096 registros). Las fuentes integradas son:

- Precio Bolsa Nacional Ponderado ($/kWh)
- Demanda Energía SIN
- Generación Total y Generación Hidráulica
- Reservas y Vertimientos de embalses
- Aportes de caudal por río
- Régimen ENSO (El Niño / La Niña / Neutro)

### 3. Preparación de Datos
- **Integración** de 6 fuentes heterogéneas mediante llave de cruce por fecha.
- **Selección de variables**: descarte de constantes y variables con fuga de información.
- **Limpieza de atípicos**: el único outlier significativo (Demanda No Atendida del 17/09/2024) fue verificado en el IDO de XM y reemplazado con la media de la variable.
- **Tratamiento de nulos**: imputación con 0 (Demanda No Atendida verificada), eliminación de registros sin ventana temporal suficiente (delta_reservas_7d) y sin día siguiente disponible (precio_d+1).
- **Reducción de redundancias**: eliminación de variables con correlación > 0.95 conservando la de mayor interpretabilidad hidrológica.

### 4. Modelado
Algoritmo: **XGBoost** con optimización de hiperparámetros via Optuna.

### 5. Evaluación
Métricas: MAPE, MAE y Directional Accuracy sobre conjunto de prueba.

---

## 📐 Variables del Modelo

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `periodo` | float | Año del registro |
| `mes` | float | Mes del registro |
| `Generación_kWh` | float | Generación total diaria del SIN |
| `Demanda_No_Atendida_kWh` | float | Energía no suministrada (0 en condiciones normales) |
| `Exportaciones_kWh` | float | Exportaciones diarias a sistemas vecinos |
| `Importaciones_kWh` | float | Importaciones diarias desde sistemas vecinos |
| `Volumen_Mm³` | float | Volumen total almacenado en embalses |
| `Aportes_Caudal_m3/s` | float | Aportes hídricos diarios agregados |
| `Mínimo_Generación_Hidraulica_kWh` | float | Menor generación diaria entre recursos hídricos |
| `delta_reservas_7d` | float | Variación del nivel útil vs. 7 días atrás |
| `regimen_enso` | categoría | Régimen climático: `Niño`, `Niña` o `neutro` |

**Variable objetivo:** `precio_d+1` — Precio Bolsa Nacional Ponderado del día siguiente ($/kWh).

---

## 🚀 Aplicación Streamlit — Demo en Vivo

[![Streamlit App](https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png)](https://k4yr3-streamlit-deployment-sin-app-abqxzp.streamlit.app/)

🔗 **URL:**  [https://k4yr3-streamlit-deployment-sin-app-abqxzp.streamlit.app/](https://k4yr3-streamlit-deployment-sin-app-abqxzp.streamlit.app/)

La aplicación está desplegada en **Streamlit Community Cloud**, integrada directamente con este repositorio de GitHub. Cualquier `push` a la rama principal actualiza el despliegue de forma automática.

### Pantallazos de la aplicación

**Vista principal — Carga de datos y estructura requerida**

![Vista principal de la app](img/Prediction_SIN_Streamlit.jpg)

> *Interfaz de carga del modelo (.pkl) desde la barra lateral, descripción de la estructura del CSV requerido y uploader de datos.*

**Resultado de predicciones con descarga**

![Resultado predicciones](img/Prediction_SIN_result_Streamlit.jpg)

> *Tabla con la columna `Prediccion_precio_d+1` generada y botón de descarga en CSV.*

---

### Cómo usar la app

1. Acceder a la [URL del despliegue](https://k4yr3-streamlit-deployment-sin-app-abqxzp.streamlit.app/).
2. En la barra lateral, cargar el archivo `modelo_final.pkl` si no se detecta automáticamente.
3. Descargar el archivo de ejemplo [`datos_prediccion_ejemplo.csv`](datos_prediccion_ejemplo.csv) incluido en este repositorio.
4. Subir el CSV en la sección principal de la app.
5. La app preprocesa los datos, aplica el scaler y genera las predicciones automáticamente.
6. Descargar el resultado con el botón **"Descargar predicciones CSV"**.

### Archivo de ejemplo

El repositorio incluye [`datos_prediccion_ejemplo.csv`](datos_prediccion_ejemplo.csv) con 10 filas representativas de diferentes condiciones operativas del SIN (épocas de El Niño, neutro y La Niña), listo para probar directamente en la app sin necesidad de preparar datos propios.

---

### Integración con GitHub y despliegue continuo

El despliegue en Streamlit Community Cloud está conectado directamente a este repositorio. Para replicarlo en tu propia cuenta:

1. Hacer fork de este repositorio en tu cuenta de GitHub.
2. Ir a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión con GitHub.
3. Hacer clic en **"New app"**, seleccionar el repositorio, la rama `main` y el archivo `app.py`.
4. El despliegue se activa automáticamente y se sincroniza con cada `push` a la rama principal.

```bash
# Clonar el repositorio
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar localmente
streamlit run app.py
```

---

## 🛠️ Stack Tecnológico

| Componente | Herramienta |
|------------|-------------|
| Lenguaje | Python 3.11+ |
| Entorno de análisis | Jupyter Notebook / Google Colab |
| Datos | pandas, numpy, openpyxl |
| Modelo ML | XGBoost, scikit-learn |
| Optimización | Optuna |
| Interpretabilidad | SHAP |
| Visualización | matplotlib, seaborn, plotly |
| Deploy | Streamlit Community Cloud |
| Control de versiones | Git + GitHub |

---

## 📦 Requisitos

```txt
streamlit
pandas
numpy
scikit-learn
xgboost
```

---

## 📁 Datos

Los datos históricos son publicados por **XM** a través de la plataforma [Sinergox](https://sinergox.xm.com.co/) con frecuencia diaria, organizados por año y categoría. Para el período 2023–2025 se trabajó con las siguientes categorías:

- Demandas y Fronteras
- Hidrología (Reservas y Aportes)
- Oferta y Generación
- Transacciones y Precios

El dataset consolidado procesado se almacena en `data/processed/sin_modelo_diario.csv`.

---

## 👤 Autor

**William Alejandro Pabón G.**

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia MIT. Ver `LICENSE` para más detalles.
