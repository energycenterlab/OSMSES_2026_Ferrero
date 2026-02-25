import pandapipes as pp
import pandas as pd
import numpy as np
from pandapipes.properties.fluids import create_constant_fluid


# --- network input data ---
mdot_consumers = 553 / 3600 #kg/s
delta_t_consumers = 30      # K
t_supply_producer = 70      # °C
t_ext_ground = 10           # °C

offset=(0.5,0.5,0.15)

# --- initialization ---
t_initial = 20              # °C
p_initial = 1               # bar


def create_net(nodes_file, pipes_file, fluid_props=None):
    """
    Thermal network creation in pandapipes

    :param nodes_file: path file Excel nodi
    :param pipes_file: path file Excel pipe

    :return: pandapipes network, node_map
    """

    # --- READ DATA ---
    nodes = pd.read_excel(nodes_file)
    pipes = pd.read_excel(pipes_file)

    # --- Heat transfer coefficient calculation dfrom input data ---
    def calculate_u_w_per_m2k(row):
        d_int = row['diameter_m']
        t_int = row['t_pipe_m']
        t_ins = row['t_ins_m']
        t_ext = 0.0

        lambda_int = 0.35   # W/mK
        lambda_ins = 0.026  # W/mK
        lambda_c = 0.4      # W/mK

        r_int = d_int / 2
        r_1 = r_int + t_int
        r_2 = r_1 + t_ins
        r_ext = r_2 + t_ext

        R_prime_int = np.log(r_1 / r_int) / (2 * np.pi * lambda_int)
        R_prime_ins = np.log(r_2 / r_1) / (2 * np.pi * lambda_ins)
        R_prime_c = np.log(r_ext / r_2) / (2 * np.pi * lambda_c)

        R_prime_global = R_prime_int + R_prime_ins + R_prime_c

        U_L = 1 / R_prime_global
        U = U_L / (2 * np.pi * r_int)

        return U

    pipes["u_w_per_m2k"] = pipes.apply(calculate_u_w_per_m2k, axis=1)

    # --- CREATE NETWORK ---
    net = pp.create_empty_network(name="Network_0")

    # --- DEFINE FLUID ---
    if fluid_props is None:
        fluid_props = dict(
            name="water_50",
            fluid_type="liquid",
            density=988,
            viscosity=0.0005434,
            heat_capacity=4180,
            thermal_conductivity=0.64,
            temperature=50 + 273.15
        )

    fluid = create_constant_fluid(**fluid_props)
    net.fluid = fluid

    # --- NODES ---
    node_map = {}
    for idx, row in nodes.iterrows():
        name = row["node_id"]
        name_s = f"{name}_s"
        name_r = f"{name}_r"

        # supply junction
        j_s = pp.create_junction(
            net,
            pn_bar=p_initial,
            tfluid_k=t_initial + 273.15,
            height_m=row.get("z",0),
            name=name_s,
            geodata=(row["x"], row["y"])
        )
        # return junction
        j_r = pp.create_junction(
            net,
            pn_bar=p_initial,
            tfluid_k=t_initial + 273.15,
            height_m=row.get("z",0),
            name=name_r,
            geodata=(row["x"] + offset[0], row["y"] + offset[1])
        )

        node_map[name] = {"supply": j_s, "return": j_r}

        # --- SUBSTATIONS ---
        if "SimpleDistrict" in name:
            pp.create_heat_consumer(
                net,
                from_junction=j_s,
                to_junction=j_r,
                deltat_k=delta_t_consumers,
                controlled_mdot_kg_per_s=mdot_consumers,
                name=name
            )

        # --- HEATING STATION ---
        if name == "i":
            pp.create_circ_pump_const_pressure(
                net,
                return_junction=j_r,
                flow_junction=j_s,
                p_flow_bar=p_initial,
                plift_bar=0.10,
                t_flow_k=t_supply_producer + 273.15,
                name="Producer"
            )

    # --- PIPES ---
    for idx, row in pipes.iterrows():
        start = row["start_node"]
        end = row["end_node"]
        name_s = f"{start}_to_{end}_s"
        name_r = f"{start}_to_{end}_r"

        start_s = node_map[start]["supply"]
        end_s   = node_map[end]["supply"]
        start_r = node_map[end]["return"]
        end_r   = node_map[start]["return"]

        # supply
        pp.create_pipe_from_parameters(
            net,
            from_junction=start_s,
            to_junction=end_s,
            length_km=row["length_m"]/1000,
            diameter_m=row["diameter_m"],
            k_mm=0.007,
            u_w_per_m2k=row["u_w_per_m2k"],
            text_k=t_ext_ground + 273.15,
            name=name_s
        )

        # return
        pp.create_pipe_from_parameters(
            net,
            from_junction=start_r,
            to_junction=end_r,
            length_km=row["length_m"]/1000,
            diameter_m=row["diameter_m"],
            k_mm=0.007,
            u_w_per_m2k=row["u_w_per_m2k"],
            text_k=t_ext_ground + 273.15,
            name=name_r
        )

    return net, node_map