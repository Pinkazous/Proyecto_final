Aquí tienes un archivo `README.md` completo, profesional y adaptado a la estructura de tu proyecto y los modelos de Parmessano:

```markdown
# Parmessano — Optimizador y Proyector de Personal por Estación

Sistema inteligente de pronóstico de demanda transaccional y dimensionamiento operativo de personal por estación de trabajo (cocina, barra, salón) para sucursales de **Parmessano** (*Atlantis*, *Santafe*, *Atrio*). El sistema ejecuta modelos de Machine Learning ensamblados (`ExtraTrees`) entrenados con historial de ventas y traduce las transacciones pico proyectadas en requerimientos de colaboradores (*pax*) basándose en matrices de productividad por nivel operativo.

---

## 📁 Estructura del Repositorio

```text
APP/
├── datos/
│   ├── Gestion_Personal_Documento_Ajustado_v8.xlsx   # Maestro de productividad y áreas de servicio
│   ├── Plantilla_Gestion_Personal_v3.xlsx          # Plantilla operativa de turnos
│   └── venta_acumulada_2026-01_a_2026-09.csv       # Historial unificado de transacciones (UTC -> local)
├── modelos/
│   ├── modelo_transaccionalidad_suc116.joblib      # Pipeline ExtraTrees - Sucursal 116 (Atlantis)
│   ├── modelo_transaccionalidad_suc117.joblib      # Pipeline ExtraTrees - Sucursal 117 (Santafe)
│   └── modelo_transaccionalidad_suc122.joblib      # Pipeline ExtraTrees - Sucursal 122 (Atrio)
├── scr/
│   └── app.py                                      # Aplicación web interactiva (Streamlit)
├── requirements.txt                                # Dependencias del proyecto
└── README.md                                       # Documentación principal

```

---

## ⚙️ Requisitos Previos

* **Python**: `3.10` o superior recomendado.
* **Git** y **Git LFS** (recomendado para gestionar los archivos `.joblib` de gran tamaño).

---

## 🚀 Instrucciones de Instalación

1. **Clonar el repositorio y ubicarse en la raíz de la app**:
```bash
git clone <url-del-repositorio>
cd APP

```


2. **Crear y activar un entorno virtual**:
* *Windows (PowerShell / CMD)*:
```bash
python -m venv venv
venv\Scripts\activate

```


* *macOS / Linux*:
```bash
python3 -m venv venv
source venv/bin/activate

```




3. **Instalar dependencias**:
```bash
pip install --upgrade pip
pip install -r requirements.txt

```



---

## 💡 Instrucciones Básicas de Uso

1. **Ejecutar la interfaz web (Streamlit)**:
```bash
python -m streamlit run scr/app.py

```


2. **Interactuar con el tablero**:
* **Sucursal**: Selecciona entre *Atlantis* (116), *Santafe* (117) o *Atrio* (122).
* **Fecha de Proyección**: Define la fecha a proyectar (el sistema calcula automáticamente festivos, feriados y estacionalidad cíclica).
* **Nivel Operativo Personal**: Simula sensibilidad de dotación (*Básico*, *Intermedio*, *Avanzado*).


3. **Leer los resultados**:
* **Gráfico izquierdo**: Carga transaccional apilada por estación a lo largo de las franjas horarias operativas.
* **Tabla derecha**: Conversión automática de transacciones pico a personas requeridas (`pax`) por estación y área de servicio (*Cocina 1*, *Salón*, *Bar*).



---

## 🔗 Enlaces y Recursos Relevantes

* **Tablero en Vivo (Cloud)**: [Enlace a despliegue en Streamlit Cloud / AWS](https://www.google.com/search?q=https://share.streamlit.io/tu-usuario/parmessano-app&utm_source=gemini) *(pendiente de deploy)*.
* **Notebooks de Entrenamiento y Descubrimiento**:
* [suspicious link removed] (Pipeline de preprocesamiento, validación temporal y entrenamiento ExtraTrees).


* **Fuentes de Negocio**: Matriz de redimensionamiento validada bajo la Ley Emiliani y benchmarks de turnos corporativos.

---

## 🛠️ Stack Tecnológico

* **Core / UI**: [Streamlit](https://streamlit.io/?utm_source=gemini)
* **ML / Ensamble**: [Scikit-learn](https://scikit-learn.org/?utm_source=gemini) (`ExtraTreesRegressor`, `Pipeline`, `ColumnTransformer`)
* **Procesamiento de Datos**: [Pandas](https://pandas.pydata.org/?utm_source=gemini), [NumPy](https://numpy.org/?utm_source=gemini)
* **Visualización**: [Matplotlib](https://matplotlib.org/?utm_source=gemini)

```

```