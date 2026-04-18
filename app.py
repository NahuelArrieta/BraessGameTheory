import streamlit as st
import matplotlib.pyplot as plt
import random

# --- CLASES DE AGENTES (Lógica simplificada del Profesor) ---
class Agente:
    def __init__(self, id, alpha, tipo):
        self.id = id
        self.alpha = alpha
        self.tipo = tipo
        self.p = 0.5  # Creencia inicial de saturación

    def actualizar_creencia(self, hubo_sat):
        self.p = (1 - self.alpha) * self.p + self.alpha * hubo_sat

    def decidir(self, c_s, c_libre, c_sat):
        if self.tipo == "Neutral":
            e_ca = (self.p * c_sat) + ((1 - self.p) * c_libre)
            return "Atajo" if e_ca < c_s else "Segura"
        else: # Averso (Costo cuadrático t^2)
            costo_atajo = (self.p * (c_sat**2)) + ((1 - self.p) * (c_libre**2))
            return "Atajo" if costo_atajo < (c_s**2) else "Segura"

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Simulador Paradoja de Braess", layout="wide")
st.title("🧪 Laboratorio: Paradoja de Braess")
st.markdown("Ajustá los parámetros para ver cómo la psicología del riesgo colapsa la red.")

# Sidebar: Controles
st.sidebar.header("Parámetros de la Red")
n_agentes = st.sidebar.slider("N° de Agentes", 10, 500, 100)
capacidad = st.sidebar.slider("Capacidad del Atajo (K)", 5, 100, 25)
c_s = st.sidebar.number_input("Costo Ruta Segura (Cs)", value=45)
c_libre = st.sidebar.number_input("Costo Atajo Libre (Clibre)", value=10)
gamma = st.sidebar.slider("Factor de Congestión (Gamma)", 0.1, 5.0, 1.5)

st.sidebar.header("Población")
pct_aversos = st.sidebar.slider("% Agentes Aversos (t²)", 0, 100, 50)
rondas = st.sidebar.slider("Rondas de Simulación", 10, 200, 100)

# Inicializar agentes
poblacion = []
for i in range(n_agentes):
    tipo = "Averso" if i < (n_agentes * pct_aversos / 100) else "Neutral"
    poblacion.append(Agente(i, alpha=0.2, tipo=tipo))

# Simulación
historial_flujo = []
historial_costo_medio = []

for r in range(rondas):
    decisiones = [a.decidir(c_s, c_libre, c_libre + gamma * (n_agentes-capacidad)) for a in poblacion]
    x = decisiones.count("Atajo")
    
    # Costo dinámico
    costo_real_atajo = c_libre + gamma * max(0, x - capacidad)
    hubo_sat = 1 if x > capacidad else 0
    
    # Feedback
    for a in poblacion:
        a.actualizar_creencia(hubo_sat)
        
    # Guardar métricas
    costo_total = (x * costo_real_atajo) + ((n_agentes - x) * c_s)
    historial_flujo.append(x)
    historial_costo_medio.append(costo_total / n_agentes)

# --- VISUALIZACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Flujo en el Atajo")
    fig1, ax1 = plt.subplots()
    ax1.plot(historial_flujo, color="royalblue")
    ax1.axhline(capacidad, color="red", linestyle="--", label="Capacidad K")
    ax1.set_xlabel("Ronda")
    ax1.set_ylabel("Agentes")
    ax1.legend()
    st.pyplot(fig1)

with col2:
    st.subheader("Costo Medio del Viaje")
    fig2, ax2 = plt.subplots()
    ax2.plot(historial_costo_medio, color="orange")
    ax2.axhline(c_s, color="green", linestyle="--", label="Costo sin Atajo")
    ax2.set_xlabel("Ronda")
    ax2.set_ylabel("Minutos")
    ax2.legend()
    st.pyplot(fig2)

# Métrica del Costo de la Anarquía (PoA)
poa_final = historial_costo_medio[-1] / ( (capacidad*c_libre + (n_agentes-capacidad)*c_s) / n_agentes )
st.metric("Price of Anarchy (PoA)", f"{poa_final:.2f}")