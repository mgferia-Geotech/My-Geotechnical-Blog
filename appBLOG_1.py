import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st 
from scipy.stats import beta, gaussian_kde


# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Geotechnical Engineering Blog", layout="centered")

# --- CONFIGURACIÓN PARA MÓVILES (NUEVO) ---
# Esto evita que el zoom se active al tocar con el dedo y quita la barra de herramientas
plotly_config = {
    'scrollZoom': False,
    'displayModeBar': False,
    'staticPlot': False,
}

# --- BLOG HEADER SECTION ---
st.markdown("""
    <h1 style='margin-bottom: 0px;'>La ilusión del Factor de Seguridad</h1>
    <p style='font-size: 1.2em; margin-top: -10px; color: black;'>
        (Con gráficos interactivos)
    </p>
    """, unsafe_allow_html=True)

st.write("""
**Por: Mauricio García F** | *Publicado: Enero 2026* """)

st.write("""
** ⏱️Tiempo de lectura: 4 min** """)

st.write("""

¿Un talud con un Factor de Seguridad (*FS*) de 1.5 es realmente más seguro que uno con un *FS* de 1.3?

La práctica tradicional nos diría que sí. Pero la realidad es mucho más compleja: el *FS* es solo  una
fotografía estática en un mundo de probabilidades. Ignorar la incertidumbre en nuestros modelos puede generar 
una sensación de seguridad puramente nominal, alejándonos de la verdadera estabilidad del terreno.

""")

st.divider() # Visual line separator

#--------------------------------------
# El Problema: El dogma del *FS=1.5*
#--------------------------------------
st.header("El Problema: el dogma del *FS=1.5*") #El Problema: El dogma del 1.5 EL PROBLEMA: EL DOGMA DEL 1.5
st.write("""
En la ingeniería de estabilidad de taludes, el número 1.5 se ha convertido en un dogma. 
Lo usamos como un escudo para protegernos de la inestabilidad, pero es un escudo débil.

El *FS* nos dice qué tan lejos estaríamos de la falla **si todas nuestras suposiciones fueran perfectas**, pero, 
sabemos que la perfección en geotecnia es un mito.

Hace unos meses, en un conversatorio de la Sociedad Colombiana de Geotecnia (SCG), mis colegas discutían sobre 
factores de seguridad y factores detonantes de inestabilidad. Surgió una conclusión inesperada (casi herética):

*“el factor de seguridad es uno de los conceptos que la geotecnia debería abandonar (o en palabras de uno de mis mentores: debería estar en el museo)”*

El problema es que intentamos usar el *FS* —una respuesta **fija y rígida (determinista)**— para resolver un problema que es, por naturaleza, **incierto y variable (probabilista)**.

""")

st.divider() # Visual line separator
# --- INTERACTIVE CONTROLS (INSIDE THE BLOG) ---
st.header("El suelo como una 'nube' de posibilidades")
st.write("""
La clave está en abandonar la idea de concebir los parámetros geotécnicos como valores únicos para empezar a representarlos como lo que realmente son: **distribuciones**.

Por ejemplo, imaginemos que la resistencia no drenada (*$S_u$*) no es un punto fijo, sino una 'nube' de posibilidades (lo que llamamos *funciones de distribución de probabilidad* o **PDF**).

""")

#----------------------------------------------------
# Ejemplo 1: Misma resistencia, diferente estabilidad 
#----------------------------------------------------
st.subheader("Mismos datos, distinta estabilidad: La trampa del valor promedio") #Ejemplo 1: Misma resistencia, diferente estabilidad

st.write("""
Para ilustrar este concepto supongamos un caso típico: un talud de 15 m de altura en un suelo homogéneo con un *$S_u$* de 70 kPa. 
En el papel, este valor es una constante, pero en el terreno es solo el promedio de una variable muchas mas compleja.

**¿Qué tan seguros estamos de ese valor de 70 kPa?** No todos los 70 kPa son iguales y nuestra confianza en este valor la podemos traducir técnicamente mediente el Coeficiente de Variación (*$CoV$*)

El *$CoV$* refleja la incertidumbre natural (aleatoria) y la incertidumbre de conocimiento (epistémica) Pensémoslo así:

- Un *$CoV$* de 5-10% refleja una incertidumbre combinada reducida. Es decir, que la variabilidad natural es baja y que conocemos muy bien nuestro suelo.
 Su gráfica PDF  es esbelta y estrecha.
 
- Un *$CoV$* alto (20-30% o más) indicaría una alta variabilidad natural o poco conocimiento del suelo. Su PDF se aplana y se ensancha, reflejando un espectro de posibilidades mucho más incierto.
""")

#st.info("La **Figura Interactiva No. 1** representa la incertidumbre de esa resistencia. Para este modelo, he utilizado una distribución tipo PERT (de la familia de las Beta), que nos permite definir la PDF de *$S_u$* con tres datos: el valor más probable, el mínimo y el máximo.")
st.info("La **Figura Interactiva No. 1** modela esta incertidumbre mediante una distribución tipo PERT (familia Beta). Esta nos permite definir la PDF del $S_u$ usando solo tres datos: valores mínimo, máximo y más probable.")


#------------------------------------
# FIGURE INTERACTIVE No. 1 
#------------------------------------
st.markdown("<p style='text-align: center;'><strong>Figura Interactiva No.1</strong></p>", unsafe_allow_html=True)
# --- SLIDERS ---
col_slider1, col_slider2 = st.columns([1, 1])
with col_slider1:
    cov = st.slider('Selecciona el *$CoV$*', 0.05, 0.30, 0.15)
with col_slider2:
    st.warning(f"CoV: {cov:.2f}. Se traduce en una desviación estándar de {cov*70:.1f} kPa.", icon="⚠️")

# --- GEOTECHNICAL CALCULATIONS (RETAINED) ---
H = 15          
gamma = 19      
Ns = 0.181     
SU_MEAN = 70    
SAMPLES = 10000 

def run_analysis(cov):
    std_dev = cov * SU_MEAN 
    width = std_dev * 6
    low_su = SU_MEAN - width/2
    high_su = SU_MEAN + width/2
    mode_su = SU_MEAN 
    
    alpha = 1 + 4 * (mode_su - low_su) / (high_su - low_su)
    beta_param = 1 + 4 * (high_su - mode_su) / (high_su - low_su)
    
    su_samples = beta.rvs(alpha, beta_param, loc=low_su, scale=width, size=SAMPLES)
    actual_mean_su = np.mean(su_samples)
    
    fs_samples = su_samples / (Ns * gamma * H)
    pf = np.sum(fs_samples < 1.0) / SAMPLES
    mean_fs_val = np.mean(fs_samples)
    
    # Scaling logic
    bin_size_su, bin_size_fs = 2.0, 0.05
    su_x_line = np.linspace(low_su, high_su, 200)
    su_y_freq = beta.pdf(su_x_line, alpha, beta_param, loc=low_su, scale=width) * SAMPLES * bin_size_su
    mean_su_freq = beta.pdf(actual_mean_su, alpha, beta_param, loc=low_su, scale=width) * SAMPLES * bin_size_su

    fs_line = np.linspace(0.01, 3.0, 500) 
    kde_func = gaussian_kde(fs_samples)
    fs_kde_freq = kde_func(fs_line) * SAMPLES * bin_size_fs
    mean_fs_freq = kde_func(mean_fs_val)[0] * SAMPLES * bin_size_fs

    return su_samples, su_x_line, su_y_freq, actual_mean_su, mean_su_freq, \
           fs_samples, fs_line, fs_kde_freq, mean_fs_val, mean_fs_freq, pf, low_su, high_su

# Run calculations
su_samples, su_x, su_y, m_su, m_su_y, fs_samples, fs_x, fs_y, m_fs, m_fs_y, pf, low_su, high_su = run_analysis(cov)

# --- BUILD SINGLE FIGURE (LEFT PLOT ONLY) ---
fig = go.Figure()

# Add Histogram
fig.add_trace(go.Histogram(
    x=su_samples, 
    xbins=dict(start=low_su, end=high_su, size=2.0), 
    marker_color='rgba(155, 89, 182, 0.6)', 
    name='Su Hist'
))

# Add Trend Line
fig.add_trace(go.Scatter(
    x=su_x, 
    y=su_y, 
    mode='lines', 
    line=dict(color='#9b59b6', width=3), 
    name='Su Trend'
))

# Add Mean Marker
fig.add_trace(go.Scatter(
    x=[m_su], 
    y=[m_su_y], 
    mode='markers+text', 
    marker=dict(color='#9b59b6', size=1), 
    text=[f"Prom: {m_su:.1f}"],
    textposition="top center",
    textfont=dict(size=15)
))

# Add Min Marker
fig.add_trace(go.Scatter(
    x=[low_su], 
    y=[100], 
    mode='markers+text', 
    marker=dict(color='#9b59b6', size=1), 
    text=[f"Min: {low_su:.1f}"],
    textposition="top left",
    textfont=dict(size=15)
))

# Add Max Marker
fig.add_trace(go.Scatter(
    x=[high_su], 
    y=[100], 
    mode='markers+text', 
    marker=dict(color='#9b59b6', size=1), 
    text=[f"Max: {high_su:.1f}"],
    textposition="top right",
    textfont=dict(size=15)
))

# Layout updates for a single plot
fig.update_layout(
    #title="Figura Interactiva 1",
    template="plotly_white", 
    barmode='overlay', 
    showlegend=False, 
    height=250,                                                                                                                                             

# --- CAMBIO AQUÍ: Reducción de márgenes ---
    margin=dict(t=0, b=20, l=10, r=10),
    dragmode=False, # Desactiva el arrastre del zoom    
    
    # Configuración del Eje X
    xaxis=dict(
        title=dict(
            text="Su (kPa)",
            font=dict(size=20) # Tamaño del título del eje
        ),
        tickfont=dict(size=16)   # Tamaño de los números/etiquetas del eje
    ),
    
    # Configuración del Eje Y
    yaxis=dict(
        title=dict(
            text="Frecuencia",
            font=dict(size=20) # Tamaño del título del eje
        ),
        tickfont=dict(size=16)   # Tamaño de los números/etiquetas del eje
    )
)

# Axis formatting
fig.update_xaxes(range=[-30, 180])
fig.update_yaxes(range=[0, 2200])

# Display in Streamlit

st.plotly_chart(fig, use_container_width=True, config=plotly_config)

st.info("💡 Observa cómo, aunque el valor más probable sigue siendo 70 kPa, el rango de valores posibles (mínimos y máximos) se expande drásticamente al variar el *$CoV$*. ")


st.write("""Si simulamos 10,000 veces el valor de *$Su$* a partir de su PDF y calculamos el *$FS$* para cada valor (un proceso conocido como Monte Carlo),
 obtendremos un histograma de resultados del *$FS$* como el de la **Figura Interactiva No. 2**.""")

st.write("""**Notaremos algo realmente interesante**: aunque el *$FS$* promedio sea estable, si aumentamos la 
incertidumbre (el *$CoV$*), algunos de esos 10,000 cálculos del *$FS$* caerán por debajo de 1.0. La proporción de esos 
casos es nuestra ***probabilidad de falla*** (*$P_f$*).""")

#------------------------------------
# FIGURE INTERACTIVE No. 2 
#------------------------------------
st.markdown("<p style='text-align: center;'><strong>Figura Interactiva No.2</strong></p>", unsafe_allow_html=True)
# Sliders are now inside the main page, not the sidebar
col_slider3, col_slider4 = st.columns([1, 1])
with col_slider3:
    cov = st.slider('Selecciona el CoV', 0.1, 0.30, 0.15)
#with col_slider2:
#    st.info(f"Current CoV: {cov:.2f}. This translates to a standard deviation of {cov*70:.1f} kPa.")

# --- GEOTECHNICAL CALCULATIONS (NO CHANGES) ---
H = 15          
gamma = 19      
Ns = 0.181      
SU_MEAN = 70    
SAMPLES = 10000 

def run_analysis(cov):
    std_dev = cov * SU_MEAN 
    width = std_dev * 6
    low_su = SU_MEAN - width/2
    high_su = SU_MEAN + width/2
    mode_su = SU_MEAN 
    
    alpha = 1 + 4 * (mode_su - low_su) / (high_su - low_su)
    beta_param = 1 + 4 * (high_su - mode_su) / (high_su - low_su)
    
    su_samples = beta.rvs(alpha, beta_param, loc=low_su, scale=width, size=SAMPLES)
    actual_mean_su = np.mean(su_samples)
    
    fs_samples = su_samples / (Ns * gamma * H)
    pf = np.sum(fs_samples < 1.0) / SAMPLES
    mean_fs_val = np.mean(fs_samples)
    
    # Scaling logic
    bin_size_su, bin_size_fs = 2.0, 0.05
    su_x_line = np.linspace(low_su, high_su, 200)
    su_y_freq = beta.pdf(su_x_line, alpha, beta_param, loc=low_su, scale=width) * SAMPLES * bin_size_su
    mean_su_freq = beta.pdf(actual_mean_su, alpha, beta_param, loc=low_su, scale=width) * SAMPLES * bin_size_su

    fs_line = np.linspace(0.01, 3.0, 500) 
    kde_func = gaussian_kde(fs_samples)
    fs_kde_freq = kde_func(fs_line) * SAMPLES * bin_size_fs
    mean_fs_freq = kde_func(mean_fs_val)[0] * SAMPLES * bin_size_fs

    return su_samples, su_x_line, su_y_freq, actual_mean_su, mean_su_freq, \
           fs_samples, fs_line, fs_kde_freq, mean_fs_val, mean_fs_freq, pf, low_su, high_su

# Run logic
su_samples, su_x, su_y, m_su, m_su_y, fs_samples, fs_x, fs_y, m_fs, m_fs_y, pf, low_su, high_su = run_analysis(cov)

# Build Figure
fig1 = make_subplots(rows=1, cols=2, subplot_titles=("Input: Resistencia", "Output: Estabilidad "))

# Add traces (Same as your Jupyter code)
fig1.add_trace(go.Histogram(x=su_samples, xbins=dict(start=low_su, end=high_su, size=2.0), marker_color='rgba(155, 89, 182, 0.6)', name='Su Hist'), row=1, col=1)
fig1.add_trace(go.Scatter(x=su_x, y=su_y, mode='lines', line=dict(color='#9b59b6', width=3), name='Su Trend'), row=1, col=1)
fig1.add_trace(go.Scatter(x=[m_su], y=[m_su_y], mode='markers+text', marker=dict(color='black', size=1), 
                         text=[f"Prom: {m_su:.1f}"], textposition="top center", 
                         textfont=dict(size=15)), row=1, col=1)

fig1.add_trace(go.Histogram(x=fs_samples[fs_samples < 1.0], xbins=dict(start=0, end=1.0, size=0.05), marker_color='#e74c3c', name='Fail'), row=1, col=2)
fig1.add_trace(go.Histogram(x=fs_samples[fs_samples >= 1.0], xbins=dict(start=1.0, end=5.0, size=0.05), marker_color='#27ae60', name='Safe'), row=1, col=2)
fig1.add_trace(go.Scatter(x=fs_x, y=fs_y, mode='lines', line=dict(color='#2c3e50', width=2), name='KDE'), row=1, col=2)
fig1.add_trace(go.Scatter(x=[m_fs], y=[m_fs_y], mode='markers+text', marker=dict(color='black', size=1), 
                         text=[f"Prom: {m_fs:.2f}"], textposition="top center", 
                         textfont=dict(size=15)), row=1, col=2)

fig1.update_layout(template="plotly_white", barmode='overlay', showlegend=False, height=250, margin=dict(t=0, b=20, l=10, r=10), dragmode=False)
# --- CAMBIO AQUÍ: Reducción de márgenes ---
fig1.update_xaxes(title_text="Su (kPa)", range=[0, 150], row=1, col=1)
fig1.update_yaxes(title_text="Frecuencia", range=[0, 1500], row=1, col=1)
fig1.update_xaxes(title_text="FS", range=[0.0, 3.0], row=1, col=2)
fig1.update_yaxes(title_text=" ", range=[0, 1500], row=1, col=2)
fig1.add_vline(x=1.0, line_dash="dash", line_color="black", line_width=0.5, row=1, col=2)
fig1.add_annotation(
    xref="x2", yref="y2", # Indica que pertenece al segundo gráfico (derecha)
    x=1.4,                # Posición en el eje FS (ajustado a la derecha)
    y=1300,               # Posición en el eje Frecuencia (ajustado al rango 1500)
    text=f"<b>Pf: {pf:.2%}</b>",
    showarrow=False,
    font=dict(size=18, color="#e74c3c"),
    bgcolor="white", 
    bordercolor="#e74c3c",
    borderwidth=2,
    borderpad=4
)

st.plotly_chart(fig1, use_container_width=True, config=plotly_config)

st.success("💡 Prueba esto: Cambia el valor del *CoV* y observa su impacto en la probabilidad de falla.")

#--------------------------------------
# Ejemplo 2: La Paradoja de la Ignorancia
#--------------------------------------

st.subheader("Ejemplo 2: La Paradoja de la Ignorancia")

st.write("""
Veamos las implicaciones de la incertidumbre en la estabilidad de taludes. Comparemos estos dos escenarios de diseño:
""")

# --- 1. Crear las dos columnas principales ---
col_tabla, col_grafica = st.columns([1.0, 1.0], gap="small", vertical_alignment="center")

# --- COLUMNA IZQUIERDA: Tabla de Parámetros ---
with col_tabla:
    st.markdown("""
| Parámetro | Escenario 1  | Escenario 2  |
| :--- | :--- | :--- |
| **Incertidumbre** | Alta (CoV 20%) | Baja (CoV 10%) |
| **Resistencia promedio ($S_u$)** | 65 kPa  | 55 kPa  |
| **Diseño Final** | Inclinación 45° | Inclinación 53° |
| **Factor de seguridad $FS$** | 1.58 | 1.33 |
| **Probabilidad de Falla $P_f$** | 🔴 **MÁS ALTA** | 🟢 **MÁS BAJA** |
""")
    

# --- COLUMNA DERECHA: Gráficos Geométricos ---
with col_grafica:
    # Parámetros constantes
    H = 12
    base_depth = -5#-5
    
    # Coordenadas Talud 1 (45°) -> dx = 12/tan(45) = 12
    dx1 = 12
    slope1_x = [10, 0, -dx1, -dx1-15, -dx1-15, 10, 10]
    slope1_y = [0, 0, H, H, base_depth, base_depth, 0]

    # Coordenadas Talud 2 (53°) -> dx = 12/tan(53) = 9.04
    dx2 = H / np.tan(np.radians(53))
    slope2_x = [10, 0, -dx2, -dx2-15, -dx2-15, 10, 10]
    slope2_y = [0, 0, H, H, base_depth, base_depth, 0]

    # Crear Subplots Verticales
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=("Escenario 1 (1H:1V - 45°)", 
                                        "Escenario 2 (3H:4V - 53°)"),
                        vertical_spacing=0.2)

    # Gráfico Superior (45°)
    fig.add_trace(go.Scatter(
        x=slope1_x, y=slope1_y,
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.3)',
        line=dict(color='black', width=2),
        mode='lines',
        name='45°'
    ), row=1, col=1)

    # Gráfico Inferior (53°)
    fig.add_trace(go.Scatter(
        x=slope2_x, y=slope2_y,
        fill='toself',
        fillcolor='rgba(52, 152, 219, 0.3)',
        line=dict(color='black', width=2),
        mode='lines',
        name='53°'
    ), row=2, col=1)

    # Configuración de Layout y Escala 1:1
    fig.update_layout(
        height=350,
        margin=dict(t=20, b=20, l=10, r=10),
        template="plotly_white",
        showlegend=False, 
        dragmode=False
    )
    
    # Aplicar escala 1:1 a ambos subplots
    fig.update_yaxes(scaleanchor="x", scaleratio=1, range=[base_depth, H+3])
    fig.update_xaxes(range=[-30, 15])
    
    st.plotly_chart(fig, use_container_width=True, config=plotly_config)



st.info("**Esta es la paradoja**: el talud del Escenario 1, con mayor resistencia y un $FS$ de 1.5, es más inseguro que el del Escenario 2 que tiene menor resistencia y mayor inclinación.\n\n **Nuestra propia ignorancia castigó el diseño**, obligándonos a ser conservadores en el papel, pero peligrosos en la realidad.")
st.write("""La **Figura Interactiva 3** nos ayuda a entender la paradoja:
""")

#------------------------------------
# FIGURE INTERACTIVE No. 3 
#------------------------------------
st.markdown("<p style='text-align: center;'><strong>Figura Interactiva No.3</strong></p>", unsafe_allow_html=True)

# --- PARÁMETROS GEOTÉCNICOS CONSTANTES ---
H = 12
gamma = 19
Ns1 = 0.181  
Ns2 = 0.181  
SAMPLES = 10000

# --- INTERFAZ DE USUARIO (SLIDERS) ---
col_sidebar1, col_sidebar2 = st.columns(2)

with col_sidebar1:
    cov1 = st.slider('$CoV$ Escenario 1', 0.1, 0.3, 0.20, 0.01)

with col_sidebar2:
    cov2 = st.slider('$CoV$ Escenario 2:', 0.1, 0.3, 0.10, 0.01)

# --- PROCESAMIENTO DE DATOS ---
def calculate_data(mean, cov, Ns, H, gamma, SAMPLES):
    std = cov * mean
    w = std * 6
    low, high = mean - w/2, mean + w/2
    samples = beta.rvs(4, 4, loc=low, scale=w, size=SAMPLES)
    fs = samples / (Ns * gamma * H)
    pf = np.sum(fs < 1.0) / SAMPLES
    mean_fs = np.mean(fs)
    return samples, fs, pf, mean_fs, low, high, w

# Ejecutar cálculos para ambos taludes
s1, fs1, pf1, m_fs1, l1, h1, w1 = calculate_data(65, cov1, Ns1, H, gamma, SAMPLES)
s2, fs2, pf2, m_fs2, l2, h2, w2 = calculate_data(55, cov2, Ns2, H, gamma, SAMPLES)

# --- CREACIÓN DE LA FIGURA 2x2 ---
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        f" ", #f"Escenario 1 Su - CoV: {cov1:.0%}"
        f" ", #f"Escenario 2 Su - CoV: {cov2:.0%}"
        f" ", #f"Escenario 1 - Pf: {pf1:.2%}"
        f" ", #f"Escenario 2 - Pf: {pf2:.2%}"
    ),
    vertical_spacing=0.30,
    horizontal_spacing=0.2
)

# --- TOP LEFT: Su 1 ---
x_line1 = np.linspace(l1, h1, 100)
y_line1 = beta.pdf(x_line1, 4, 4, loc=l1, scale=w1) * SAMPLES * 2.0 
fig.add_trace(go.Scatter(x=x_line1, y=y_line1, fill='tozeroy', line=dict(color='#9b59b6'), name='Su 1'), row=1, col=1)
fig.add_trace(go.Scatter(x=[65], y=[max(y_line1)], mode='markers+text', text=["Media: 65"], textposition="top center", marker=dict(color='black')), row=1, col=1)

# --- TOP RIGHT: Su 2 ---
x_line2 = np.linspace(l2, h2, 100)
y_line2 = beta.pdf(x_line2, 4, 4, loc=l2, scale=w2) * SAMPLES * 2.0
fig.add_trace(go.Scatter(x=x_line2, y=y_line2, fill='tozeroy', line=dict(color='#3498db'), name='Su 2'), row=1, col=2)
fig.add_trace(go.Scatter(x=[55], y=[max(y_line2)], mode='markers+text', text=["Media: 55"], textposition="top center", marker=dict(color='black')), row=1, col=2)

# --- BOTTOM LEFT: FS 1 ---
fig.add_trace(go.Histogram(x=fs1[fs1<1], xbins=dict(size=0.05), marker_color='#e74c3c'), row=2, col=1)
fig.add_trace(go.Histogram(x=fs1[fs1>=1], xbins=dict(size=0.05), marker_color='#27ae60'), row=2, col=1)
kde1 = gaussian_kde(fs1)
kde_x1 = np.linspace(0.5, 2.5, 100)
kde_y1 = kde1(kde_x1) * SAMPLES * 0.05
fig.add_trace(go.Scatter(x=kde_x1, y=kde_y1, line=dict(color='black', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=[m_fs1], y=[kde1(m_fs1)[0]*SAMPLES*0.05], mode='markers+text', text=[f"Mean: {m_fs1:.2f}"], textposition="top center", marker=dict(color='black')), row=2, col=1)

# --- BOTTOM RIGHT: FS 2 ---
fig.add_trace(go.Histogram(x=fs2[fs2<1], xbins=dict(size=0.05), marker_color='#e74c3c'), row=2, col=2)
fig.add_trace(go.Histogram(x=fs2[fs2>=1], xbins=dict(size=0.05), marker_color='#27ae60'), row=2, col=2)
kde2 = gaussian_kde(fs2)
kde_x2 = np.linspace(0.5, 2.5, 100)
kde_y2 = kde2(kde_x2) * SAMPLES * 0.05
fig.add_trace(go.Scatter(x=kde_x2, y=kde_y2, line=dict(color='black', width=2)), row=2, col=2)
fig.add_trace(go.Scatter(x=[m_fs2], y=[kde2(m_fs2)[0]*SAMPLES*0.05], mode='markers+text', text=[f"Mean: {m_fs2:.2f}"], textposition="top center", marker=dict(color='black')), row=2, col=2)

# --- CONFIGURACIÓN FINAL ---
fig.update_layout(height=300, template="plotly_white", barmode='overlay', showlegend=False, margin=dict(t=20, b=50, l=10, r=10), dragmode=False)
fig.update_xaxes(title_text="Su (kPa)", range=[0, 130], row=1)
fig.update_xaxes(title_text=f"Escenario 1<br><b>Pf: {pf1:.2%}</b>", range=[0.0, 3.0],row=2, col=1)
fig.update_xaxes(title_text=f"Escenario 2<br><b>Pf: {pf2:.2%}</b>", range=[0.0, 3.0],row=2, col=2)
fig.update_yaxes(title_text=" ", row=1, range=[0, 1800])
fig.update_yaxes(title_text=" ", row=2, range=[0, 1800])
fig.add_vline(x=1.0, line_dash="dash", line_color="grey", row=2, col=1, line_width=0.5)
fig.add_vline(x=1.0, line_dash="dash", line_color="grey", row=2, col=2, line_width=0.5)

# Mostrar gráfico en Streamlit

st.plotly_chart(fig, use_container_width=True, config=plotly_config)

st.warning("En términos estadisticos diríamos que el talud del **Escenario 1 es {pf1/pf2:.0f} o más veces más propenso a fallar que el talud del Escenario 2**.", icon="⚠️")
  

st.divider() # Visual line separator
st.header("""Conclusión: ¿Seguridad real o ilusión contractual?""")

st.write("""
En el conversatorio de la SCG, un colega lo resumió perfectamente: reducir la incertidumbre le permitía 
diseñar taludes más inclinados con un *$FS$* de 1.3, ahorrando millones en excavaciones y obras, manteniendo 
un nivel de estabilidad real mayor que un FS de 1.5.

Lamentablemente, a veces la *rigidez normativa* nos obliga a veces a gastar dinero innecesario para cumplir con
 un número que es, en el fondo, una ilusión.


**En resumen**: un *$FS$* de 1.5 sin contexto es solo un número reconfortante, 
pero potencialmente engañoso. En geotecnia no buscamos la certeza absoluta, sino la gestión inteligente de la incertidumbre. 

""")

st.success('**Próxima entrega: *Estadística bayesiana* o porque los geotecnista somos *bayesianos* innatos**', icon="✍🏼")































