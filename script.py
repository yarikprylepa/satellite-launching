import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

#physical constants
g = 9.8
rho_air = 1.225
mu_air = 1.8e-5
R_earth = 6.371e6
mu_earth = 3.986004418e14

#chosen parameters
H = 500e3
ms = 2000.0
M0 = 5.0210e5
M_s = 2.0e3
u = 3500.0
lam1 = 2000.0
lam3 = 2000.0
v0 = 0.0
rocket_diameter = 4.0
A_cross = np.pi * rocket_diameter**2 / 4.0
Cd = 0.75
k_stokes = 6 * np.pi * mu_air

drag_model = 'none'

#plot style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.dpi': 140,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'legend.fontsize': 10,
    'font.size': 10
})

#drag force
def drag_force(v):
    if drag_model == 'none':
        return 0.0
    if drag_model == 'stokes':
        return -k_stokes * rocket_diameter * v
    if drag_model == 'quadratic':
        return -0.5 * rho_air * Cd * A_cross * v * abs(v)
    raise ValueError("drag_model must be 'none', 'stokes', or 'quadratic'")

#phase 1, powered ascent
def phase1_rhs(t, y):
    x, v, M = y
    if M <= M_s + ms:
        thrust = 0.0
        dMdt = 0.0
    else:
        thrust = lam1 * u
        dMdt = -lam1
    Fd = drag_force(v)
    dvdt = (thrust + Fd) / M - g
    return [v, dvdt, dMdt]

def reach_H(t, y):
    return y[0] - H
reach_H.terminal = True
reach_H.direction = 1

def burnout(t, y):
    return y[2] - (M_s + ms)
burnout.terminal = True
burnout.direction = -1

#phase 2, coasting
def phase2_rhs(t, y):
    x, v = y
    Fd = drag_force(v)
    dvdt = Fd / M2_const - g
    return [v, dvdt]

def reach_apex(t, y):
    return y[1]
reach_apex.terminal = True
reach_apex.direction = -1

#phase 3, descent
def phase3_rhs(t, y):
    x, v, M = y
    if M <= M_s:
        thrust = 0.0
        dMdt = 0.0
    else:
        thrust = lam3 * u
        dMdt = -lam3
    Fd = drag_force(v)
    dvdt = (thrust + Fd) / M - g
    return [v, dvdt, dMdt]

def reach_ground(t, y):
    return y[0]
reach_ground.terminal = True
reach_ground.direction = -1

#solve phase 1
sol1 = solve_ivp(
    phase1_rhs,
    (0, 1000),
    [0.0, v0, M0],
    events=[reach_H, burnout],
    dense_output=True,
    max_step=0.2
)

reached_H = len(sol1.t_events[0]) > 0
reached_burnout = len(sol1.t_events[1]) > 0

if not reached_H and reached_burnout:
    raise RuntimeError("Rocket burns out before reaching H. Try lowering H or increasing u/lam1 further.")
if not reached_H:
    raise RuntimeError("Phase 1 did not reach H. Adjust parameters.")

t1 = sol1.t_events[0][0]
x1_end, v1_end, M1_end = sol1.sol(t1)

M2_const = M1_end - ms
if M2_const <= M_s:
    raise RuntimeError("Not enough rocket mass remains after satellite release.")

#solve phase 2
sol2 = solve_ivp(
    phase2_rhs,
    (t1, t1 + 5000),
    [x1_end, v1_end],
    events=reach_apex,
    dense_output=True,
    max_step=0.2
)

if len(sol2.t_events[0]) == 0:
    raise RuntimeError("Phase 2 did not reach apex.")

t2 = sol2.t_events[0][0]
x2_end, v2_end = sol2.sol(t2)

#solve phase 3
sol3 = solve_ivp(
    phase3_rhs,
    (t2, t2 + 5000),
    [x2_end, v2_end, M2_const],
    events=reach_ground,
    dense_output=True,
    max_step=0.2
)

t3 = sol3.t_events[0][0] if len(sol3.t_events[0]) else sol3.t[-1]

#sample solutions
T1 = np.linspace(sol1.t[0], t1, 500)
Y1 = sol1.sol(T1)

T2 = np.linspace(sol2.t[0], t2, 400)
Y2 = sol2.sol(T2)

T3 = np.linspace(sol3.t[0], t3, 500)
Y3 = sol3.sol(T3)

T = np.concatenate([T1, T2, T3])
X = np.concatenate([Y1[0], Y2[0], Y3[0]])
V = np.concatenate([Y1[1], Y2[1], Y3[1]])
M = np.concatenate([Y1[2], np.full_like(T2, M2_const), Y3[2]])

#analytical formulas
def M1_exact(t):
    return M0 - lam1 * t

def v1_exact(t):
    return v0 + u * np.log(M0 / (M0 - lam1 * t)) - g * t

def x1_exact(t):
    return v0 * t + (u / lam1) * ((M0 - lam1*t) * np.log(M0 / (M0 - lam1*t)) + lam1*t) - 0.5 * g * t**2

def v2_exact(t):
    return v1_exact(t1) - g * (t - t1)

def x2_exact(t):
    return x1_exact(t1) + v1_exact(t1) * (t - t1) - 0.5 * g * (t - t1)**2

#orbit calculations
orbital_radius = R_earth + H
v_orbit = np.sqrt(mu_earth / orbital_radius)
T_orbit = 2 * np.pi * np.sqrt(orbital_radius**3 / mu_earth)

phi = np.linspace(0, 2*np.pi, 600)
earth_x = R_earth * np.cos(phi)
earth_y = R_earth * np.sin(phi)
orbit_x = orbital_radius * np.cos(phi)
orbit_y = orbital_radius * np.sin(phi)

#graph 1: full mission height
plt.figure(figsize=(9, 5))
plt.plot(T, X / 1000, lw=2)
plt.axvline(t1, color='k', ls='--', alpha=0.5, label='Satellite release')
plt.axvline(t2, color='k', ls=':', alpha=0.5, label='Maximum height')
plt.xlabel('Time (s)')
plt.ylabel('Height x(t) (km)')
plt.title('Rocket height over full mission')
plt.legend()
plt.tight_layout()
plt.show()

#graph 2: full mission velocity
plt.figure(figsize=(9, 5))
plt.plot(T, V, lw=2)
plt.axhline(0, color='k', alpha=0.4)
plt.axvline(t1, color='k', ls='--', alpha=0.5)
plt.axvline(t2, color='k', ls=':', alpha=0.5)
plt.xlabel('Time (s)')
plt.ylabel('Velocity v(t) (m/s)')
plt.title('Rocket velocity over full mission')
plt.tight_layout()
plt.show()

#graph 3: full mission mass
plt.figure(figsize=(9, 5))
plt.plot(T, M, lw=2)
plt.axvline(t1, color='k', ls='--', alpha=0.5)
plt.axvline(t2, color='k', ls=':', alpha=0.5)
plt.xlabel('Time (s)')
plt.ylabel('Mass M(t) (kg)')
plt.title('Rocket mass over full mission')
plt.tight_layout()
plt.show()

#graph 4: phase 1 analytical vs numerical
fig, axs = plt.subplots(3, 1, figsize=(9, 10), sharex=True)

axs[0].plot(T1, Y1[0], label='Numerical')
if drag_model == 'none':
    axs[0].plot(T1, x1_exact(T1), '--', label='Analytical')
axs[0].set_ylabel('x (m)')
axs[0].set_title('Phase 1: Height')
axs[0].legend()

axs[1].plot(T1, Y1[1], label='Numerical')
if drag_model == 'none':
    axs[1].plot(T1, v1_exact(T1), '--', label='Analytical')
axs[1].set_ylabel('v (m/s)')
axs[1].set_title('Phase 1: Velocity')

axs[2].plot(T1, Y1[2], label='Numerical')
if drag_model == 'none':
    axs[2].plot(T1, M1_exact(T1), '--', label='Analytical')
axs[2].set_ylabel('M (kg)')
axs[2].set_xlabel('t (s)')
axs[2].set_title('Phase 1: Mass')

fig.tight_layout()
plt.show()

#graph 5: phase 2 analytical vs numerical
fig, axs = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

axs[0].plot(T2, Y2[0], label='Numerical')
if drag_model == 'none':
    axs[0].plot(T2, x2_exact(T2), '--', label='Analytical')
axs[0].set_ylabel('x (m)')
axs[0].set_title('Phase 2: Height')
axs[0].legend()

axs[1].plot(T2, Y2[1], label='Numerical')
if drag_model == 'none':
    axs[1].plot(T2, v2_exact(T2), '--', label='Analytical')
axs[1].set_ylabel('v (m/s)')
axs[1].set_xlabel('t (s)')
axs[1].set_title('Phase 2: Velocity')

fig.tight_layout()
plt.show()

#graph 6: phase 3 descent
fig, axs = plt.subplots(3, 1, figsize=(9, 10), sharex=True)

axs[0].plot(T3, Y3[0])
axs[0].set_ylabel('x (m)')
axs[0].set_title('Phase 3: Height')

axs[1].plot(T3, Y3[1])
axs[1].set_ylabel('v (m/s)')
axs[1].set_title('Phase 3: Velocity')

axs[2].plot(T3, Y3[2])
axs[2].set_ylabel('M (kg)')
axs[2].set_xlabel('t (s)')
axs[2].set_title('Phase 3: Mass')

fig.tight_layout()
plt.show()

#graph 7: LEO orbit
plt.figure(figsize=(7, 7))
plt.plot(earth_x / 1000, earth_y / 1000, label='Earth surface')
plt.plot(orbit_x / 1000, orbit_y / 1000, label='Circular LEO orbit')
plt.gca().set_aspect('equal', adjustable='box')
plt.xlabel('x (km)')
plt.ylabel('y (km)')
plt.title('Idealised circular LEO orbit at 500 km altitude')
plt.legend()
plt.tight_layout()
plt.show()

print('t1 =', round(float(t1), 2), 's')
print('t2 =', round(float(t2), 2), 's')
print('t3 =', round(float(t3), 2), 's')
print('LEO orbital speed =', round(v_orbit / 1000, 3), 'km/s')
print('LEO orbital period =', round(T_orbit / 60, 2), 'minutes')