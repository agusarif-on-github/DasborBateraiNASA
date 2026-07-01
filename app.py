import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Data Baterai Lithium-ion NASA",
    page_icon="🔋",
    layout="wide"
)

# Path ke data
DATA_BASE_PATH = r"D:\Akademika S3\Estimasi SoH dgn ICA dan KF\Proyek Dashboard\data_B0005"

@st.cache_data
def load_csv_files():
    """Memuat semua file CSV dari direktori data"""
    data_path = Path(DATA_BASE_PATH)
    csv_files = sorted(data_path.glob("*.csv"))
    return csv_files

@st.cache_data
def read_csv_file(file_path):
    """Membaca file CSV dan mengembalikan DataFrame"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error membaca file {file_path}: {e}")
        return None

def get_available_columns(df):
    """Mendapatkan kolom yang tersedia dari DataFrame"""
    if df is None:
        return []
    return df.columns.tolist()

def get_unit_mapping():
    """Mapping satuan untuk setiap variabel"""
    return {
        'Voltage_measured': 'V',
        'Current_measured': 'A',
        'Temperature_measured': '°C',
        'Current_charge': 'A',
        'Current_load': 'A',
        'Voltage_charge': 'V',
        'Voltage_load': 'V',
        'Time': 's',
        'Capacity': 'Ahr'
    }

def get_column_unit(column_name):
    """Mendapatkan satuan untuk kolom tertentu"""
    unit_mapping = get_unit_mapping()
    return unit_mapping.get(column_name, '')

def create_single_plot(df, x_column, y_column, title):
    """Membuat grafik plotly untuk satu variabel"""
    if df is None:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_column],
        y=df[y_column],
        mode='lines',
        name=y_column,
        line=dict(width=2, color='#1f77b4')
    ))
    
    # Mendapatkan satuan
    x_unit = get_column_unit(x_column)
    y_unit = get_column_unit(y_column)
    
    x_label = f"{x_column} ({x_unit})" if x_unit else x_column
    y_label = f"{y_column} ({y_unit})" if y_unit else y_column
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        hovermode='x unified',
        margin=dict(l=50, r=20, t=50, b=50),
        height=300
    )
    
    return fig

def main():
    st.title("🔋 Dashboard Data Baterai Lithium-ion NASA")
    st.markdown("""
    Dashboard ini untuk visualisasi data pengukuran sel baterai Lithium-ion dari repositori NASA.
    Data mencakup tegangan, arus, suhu, dan parameter lainnya selama proses pengosongan muatan (discharge).
    """)
    
    # Sidebar untuk navigasi
    st.sidebar.header("Konfigurasi Data")
    
    # Memuat file CSV yang tersedia
    csv_files = load_csv_files()
    
    if not csv_files:
        st.error("Tidak ada file CSV yang ditemukan di direktori data!")
        st.info(f"Path yang dicari: {DATA_BASE_PATH}")
        return
    
    # Dropdown untuk memilih file
    file_names = [f.name for f in csv_files]
    selected_file = st.sidebar.selectbox(
        "Pilih File Data",
        file_names,
        index=0
    )
    
    # Mendapatkan path file yang dipilih
    selected_file_path = next(f for f in csv_files if f.name == selected_file)
    
    # Membaca data
    df = read_csv_file(selected_file_path)
    
    if df is None:
        return
    
    # Menampilkan informasi file
    st.sidebar.subheader("Informasi File")
    st.sidebar.write(f"**Nama File:** {selected_file}")
    st.sidebar.write(f"**Jumlah Baris:** {len(df)}")
    st.sidebar.write(f"**Jumlah Kolom:** {len(df.columns)}")
    
    # Mendapatkan kolom yang tersedia
    available_columns = get_available_columns(df)
    
    # Memilih kolom untuk sumbu X
    default_x = "Time" if "Time" in available_columns else available_columns[0]
    x_column = st.sidebar.selectbox(
        "Sumbu X (Waktu)",
        available_columns,
        index=available_columns.index(default_x) if default_x in available_columns else 0
    )
    
    # Memilih kolom untuk sumbu Y (multi-select)
    default_y = [col for col in available_columns if col != x_column]
    y_columns = st.sidebar.multiselect(
        "Sumbu Y (Variabel untuk ditampilkan)",
        available_columns,
        default=default_y[:4] if len(default_y) >= 4 else default_y
    )
    
    # Tab untuk tampilan berbeda
    tab1, tab2, tab3 = st.tabs(["📊 Grafik", "📋 Data Tabel", "📈 Statistik"])
    
    with tab1:
        st.subheader(f"Visualisasi Data: {selected_file}")
        
        if y_columns:
            # Menampilkan setiap variabel dalam grafik terpisah
            for i, col in enumerate(y_columns):
                with st.container():
                    fig = create_single_plot(df, x_column, col, f"{col} vs {x_column}")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    st.markdown("---")  # Garis pemisah antar grafik
        else:
            st.warning("Silakan pilih minimal satu variabel untuk sumbu Y")
    
    with tab2:
        st.subheader("Data Mentah")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Opsi download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data sebagai CSV",
            data=csv,
            file_name=f"{selected_file}",
            mime='text/csv'
        )
    
    with tab3:
        st.subheader("Statistik Deskriptif")
        if df.select_dtypes(include=['number']).columns.any():
            st.dataframe(df.describe(), use_container_width=True)
        else:
            st.info("Tidak ada data numerik untuk statistik")

if __name__ == "__main__":
    main()
