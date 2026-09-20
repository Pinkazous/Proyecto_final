from datetime import date, datetime, timedelta
from pathlib import Path
import sys
import unicodedata
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# Stub de compatibilidad para pickles del notebook
if not hasattr(sys.modules['__main__'], 'ModeloSucursal'):
  sys.modules['__main__'].ModeloSucursal = type('ModeloSucursal', (object,), {})

st.set_page_config(
    page_title='Proyección de Personal - Parmessano', layout='wide'
)

# Estructura: APP/scr/app.py -> parent.parent es la raíz APP/
ROOT_DIR = (
    Path(__file__).resolve().parent.parent
    if '__file__' in locals()
    else Path('.').resolve()
)
DATOS_DIR = ROOT_DIR / 'datos'
MODELOS_DIR = ROOT_DIR / 'modelos'
EXCEL_PATH = DATOS_DIR / 'Gestion_Personal_Documento_Ajustado_v8.xlsx'

PALETA_ESTACIONES = [
    '#2a78d6',
    '#eb6834',
    '#1baf7a',
    '#eda100',
    '#e87ba4',
    '#008300',
    '#4a3aa7',
    '#e34948',
    '#8b5cf6',
]


def extraer_predictor(obj):
  """Busca recursivamente o en atributos/llaves un objeto con método .predict()."""
  if hasattr(obj, 'predict'):
    return obj
  if isinstance(obj, dict):
    for k in ['model', 'pipeline', 'estimator', 'regressor', 'predictor']:
      if k in obj and hasattr(obj[k], 'predict'):
        return obj[k]
    for v in obj.values():
      res = extraer_predictor(v)
      if res is not None:
        return res
  elif hasattr(obj, '__dict__'):
    for v in obj.__dict__.values():
      res = extraer_predictor(v)
      if res is not None:
        return res
  return None


@st.cache_resource
def load_model(sucursal):
  model_path = MODELOS_DIR / f'modelo_transaccionalidad_suc{sucursal}.joblib'
  if model_path.exists():
    try:
      obj = joblib.load(model_path)
      pred_obj = extraer_predictor(obj)
      return pred_obj if pred_obj is not None else obj
    except Exception:
      return None
  return None


@st.cache_data
def load_maestros():
  if not EXCEL_PATH.exists():
    return {}, {}, []
  try:
    xl = pd.ExcelFile(EXCEL_PATH)
    prod_df = xl.parse('Productividad')
    prod_map = (
        prod_df.groupby(['Estacion', 'Nivel'])[
            'Promedio de transacciones por hora'
        ]
        .first()
        .to_dict()
    )

    areas_df = xl.parse('Areas y Estaciones')[['Area de servicio', 'Estacion']]
    areas_df.columns = ['area', 'estacion']
    areas_df['estacion'] = (
        areas_df['estacion']
        .astype(str)
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
    )
    mapa_area = dict(zip(areas_df['estacion'], areas_df['area']))

    est_suc_df = xl.parse('Estaciones Sucursal')
    estaciones_validas = (
        est_suc_df['Estacion']
        .astype(str)
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .unique()
        .tolist()
    )
    return prod_map, mapa_area, estaciones_validas
  except Exception:
    return {}, {}, []


prod_map, mapa_area, estaciones_validas = load_maestros()
if not estaciones_validas:
  estaciones_validas = [
      'Caja / Toma Pedidos',
      'Cocina Fria',
      'Freidora / Apanados',
      'Jugos',
      'Panaderia Y Reposteria',
      'Parrilla',
      'Pastas',
      'Sodas',
      'preparacion de bebidas',
  ]


def domingo_de_pascua(anio: int) -> date:
  a = anio % 19
  b, c = divmod(anio, 100)
  d, e = divmod(b, 4)
  f = (b + 8) // 25
  g = (b - f + 1) // 3
  h = (19 * a + b - d - g + 15) % 30
  i, k = divmod(c, 4)
  ele = (32 + 2 * e + 2 * i - h - k) % 7
  m = (a + 11 * h + 22 * ele) // 451
  mes, dia = divmod(h + ele - 7 * m + 114, 31)
  return date(anio, mes, dia + 1)


def _siguiente_lunes(d: date) -> date:
  return d + timedelta(days=(7 - d.weekday()) % 7)


def festivos_colombia(anio: int) -> set:
  p = domingo_de_pascua(anio)
  fijos = [
      date(anio, 1, 1),
      date(anio, 5, 1),
      date(anio, 7, 20),
      date(anio, 8, 7),
      date(anio, 12, 8),
      date(anio, 12, 25),
      p - timedelta(days=3),
      p - timedelta(days=2),
  ]
  trasladables = [
      date(anio, 1, 6),
      date(anio, 3, 19),
      date(anio, 6, 29),
      date(anio, 8, 15),
      date(anio, 10, 12),
      date(anio, 11, 1),
      date(anio, 11, 11),
      p + timedelta(days=39),
      p + timedelta(days=60),
      p + timedelta(days=68),
  ]
  s = set(fijos)
  for d in trasladables:
    s.add(_siguiente_lunes(d))
  return s


def construir_features_prediccion(fechas_sel, horas_op, estaciones):
  fest_set = festivos_colombia(fechas_sel.year)
  filas = []
  dt = pd.to_datetime(fechas_sel)
  f_date = dt.date()
  es_fest = int(f_date in fest_set)
  f_vis = int((f_date + timedelta(days=1)) in fest_set)
  f_post = int((f_date - timedelta(days=1)) in fest_set)
  es_pue = int(es_fest == 1 and dt.dayofweek == 0)

  for h in horas_op:
    for st in estaciones:
      filas.append({
          'hora': int(h),
          'dia_semana': int(dt.dayofweek),
          'dia_mes': int(dt.day),
          'mes': int(dt.month),
          'trimestre': int(dt.quarter),
          'es_fin_semana': int(dt.dayofweek >= 5),
          'es_inicio_mes': int(dt.day <= 3),
          'es_fin_mes': int(dt.is_month_end),
          'hora_sin': np.sin(2 * np.pi * h / 24),
          'hora_cos': np.cos(2 * np.pi * h / 24),
          'dia_semana_sin': np.sin(2 * np.pi * dt.dayofweek / 7),
          'dia_semana_cos': np.cos(2 * np.pi * dt.dayofweek / 7),
          'mes_sin': np.sin(2 * np.pi * dt.month / 12),
          'mes_cos': np.cos(2 * np.pi * dt.month / 12),
          'es_festivo': es_fest,
          'es_vispera_festivo': f_vis,
          'es_post_festivo': f_post,
          'es_puente': es_pue,
          'dia_semana_efectivo': 6 if es_fest == 1 else int(dt.dayofweek),
          'estacion': str(st),
          'area': str(mapa_area.get(st, 'SIN AREA')),
          'fecha': dt,
      })
  return pd.DataFrame(filas)


st.title('Optimizador y Proyector de Personal por Estación')
st.markdown(
    'Interfaz interactiva de predicción de recursos por estación basada en'
    ' modelos transaccionales entrenados.'
)

col1, col2, col3 = st.columns(3)
with col1:
  suc = st.selectbox(
      'Sucursal', [116, 117, 122], format_func=lambda x: f'Sucursal {x}'
  )
with col2:
  fecha = st.date_input('Fecha de Proyección', value=date(2026, 9, 21))
with col3:
  nivel = st.selectbox(
      'Nivel Operativo Personal',
      ['BASICO', 'INTERMEDIO', 'AVANZADO'],
      index=1,
  )

model = load_model(suc)
if model is None or not hasattr(model, 'predict'):
  st.warning(
      f'⚠️ No se encontró un estimador ejecutable con .predict() para la'
      f' sucursal {suc}.'
  )
else:
  st.success(
      f'✅ Modelo `ExtraTrees` de sucursal {suc} activo y ejecutando inferencia'
      ' real.'
  )

horas_op = list(range(8, 22))
estaciones_disp = [
    'Caja / Toma Pedidos',
    'Cocina Fria',
    'Freidora / Apanados',
    'Jugos',
    'Panaderia Y Reposteria',
    'Parrilla',
    'Pastas',
    'Sodas',
    'preparacion de bebidas',
]

X_pred = construir_features_prediccion(fecha, horas_op, estaciones_disp)

pred_tx = np.zeros(len(X_pred))
if model is not None and hasattr(model, 'predict'):
  try:
    pred_tx = model.predict(X_pred)
    pred_tx = np.clip(pred_tx, 0, None)
  except Exception as e:
    st.error(f'Error al ejecutar inferencia: {e}')
    pred_tx = np.zeros(len(X_pred))

X_pred['pred_tx'] = pred_tx

matrix_df = (
    X_pred.pivot(index='hora', columns='estacion', values='pred_tx')
    .reindex(index=horas_op, fill_value=0)
)

c_chart, c_table = st.columns(2)

with c_chart:
  st.subheader('Carga Proyectada por Franja Horaria (Apilado por Estación)')
  fig, ax = plt.subplots(figsize=(8, 4.5))
  bottom = np.zeros(len(horas_op))
  estaciones_presentes = matrix_df.columns.tolist()
  for i, st_name in enumerate(estaciones_presentes):
    vals = matrix_df[st_name].values
    ax.bar(
        [f'{h}:00' for h in horas_op],
        vals,
        bottom=bottom,
        label=st_name,
        color=PALETA_ESTACIONES[i % len(PALETA_ESTACIONES)],
    )
    bottom += vals
  ax.set_ylabel('Transacciones estimadas')
  ax.set_xlabel('Hora Local')
  ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=7)
  plt.xticks(rotation=45)
  st.pyplot(fig)

with c_table:
  mult_nivel = {'BASICO': 0.75, 'INTERMEDIO': 1.0, 'AVANZADO': 1.30}.get(
      nivel, 1.0
  )
  st.subheader('Desglose Personal (Pico por Estación)')
  rows = []
  pico_df = matrix_df.max(axis=0)
  for st_name in estaciones_presentes:
    tx_p = pico_df[st_name]
    base_bench = prod_map.get((st_name, 'INTERMEDIO'), 25.0)
    if isinstance(base_bench, dict):
      base_bench = 25.0
    efectivo_bench = max(5.0, float(base_bench) * mult_nivel)
    p_req = (
        max(1, int(np.ceil(tx_p / efectivo_bench)))
        if efectivo_bench > 0
        else 1
    )
    area_name = str(mapa_area.get(st_name, 'Operación'))
    rows.append({
        'Estación': st_name,
        'Área': area_name,
        'Tx/h Pico': round(float(tx_p), 1),
        'Personal Req.': f'{p_req} pax',
    })
  st.dataframe(pd.DataFrame(rows), hide_index=True)