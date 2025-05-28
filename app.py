import pandas as pd
import streamlit as st
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Ranking Ponderado", layout="centered")

st.title("📊 Ranking Ponderado de Productos")

# --- Subir archivo Excel ---
archivo_subido = st.file_uploader("🔼 Sube tu archivo Excel", type=["xlsx"])
hoja = st.text_input("Nombre de la hoja:", value="Export")

# --- Pesos configurables ---
st.markdown("### Ajustes de pesos para las métricas")
peso_nmv = st.slider("Peso NMV Producto", 0.0, 1.0, 0.3, step=0.05)
peso_unidades = st.slider("Peso Unidades", 0.0, 1.0, 0.4, step=0.05)
peso_visitas = st.slider("Peso Visitas", 0.0, 1.0, 0.2, step=0.05)
peso_tc = st.slider("Peso TC", 0.0, 1.0, 0.1, step=0.05)

PESOS = {
    'NMV Producto': peso_nmv,
    'Unidades': peso_unidades,
    'Visitas': peso_visitas,
    'TC': peso_tc
}

# Normalizar pesos para que sumen 1
peso_total = sum(PESOS.values())
PESOS = {k: v / peso_total for k, v in PESOS.items()}

if archivo_subido:
    try:
        df = pd.read_excel(archivo_subido, sheet_name=hoja)
        columnas_necesarias = list(PESOS.keys()) + ['SKU', 'Producto']

        if not all(col in df.columns for col in columnas_necesarias):
            st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_necesarias)}")
        else:
            # Convertir a numérico y limpiar
            for col in PESOS.keys():
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=PESOS.keys(), inplace=True)

            # Normalizar y calcular puntaje
            for col in PESOS.keys():
                min_val, max_val = df[col].min(), df[col].max()
                df[f"{col}_norm"] = (df[col] - min_val) / (max_val - min_val) if max_val > min_val else 0

            df['Puntaje_Ponderado'] = sum(
                df[f"{col}_norm"] * peso for col, peso in PESOS.items()
            )

            df_ordenado = df.sort_values(by='Puntaje_Ponderado', ascending=False).reset_index(drop=True)
            columnas_finales = ['SKU', 'Producto', 'Puntaje_Ponderado']
            df_export = df_ordenado[columnas_finales]

            st.success("✅ ¡Ranking generado exitosamente!")
            st.dataframe(df_export.head(20))

            # Botón de descarga
            output = BytesIO()
            df_export.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="⬇️ Descargar archivo Excel",
                data=output,
                file_name="ranking_ponderado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            with st.expander("📷 Ver ejemplo del archivo a subir"):
             imagen = Image.open("prueba.png")
            st.image(imagen, caption="Ejemplo de archivo con columnas requeridas", use_column_width=True)

    

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
