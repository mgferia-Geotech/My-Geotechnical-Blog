import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st 
from scipy.stats import norm

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Geotechnical Engineering Blog", layout="centered")

# --- MOBILE CONFIGURATION ---
# Esto evita que el zoom se active al tocar con el dedo y quita la barra de herramientas
plotly_config = {
    'scrollZoom': False,
    'displayModeBar': False,
    'staticPlot': False,
}

# --- BLOG HEADER ---
st.markdown("""
    <h1 style='margin-bottom: 0px;'>¿Somos los geotecnistas bayesianos innatos?</h1>
    <p style='font-size: 1.2em; margin-top: -10px; color: grey;'>
        ESTADÍSTICA BAYESIANA EN GEOTECNIA
    </p>
    """, unsafe_allow_html=True)

st.write("""
**Por: Mauricio García F** | *Publicado: Febrero 2026* """)

st.write("""
** ⏱️Tiempo de lectura: 4 min** """)

st.write("""
Se ha dicho hasta la saciedad que la geotecnia, por tratar con materiales naturales, debería estar más enfocada hacia la estadística y la probabilidad. 
Pero la probabilidad como disciplina se nos ha contado de manera incompleta. 

Básicamente, existen dos formas de entender la probabilidad:

- **La escuela frecuentista:** La probabilidad es el resultado de miles de ensayos (el sueño de cualquier laboratorio, pero la pesadilla del presupuesto).
- **La escuela bayesiana:** La probabilidad es una mezcla entre conocimiento previo e información de investigación geotécnica del proyecto.

Es a esta *última escuela* hacia la que más me oriento cuando pienso en nuestro trabajo como geotecnistas. 

""")

st.divider()

# --- BAYESIAN ANALYSIS SECTION ---
st.header("El enfoque bayesiano: Una máquina de actualización")
st.write("""
El Teorema de Bayes no es más que una ecuación para actualizar nuestro conocimiento a medida que obtenemos información. 
En términos simples, es cómo funciona nuestro cerebro y cómo interpretamos la realidad (ciclo de aprendizaje continuo):

1. **Conocimiento previo (Prior)**: Lo que creemos saber antes de ver cualquier dato o información (nuestras creencias).
2. **Evidencia (Likelihood)**: Lo que nos dicen los nuevos datos.
3. **Conocimiento actualizado (Posterior)**: Nuestro nuevo conocimiento luego de contrastar ambos.


Matemáticamente, el teorema de Bayes es elegante:
""")

# --- OPTION 1: THE EQUATION ---
st.latex(r'''
P(\theta | \text{Data}) \propto P(\text{Data} | \theta) \cdot P(\theta)
''')

st.info("En palabras simples: El conocimiento actualizado es el resultado de pasar el conocimiento previo por el tamiz de la evidencia.", icon ="💡")


st.header("El Método Observacional: Bayes en geotecnia")

st.write("""El Método Observacional en geotecnia es la aplicación cualitativa de este teorema.

1. **Diseñamos** escenarios basados en nuestra experiencia (Prior).
2. **Monitoreamos** el comportamiento real de la estructura (Likelihood).
3. **Ajustamos** el diseño sobre la marcha para adaptarlo a la realidad observada (Posterior).

Dado que aplicamos el método observacional a nuestros diseños podemos suponer que como geotecnistas somos bayesianos. Sin embargo, esta aplicación 
cualitativa nos hace confiar a veces excesivamente en el *juicio de expertos*. El problema es que 
el juicio humano es difícil de explicar y muy propenso a los sesgos.

La buena noticia es que el teorema de Bayes permite cuantificar matemáticamente nuestra intuición y el "juicio experto".
""")

st.header("¿Cómo aplicar Bayes en geotecnia? (un ejemplo práctico)")

st.write("""Supongamos que queremos evaluar la resistencia no drenada (*$Su$*) de una arcilla. Tenemos dos fuentes de información que no coinciden completamente. ¿A cuál le creemos?
Usemos el teorema de Bayes para dar una respuesta técnica (ver figura más abajo):

**1. El punto de partida (Prior):** Basado en estudios antiguos y en nuestra experiencia en la zona, estimamos que la resistencia es 50 kPa. Como confiamos en esa información, pero sabemos que no es perfecta, le asignamos una incertidumbre (CoV) del 15%.
En la gráfica corresponde a la línea azul discontinua.

**2. La nueva evidencia (Likelihood):** Decidimos realizar ensayos de veleta in situ. Obtenemos estos valores: [58, 62, 55, 52, 80, 71] kPa. Los datos nuevos sugieren una resistencia mayor a la que pensábamos.
En la gráfica está representada por la línea naranja.

**3. El conocimiento actualizado (Posterior):** En lugar de descartar nuestra experiencia o ignorar los datos nuevos, el teorema de Bayes combina ambas fuentes de información. 
El resultado es la línea verde.
""")


# --- SITE DATA (The "Likelihood" Source) ---
SITE_DATA = [58, 62, 55, 52, 80, 71] 
OBS_MEAN = np.mean(SITE_DATA)
OBS_STD = np.std(SITE_DATA) if len(SITE_DATA) > 1 else 5.0
N_OBS = len(SITE_DATA)
std_error = OBS_STD / np.sqrt(N_OBS)

# --- CALCULATIONS FUNCTION ---
def run_bayesian_logic(prior_m, prior_cov):
    prior_s = prior_m * prior_cov
    
    # Bayesian Normal-Normal Conjugate Update
    prec_prior = 1 / (prior_s**2)
    prec_obs = N_OBS / (OBS_STD**2)
    
    post_var = 1 / (prec_prior + prec_obs)
    post_m = (prec_prior * prior_m + prec_obs * OBS_MEAN) / (prec_prior + prec_obs)
    post_s = np.sqrt(post_var)
    
    x_su = np.linspace(0, 150, 500)
    return x_su, prior_m, prior_s, post_m, post_s

# --- 1. SLIDERS (PLACED BEFORE THE PLOT) ---
st.warning("""
    **Instrucciones de interacción:**
    
    Ajusta los parámetros **Prior Mean** y **Prior CoV** para observar cómo varía la distribución **Posterior**.
    
    1. Observa que para **CoV altos** (p.ej. CoV=0.3), los datos tienen una fuerte influencia sobre el posterior (el modelo confía más en la evidencia).
    2. Por el contrario, para **CoV bajos** (p.ej. CoV=0.1), el resultado es una combinación equilibrada de ambas fuentes de información.
    """, icon="⚠️")

col_slider1, col_slider2 = st.columns([1, 1])
with col_slider1:
    prior_m = st.slider('Prior Mean $s_u$ (kPa)', 40, 80, 50, step=2)
with col_slider2:
    prior_cov = st.slider('Prior $CoV$', 0.05, 0.40, 0.15, step=0.01)

# Run calculations based on slider input
x_su, p_m, p_s, po_m, po_s = run_bayesian_logic(prior_m, prior_cov)

# --- 2. BUILD THE FIGURE ---
fig_bayesian = go.Figure()

# 1. Field Data Markers (Red dots on axis)
fig_bayesian.add_trace(go.Scatter(
    x=SITE_DATA, y=[0]*N_OBS, mode='markers', name='Datos de Campo',
    marker=dict(symbol='circle', size=8, color='#e74c3c', line=dict(width=1, color='black')),
    cliponaxis=False
))

# 2. Prior Distribution (Blue Dash)
fig_bayesian.add_trace(go.Scatter(
    x=x_su, y=norm.pdf(x_su, p_m, p_s), name='Prior (Juicio)', 
    line=dict(dash='dash', color='#007bff', width=2), 
    fill='tozeroy', fillcolor='rgba(0, 123, 255, 0.05)'
))

# 3. Likelihood (Orange Shade)
fig_bayesian.add_trace(go.Scatter(
    x=x_su, y=norm.pdf(x_su, OBS_MEAN, std_error), name='Likelihood (Evidencia)', 
    line=dict(color='#ff7f0e', width=3), 
    fill='toself', fillcolor='rgba(255, 127, 14, 0.1)'
))

# 4. Posterior Distribution (Green Solid)
fig_bayesian.add_trace(go.Scatter(
    x=x_su, y=norm.pdf(x_su, po_m, po_s), name='Posterior (Actualizado)', 
    line=dict(color='#2ca02c', width=4), 
    fill='tozeroy', fillcolor='rgba(44, 160, 44, 0.2)'
))
# --- ADD THIS SECTION TO CALCULATE PEAK VALUES ---
# Calculate the y-coordinate (PDF height) at the mean for each curve
y_peak_prior = norm.pdf(p_m, p_m, p_s)
y_peak_like = norm.pdf(OBS_MEAN, OBS_MEAN, std_error)
y_peak_post = norm.pdf(po_m, po_m, po_s)

# Add Mean Markers/Labels to the plot
# Label for Prior
fig_bayesian.add_trace(go.Scatter(
    x=[p_m], y=[y_peak_prior], mode='markers+text',
    text=[f"{p_m:.1f}"], textposition="top left",
    textfont=dict(size=18, color='#1e1f21'),
    marker=dict(color='#007bff', size=8), showlegend=False
))

# Label for Likelihood
fig_bayesian.add_trace(go.Scatter(
    x=[OBS_MEAN], y=[y_peak_like], mode='markers+text',
    text=[f"{OBS_MEAN:.1f}"], textposition="top right",
    textfont=dict(size=18, color='#1e1f21'),
    marker=dict(color='#ff7f0e', size=8), showlegend=False
))

# Label for Posterior
fig_bayesian.add_trace(go.Scatter(
    x=[po_m], y=[y_peak_post], mode='markers+text',
    text=[f"{po_m:.1f}"], textposition="top center",
    textfont=dict(size=18, color='#1e1f21'),
    marker=dict(color='#2ca02c', size=10, symbol='diamond'), showlegend=False
))

# Layout updates
fig_bayesian.update_layout(
    template="plotly_white",
    height=450,
    margin=dict(t=10, b=20, l=10, r=10),
    xaxis=dict(title="Resistencia No Drenada Su (kPa)", range=[20, 100], tickfont=dict(size=14)),
    yaxis=dict(title="Densidad", range=[-0.005, 0.25], tickfont=dict(size=14)),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    dragmode=False
)


# --- 3. DISPLAY THE PLOT ---
# Ensure plotly_config is defined or remove the config parameter
st.plotly_chart(fig_bayesian, use_container_width=True)

st.info("La curva posterior (verde) acepta los datos nuevos pero mantiene la influencia de los estudios antiguos y de nuestra experiencia.", icon="🏆")

st.header("De la intuición y el juicio experto al marco matemático")

st.write("""
Los geotecnistas somos bayesianos intuitivos, no solo por la aplicación del método observacional sino 
por la manera como estimamos parámetros. Pero nuestra intuición tiene un límite.  El teorema de Bayes no 
reemplaza nuestra experiencia, nos proporciona un marco matemático donde podemos cuantificarla.

**Es hora de ponerle números a nuestro “juicio experto”**.
""")

st.success("Próxima entrada: sobre cómo elegimos los parámetros de diseño y sus herramientas estadisticas de apoyo.", icon = "📅")

