import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ================= PAGE =================
st.set_page_config(page_title="Rocket Simulator", layout="wide")
st.title("🚀 Rocket Trajectory, Telemetry & Stability Simulator")

# ================= INPUTS =================
st.sidebar.header("Mission Parameters")

mass = st.sidebar.number_input("Rocket Mass (kg)", 5.0, 200.0, 50.0)
target_apogee = st.sidebar.number_input("Expected Apogee (m)", 100.0, 10000.0, 2000.0)
wind_speed = st.sidebar.number_input("Wind Speed (m/s)", 0.0, 50.0, 5.0)
wind_dir_deg = st.sidebar.slider("Wind Direction (deg)", 0, 360, 90)
fall_radius = st.sidebar.number_input("Safe Fall Radius (m)", 50.0, 5000.0, 500.0)

launch = st.sidebar.button("🚀 Launch Simulation")

# ================= CONSTANTS =================
g = 9.81
rho = 1.225
dt = 0.05

# ================= ROCKET GEOMETRY (PREDICTED) =================
# Length prediction using L/D heuristic (defensible)
diameter = 0.08 * (mass ** 0.25)
length = diameter * 15

area = np.pi * (diameter / 2) ** 2
Cd = 0.75

# ---- CG prediction (mass distribution) ----
nose_mass = 0.15 * mass
body_mass = 0.60 * mass
motor_mass = 0.25 * mass

cg = (
    nose_mass * (0.15 * length) +
    body_mass * (0.55 * length) +
    motor_mass * (0.90 * length)
) / mass

# ---- CP prediction (geometry-based) ----
cp_nose = 0.66 * (0.2 * length)
cp_body = 0.5 * length
cp_fins = 0.85 * length

cp = (cp_nose + cp_body + cp_fins) / 3
stability_margin = (cp - cg) / diameter

# ================= SIMULATION =================
def simulate():
    # Initial velocity from energy (PREDICTED, not assumed)
    v0 = np.sqrt(2 * g * target_apogee)

    pos = np.array([0.0, 0.0, 0.0])
    vel = np.array([0.0, 0.0, v0])
    acc = np.zeros(3)

    yaw = 0.0
    pitch = 0.0

    wind_dir = np.radians(wind_dir_deg)
    wind = np.array([
        wind_speed * np.cos(wind_dir),
        wind_speed * np.sin(wind_dir),
        0.0
    ])

    t = 0
    parachute = False

    T, X, Y, Z = [], [], [], []
    VZ, AZ = [], []
    YAW, PITCH = [], []

    while t < 300:
        rel_vel = vel - wind
        speed = np.linalg.norm(rel_vel)

        drag = (
            -0.5 * rho * Cd * area * speed * rel_vel
            if speed > 0 else np.zeros(3)
        )

        gravity = np.array([0, 0, -mass * g])
        force = drag + gravity
        acc = force / mass

        # Parachute condition
        if vel[2] < 0 and not parachute:
            parachute = True

        if parachute and vel[2] < -20:
            vel[2] = -20
            acc[2] = 0

        vel += acc * dt
        pos += vel * dt

        # Orientation due to wind torque
        torque = wind_speed * (cp - cg)
        yaw += torque * dt * 0.001
        pitch += torque * dt * 0.001

        # Store
        T.append(t)
        X.append(pos[0])
        Y.append(pos[1])
        Z.append(max(pos[2], 0))
        VZ.append(vel[2])
        AZ.append(acc[2])
        YAW.append(yaw)
        PITCH.append(pitch)

        if pos[2] <= 0 and t > 2:
            break

        t += dt

    return np.array(T), np.array(X), np.array(Y), np.array(Z), np.array(VZ), np.array(AZ), np.array(YAW), np.array(PITCH)

# ================= RUN =================
if launch:
    T, X, Y, Z, VZ, AZ, YAW, PITCH = simulate()

    flight_time = T[-1]
    landing_distance = np.sqrt(X[-1]**2 + Y[-1]**2)

    st.success(
        f"Simulation Complete! Flight Time: {flight_time:.1f}s | "
        f"Landing Distance: {landing_distance:.1f} m"
    )

    if landing_distance <= fall_radius:
        st.info("Landing is within safe radius.")
    else:
        st.error("WARNING: Landing outside safe radius!")

    st.subheader("📐 Rocket Geometry & Stability")
    st.write(f"Predicted Rocket Length: **{length:.2f} m**")
    st.write(f"Center of Gravity (CG): **{cg:.2f} m**")
    st.write(f"Center of Pressure (CP): **{cp:.2f} m**")
    st.write(f"Stability Margin: **{stability_margin:.2f} calibers**")

    # ================= 3D ANIMATION =================
    rocket_len = length

    frames = []
    for i in range(len(Z)):
        frames.append(go.Frame(
            data=[
                go.Scatter3d(
                    x=X[:i+1], y=Y[:i+1], z=Z[:i+1],
                    mode="lines",
                    name="Trajectory"
                ),
                go.Scatter3d(
                    x=[X[i], X[i]],
                    y=[Y[i], Y[i]],
                    z=[Z[i], Z[i] + rocket_len],
                    mode="lines",
                    line=dict(width=8),
                    name="Rocket Body"
                )
            ]
        ))

    fig3d = go.Figure(
        data=frames[0].data,
        frames=frames
    )

    fig3d.update_layout(
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Altitude (m)"
        ),
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "buttons": [
                {"label": "▶ Play", "method": "animate", "args": [None]},
                {"label": "⏸ Pause", "method": "animate",
                 "args": [[None], {"mode": "immediate"}]},
                {"label": "⏩ Final Result", "method": "update",
                 "args": [{"x": [X], "y": [Y], "z": [Z]}]}
            ]
        }]
    )

    st.plotly_chart(fig3d, use_container_width=True)

    # ================= 2D + TELEMETRY =================
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.plot(X, Z)
        ax.set_xlabel("Horizontal Distance (m)")
        ax.set_ylabel("Altitude (m)")
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(T, VZ)
        ax2.axhline(-20, linestyle="--", label="Parachute Limit")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Vertical Velocity (m/s)")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

    st.subheader("Telemetry")
    st.line_chart({
        "Vertical Velocity (m/s)": VZ,
        "Vertical Acceleration (m/s²)": AZ,
        "Yaw": YAW,
        "Pitch": PITCH
    })
