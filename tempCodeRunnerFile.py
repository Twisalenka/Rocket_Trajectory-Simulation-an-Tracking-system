import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Constants
g = 9.81  # gravity (m/s^2)
dt = 0.1  # time step (s)
drag_coeff = 0.02
parachute_speed = 20  # m/s (fixed descent speed)

st.title("🚀 Rocket Trajectory Simulation & Tracking Tool")

st.sidebar.header("Input Parameters")

mass = st.sidebar.number_input("Rocket Mass (kg)", min_value=1.0, value=20.0)
apogee = st.sidebar.number_input("Expected Apogee (m)", min_value=50.0, value=500.0)
wind_speed = st.sidebar.number_input("Wind Speed (m/s)", value=5.0)
wind_dir = st.sidebar.number_input("Wind Direction (degrees)", value=0.0)
fall_radius = st.sidebar.number_input("Allowed Fall Radius (m)", value=100.0)

# Convert wind direction
wind_dx = wind_speed * np.cos(np.radians(wind_dir))

# Initial conditions
x, y = 0, 0
vx, vy = 0, np.sqrt(2 * g * apogee)  # initial vertical velocity estimate

trajectory_x = []
trajectory_y = []

# Ascent Phase
while vy > 0:
    drag = drag_coeff * vy**2
    vy -= (g + drag / mass) * dt
    y += vy * dt
    x += wind_dx * dt
    trajectory_x.append(x)
    trajectory_y.append(y)

# Descent Phase (Parachute)
while y > 0:
    y -= parachute_speed * dt
    x += wind_dx * dt
    trajectory_x.append(x)
    trajectory_y.append(max(y, 0))

landing_distance = abs(x)

# Plot
fig, ax = plt.subplots()
ax.plot(trajectory_x, trajectory_y, label="Rocket Trajectory")
ax.scatter(trajectory_x[-1], trajectory_y[-1], color="red", label="Landing Point")
ax.set_xlabel("Horizontal Distance (m)")
ax.set_ylabel("Altitude (m)")
ax.set_title("Rocket Flight Trajectory")
ax.legend()
ax.grid()

st.pyplot(fig)

# Results
st.subheader("📊 Results")
st.write(f"**Apogee Achieved:** {max(trajectory_y):.2f} m")
st.write(f"**Landing Distance:** {landing_distance:.2f} m")

if landing_distance <= fall_radius:
    st.success("✅ Rocket landed within safe fall radius.")
else:
    st.error("❌ Rocket landed outside the safe fall radius.")
