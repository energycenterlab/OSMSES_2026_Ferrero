# Enhancing *pandapipes* for Dynamic Simulation of District Heating Networks

This repository contains the source code, datasets, and validation scripts for the study presented at the **OSMSES 2026** conference. The research focuses on assessing and enhancing open-source Python-based tools for District Heating Network (DHN) modelling using the **DESTEST** benchmarking framework.

## Motivation
The project addresses the limitations of static thermo-hydraulic solvers in capturing transient dynamics, such as thermal inertia and transport delays. We introduce a **hybrid enhancement strategy** for the `pandapipes` steady-state formulation, triggered by a **change point detection algorithm**. This approach allows the replication of "plug flow" behavior through exponential decay and transport delay ($t_d$ and $\tau$) corrections, maintaining computational efficiency while matching the accuracy of fully-dynamic reference models (Modelica).

## Repository Structure & Workflow

To reproduce the results and the figures presented in the paper, the following workflow is recommended:

### 1. Input Data (`InputData/`)
Before running the simulations, ensure that the topology and boundary conditions are correctly placed:
* `nodes_data.csv` & `pipes_data.csv`: Definition of the network layout for the DESTEST procedure (CE0 and CE1).
* `heat_profile_1_building_SFH_Network_1`: Time-series demand profiles for the dynamic scenarios (CE1).

### 2. Simulation Notebooks (`Notebooks/`)
The simulation logic is organized by case study:
* **Steady-State Simulation (CE0):**
    * `Network_0_pyDHN.ipynb`: DESTEST CE0 implementation using the `pyDHN` quasi-dynamic solver.
    * `Network_0_pandapipes.ipynb`: DESTEST CE0 implementation using the standard `pandapipes` solver.
* **Dynamic Simulation (CE1):**
    * `Network_1_pyDHN.ipynb`: DESTEST CE1 implementation using the `pyDHN` quasi-dynamic solver.
    * `Network_1_pandapipes.ipynb`: DESTEST CE1 implementation using the standard `pandapipes` solver + implementation of the dynamic temperature control strategy.

### 3. Comparison & Validation
* **`DESTESTModelsComparison.ipynb`**: This notebook aggregates the outputs from the `Results/` folder, performs the statistical validation (RMSE), and generates the final comparison plots.

---
