import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Rocket Simulator", layout="wide")
st.title("🚀 Rocket Trajectory, Telemetry & 3D Animation")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Mission Parameters")

mass = st.sidebar.number_input("Rocket Mass (kg)", 1.0, 200.0, 50.0)
target_apogee = st.sidebar.number_input("Target Apogee (m)", 100.0, 5000.0, 1000.0)
wind_speed = st.sidebar.number_input("Wind Speed (m/s)", 0.0, 50.0, 5.0)
wind_dir = st.sidebar.slider("Wind Direction (deg)", 0, 360, 90)

# ---------------- PHYSICS ----------------
def simulate():
    g = 9.81
    dt = 0.1
    v0 = np.sqrt(2 * g * target_apogee) * 1.1

    x, z = 0.0, 0.0
    vx, vz = 0.0, v0

    wind_x = wind_speed * np.cos(np.radians(wind_dir)) * 0.4

    t, X, Z, VZ, AZ = [], [], [], [], []

    time = 0
    while True:
        drag = 0.002 * vz**2
        az = -g - drag/mass if vz > 0 else -g + drag/mass

        if vz < 0 and vz < -20:   # parachute
            vz = -20
            az = 0

        vz += az * dt
        vx += wind_x / mass * dt

        x += vx * dt
        z += vz * dt
        time += dt

        if z < 0:
            z = 0

        t.append(time)
        X.append(x)
        Z.append(z)
        VZ.append(vz)
        AZ.append(az)

        if z == 0 and vz < 0:
            break

    return t, X, Z, VZ, AZ, max(Z)

# ---------------- RUN ----------------
if st.button("🚀 Launch Simulation"):
    t, X, Z, VZ, AZ, max_height = simulate()
        # -------- Mission Summary --------
    flight_time = t[-1]
    landing_distance = abs(X[-1])

    st.success(
        f"Simulation Complete! Flight Time: {flight_time:.1f}s | "
        f"Landing Distance: {landing_distance:.1f}m"
    )

    safety_radius = 500  
    if landing_distance <= safety_radius:
        st.info("Landing is within safe radius.")
    else:
        st.error("WARNING: Landing is outside the safe radius!")

    st.success(f"Expected Maximum Height Achieved: {max_height:.2f} m")

        # ---------------- 3D ROCKET ANIMATION ----------------
    st.subheader("🛰 3D Rocket Motion")

    rocket_length = max_height / 30
    frames = []

    for i in range(len(Z)):
        frames.append(go.Frame(
            data=[
                go.Scatter3d(
                    x=X[:i+1],
                    y=[0]*(i+1),
                    z=Z[:i+1],
                    mode="lines",
                    line=dict(color="blue", width=4),
                    name="Rocket Path"
                ),
                go.Scatter3d(
                    x=[X[i], X[i]],
                    y=[0, 0],
                    z=[Z[i], Z[i] + rocket_length],
                    mode="lines",
                    line=dict(color="red", width=10),
                    name="Rocket Body"
                ),
                go.Scatter3d(
                    x=[X[i]],
                    y=[0],
                    z=[Z[i] + rocket_length],
                    mode="markers",
                    marker=dict(size=6, symbol="diamond", color="black"),
                    name="Nose Cone"
                )
            ]
        ))

    fig3d = go.Figure(
        data=frames[0].data,
        frames=frames
    )

    fig3d.update_layout(
        scene=dict(
            xaxis_title="Wind Drift (m)",
            yaxis_title="Y",
            zaxis_title="Altitude (m)",
            zaxis=dict(range=[0, max_height + 300])
        ),
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "x": 0.05,
            "y": 1.15,
            "buttons": [
                {
                    "label": "▶ Play",
                    "method": "animate",
                    "args": [None]
                },
                {
                    "label": "⏸ Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0},
                        "mode": "immediate"
                    }]
                },
                {
                    "label": "⏩ Final Result",
                    "method": "update",
                    "args": [{
                        "x": [X, [X[-1], X[-1]], [X[-1]]],
                        "y": [[0]*len(X), [0, 0], [0]],
                        "z": [Z, [Z[-1], Z[-1] + rocket_length], [Z[-1] + rocket_length]]
                    }]
                }
            ],
            "bgcolor": "#E6E6E6",
            "bordercolor": "black",
            "borderwidth": 1,
            "font": {"color": "black", "size": 14}
        }]
    )


    st.plotly_chart(fig3d, use_container_width=True)

    # ---------------- 2D GRAPHS ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2D Trajectory (Side View)")
        fig, ax = plt.subplots()
        ax.plot(X, Z)
        ax.set_xlabel("Horizontal Distance (m)")
        ax.set_ylabel("Altitude (m)")
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        st.subheader("Vertical Velocity vs Time")
        fig2, ax2 = plt.subplots()
        ax2.plot(t, VZ)
        ax2.axhline(-20, linestyle="--", label="Parachute Limit")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Velocity (m/s)")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

    # ---------------- TELEMETRY ----------------
    st.subheader("Telemetry Data")
    st.line_chart(
        {
            "Time": t,
            "Vertical Velocity (m/s)": VZ,
            "Vertical Acceleration (m/s²)": AZ
        },
        x="Time"
    )
