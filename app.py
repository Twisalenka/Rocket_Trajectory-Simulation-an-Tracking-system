import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. SET UP THE APP LAYOUT ---
st.set_page_config(page_title="Rocket Trajectory Simulator", layout="wide")
st.title("🚀 Rocket Flight Trajectory Simulator")
st.markdown("Simulate rocket motion with gravity, wind, and parachute descent.")

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Mission Parameters")

rocket_mass = st.sidebar.number_input("Rocket Weight (kg)", min_value=1.0, value=50.0)
target_apogee = st.sidebar.number_input("Expected Apogee (meters)", min_value=100.0, value=1000.0)
wind_speed = st.sidebar.number_input("Wind Speed (m/s)", value=5.0)
wind_direction = st.sidebar.slider("Wind Direction (Degrees)", 0, 360, 90) # 90 means blowing East
fall_radius_limit = st.sidebar.number_input("Safety Fall Radius (m)", value=500.0)

# --- 3. PHYSICS ENGINE ---
def simulate_flight(mass, apogee, wind_spd, wind_dir_deg):
    # Constants
    g = 9.81  # Gravity (m/s^2)
    dt = 0.1  # Time step (seconds)
    
    # Calculate required Launch Velocity to reach Apogee (v = sqrt(2gh))
    # We add 20% extra force to account for air drag slowing it down
    initial_velocity = np.sqrt(2 * g * apogee) * 1.1 
    
    # Initial State [x, y, vx, vy]
    x, y = 0.0, 0.0
    vx = 0.0
    vy = initial_velocity
    
    # Wind components (Wind pushes the rocket)
    wind_angle_rad = np.radians(wind_dir_deg)
    wind_fx = wind_spd * np.cos(wind_angle_rad) * 0.5 # 0.5 is a drag coefficient factor
    
    # Data storage for plotting
    time_points = [0]
    x_points = [0]
    y_points = [0]
    vy_points = [vy]
    ay_points = [-g] # Initial accel is gravity
    
    t = 0
    parachute_deployed = False

    # SIMULATION LOOP
    while y >= 0:
        # 1. Forces
        # Gravity always pulls down
        ay = -g
        
        # Aerodynamic Drag (Air resistance opposes movement)
        # Drag increases with speed squared (v^2)
        drag = 0.002 * (vy**2) 
        if vy > 0: # Moving up
            ay -= (drag / mass)
        else: # Moving down
            ay += (drag / mass)

        # 2. Update Velocity
        vy += ay * dt
        vx += (wind_fx / mass) * dt # Wind pushes horizontally

        # 3. Parachute Logic (The User's specific Request)
        # If falling (vy < 0) and parachute is out, cap speed at -20 m/s
        if vy < 0: 
            parachute_deployed = True
            if vy < -20:
                vy = -20
                ay = 0 # Terminal velocity reached, no more acceleration

        # 4. Update Position
        x += vx * dt
        y += vy * dt
        t += dt

        # Stop if we hit ground
        if y < 0:
            y = 0
            break

        # Store data
        time_points.append(t)
        x_points.append(x)
        y_points.append(y)
        vy_points.append(vy)
        ay_points.append(ay)

    return time_points, x_points, y_points, vy_points, ay_points

# --- 4. RUN SIMULATION & PLOT ---
if st.button("Launch Simulation"):
    t, x, y, vy, ay = simulate_flight(rocket_mass, target_apogee, wind_speed, wind_direction)
    
    # Landing calculation
    landing_spot = np.sqrt(x[-1]**2)
    st.success(f"Simulation Complete! Flight Time: {t[-1]:.1f}s | Landing Distance: {landing_spot:.1f}m")
    
    if landing_spot > fall_radius_limit:
        st.error(f"WARNING: Rocket landed outside safety radius ({fall_radius_limit}m)!")
    else:
        st.info("Landing is within safe radius.")

    # Layout for Graphs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Flight Trajectory (Side View)")
        fig, ax = plt.subplots()
        ax.plot(x, y, color='blue', label='Rocket Path')
        ax.set_xlabel("Horizontal Distance (m)")
        ax.set_ylabel("Altitude (m)")
        ax.grid(True)
        ax.axhline(0, color='black', linewidth=2) # The ground
        st.pyplot(fig)

    with col2:
        st.subheader("Vertical Velocity vs Time")
        fig2, ax2 = plt.subplots()
        ax2.plot(t, vy, color='red')
        ax2.axhline(-20, color='green', linestyle='--', label='Parachute Speed Limit')
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Velocity (m/s)")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)

    # Telemetry Data (Gyro/Accel approximation)
    st.subheader("Telemetry Analysis")
    chart_data = {"Time": t, "Vertical Accel (m/s²)": ay, "Velocity (m/s)": vy}
    st.line_chart(chart_data, x="Time")