"""
Universidad Nacional Autónoma de México
Facultad de Ciencias
Proyecto Matemáticas Financieras

Grupo: 9015
Alumnos: 
  Delgadillo Fernández Patricio Santiago
  Hernandez Atenco Irvin Armando
  Gónzalez Madrid Joan Ivan
  Roque Barajas Héctor David

Profesores:
  M. en R. Humberto Plata Gallegos
  Act. Edgar Yael Marbán Pérez
  M. en R. Ana Barenka Sánchez Encontra

Desarrollada en diciembre 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Generador de Tablas de Amortización",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #fff;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #fff;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #757575;
        margin: 1rem 0;
        color: #212121;
    }
    .result-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #616161;
        margin: 1rem 0;
        color: #212121;
    }
    .formula-box {
        background-color: #fff;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        border-left: 5px solid #757575;
        color: #212121;
    }
    .inst-header {
        color: #fff;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F44336;
        margin: 1rem 0;
        color: #B71C1C;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado institucional
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="inst-header">Universidad Nacional Autónoma de México</div>', unsafe_allow_html=True)
    st.markdown('<div class="inst-header">Facultad de Ciencias</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Generador de Tablas de Amortización</h1>', unsafe_allow_html=True)

# Información del proyecto
with st.expander("📋 Información del Proyecto", expanded=True):
    st.markdown("""
    **Proyecto: Matemáticas Financieras**  
    **Grupo:** 9015  
    
    **Alumnos:**
    - Delgadillo Fernández Patricio Santiago
    - Hernandez Atenco Irvin Armando
    - González Madrid Joan Ivan
    - Roque Barajas Héctor David
    
    **Profesores:**
    - M. en R. Humberto Plata Gallegos
    - Act. Edgar Yael Marbán Pérez
    - M. en R. Ana Barenka Sánchez Encontra
    
    **Desarrollado en:** Diciembre 2025
    """)

def calcular_pago_mensual(prestamo, tasa_interes_anual, plazo_meses):
    """
    Calcula el pago mensual usando el sistema francés de amortización
    """
    if plazo_meses <= 0:
        return 0.0
    
    tasa_mensual = tasa_interes_anual / 12 / 100
    if tasa_mensual > 0 and plazo_meses > 0:
        try:
            pago_base = prestamo * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
            return pago_base
        except:
            return prestamo / plazo_meses
    else:
        return prestamo / plazo_meses if plazo_meses > 0 else prestamo

def generar_tabla_amortizacion(precio_compra, enganche, tasa_interes_anual, plazo_meses, 
                              aportacion_extra=0, inicio_aportacion=1, tipo_amortizacion="Francesa",
                              tipo_aportacion="Mensual hasta el final", meses_aportacion=None):
    """
    Genera la tabla de amortización completa con aportaciones opcionales
    """
    # Validaciones iniciales
    if plazo_meses <= 0:
        return pd.DataFrame(), 0
    
    prestamo = max(0.0, precio_compra - enganche)
    if prestamo <= 0:
        return pd.DataFrame(), 0
    
    tasa_mensual = tasa_interes_anual / 12 / 100
    
    # Calcular pago mensual según el tipo de amortización
    if tipo_amortizacion == "Francesa":
        pago_mensual = calcular_pago_mensual(prestamo, tasa_interes_anual, plazo_meses)
    else:  # Sistema Alemán
        pago_capital = prestamo / plazo_meses if plazo_meses > 0 else prestamo
        pago_mensual = pago_capital + (prestamo * tasa_mensual)
    
    # Determinar meses de aportación de forma segura
    inicio_aportacion = max(1, min(inicio_aportacion, plazo_meses))
    
    if meses_aportacion is None:
        if tipo_aportacion == "Única":
            meses_aportacion = 1
        elif tipo_aportacion == "Mensual hasta el final":
            meses_aportacion = max(1, plazo_meses - inicio_aportacion + 1)
    
    # Limitar meses_aportacion a un valor razonable
    meses_aportacion = max(1, min(meses_aportacion, plazo_meses - inicio_aportacion + 1))
    
    # Inicializar listas para la tabla
    datos = []
    saldo = prestamo
    
    for mes in range(1, plazo_meses + 1):
        # Calcular interés del periodo
        interes_mes = saldo * tasa_mensual
        
        # Sistema Alemán
        if tipo_amortizacion == "Alemana":
            amortizacion = prestamo / plazo_meses if plazo_meses > 0 else 0
            pago_total = amortizacion + interes_mes
        else:  # Sistema Francés
            amortizacion = max(0, pago_mensual - interes_mes)
            pago_total = pago_mensual
        
        # Agregar aportación extra si aplica
        aportacion_este_mes = 0.0
        if aportacion_extra > 0 and mes >= inicio_aportacion:
            # Verificar tipo de aportación
            if tipo_aportacion == "Única":
                if mes == inicio_aportacion:
                    aportacion_este_mes = aportacion_extra
            elif tipo_aportacion == "Por número limitado de meses":
                if mes < inicio_aportacion + meses_aportacion:
                    aportacion_este_mes = aportacion_extra
            else:  # "Mensual hasta el final"
                aportacion_este_mes = aportacion_extra
        
        if aportacion_este_mes > 0:
            pago_total += aportacion_este_mes
            amortizacion += aportacion_este_mes
        
        # Asegurar que no haya saldo negativo
        if amortizacion > saldo:
            amortizacion = saldo
            pago_total = interes_mes + amortizacion
        
        # Actualizar saldo
        saldo_anterior = saldo
        saldo = max(0.0, saldo - amortizacion)
        
        # Agregar fila a los datos
        datos.append({
            'Mes': mes,
            'Saldo Inicial': saldo_anterior,
            'Pago Total': pago_total,
            'Interés': interes_mes,
            'Amortización': amortizacion,
            'Aportación Extra': aportacion_este_mes,
            'Saldo Final': saldo
        })
        
        if saldo <= 0:
            break
    
    df = pd.DataFrame(datos)
    return df, prestamo

def calcular_ahorro_interes(df, tasa_interes):
    """
    Calcula el ahorro en intereses por aportaciones extra
    """
    if 'Aportación Extra' not in df.columns or df.empty:
        return 0.0
    
    total_aportaciones = df['Aportación Extra'].sum()
    if total_aportaciones > 0:
        tasa_mensual = tasa_interes / 12 / 100
        return total_aportaciones * tasa_mensual * 0.5
    return 0.0

def calcular_meses_ahorrados(df, plazo_original):
    """
    Calcula cuántos meses se ahorraron por las aportaciones
    """
    if df.empty:
        return 0
    plazo_real = len(df)
    return max(0, plazo_original - plazo_real)

def crear_excel_descargable(df, resumen, tipo_aportacion="No aplica", tasa_interes=0, plazo_original=0):
    """
    Crea un archivo Excel descargable con formato profesional
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Hoja 1: Tabla de amortización
        df.to_excel(writer, sheet_name='Amortización', index=False)
        
        # Hoja 2: Resumen
        resumen_df = pd.DataFrame(list(resumen.items()), columns=['Concepto', 'Valor'])
        resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja 3: Análisis (si hay aportaciones y datos)
        if not df.empty and 'Aportación Extra' in df.columns and df['Aportación Extra'].sum() > 0:
            ahorro_interes = calcular_ahorro_interes(df, tasa_interes)
            meses_ahorrados = calcular_meses_ahorrados(df, plazo_original)
            
            analisis_df = pd.DataFrame({
                'Métrica': [
                    'Total Aportaciones Extra',
                    'Meses con aportación extra',
                    'Interés ahorrado estimado',
                    'Plazo reducido',
                    'Pago mensual promedio con aportaciones',
                    'Pago mensual promedio sin aportaciones estimado'
                ],
                'Valor': [
                    f"${df['Aportación Extra'].sum():,.2f}",
                    f"{len(df[df['Aportación Extra'] > 0])} meses",
                    f"${ahorro_interes:,.2f}",
                    f"{meses_ahorrados} meses",
                    f"${df['Pago Total'].mean():,.2f}",
                    f"${(df['Pago Total'].sum() - df['Aportación Extra'].sum()) / len(df):,.2f}" if len(df) > 0 else "$0.00"
                ]
            })
            analisis_df.to_excel(writer, sheet_name='Impacto Aportaciones', index=False)
        
        # Formatear hojas
        if not df.empty:
            worksheet1 = writer.sheets['Amortización']
            for col in range(1, len(df.columns) + 1):
                column_letter = chr(64 + col)
                column = df.columns[col-1]
                
                # Encontrar ancho máximo
                max_length = max(len(str(column)), df.iloc[:, col-1].astype(str).map(len).max())
                adjusted_width = min(max_length + 2, 30)
                worksheet1.column_dimensions[column_letter].width = adjusted_width
                
                # Formato de moneda para columnas numéricas (excepto Mes)
                if col > 1:
                    for row in range(2, len(df) + 2):
                        cell = worksheet1.cell(row=row, column=col)
                        cell.number_format = '$#,##0.00'
    
    output.seek(0)
    return output

def crear_graficos(df, prestamo, tasa_anual):
    """
    Crea gráficos interactivos para visualización
    """
    if df.empty:
        # Devolver gráfico vacío
        fig = go.Figure()
        fig.update_layout(title="No hay datos para mostrar")
        return fig
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Evolución del Saldo', 'Distribución Total de Pagos',
                       'Interés vs Capital (Primeros 12 Meses)', 'Pagos Acumulados'),
        specs=[[{'type': 'scatter'}, {'type': 'pie'}],
               [{'type': 'bar'}, {'type': 'scatter'}]]
    )
    
    # Gráfico 1: Evolución del saldo
    fig.add_trace(
        go.Scatter(x=df['Mes'], y=df['Saldo Final'], mode='lines+markers',
                  name='Saldo Pendiente', line=dict(color='#00adb5', width=3)),
        row=1, col=1
    )
    
    # Gráfico 2: Distribución total de pagos
    total_interes = df['Interés'].sum()
    total_capital = df['Amortización'].sum()
    if total_interes + total_capital > 0:
        fig.add_trace(
            go.Pie(labels=['Interés', 'Capital'], values=[total_interes, total_capital],
                  hole=0.4, marker=dict(colors=['#FF6B6B', '#4ECDC4']),
                  showlegend=True),
            row=1, col=2
        )
    
    # Gráfico 3: Interés vs Capital por mes (primeros 12 meses)
    meses_mostrar = min(12, len(df))
    if meses_mostrar > 0:
        fig.add_trace(
            go.Bar(name='Interés Mensual', x=df['Mes'][:meses_mostrar], 
                   y=df['Interés'][:meses_mostrar], marker_color='#FF6B6B',
                   showlegend=True),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(name='Capital Mensual', x=df['Mes'][:meses_mostrar], 
                   y=df['Amortización'][:meses_mostrar], marker_color='#4ECDC4',
                   showlegend=True),
            row=2, col=1
        )
    
    # Gráfico 4: Pagos acumulados
    df['Interés Acumulado'] = df['Interés'].cumsum()
    df['Capital Acumulado'] = df['Amortización'].cumsum()
    fig.add_trace(
        go.Scatter(x=df['Mes'], y=df['Interés Acumulado'], 
                  name='Interés Total', line=dict(color='#FF6B6B', width=3),
                  mode='lines+markers'),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=df['Mes'], y=df['Capital Acumulado'], 
                  name='Capital Total', line=dict(color='#4ECDC4', width=3),
                  mode='lines+markers'),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800, 
        showlegend=True, 
        title_text="Análisis de Amortización",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Actualizar ejes
    fig.update_xaxes(title_text="Mes", row=1, col=1)
    fig.update_yaxes(title_text="Saldo ($)", row=1, col=1)
    fig.update_xaxes(title_text="Mes", row=2, col=1)
    fig.update_yaxes(title_text="Monto ($)", row=2, col=1)
    fig.update_xaxes(title_text="Mes", row=2, col=2)
    fig.update_yaxes(title_text="Monto Acumulado ($)", row=2, col=2)
    
    return fig

# Sidebar para entradas de usuario
st.sidebar.markdown('<p class="sub-header">📊 Datos del Crédito</p>', unsafe_allow_html=True)

# Validación: precio_compra debe ser ≥ 0
precio_compra = st.sidebar.number_input(
    "Precio de compra ($):",
    min_value=0.0,
    value=100000.0,
    step=1000.0,
    format="%.2f"
)

# Validación: enganche debe ser ≥ 0 y ≤ precio_compra
enganche_max = max(0.0, precio_compra)
enganche_default = min(20000.0, enganche_max)

enganche = st.sidebar.number_input(
    "Enganche/Monto inicial ($):",
    min_value=0.0,
    value=enganche_default,
    max_value=enganche_max,
    step=1000.0,
    format="%.2f"
)

# Calcular préstamo automáticamente con validación
prestamo_calculado = max(0.0, precio_compra - enganche)
st.sidebar.markdown(f"""
<div style="
    background-color: #1E1E1E;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #2196F3;
    margin: 1rem 0;
    color: white;
">
    <strong>Monto del préstamo:</strong><br>
    <span style="font-size: 1.5rem; color: #4FC3F7;">${prestamo_calculado:,.2f}</span>
</div>
""", unsafe_allow_html=True)

# Validación: tasa de interés debe ser ≥ 0
tasa_interes = st.sidebar.number_input(
    "Tasa de interés anual (%):",
    min_value=0.0,
    value=12.0,
    step=0.5,
    format="%.2f"
)

# Validación: plazos debe ser ≥ 1
plazo_meses = st.sidebar.number_input(
    "Número de plazos (meses):",
    min_value=1,
    value=36,
    step=1
)

# Opciones adicionales
st.sidebar.markdown('<p class="sub-header">⚙️ Opciones Adicionales</p>', unsafe_allow_html=True)

tipo_amortizacion = st.sidebar.selectbox(
    "Tipo de amortización:",
    ["Francesa", "Alemana"],
    help="Sistema Francés: Cuota constante. Sistema Alemán: Amortización constante."
)

# Aportaciones adicionales - VERSIÓN SEGURA
st.sidebar.markdown("---")
aportaciones_check = st.sidebar.checkbox("¿Desea hacer aportaciones adicionales?")

aportacion_extra = 0
inicio_aportacion = 1
tipo_aportacion = "Mensual hasta el final"
meses_aportacion = None

if aportaciones_check:
    # Validación: aportación extra ≥ 0
    aportacion_extra = st.sidebar.number_input(
        "Monto de aportación adicional ($):",
        min_value=0.0,
        value=500.0,
        step=100.0,
        format="%.2f"
    )
    
    # Tipo de aportación
    tipo_aportacion = st.sidebar.selectbox(
        "Tipo de aportación:",
        ["Mensual hasta el final", "Única", "Por número limitado de meses"],
        help="Selecciona cómo aplicar las aportaciones adicionales"
    )
    
    # Validación segura para todos los casos
    max_mes_valido = max(1, plazo_meses)
    
    if tipo_aportacion == "Única":
        inicio_default = min(1, max_mes_valido)
        inicio_aportacion = st.sidebar.number_input(
            "¿En qué mes realizar la aportación única?",
            min_value=1,
            value=inicio_default,
            max_value=max_mes_valido,
            step=1
        )
        meses_aportacion = 1
        
    elif tipo_aportacion == "Por número limitado de meses":
        inicio_default = min(1, max_mes_valido)
        inicio_aportacion = st.sidebar.number_input(
            "¿A partir de qué mes?",
            min_value=1,
            value=inicio_default,
            max_value=max_mes_valido,
            step=1
        )
        
        # Calcular máximo seguro
        max_meses_posibles = max(1, plazo_meses - inicio_aportacion + 1)
        
        # Valor inicial seguro
        valor_inicial_seguro = min(6, max_meses_posibles)
        
        meses_aportacion = st.sidebar.number_input(
            "¿Por cuántos meses consecutivos?",
            min_value=1,
            value=valor_inicial_seguro,
            max_value=max_meses_posibles,
            step=1
        )
        
    else:  # "Mensual hasta el final"
        inicio_default = min(1, max_mes_valido)
        inicio_aportacion = st.sidebar.number_input(
            "¿A partir de qué mes?",
            min_value=1,
            value=inicio_default,
            max_value=max_mes_valido,
            step=1
        )
        meses_aportacion = max(1, plazo_meses - inicio_aportacion + 1)

# Botón para calcular
if st.sidebar.button("🚀 Calcular Tabla de Amortización", type="primary", use_container_width=True):
    # Validación final antes de calcular
    if prestamo_calculado <= 0:
        st.error("""
        **⚠️ Error de validación:**
        El monto del préstamo debe ser mayor a $0.00.
        
        **Posibles causas:**
        1. El enganche es igual o mayor al precio de compra
        2. El precio de compra es $0.00
        
        **Solución:** Ajusta el precio de compra o el enganche.
        """)
    elif plazo_meses <= 0:
        st.error("El número de plazos debe ser mayor a 0.")
    else:
        with st.spinner("Generando tabla de amortización..."):
            # Generar tabla
            df_tabla, prestamo = generar_tabla_amortizacion(
                precio_compra, enganche, tasa_interes, plazo_meses,
                aportacion_extra, inicio_aportacion, tipo_amortizacion,
                tipo_aportacion, meses_aportacion
            )
            
            if df_tabla.empty:
                st.warning("No se pudo generar la tabla de amortización. Verifica los datos ingresados.")
            else:
                # Calcular métricas importantes
                total_interes = df_tabla['Interés'].sum()
                total_pagado = df_tabla['Pago Total'].sum()
                total_aportaciones = df_tabla['Aportación Extra'].sum() if 'Aportación Extra' in df_tabla.columns else 0
                pago_promedio = df_tabla['Pago Total'].mean()
                plazo_real = len(df_tabla)
                meses_ahorrados = calcular_meses_ahorrados(df_tabla, plazo_meses)
                
                # Mostrar resumen
                st.markdown('<p class="sub-header">📈 Resumen del Crédito</p>', unsafe_allow_html=True)
                
                # Primera fila de métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Préstamo Total", f"${prestamo:,.2f}")
                with col2:
                    st.metric("Interés Total", f"${total_interes:,.2f}")
                with col3:
                    st.metric("Total a Pagar", f"${total_pagado:,.2f}")
                with col4:
                    st.metric("Plazo Real", f"{plazo_real} meses")
                
                # Segunda fila de métricas (si hay aportaciones)
                if aportaciones_check and total_aportaciones > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Aportaciones Extra", f"${total_aportaciones:,.2f}")
                    with col2:
                        st.metric("Tipo Aportación", tipo_aportacion)
                    with col3:
                        st.metric("Meses Ahorrados", f"{meses_ahorrados}")
                    with col4:
                        st.metric("Inicio Aportación", f"Mes {inicio_aportacion}")
                
                # Mostrar tabla de amortización
                st.markdown('<p class="sub-header">📋 Tabla de Amortización Completa</p>', unsafe_allow_html=True)
                
                # Formatear DataFrame para mostrar
                df_display = df_tabla.copy()
                df_display['Saldo Inicial'] = df_display['Saldo Inicial'].apply(lambda x: f"${x:,.2f}")
                df_display['Pago Total'] = df_display['Pago Total'].apply(lambda x: f"${x:,.2f}")
                df_display['Interés'] = df_display['Interés'].apply(lambda x: f"${x:,.2f}")
                df_display['Amortización'] = df_display['Amortización'].apply(lambda x: f"${x:,.2f}")
                df_display['Aportación Extra'] = df_display['Aportación Extra'].apply(lambda x: f"${x:,.2f}")
                df_display['Saldo Final'] = df_display['Saldo Final'].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(df_display, use_container_width=True, height=400)
                
                # Crear gráficos
                st.markdown('<p class="sub-header">📊 Visualizaciones</p>', unsafe_allow_html=True)
                fig = crear_graficos(df_tabla, prestamo, tasa_interes)
                st.plotly_chart(fig, use_container_width=True)
                
                # Preparar datos para Excel
                resumen_datos = {
                    'Precio de Compra': f"${precio_compra:,.2f}",
                    'Enganche': f"${enganche:,.2f}",
                    'Préstamo': f"${prestamo:,.2f}",
                    'Tasa de Interés Anual': f"{tasa_interes}%",
                    'Plazo Solicitado': f"{plazo_meses} meses",
                    'Plazo Real': f"{plazo_real} meses",
                    'Meses Ahorrados': f"{meses_ahorrados} meses",
                    'Tipo de Amortización': tipo_amortizacion,
                    'Aportación Extra Mensual': f"${aportacion_extra:,.2f}" if aportaciones_check else "$0.00",
                    'Tipo de Aportación': tipo_aportacion if aportaciones_check else "No aplica",
                    'Inicio Aportación': f"Mes {inicio_aportacion}" if aportaciones_check else "No aplica",
                    'Meses de Aportación': f"{meses_aportacion} meses" if aportaciones_check else "No aplica",
                    'Total Intereses': f"${total_interes:,.2f}",
                    'Total Capital': f"${df_tabla['Amortización'].sum():,.2f}",
                    'Total Aportaciones': f"${total_aportaciones:,.2f}",
                    'Total a Pagar': f"${total_pagado:,.2f}",
                    'Pago Promedio Mensual': f"${pago_promedio:,.2f}",
                    'Fecha de Cálculo': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                
                # Botón para descargar Excel
                excel_file = crear_excel_descargable(df_tabla, resumen_datos, tipo_aportacion, tasa_interes, plazo_meses)
                
                st.download_button(
                    label="📥 Descargar Tabla en Excel",
                    data=excel_file,
                    file_name=f"tabla_amortizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                # Información útil sobre los cálculos
                with st.expander("💡 Información Importante"):
                    st.info("""
                    **Nota sobre los cálculos:**

                    Los resultados presentados se basan en el sistema de amortización seleccionado y consideran:

                    - **Sistema Francés:** Cuota constante compuesta por interés decreciente y amortización creciente.
                    - **Sistema Alemán:** Amortización constante con cuota decreciente.
                    - **Aportaciones adicionales:** Se aplican directamente al capital, reduciendo el saldo pendiente.

                    **Consideraciones:**
                    - Los cálculos son estimados y pueden variar según condiciones específicas del crédito
                    - No incluyen comisiones, seguros o otros cargos adicionales
                    - La tasa de interés se considera fija durante todo el plazo
                    - Los pagos se calculan para periodos mensuales regulares

                    **Uso educativo:** Esta herramienta está diseñada para fines académicos y de simulación.
                    """)

else:
    # Pantalla inicial con instrucciones
    with st.expander("👋 ¡Bienvenido al Generador de Tablas de Amortización!", expanded=True):
        st.markdown("""
        **Descripción:**  
        Esta herramienta te permite calcular y visualizar la amortización de un crédito 
        bajo diferentes condiciones y escenarios.
        
        **📋 Instrucciones:**  
        1. Ingresa los datos del crédito en el panel lateral  
        2. Ajusta las opciones adicionales
        3. Haz clic en **"Calcular Tabla de Amortización"**  
        4. Visualiza y descarga los resultados  
        
        **✨ Características:**  
        • Soporte para sistemas de amortización Francesa y Alemana  
        • Aportaciones adicionales: Únicas, limitadas o mensuales  
        • Visualizaciones gráficas interactivas  
        • Exportación a Excel con formato profesional (3 hojas)  
        • Cálculo automático de métricas financieras  
        • Análisis de impacto de aportaciones  
        
        """)

# Pie de página
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><strong>Universidad Nacional Autónoma de México - Facultad de Ciencias</strong></p>
    <p>Proyecto de Matemáticas Financieras - Grupo 9015 - Diciembre 2025</p>
    <p>Este sistema utiliza fórmulas estándar de amortización para fines educativos</p>
</div>
""", unsafe_allow_html=True)