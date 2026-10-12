import streamlit as st
import numpy as np
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y ESTÉTICA INSTITUCIONAL HOSPITALARIA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ateneo Psiquiatría | Neurobiología de THC y Neurodesarrollo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo sobrio y clínico de alto contraste
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        letter-spacing: -0.3px;
    }
    .stMetric {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 12px 14px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PANEL LATERAL: PARÁMETROS DEL PACIENTE EN EL ATENEO
# -----------------------------------------------------------------------------
st.sidebar.title("Perfil Clínico del Paciente")
st.sidebar.caption("Variables farmacocinéticas, ventana ontogenética y perfil genético:")

edad_inicio = st.sidebar.slider(
    "1. Edad de inicio de consumo regular (Años)",
    min_value=12, max_value=28, value=15, step=1,
    help="Define si la exposición ocurrió durante la poda sináptica frontal (<16 años) o en etapa posmadurativa (>21 años)."
)

potencia_thc = st.sidebar.slider(
    "2. Potencia estimada de la cepa (% Δ⁹-THC)",
    min_value=2, max_value=30, value=22, step=1,
    help="Cannabis tradicional (años 80-90): 2-4%. Flores hidropónicas, extractos y vaporizadores actuales: 16-28% de THC."
)

frecuencia_semanal = st.sidebar.slider(
    "3. Frecuencia de consumo (Días/semana)",
    min_value=1, max_value=7, value=6, step=1,
    help="El consumo diario produce ocupación sostenida del receptor CB1, induciendo su internalización vesicular."
)

anios_consumo = st.sidebar.slider(
    "4. Años de consumo sostenido",
    min_value=1, max_value=15, value=5, step=1,
    help="Duración del período de exposición durante el neurodesarrollo o la adultez."
)

abstinencia_semanas = st.sidebar.slider(
    "5. Tiempo de abstinencia actual (Semanas)",
    min_value=0, max_value=24, value=0, step=1,
    help="0 = Consumo activo actual. Las 4 semanas (28 días) representan el hito de resensibilización receptora documentado por PET."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Farmacogenética Prefrontal")
polimorfismo_comt = st.sidebar.selectbox(
    "Genotipo COMT (Val158Met)",
    options=[
        "Val/Val (Actividad enzimática rápida)",
        "Val/Met (Actividad enzimática intermedia)",
        "Met/Met (Actividad enzimática lenta)"
    ],
    index=0,
    help="La catecol-O-metiltransferasa degrada la dopamina en corteza prefrontal. Val/Val tiene menor dopamina basal y mayor vulnerabilidad ejecutiva al THC."
)

# -----------------------------------------------------------------------------
# 3. MOTOR FARMACODINÁMICO HETEROGÉNEO Y PSICOMÉTRICO
# -----------------------------------------------------------------------------

# Modulador genético de COMT
if "Val/Val" in polimorfismo_comt:
    mod_comt = 1.35
    desc_gen = (
        "Genotipo Val/Val: Máxima velocidad de degradación enzimática. El tono dopaminérgico prefrontal basal es muy bajo. "
        "Cuando el THC bloquea la modulación inhibitoria retrógrada, este grupo sufre la mayor caída en memoria de trabajo y velocidad de procesamiento."
    )
elif "Val/Met" in polimorfismo_comt:
    mod_comt = 1.00
    desc_gen = (
        "Genotipo Val/Met: Actividad enzimática intermedia. Susceptibilidad promedio congruente con las curvas de cohorte poblacional."
    )
else:
    mod_comt = 0.70
    desc_gen = (
        "Genotipo Met/Met: Degradación lenta de catecolaminas. Mantiene niveles basales elevados de dopamina prefrontal, amortiguando el impacto en pruebas ejecutivas, "
        "aunque con mayor reactividad psicotomimética (paranoia/saliencia aberrante) ante dosis agudas elevadas."
    )

# Factor ontogenético de vulnerabilidad de poda (Gogtay et al. / Lewis et al.)
vuln_poda = 1.0 / (1.0 + np.exp((edad_inicio - 17.5) / 1.3))

# Carga de exposición acumulada normalizada (Unidades Cannabinoides Estándar)
carga_thc = (potencia_thc / 5.0) * (frecuencia_semanal / 7.0) * anios_consumo

# Cinética de Receptores CB1 y Modelado Regional Heterogéneo (Hirvonen et al., 2012; D'Souza et al., 2016)
# En consumo activo, el estriado y cíngulo sufren una internalización más agresiva que la corteza prefrontal
downreg_base = 0.55 * (1.0 - np.exp(-carga_thc / 3.0))

if abstinencia_semanas == 0:
    recup_factor = 0.0
else:
    recup_factor = 1.0 - np.exp(-abstinencia_semanas / 1.35)

downreg_actual = downreg_base * (1.0 - recup_factor)
disponibilidad_cb1_global = (1.0 - downreg_actual) * 100.0
disponibilidad_cb1_global = min(100.0, max(35.0, disponibilidad_cb1_global))

# Heterogeneidad regional del volumen de distribución (Vt en mL/cm3)
vt_ctrl_dlpfc = 1.35
vt_ctrl_acc = 1.25
vt_ctrl_estriado = 1.45
vt_ctrl_ventriculo = 0.05

# DLPFC: Vulnerabilidad intermedia
caida_frac_dlpfc = downreg_actual * 0.90
vt_pac_dlpfc = vt_ctrl_dlpfc * (1.0 - caida_frac_dlpfc)

# ACC (Cíngulo Anterior): Vulnerabilidad marcada
caida_frac_acc = downreg_actual * 1.05
vt_pac_acc = vt_ctrl_acc * (1.0 - caida_frac_acc)

# Estriado / Caudado / Putamen: Máxima internalización por densidad de CB1 y tono dopaminérgico
caida_frac_estriado = downreg_actual * 1.20
vt_pac_estriado = vt_ctrl_estriado * (1.0 - caida_frac_estriado)

# Ventrículos: LCR puro sin receptores CB1
vt_pac_ventriculo = vt_ctrl_ventriculo

# Reversibilidad estructural a largo plazo (Dunedin / ABCD)
capacidad_reversibilidad = 1.0 / (1.0 + np.exp(-(edad_inicio - 19.5) / 1.2))
factor_abstinencia_recup = min(1.0, (abstinencia_semanas / 24.0)) * capacidad_reversibilidad

# Subescalas neuropsicológicas WAIS-IV
caida_max_psi = 10.2 * vuln_poda * (1.0 - np.exp(-carga_thc / 4.8)) * mod_comt
caida_act_psi = -1.0 * (caida_max_psi * (1.0 - (factor_abstinencia_recup * 0.65)))

caida_max_wmi = 8.8 * vuln_poda * (1.0 - np.exp(-carga_thc / 4.8)) * mod_comt
caida_act_wmi = -1.0 * (caida_max_wmi * (1.0 - (factor_abstinencia_recup * 0.60)))

caida_max_pri = 5.0 * vuln_poda * (1.0 - np.exp(-carga_thc / 6.0))
caida_act_pri = -1.0 * (caida_max_pri * (1.0 - (factor_abstinencia_recup * 0.75)))

caida_max_vci = 1.8 * vuln_poda * (1.0 - np.exp(-carga_thc / 8.0))
caida_act_vci = -1.0 * (caida_max_vci * (1.0 - (factor_abstinencia_recup * 0.90)))

# FSIQ compuesto (CI Total)
fsiq_neto = (caida_act_psi * 0.35) + (caida_act_wmi * 0.35) + (caida_act_pri * 0.15) + (caida_act_vci * 0.15)

# Fenotipo neurobiológico
if edad_inicio < 17 and anios_consumo >= 3:
    fenotipo = "Disrupción Estructural Persistente"
    fenotipo_desc = "Pérdida de espinas dendríticas en interneuronas GABAérgicas PV+ y mielinización trunca de sustancia blanca. Secuela irreversible."
elif edad_inicio < 21:
    fenotipo = "Vulnerabilidad Intermedia"
    fenotipo_desc = "Afección mixta: desensibilización de receptores combinada con remodelado axonal parcial. Reversión incompleta."
else:
    fenotipo = "Disfunción Funcional Reversible"
    fenotipo_desc = "Downregulation aislada de receptores CB1 sin alteración estructural de microcircuitos. Recuperación completa tras cese sostenido."

# -----------------------------------------------------------------------------
# 4. ENCABEZADO Y TARJETAS MÉTRICAS INSTITUCIONALES
# -----------------------------------------------------------------------------
st.title("Dinámica de Neurodesarrollo, Plasticidad y Exposición a Δ⁹-THC")
st.markdown("**Simulador Cuantitativo de Farmacodinámica del Receptor CB1, Tomografía PET y Trayectorias Psicométricas Longitudinales** | Ateneo de Residencia de Psiquiatría")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        label="VULNERABILIDAD DE PODA CORTICAL",
        value=f"{vuln_poda * 100:.1f} %",
        help=f"Susceptibilidad ontogenética calculada a los {edad_inicio} años. Cuantifica el riesgo de poda aberrante en interneuronas GABAérgicas de parvalbúmina."
    )
    st.caption(f"Ventana de maduración prefrontal a los {edad_inicio} años.")

with col_m2:
    delta_cb1 = f"{(disponibilidad_cb1_global - 100.0):.1f} %" if disponibilidad_cb1_global < 99.0 else "Basal Fisiológico"
    st.metric(
        label="DENSIDAD CB1 EN PET ([¹⁸F]FMPEP-d₂)",
        value=f"{disponibilidad_cb1_global:.1f} %",
        delta=delta_cb1,
        help="Disponibilidad global de receptores CB1 expresados en membrana celular respecto a sujetos control sanos."
    )
    txt_abs_estado = "Consumo activo (Semana 0)" if abstinencia_semanas == 0 else f"{abstinencia_semanas} sem. de abstinencia"
    st.caption(f"Estado clínico: {txt_abs_estado}.")

with col_m3:
    st.metric(
        label="IMPACTO NETO EN CI TOTAL (FSIQ)",
        value=f"{fsiq_neto:.1f} pts",
        delta=f"{fsiq_neto:.1f} WAIS",
        delta_color="inverse",
        help="Pérdida en la Escala de Inteligencia para Adultos de Wechsler (WAIS-IV) ponderada según cohorte Dunedin y genotipo COMT."
    )
    st.caption(f"Genotipo COMT: {polimorfismo_comt.split()[0]}.")

with col_m4:
    st.metric(
        label="FENOTIPO NEUROESTRUCTURAL",
        value=fenotipo,
        help=fenotipo_desc
    )
    st.caption(fenotipo_desc[:44] + "...")

st.divider()

# -----------------------------------------------------------------------------
# 5. PESTAÑAS ACADÉMICAS
# -----------------------------------------------------------------------------
tab_pet, tab_trayectoria, tab_wais, tab_conclusiones = st.tabs([
    "🔬 1. Neuroimagen PET y Cuantificación de ROI",
    "📈 2. Trayectoria Longitudinal del CI y Ventana Crítica",
    "📊 3. Desglose Neuropsicológico (WAIS-IV) y Gemelos",
    "💎 4. Perlas Clínicas y Cierre del Ateneo"
])

# -----------------------------------------------------------------------------
# PESTAÑA 1: NEUROIMAGEN PET & CUANTIFICACIÓN REGIONAL
# -----------------------------------------------------------------------------
with tab_pet:
    st.subheader("Farmacodinámica del Receptor CB1 y Reconstrucción Tomográfica PET")
    st.markdown(
        "Esta sección modela la desensibilización por internalización vesicular (*downregulation*) de los receptores CB1 "
        "inducida por agonistas de alta potencia, evaluada mediante el radiotrazador específico de PET **[¹⁸F]FMPEP-d₂** (antagonista inverso lipofílico)."
    )
    
    col_pet_l, col_pet_r = st.columns([1, 1])
    
    with col_pet_l:
        st.markdown("**Cinética Temporal de Reversión de CB1 tras el Cese del Consumo**")
        semanas_vec = np.linspace(0, 12, 140)
        curva_recup = ((1.0 - downreg_base) + (downreg_base * (1.0 - np.exp(-semanas_vec / 1.35)))) * 100.0
        
        fig_pet_curva = go.Figure()
        
        fig_pet_curva.add_trace(go.Scatter(
            x=semanas_vec, y=[100]*len(semanas_vec),
            mode='lines', name='Control Sano (Línea Basal 100%)',
            line=dict(color='#10B981', width=1.5, dash='dash')
        ))
        
        fig_pet_curva.add_trace(go.Scatter(
            x=semanas_vec, y=curva_recup,
            mode='lines', name='Cinética de Reexpresión CB1',
            line=dict(color='#F59E0B', width=3)
        ))
        
        marcador_x = min(12.0, float(abstinencia_semanas))
        fig_pet_curva.add_trace(go.Scatter(
            x=[marcador_x], y=[disponibilidad_cb1_global],
            mode='markers+text', name='Estado Actual del Paciente',
            marker=dict(color='#EF4444', size=13, symbol='diamond'),
            text=[f"Semana {abstinencia_semanas}: {disponibilidad_cb1_global:.1f}%"],
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=11)
        ))
        
        fig_pet_curva.add_vrect(
            x0=0, x1=4, fillcolor="rgba(239, 68, 68, 0.08)",
            layer="below", line_width=0,
            annotation_text="Ventana de Resensibilización Rápida (0-4 semanas)",
            annotation_position="bottom right",
            annotation_font=dict(color="#EF4444", size=10)
        )
        
        fig_pet_curva.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0D131F',
            xaxis=dict(title="Semanas de Abstinencia Monitorizada", gridcolor='#1E293B', range=[0, 12]),
            yaxis=dict(title="Disponibilidad de Receptores CB1 (% del Basal)", gridcolor='#1E293B', range=[30, 110]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=20, b=20),
            height=370
        )
        st.plotly_chart(fig_pet_curva, use_container_width=True, key="plot_pet_curva_stable")
        
    with col_pet_r:
        st.markdown("**Corte Axial Tomográfico PET: Control Sano vs. Paciente Actual**")
        st.caption("Reconstrucción a nivel de corteza prefrontal, cíngulo anterior, estriado y ventrículos laterales.")
        
        # Malla anatómica para simular el corte axial
        n = 55
        x = np.linspace(-3, 3, n)
        y = np.linspace(-3, 3, n)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + (Y/1.2)**2)
        mascara = R <= 2.2
        
        # Componentes anatómicos del cerebro sano
        pfc = np.exp(-((X)**2 + (Y - 1.4)**2) / 0.7) * 1.10
        cing = np.exp(-((X)**2 + (Y - 0.3)**2) / 0.45) * 1.00
        estriado = (np.exp(-((X - 0.9)**2 + (Y + 0.1)**2) / 0.32) + np.exp(-((X + 0.9)**2 + (Y + 0.1)**2) / 0.32)) * 1.15
        corteza = np.exp(-((R - 1.8)**2) / 0.22) * 0.75
        ventriculos = (np.exp(-((X - 0.35)**2 + (Y - 0.3)**2) / 0.08) + np.exp(-((X + 0.35)**2 + (Y - 0.3)**2) / 0.08)) * 1.3
        
        senal_sana = np.maximum(0, (pfc + cing + estriado + corteza - ventriculos)) * mascara
        
        # Componentes anatómicos del cerebro del paciente con atenuación regional real
        pfc_pac = pfc * (1.0 - caida_frac_dlpfc)
        cing_pac = cing * (1.0 - caida_frac_acc)
        estriado_pac = estriado * (1.0 - caida_frac_estriado)
        corteza_pac = corteza * (disponibilidad_cb1_global / 100.0)
        
        senal_paciente = np.maximum(0, (pfc_pac + cing_pac + estriado_pac + corteza_pac - ventriculos)) * mascara
        
        separador = np.zeros((n, 6))
        m_dual = np.hstack([senal_sana, separador, senal_paciente])
        
        fig_pet_axial = go.Figure(data=go.Heatmap(
            z=m_dual,
            colorscale='Jet',
            zmin=0.0, zmax=1.2,
            showscale=True,
            colorbar=dict(
                title=dict(text="Unión CB1 (Vt en mL/cm³)", side="right"),
                thickness=12,
                len=0.8,
                tickfont=dict(color="#CBD5E1", size=10)
            )
        ))
        
        fig_pet_axial.add_annotation(x=13, y=51, text="CONTROL SANO (100%)", showarrow=False, font=dict(color="#10B981", size=11))
        fig_pet_axial.add_annotation(x=91, y=51, text=f"PACIENTE ({disponibilidad_cb1_global:.1f}%)", showarrow=False, font=dict(color="#EF4444" if disponibilidad_cb1_global < 85 else "#10B981", size=11))
        
        fig_pet_axial.add_annotation(x=13, y=41, text="DLPFC", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=91, y=41, text="DLPFC", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=22, y=28, text="Estriado", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        fig_pet_axial.add_annotation(x=100, y=28, text="Estriado", showarrow=True, arrowhead=2, arrowcolor="#FFFFFF", font=dict(color="#FFFFFF", size=9))
        
        fig_pet_axial.add_annotation(x=52, y=53, text="ANTERIOR (Frontal)", showarrow=False, font=dict(color="#94A3B8", size=9))
        fig_pet_axial.add_annotation(x=52, y=2, text="POSTERIOR (Occipital)", showarrow=False, font=dict(color="#94A3B8", size=9))
        
        fig_pet_axial.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=370
        )
        st.plotly_chart(fig_pet_axial, use_container_width=True, key="plot_pet_axial_stable")

    # Guía de lectura del mapa de color
    st.info(
        "**INTERPRETACIÓN RADIOLÓGICA DEL MAPA DE COLOR EN PET:**\n\n"
        "* **Rojo / Naranja intenso (Vt > 1.1 mL/cm³):** Densidad fisiológica normal. La membrana plasmática de las interneuronas GABAérgicas y neuronas espinosas medias tiene abundantes receptores CB1 listos para modular la sinapsis.\n"
        "* **Amarillo / Verde (Vt ≈ 0.7 - 0.9 mL/cm³):** Desensibilización e inicio de reciclaje endosomal. La señal inhibitoria retrógrada se vuelve errática.\n"
        "* **Azul frío / Cian (Vt < 0.6 mL/cm³):** Downregulation marcada. El receptor fue secuestrado al citoplasma; la neurona pierde su freno presináptico y queda desinhibida.\n"
        "* **Negro / Azul marino central:** Ventrículos laterales. Líquido cefalorraquídeo sin receptores (control anatómico de ruido de fondo)."
    )

    # Cuantificación regional de volumen de distribución (Vt) con explicación semiológica individual
    st.markdown("#### Cuantificación de Volumen de Distribución Regional ($V_T$ en $\\text{mL/cm}^3$)")
    st.caption("El volumen de distribución $V_T$ es la relación matemática entre el radiotrazador unido al receptor cerebral y su fracción libre en plasma. Menor $V_T$ indica directamente menor cantidad de receptores CB1 disponibles.")
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.metric(
            label="DLPFC (Corteza Prefrontal Dorsolateral)",
            value=f"{vt_pac_dlpfc:.2f} mL/cm³",
            delta=f"{-caida_frac_dlpfc*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Impacto:** Memoria de trabajo y control inhibitorio. Al caer el freno CB1 sobre interneuronas de parvalbúmina, colapsa la sincronía en banda gamma (40 Hz).")
        
    with col_t2:
        st.metric(
            label="Cíngulo Anterior (ACC)",
            value=f"{vt_pac_acc:.2f} mL/cm³",
            delta=f"{-caida_frac_acc*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Impacto:** Detección de conflicto cognitivo y monitoreo de errores. Su hipofunción explica el sesgo atencional hacia el consumo y la perseveración en conductas automáticas.")
        
    with col_t3:
        st.metric(
            label="Estriado / Caudado / Accumbens",
            value=f"{vt_pac_estriado:.2f} mL/cm³",
            delta=f"{-caida_frac_estriado*100:.1f} %",
            delta_color="inverse"
        )
        st.caption("**Impacto:** Sistema de recompensa y saliencia. Es la región de mayor pérdida receptora en consumo diario; fundamenta la anhedonia y la hipodopaminergia en abstinencia.")
        
    with col_t4:
        st.metric(
            label="Ventrículos Laterales (LCR)",
            value=f"{vt_pac_ventriculo:.2f} mL/cm³",
            delta="0.0 % (Basal)",
            delta_color="off"
        )
        st.caption("**Impacto:** Control radiológico negativo. Al carecer de receptores CB1, valida que la atenuación observada en las otras regiones es fisiopatológica y no un artefacto técnico.")

    st.markdown("---")

    # Explicación del estado actual del paciente
    if abstinencia_semanas == 0:
        st.error(
            f"**ESTADO CLÍNICO: CONSUMO ACTIVO ({potencia_thc}% THC, {frecuencia_semanal} días/semana):** "
            f"La estimulación suprafisiológica continuada mantiene a los receptores CB1 fosforilados por cinasas GRKs y acoplados a beta-arrestina-2, "
            f"provocando su internalización hacia endosomas intracelulares. En el corte PET se observa una reducción del {100 - disponibilidad_cb1_global:.1f}% "
            f"en la unión del radiotrazador. Clínicamente, el paciente presenta saturación farmacodinámica con desinhibición dopaminérgica subcortical y pérdida del control ejecutivo frontal."
        )
    elif abstinencia_semanas < 4:
        st.warning(
            f"**ESTADO CLÍNICO: FASE DE RESENSIBILIZACIÓN ACTIVA ({abstinencia_semanas} semanas de abstinencia monitorizada):** "
            f"Los endosomas están reciclando y reinsertando progresivamente los receptores CB1 en la membrana neuronal. "
            f"La densidad actual se ubica en el {disponibilidad_cb1_global:.1f}%. La imagen de PET muestra que el estriado y la DLPFC comienzan a recuperar "
            f"tonalidades amarillas y naranjas, aunque persiste aún una neurotransmisión GABAérgica inestable, sustrato del insomnio y la irritabilidad propios del síndrome de abstinencia."
        )
    else:
        st.success(
            f"**ESTADO CLÍNICO: RECUPERACIÓN RECEPTORA COMPLETA ({abstinencia_semanas} semanas de abstinencia confirmada):** "
            f"Superado el umbral de 4 semanas (28 a 30 días documentados por Hirvonen et al.), el volumen de unión del radiotrazador [¹⁸F]FMPEP-d₂ "
            f"se normaliza al {disponibilidad_cb1_global:.1f}%, siendo indistinguible de la de un sujeto control sano. "
            f"**Advertencia para el ateneo:** La recuperación del receptor no regenera la conectividad sináptica si la poda axonal ya fue truncada durante la adolescencia."
        )

    with st.expander("📚 Analogía Pedagógica: La Fábrica y el Freno de Mano", expanded=True):
        st.markdown(
            "El receptor CB1 funciona como el **pedal de freno retrógrado** de la neurona. Cuando entra THC a dosis masivas y continuas, la neurona siente "
            "que el pedal está trabado a fondo; para evitar destruirse, *desmonta el pedal y lo esconde dentro del chasis* (internalización a vesículas). "
            "A las 4 semanas de abstinencia, la célula vuelve a colocar el pedal en su lugar.\n\n"
            "**El mensaje crítico para la residencia:** *Que el pedal esté de vuelta no significa que la estructura del motor siga intacta si el consumo ocurrió "
            "mientras el auto aún se estaba ensamblando en la fábrica (la adolescencia).*"
        )

# -----------------------------------------------------------------------------
# PESTAÑA 2: TRAYECTORIA LONGITUDINAL DEL CI
# -----------------------------------------------------------------------------
with tab_trayectoria:
    st.subheader("Trayectoria Longitudinal del Coeficiente Intelectual (10 a 45 años)")
    st.caption("Contraste psicométrico sustentado en la cohorte de Dunedin (Meier et al., PNAS 2012 / Am J Psychiatry 2022).")
    
    edades = np.linspace(10, 45, 180)
    ci_base = 100.0
    edad_cese = edad_inicio + anios_consumo
    
    ci_vals = []
    ci_low = []
    ci_high = []
    
    for e in edades:
        if e < edad_inicio:
            val = ci_base
        elif e <= edad_cese:
            prog = (e - edad_inicio) / max(1, anios_consumo)
            val = ci_base - (abs(fsiq_neto) * prog)
        else:
            t_post = e - edad_cese
            perdida = abs(fsiq_neto)
            recup = perdida * (0.80 * capacidad_reversibilidad) * min(1.0, t_post / 2.0)
            val = ci_base - perdida + recup
            
        ci_vals.append(val)
        disp = 2.0 + (0.3 * (e - 10) / 10.0)
        ci_low.append(val - disp)
        ci_high.append(val + disp)
        
    fig_tr = go.Figure()
    
    fig_tr.add_trace(go.Scatter(
        x=np.concatenate([edades, edades[::-1]]),
        y=np.concatenate([ci_high, ci_low[::-1]]),
        fill='toself', fillcolor='rgba(239, 68, 68, 0.08)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip", showlegend=False
    ))
    
    fig_tr.add_trace(go.Scatter(
        x=edades, y=[100]*len(edades),
        mode='lines', name='Control Normativo Poblacional (Sin exposición)',
        line=dict(color='#64748B', width=2, dash='dash')
    ))
    
    fig_tr.add_trace(go.Scatter(
        x=edades, y=ci_vals,
        mode='lines', name='Paciente Simulado',
        line=dict(color='#EF4444', width=3.5)
    ))
    
    fig_tr.add_vline(x=edad_inicio, line_width=1.5, line_dash="dot", line_color="#F59E0B")
    fig_tr.add_annotation(x=edad_inicio, y=107, text=f"Inicio regular ({edad_inicio}a)", showarrow=False, font=dict(color="#F59E0B", size=11), bgcolor="#1E293B")
    
    fig_tr.add_vline(x=edad_cese, line_width=1.5, line_dash="dot", line_color="#10B981")
    fig_tr.add_annotation(x=edad_cese, y=104, text=f"Cese ({edad_cese}a)", showarrow=False, font=dict(color="#10B981", size=11), bgcolor="#1E293B")
    
    min_y = min(85.0, min(ci_low) - 2)
    fig_tr.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0D131F',
        xaxis=dict(title="Edad Cronológica (Años)", gridcolor='#1E293B', range=[10, 45]),
        yaxis=dict(title="Puntuación Escala WAIS (CI Total)", gridcolor='#1E293B', range=[min_y, 110.0]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=20, b=20),
        height=390
    )
    st.plotly_chart(fig_tr, use_container_width=True, key="plot_tr_long_stable")
    
    if edad_inicio < 17:
        st.error(
            f"**VENTANA CRÍTICA AFECTADA:** Al iniciar a los {edad_inicio} años, la exposición coincidió con el pico de poda sináptica de interneuronas de parvalbúmina (PV+) "
            f"y la mielinización del fascículo uncinado. La pérdida estimada es de {abs(fsiq_neto):.1f} puntos de CI Total. Aun con cese posterior del consumo, "
            f"la capacidad de reversibilidad es de apenas {capacidad_reversibilidad*100:.1f}%, reproduciendo el daño estructural irreversible documentado por Meier et al. en Dunedin."
        )
    else:
        st.info(
            f"**INICIO EN FASE POSMADURATIVA:** Al iniciar a los {edad_inicio} años, las redes sinápticas frontales y los tractos de sustancia blanca ya habían completado "
            f"su arquitectura estructural adulta. La caída en rendimiento durante el consumo activo responde a saturación funcional reversible. Tras la abstinencia, "
            f"el modelo predice una recuperación del {capacidad_reversibilidad*100:.1f}% del rendimiento basal."
        )

    with st.expander("📚 Analogía Pedagógica: Cemento Fresco vs. Cemento Fraguado", expanded=True):
        st.markdown(
            "El cerebro adolescente es **cemento fresco**: cualquier pisada o alteración química durante el fraguado deja una huella permanente para el resto de la vida "
            "(pérdida estructural de arborización dendrítica).\n\n"
            "El cerebro de un adulto de 24 años es **cemento ya seco**: el cannabis derrama barro encima (disfunción ejecutiva transitoria mientras está bajo el tóxico), "
            "pero tras unas semanas de limpieza y abstinencia, la estructura original sigue estando debajo intacta."
        )

# -----------------------------------------------------------------------------
# PESTAÑA 3: DESGLOSE WAIS-IV Y CONTROL DE GEMELOS
# -----------------------------------------------------------------------------
with tab_wais:
    st.subheader("Desglose por Dominios Neuropsicológicos (Escala WAIS-IV)")
    st.caption("Por qué la noción de 'pérdida homogénea de CI' es metodológicamente incorrecta: afección selectiva en dominios fluidos vs. conservación de áreas cristalizadas.")
    
    col_wais_l, col_wais_r = st.columns([1, 1])
    
    with col_wais_l:
        st.markdown("**Variación respecto a la Línea de Base por Dominio**")
        doms = [
            "Velocidad de Procesamiento (PSI)",
            "Memoria de Trabajo (WMI)",
            "Razonamiento Perceptivo (PRI)",
            "Comprensión Verbal (VCI)"
        ]
        vals = [caida_act_psi, caida_act_wmi, caida_act_pri, caida_act_vci]
        
        fig_wais_bar = go.Figure(go.Bar(
            x=vals, y=doms, orientation='h',
            marker=dict(
                color=['#EF4444', '#F59E0B', '#3B82F6', '#10B981'],
                line=dict(color='#1E293B', width=1)
            ),
            text=[f"{v:.1f} pts" for v in vals],
            textposition='outside',
            textfont=dict(color="#FFFFFF", size=11)
        ))
        
        min_x = min(-12.0, min(vals) - 2.5)
        fig_wais_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#0D131F',
            xaxis=dict(title="Diferencial respecto a la Línea Basal (Puntos WAIS-IV)", gridcolor='#1E293B', range=[min_x, 1]),
            yaxis=dict(gridcolor='#1E293B', autorange="reversed"),
            margin=dict(l=20, r=30, t=10, b=20),
            height=340
        )
        st.plotly_chart(fig_wais_bar, use_container_width=True, key="plot_wais_bar_stable")
        
    with col_wais_r:
        st.markdown("**Correlato Semiográfico y Circuitos Afectados**")
        st.markdown(
            f"* **Velocidad de Procesamiento (PSI) [{caida_act_psi:.1f} pts]:** Mayor deterioro. Correlaciona con menor anisotropía fraccional en el "
            f"**cuerpo calloso y fascículo uncinado** demostrada mediante Resonancia con Tensor de Difusión (DTI). En la consulta: bradipsiquia y lentitud psicomotriz al resolver tareas secuenciales.\n"
            f"* **Memoria de Trabajo (WMI) [{caida_act_wmi:.1f} pts]:** Pérdida de sincronía en oscilaciones gamma (40 Hz) en la "
            f"**corteza prefrontal dorsolateral (DLPFC)** por desensibilización del freno GABAérgico retrogrado. En la consulta: dificultad para retener series numéricas inversas y pérdida del hilo conversacional.\n"
            f"* **Comprensión Verbal (VCI) [{caida_act_vci:.1f} pts]:** Redes cristalizadas de alta resiliencia ontogenética; vocabulario y abstracción verbal se mantienen estables."
        )
        
    st.info(f"**FARMACOGENÉTICA COMT Val158Met ({polimorfismo_comt.split()[0]}):** {desc_gen}")
    st.divider()
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.warning(
            "**Objeción Metodológica: Rogeberg (PNAS, 2013)**\n\n"
            "Argumentó que la caída de CI observada en Dunedin obedecía a variables socioeconómicas confusoras "
            "(menor nivel socioeconómico basal y deserción escolar temprana), no a neurotoxicidad directa."
        )
        
    with col_e2:
        st.success(
            "**Resolución Científica: Jackson et al. (PNAS, 2016)**\n\n"
            "Estudio en **gemelos monocigóticos discordantes**: al controlar al 100% la carga genética y el entorno sociofamiliar compartido, "
            "el gemelo expuesto presentó un déficit selectivo dosis-dependiente en **velocidad de procesamiento y memoria de trabajo**, "
            "validando el sustrato biológico neurotóxico directo."
        )

# -----------------------------------------------------------------------------
# PESTAÑA 4: PERLAS CLÍNICAS Y CONCLUSIONES
# -----------------------------------------------------------------------------
with tab_conclusiones:
    st.subheader("Perlas Clínicas de Cierre: Lo que el Psiquiatra debe llevarse a la Sala y Guardia")
    st.caption("Síntesis traslacional basada en la evidencia presentada:")

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.success(
            "**1. La Disociación Receptor-Estructura:**\n\n"
            "Que los receptores CB1 se recuperen al 100% en PET tras 4 semanas de abstinencia **no equivale a que el cerebro se haya curado**. "
            "En el adolescente, el receptor vuelve a la membrana pero la arborización dendrítica y la mielinización que debían ocurrir en esa ventana "
            "temporal quedaron truncadas de forma irreversible."
        )
        st.info(
            "**2. La Falacia del 'CI Global':**\n\n"
            "El cannabis no deteriora todas las funciones cognitivas por igual. En la práctica clínica y pericial, no busques deterioro en comprensión verbal "
            "o vocabulario; el daño específico radica en **velocidad de procesamiento psicomotriz (PSI) y memoria de trabajo (WMI)**, correlacionando con las fibras "
            "de sustancia blanca y la sincronía gamma a 40 Hz."
        )

    with c_p2:
        st.warning(
            "**3. Interacción Gen-Ambiente (GxE):**\n\n"
            "El impacto cognitivo y psicótico no depende únicamente de los gramos consumidos. La dotación genética en enzimas de degradación dopaminérgica "
            "(**COMT Val158Met**) y señalización de supervivencia neuronal (**AKT1**) explica por qué dos pacientes con la misma exposición presentan evoluciones pronósticas divergentes."
        )
        st.error(
            "**4. La Ventana Crítica de los 16-18 Años:**\n\n"
            "El factor pronóstico determinante no es la potencia del cannabis en la adultez, sino la **edad del primer consumo regular**. Retrasar el inicio del consumo "
            "más allá de los 20-21 años transforma un riesgo de daño neuroestructural permanente en una disfunción funcional predominantemente reversible tras la cesación sostenida."
        )
        