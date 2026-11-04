import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Geometría 3D: círculo, elipse y recta",
    page_icon="📐",
    layout="wide",
)

st.markdown(
    """
    <style>
    .banner {
        background: linear-gradient(90deg, #0077B6, #00B4D8);
        padding: 18px 26px;
        border-radius: 14px;
        margin-bottom: 18px;
    }
    .banner h1 { color: white; margin: 0; font-size: 1.9rem; }
    .banner p  { color: #E8F7FF; margin: 4px 0 0 0; }
    </style>
    <div class="banner">
        <h1>📐 Geometría 3D interactiva</h1>
        <p>Círculo, elipse y recta en el espacio. Edita los valores del panel
        izquierdo y arrastra el gráfico para girarlo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Funciones matemáticas
# ------------------------------------------------------------------
def rotacion(rx, ry, rz):
    """Matriz de rotación a partir de ángulos en grados (ejes X, Y, Z)."""
    rx, ry, rz = np.radians([rx, ry, rz])
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(rx), -np.sin(rx)],
                   [0, np.sin(rx), np.cos(rx)]])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry)],
                   [0, 1, 0],
                   [-np.sin(ry), 0, np.cos(ry)]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                   [np.sin(rz), np.cos(rz), 0],
                   [0, 0, 1]])
    return Rz @ Ry @ Rx


def puntos_curva(f, n=360):
    """Puntos 3D de un círculo o elipse (círculo = elipse con a = b)."""
    t = np.linspace(0, 2 * np.pi, n)
    local = np.vstack([f["a"] * np.cos(t), f["b"] * np.sin(t), np.zeros_like(t)])
    R = rotacion(f["rx"], f["ry"], f["rz"])
    return R @ local + np.array(f["centro"]).reshape(3, 1)


# ------------------------------------------------------------------
# Panel lateral: controles editables
# ------------------------------------------------------------------
st.sidebar.title("⚙️ Panel de control")
st.sidebar.caption("Todo se actualiza al instante.")


def panel_figura(titulo, k, elipse, color, centro, giro):
    with st.sidebar.expander(titulo, expanded=True):
        on = st.checkbox("Mostrar", True, key=f"{k}_on")
        if elipse:
            a = st.slider("Semieje a (X local)", 0.5, 10.0, 5.0, 0.1, key=f"{k}_a")
            b = st.slider("Semieje b (Y local)", 0.5, 10.0, 2.5, 0.1, key=f"{k}_b")
        else:
            a = st.slider("Radio", 0.5, 10.0, 3.0, 0.1, key=f"{k}_r")
            b = a
        st.markdown("**Centro**")
        c1, c2, c3 = st.columns(3)
        cx = c1.number_input("X", value=float(centro[0]), step=0.5, key=f"{k}_cx")
        cy = c2.number_input("Y", value=float(centro[1]), step=0.5, key=f"{k}_cy")
        cz = c3.number_input("Z", value=float(centro[2]), step=0.5, key=f"{k}_cz")
        st.markdown("**Giro (grados)**")
        rx = st.slider("Alrededor del eje X", -180, 180, giro[0], key=f"{k}_rx")
        ry = st.slider("Alrededor del eje Y", -180, 180, giro[1], key=f"{k}_ry")
        rz = st.slider("Alrededor del eje Z", -180, 180, giro[2], key=f"{k}_rz")
        col = st.color_picker("Color", color, key=f"{k}_col")
        relleno = st.checkbox("Rellenar superficie", False, key=f"{k}_fill")
    return dict(on=on, a=a, b=b, centro=(cx, cy, cz), rx=rx, ry=ry, rz=rz,
                color=col, relleno=relleno)


circulo = panel_figura("⭕ Círculo", "c", False, "#00B4D8", (0, 0, 0), (0, 0, 0))
elipse = panel_figura("🥚 Elipse", "e", True, "#F77F00", (0, 0, 2), (45, 0, 0))

with st.sidebar.expander("📏 Recta", expanded=True):
    r_on = st.checkbox("Mostrar", True, key="r_on")
    st.markdown("**Punto 1**")
    p1c = st.columns(3)
    x1 = p1c[0].number_input("X", value=-6.0, step=0.5, key="x1")
    y1 = p1c[1].number_input("Y", value=-4.0, step=0.5, key="y1")
    z1 = p1c[2].number_input("Z", value=-2.0, step=0.5, key="z1")
    st.markdown("**Punto 2**")
    p2c = st.columns(3)
    x2 = p2c[0].number_input("X", value=6.0, step=0.5, key="x2")
    y2 = p2c[1].number_input("Y", value=4.0, step=0.5, key="y2")
    z2 = p2c[2].number_input("Z", value=6.0, step=0.5, key="z2")
    ext = st.slider("Extender la recta (× su longitud)", 0.0, 2.0, 0.0, 0.1, key="ext")
    r_col = st.color_picker("Color", "#2DC653", key="r_col")
    r_marc = st.checkbox("Marcar los puntos 1 y 2", True, key="r_marc")

with st.sidebar.expander("🎨 Vista y estilo", expanded=False):
    ancho = st.slider("Grosor de las líneas", 1, 12, 6)
    vista = st.selectbox(
        "Vista de la cámara",
        ["Isométrica", "Superior (plano XY)", "Frontal (plano XZ)", "Lateral (plano YZ)"],
    )
    tema = st.selectbox("Tema del gráfico", ["Claro", "Oscuro"])
    ejes = st.checkbox("Mostrar ejes", True)
    cuadricula = st.checkbox("Mostrar cuadrícula", True)
    centros = st.checkbox("Marcar los centros", True)
    altura = st.slider("Altura del gráfico (px)", 400, 900, 650, 10)

CAMARAS = {
    "Isométrica": dict(eye=dict(x=1.6, y=1.6, z=1.2)),
    "Superior (plano XY)": dict(eye=dict(x=0.0, y=0.001, z=2.6)),
    "Frontal (plano XZ)": dict(eye=dict(x=0.0, y=-2.6, z=0.001)),
    "Lateral (plano YZ)": dict(eye=dict(x=2.6, y=0.0, z=0.001)),
}

# ------------------------------------------------------------------
# Construcción del gráfico 3D
# ------------------------------------------------------------------
fig = go.Figure()
tablas = []
resumen = {}


def hover(nombre):
    return "x=%{x:.2f}<br>y=%{y:.2f}<br>z=%{z:.2f}<extra>" + nombre + "</extra>"


for nombre, f in (("Círculo", circulo), ("Elipse", elipse)):
    if not f["on"]:
        continue
    p = puntos_curva(f)
    fig.add_trace(go.Scatter3d(
        x=p[0], y=p[1], z=p[2], mode="lines", name=nombre,
        line=dict(color=f["color"], width=ancho), hovertemplate=hover(nombre),
    ))
    if f["relleno"]:
        n = p.shape[1]
        cx, cy, cz = f["centro"]
        fig.add_trace(go.Mesh3d(
            x=np.append(p[0], cx), y=np.append(p[1], cy), z=np.append(p[2], cz),
            i=np.full(n - 1, n), j=np.arange(n - 1), k=np.arange(1, n),
            color=f["color"], opacity=0.25, showlegend=False, hoverinfo="skip",
        ))
    if centros:
        fig.add_trace(go.Scatter3d(
            x=[f["centro"][0]], y=[f["centro"][1]], z=[f["centro"][2]],
            mode="markers", marker=dict(size=5, color=f["color"], symbol="diamond"),
            showlegend=False, hovertemplate=hover(nombre + " (centro)"),
        ))
    tablas.append(pd.DataFrame({"Figura": nombre, "x": p[0], "y": p[1], "z": p[2]}))
    resumen[nombre] = f

if r_on:
    P1 = np.array([x1, y1, z1])
    P2 = np.array([x2, y2, z2])
    d = P2 - P1
    inicio, fin = P1 - ext * d, P2 + ext * d
    fig.add_trace(go.Scatter3d(
        x=[inicio[0], fin[0]], y=[inicio[1], fin[1]], z=[inicio[2], fin[2]],
        mode="lines", name="Recta", line=dict(color=r_col, width=ancho),
        hovertemplate=hover("Recta"),
    ))
    if r_marc:
        fig.add_trace(go.Scatter3d(
            x=[P1[0], P2[0]], y=[P1[1], P2[1]], z=[P1[2], P2[2]],
            mode="markers+text", text=["P1", "P2"], textposition="top center",
            marker=dict(size=6, color=r_col), showlegend=False,
            hovertemplate=hover("Punto"),
        ))
    tablas.append(pd.DataFrame({
        "Figura": "Recta",
        "x": [inicio[0], fin[0]], "y": [inicio[1], fin[1]], "z": [inicio[2], fin[2]],
    }))

fig.update_layout(
    template="plotly_dark" if tema == "Oscuro" else "plotly_white",
    height=altura,
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(orientation="h", y=1.04, x=0),
    scene=dict(
        xaxis=dict(title="X", visible=ejes, showgrid=cuadricula),
        yaxis=dict(title="Y", visible=ejes, showgrid=cuadricula),
        zaxis=dict(title="Z", visible=ejes, showgrid=cuadricula),
        aspectmode="data",
        camera=CAMARAS[vista],
    ),
)

# ------------------------------------------------------------------
# Pestañas
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Gráfico 3D", "📐 Ecuaciones", "🗂️ Datos", "ℹ️ Ayuda"])

with tab1:
    if not fig.data:
        st.info("Activa al menos una figura en el panel de la izquierda.")
    else:
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Arrastra para girar · rueda del mouse para acercar · "
                   "el ícono de cámara (arriba a la derecha del gráfico) descarga una imagen PNG.")

with tab2:
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("⭕ Círculo")
        if circulo["on"]:
            r = circulo["a"]
            normal = rotacion(circulo["rx"], circulo["ry"], circulo["rz"]) @ np.array([0, 0, 1])
            st.metric("Radio", f"{r:.2f}")
            st.metric("Circunferencia", f"{2 * np.pi * r:.2f}")
            st.metric("Área", f"{np.pi * r ** 2:.2f}")
            st.latex(rf"x'^2 + y'^2 = {r:.2f}^2")
            st.caption(f"Vector normal al plano: ({normal[0]:.2f}, {normal[1]:.2f}, {normal[2]:.2f})")
        else:
            st.write("Oculto")

    with col_b:
        st.subheader("🥚 Elipse")
        if elipse["on"]:
            a, b = elipse["a"], elipse["b"]
            mayor, menor = max(a, b), min(a, b)
            exc = np.sqrt(1 - (menor / mayor) ** 2)
            perim = np.pi * (3 * (a + b) - np.sqrt((3 * a + b) * (a + 3 * b)))
            st.metric("Semiejes (a, b)", f"{a:.2f}, {b:.2f}")
            st.metric("Excentricidad", f"{exc:.3f}")
            st.metric("Área", f"{np.pi * a * b:.2f}")
            st.metric("Perímetro (aprox.)", f"{perim:.2f}")
            st.latex(rf"\frac{{x'^2}}{{{a:.2f}^2}} + \frac{{y'^2}}{{{b:.2f}^2}} = 1")
        else:
            st.write("Oculta")

    with col_c:
        st.subheader("📏 Recta")
        if r_on:
            d = np.array([x2 - x1, y2 - y1, z2 - z1])
            largo = np.linalg.norm(d)
            if largo == 0:
                st.warning("Los puntos 1 y 2 son iguales: no definen una recta.")
            else:
                st.metric("Distancia P1 → P2", f"{largo:.2f}")
                st.metric("Vector dirección", f"({d[0]:.2f}, {d[1]:.2f}, {d[2]:.2f})")
                st.latex(
                    rf"\vec r(t) = ({x1:.2f},\,{y1:.2f},\,{z1:.2f})"
                    rf" + t\,({d[0]:.2f},\,{d[1]:.2f},\,{d[2]:.2f})"
                )
        else:
            st.write("Oculta")

    st.caption("x' e y' son las coordenadas dentro del plano propio de la figura "
               "(antes de aplicar el giro y el desplazamiento del centro).")

with tab3:
    if tablas:
        df = pd.concat(tablas, ignore_index=True)
        st.dataframe(df, use_container_width=True, height=400)
        st.download_button(
            "⬇️ Descargar puntos en CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="puntos_3d.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay figuras activas.")

with tab4:
    st.markdown(
        """
        **Cómo usar la aplicación**

        1. Usa el **panel izquierdo** para activar o desactivar cada figura.
        2. Cambia el **radio, los semiejes, el centro y el giro** de círculo y elipse.
        3. Define la **recta** con dos puntos 3D y, si quieres, extiéndela.
        4. Cambia la **vista de la cámara** y el **tema** en *Vista y estilo*.
        5. Mira las fórmulas en **Ecuaciones** y descarga los puntos en **Datos**.

        **Giro:** cada figura nace en el plano XY. Los tres controles de giro la rotan
        alrededor de los ejes X, Y y Z (en ese orden de aplicación: X, luego Y, luego Z).
        """
    )
