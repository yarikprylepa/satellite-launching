# Modelling Satellite Launching

## Programming part of Group Project in Python

The task is to model the process in which a rocket carrying a satellite of mass $$m_s$$ is launched vertically from the Earth's surface at time $$t = 0$$ with initial velocity $$v_0$$ and total initial mass $$M_0$$. The rocket moves upward by ejecting mass downward at a constant rate $$\lambda > 0$$, with exhaust speed $$u > 0$$ relative to the rocket. The rocket must reach a Low Earth Orbit altitude $$H < 2000$$ km, release the satellite, and then adjust its propulsion so that it slows down, reaches a maximum height, falls back toward Earth under gravity, and lands with zero velocity. The acceleration due to gravity is assumed constant throughout the motion. Modelling includes both cases with and without air resistance which is approximated using Stokes' law, with drag proportional to the velocity and rocket diameter.

## What this project includes

- **Parameter research**  
   collect realistic values for quantities such as satellite mass, rocket mass, rocket dimensions, LEO altitude, launch velocity, and atmospheric properties
- **Mathematical model development**  
   formulate equations of motion for the rocket during launch and landing, and choose suitable parameter values so the rocket can reach orbit and return safely
- **Solution of the model**  
   solve the resulting initial value problems for displacement $$x(t)$$, velocity $$v(t)$$, and mass $$M(t)$$, using analytical methods where possible and numerical methods where needed
- **Plots and visualisation**  
   produce separate plots for displacement, velocity, and mass as functions of time. If both analytical and numerical solutions are available, compare them on the same figures
- **Air resistance case**  
   where drag is included, numerical solutions may be required if analytical solutions are too difficult to obtain
- **Discussion of realism and limitations**  
   evaluate how well the mathematical model represents real rocket launching and landing, and identify factors that could improve the model
   
## What is in this repository
- the written report;
- derivations of the mathematical model;
- code for analytical and numerical solutions;
- generated plots for $$x(t)$$, $$v(t)$$, and $$M(t)$$;
- any appendices or supporting calculations relevant to the final submission version
