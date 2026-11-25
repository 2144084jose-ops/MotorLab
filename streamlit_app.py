import math
import streamlit as st

st.set_page_config(
    page_title="MotorLab",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp {
        background: #080039;
        color: white;
    }
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3, p, label {
        color: white !important;
    }
    .motor-plate {
        background: #D9D9D9;
        color: #080039;
        border: 5px solid #464646;
        border-radius: 12px;
        padding: 1.4rem 2rem 1.8rem 2rem;
        box-shadow: 0 8px 22px rgba(0,0,0,.28);
        margin: 1rem auto;
    }
    .plate-heading {
        color: #080039;
        text-align: center;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: 2px;
        border-bottom: 3px solid #080039;
        padding-bottom: .8rem;
        margin-bottom: 1rem;
    }
    .stNumberInput label {
        color: #080039 !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
    }
    .stNumberInput input {
        background: #F7F7F7 !important;
        color: #080039 !important;
        font-weight: 700 !important;
    }
    div.stButton > button {
        background: #D9D9D9;
        color: #080039;
        border: 2px solid white;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.05rem;
        padding: .65rem 2.5rem;
        display: block;
        margin: 1rem auto;
    }
    div.stButton > button:hover {
        background: white;
        color: #080039;
        border-color: white;
    }
    .result-card {
        background: #D9D9D9;
        color: #080039;
        border-radius: 9px;
        padding: 1rem 1.2rem;
        margin: .4rem 0;
        min-height: 75px;
    }
    .result-name {
        color: #080039;
        font-weight: 800;
        font-size: .95rem;
    }
    .result-value {
        color: #080039;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: .25rem;
    }
    .stAlert p { color: inherit !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center; color:white; font-size:2.7rem;'>⚙️ MotorLab</h1>"
    "<p style='text-align:center; color:#D9D9D9 !important;'>Análisis y cálculo de parámetros de motores eléctricos</p>",
    unsafe_allow_html=True,
)

st.markdown("<div class='motor-plate'>", unsafe_allow_html=True)
st.markdown("<div class='plate-heading'>PLACA DE DATOS DEL MOTOR</div>", unsafe_allow_html=True)

with st.form("motor_data"):
    c1, c2, c3 = st.columns(3)
    with c1:
        hp = st.number_input("HP", min_value=0.0, value=50.0, step=1.0, format="%.2f")
        volts = st.number_input("VOLTS", min_value=0.0, value=220.0, step=1.0, format="%.2f")
        amps = st.number_input("AMPS", min_value=0.0, value=6.0, step=0.5, format="%.2f")
    with c2:
        fp = st.number_input("FP", min_value=0.0, max_value=1.0, value=0.85, step=0.01, format="%.2f")
        rpm = st.number_input("RPM", min_value=0.0, value=1670.0, step=10.0, format="%.2f")
        poles = st.number_input("P (número de polos)", min_value=1, value=4, step=1)
    with c3:
        hz = st.number_input("HZ", min_value=0.0, value=60.0, step=1.0, format="%.2f")
        hours_day = st.number_input("Horas de funcionamiento al día", min_value=0.0, max_value=24.0, value=24.0, step=1.0, format="%.2f")
        st.markdown("<div style='color:#080039; padding-top:1.9rem; font-weight:700;'>Periodo de cálculo: 30 días</div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("CALCULAR")

st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    try:
        # Se conservan las fórmulas del programa de escritorio MotorLab.
        hrs = 30 * hours_day

        if hp <= 0 or volts <= 0 or amps <= 0 or rpm <= 0:
            raise ValueError("Los valores de HP, voltaje, corriente y RPM deben ser positivos.")
        if not 0 < fp <= 1:
            raise ValueError("El factor de potencia debe estar entre 0 y 1.")
        if poles <= 0 or hz <= 0 or not 0 < hrs <= 720:
            raise ValueError("Revisa el número de polos, la frecuencia y las horas de funcionamiento.")

        ns = 120 * hz / poles
        slip = (ns - rpm) / ns * 100
        torque = 1.356 * (hp * 5252) / rpm
        efficiency = hp * 746 / (1.73205 * volts * amps * fp) * 100
        penalty = 0.6 * (0.95 / fp - 1)
        bonus = 0.25 * (1 - 0.95 / 0.98)
        kwh = hp * 0.746 * hrs
        charge = kwh * 3 * (1 + penalty)
        phi = math.acos(fp)
        tangent = math.tan(phi)

        q1 = kwh * tangent
        q2 = kwh * 0.203059
        capacitor_kvar = (q1 - q2) / hrs
        capacitor_bank = math.ceil(capacitor_kvar / 10) * 10

        capacitor_cost = capacitor_bank * 1300
        investment = capacitor_cost + 26000
        savings = charge - kwh * 3 * (1 - bonus)

        if savings <= 0:
            raise ValueError("El ahorro mensual calculado no es positivo; revisa el factor de potencia y los datos ingresados.")

        payback = math.ceil(investment / savings)

        st.markdown("<h2 style='text-align:center; margin-top:2rem;'>RESULTADOS DEL MOTOR</h2>", unsafe_allow_html=True)
        st.caption("Resultados calculados con los datos ingresados. Los costos son estimaciones según los valores establecidos en el programa.")

        results = [
            ("Velocidad síncrona", f"{ns:.2f} RPM"),
            ("Deslizamiento", f"{slip:.2f} %"),
            ("Torque", f"{torque:.2f} N·m"),
            ("Eficiencia", f"{efficiency:.2f} %"),
            ("Consumo mensual", f"{kwh:.2f} kWh"),
            ("Cobro mensual", f"${charge:,.2f}"),
            ("Banco de capacitores requerido", f"{capacitor_kvar:.2f} kVAR"),
            ("Capacidad comercial estimada", f"{capacitor_bank:.2f} kVAR"),
            ("Costo del banco de capacitores", f"${capacitor_cost:,.2f}"),
            ("Inversión total aproximada", f"${investment:,.2f}"),
            ("Ahorro mensual estimado", f"${savings:,.2f}"),
            ("Retorno de inversión", f"{payback} meses"),
        ]

        for start in range(0, len(results), 3):
            cols = st.columns(3)
            for col, (name, value) in zip(cols, results[start:start + 3]):
                with col:
                    st.markdown(
                        f"<div class='result-card'><div class='result-name'>{name}</div>"
                        f"<div class='result-value'>{value}</div></div>",
                        unsafe_allow_html=True,
                    )

        st.info("Nota: los resultados dependen de los datos introducidos y de las fórmulas y tarifas configuradas en MotorLab.")
    except (ValueError, ZeroDivisionError) as error:
        st.error(f"No fue posible realizar el cálculo. {error}")

st.markdown(
    "<p style='text-align:center; color:#D9D9D9 !important; margin-top:2.5rem; font-size:.85rem;'>"
    "MotorLab | Herramienta de apoyo para el análisis de motores eléctricos</p>",
    unsafe_allow_html=True,
)
