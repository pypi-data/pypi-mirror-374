import re
from ast import literal_eval
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from renovexpy.off_the_fly import query_surrogate_models
from renovexpy.optimization import find_optimal_packages, pareto_optimization
from renovexpy.renovation import get_rm_options

pd.set_option("display.max_columns", None)

param_labels = {
    "building_position": "Building position",
    "building_orientation": "Building orientation",
    "floor_type": "Floor type",
    "WWR": "Window-to-wall ratio",
    "floor_insulation": "Floor insulation [material, position, R-value]",
    "roof_insulation": "Roof insulation [material, position, R-value]",
    "wall_insulation": "Wall insulation [material, position, R-value]",
    ("glazing", "window_frame"): "Glazing and window frame",
    "heating_system": "Heating system",
    "vent_type": "Ventilation system",
    "N_pv": "Number of PV panels",
    "airtightness": "Airtightness",
    "shaded_surfaces": "Shading",
    "radiator_area": "Radiator area [m²]",
    "glazing": "Glazing",
    "window_frame": "Window frame",
}

value_labels = {
    ("building_position", "middle"): "Middle",
    ("building_position", "corner"): "Corner",
    ("building_orientation", "S"): "South",
    ("building_orientation", "W"): "West",
    ("heating_system", "VR"): "Standard gas boiler",
    ("heating_system", "HR107"): "High-efficiency gas boiler",
    ("heating_system", "HP 5kW"): "Heat pump 5kW",
    ("heating_system", "HP 7kW"): "Heat pump 7kW",
    ("heating_system", "HP 10kW"): "Heat pump 10kW",
    ("heating_system", "HP 3kW Intergas + HR107 Parallel"): "Hybrid heat pump 5kW",
    ("shaded_surfaces", "[]"): "None",
    ("shaded_surfaces", "['SouthWall_0F', 'SouthWall_1FS']"): "South facade",
    (
        "shaded_surfaces",
        "['SouthWall_0F', 'SouthWall_1FS', 'NorthWall_0F', 'NorthWall_1FN']",
    ): "South + North facades",
    # PV panels
    ("N_pv", "0"): "0",
    ("N_pv", "11"): "11 (Half roof)",
    ("N_pv", "22"): "22 (Whole roof)",
}
mat_labels = {
    "Rockwool": "Mineral wool",
    "Icynene": "Polyurethane foam",
    "SingleGlz": "Single glazing",
    "DoubleGlz": "Double glazing",
    "TripleGlz": "Triple glazing",
}


def clean_df_opt(df_opt, pre_renov_config):
    """
    Cleans the DataFrame of optimal packages for display.
    - Renames columns to be more readable using param_labels.
    - Formats the values in the columns using the logic from get_clean_options.
    """
    df_cleaned = df_opt.copy()
    for col in df_cleaned.columns:
        if col == "N_pv":
            df_cleaned[col] = df_cleaned[col].astype(str)
        clean_col = param_labels.get(col, col)
        if col == "glazing" or "insulation_0" in col:
            # Use mat_labels
            df_cleaned[clean_col] = df_cleaned[col].replace(mat_labels)
        else:
            # Use value_labels
            mapping = {
                key: val for (param, key), val in value_labels.items() if param == col
            }
            df_cleaned[clean_col] = df_cleaned[col].replace(mapping)
        if clean_col != col:
            del df_cleaned[col]
    # Merge insulation columns
    if "floor_insulation_1" not in df_cleaned.columns:
        df_cleaned["floor_insulation_1"] = "External"
    for surf in ["floor", "roof", "wall"]:
        cols = [f"{surf}_insulation_{k}" for k in range(3)]
        curr_R = pre_renov_config[f"{surf}_insulation"][2]
        L = df_cleaned[cols].values.tolist()
        L = [
            f"{mat}, {pos}, R={R-curr_R}" if R - curr_R != 0 else "None"
            for mat, pos, R in L
        ]
        df_cleaned[surf.capitalize() + " insulation"] = L
        df_cleaned.drop(columns=cols, inplace=True)
    return df_cleaned


def get_clean_options(param, options):
    if param in ["floor_insulation", "roof_insulation", "wall_insulation"]:
        options_clean = []
        for mat, pos, R in options:
            if R == 0:
                options_clean.append("None")
            else:
                mat_clean = mat_labels.get(mat, mat)
                options_clean.append(f"{mat_clean}, {pos}, R={R}")
    elif param == ("glazing", "window_frame"):
        options_clean = [f"{mat_labels.get(gl, gl)} [{fr} frame]" for gl, fr in options]
    else:
        options_clean = [value_labels.get((param, str(v)), v) for v in options]
    return options_clean


def get_raw_config(clean_config):
    """
    Converts a clean configuration dictionary (from Streamlit UI) back to its raw format.
    This function is the inverse of get_clean_options.
    """
    raw_config = clean_config.copy()
    reversed_value_labels = {
        (param, clean_val): raw_val
        for (param, raw_val), clean_val in value_labels.items()
    }
    reversed_mat_labels = {v: k for k, v in mat_labels.items()}

    for param, clean_value in clean_config.items():
        # Reverse simple value labels
        if (param, clean_value) in reversed_value_labels:
            raw_config[param] = reversed_value_labels[(param, clean_value)]
            if param in ["shaded_surfaces", "N_pv"]:
                raw_config[param] = literal_eval(raw_config[param])
            continue

        # Reverse insulation options
        if param in ["floor_insulation", "roof_insulation", "wall_insulation"]:
            if clean_value == "None":
                raw_config[param] = ["Rockwool", "External", 0]
            else:
                # Parse "Material, position, R=Value"
                mat_clean, pos, R_str = parts = clean_value.split(", ")
                mat = reversed_mat_labels.get(mat_clean, mat_clean)
                R = float(R_str.split("=")[1])
                raw_config[param] = [mat, pos, R]
            continue

        # Reverse glazing and window frame
        if param == ("glazing", "window_frame"):
            # Parse "Glazing [frame frame]"
            match = re.match(r"^(.*) \[(.*) frame\]$", clean_value)
            if match:
                gl_clean, fr = match.groups()
                gl = reversed_mat_labels.get(gl_clean, gl_clean)
                raw_config[param] = (gl, fr)
            continue

    return raw_config


pre_renov_options = {
    "building_position": ["middle", "corner"],
    "building_orientation": ["S", "W"],
    "floor_type": ["Wood", "Concrete"],
    "WWR": (0.2, 0.8),
}
pre_renov_options.update(get_rm_options())

pre_renov_menu = {
    "📐 Geometry": ["building_position", "building_orientation"],
    "🧱 Constructions": [
        "floor_type",
        "floor_insulation",
        "roof_insulation",
        "wall_insulation",
    ],
    "🪟 Windows": ["WWR", ("glazing", "window_frame"), "shaded_surfaces"],
    "🌡️ Energy and heating": ["heating_system", "radiator_area", "N_pv"],
    "💨 Ventilation": ["vent_type", "airtightness"],
}
categories_in_col1 = ["📐 Geometry", "🌡️ Energy and heating", "💨 Ventilation"]

unknown_params = {
    "n_occupants": (1, 2, 4),
    "heated_zones": (
        ["0F"],
        ["0F", "1FS"],
        ["0F", "1FS", "1FN"],
        ["0F", "1FS", "2F"],
        ["0F", "1FS", "1FN", "2F"],
    ),
    "heating_setpoint": (
        "Always_21",
        "N17_D19",
        "N15_D19",
        "N17_D20",
        "N15_M17_D16_E19",
    ),
    "window_vent_profile": (1, 2, 3, 4),
    "use_vent_grilles": (True, False),
    "mech_vent_profile": (1, 2, 3),
    "shading_profile": (1, 2, 3, 4),
    "epw_file": ("DeBilt_2000", "DeBilt_2050", "DeBilt_2100"),
}

kpis = [
    # Energy
    "Heating demand [kWh]",
    "Electricity OPP [kW]",
    # Cost
    "Renovation cost [€]",
    "TCO over 30 years [€]",
    "Payback period [year]",
    # CO2
    "CO2 emissions [kgCO2]",
    "CO2 reduction per euro [kgCO2/€]",
    # Comfort
    "Overheating [h]",
    "CO2 excess [h]",
]

# Init session state
if "pre_renov_config" not in st.session_state:
    st.session_state.pre_renov_config = {
        "building_type": "terraced_house",
        "occupant_activity_level": "mid",
        "lighting_power_per_area": 1,
        "equipment_power_per_area": 1,
        "shading_position": "External",
    }

# --- Streamlit App ---

st.set_page_config(layout="wide", page_title="Renovation Explorer")


st.title("Renovation Explorer: Demo off-the-fly model")
st.markdown(
    """
    <hr style="border: none; height: 6px; background-color: #333;" />
    """,
    unsafe_allow_html=True,
)

# Inputs section
st.header("🏠 1. Specify current house state")
for category, L_param in pre_renov_menu.items():
    st.subheader(category)
    for param in L_param:
        if param == "floor_insulation":
            floor_type = st.session_state.pre_renov_config.get(
                "floor_type", "wood"
            ).lower()
            options = pre_renov_options[f"{floor_type}_{param}"]
        else:
            options = pre_renov_options[param]
        options_clean = get_clean_options(param, options)
        if isinstance(options, list):
            st.session_state.pre_renov_config[param] = st.selectbox(
                param_labels[param], options_clean
            )
        elif isinstance(options, tuple):
            st.session_state.pre_renov_config[param] = st.slider(
                param_labels[param],
                min_value=options[0],
                max_value=options[1],
                value=(options[0] + options[1]) / 2,
                step=0.01,
            )
st.markdown(
    """
    <hr style="border: none; height: 6px; background-color: #333;" />
    """,
    unsafe_allow_html=True,
)


# Simulation section
st.header("⚙️ 2. Simulate renovation packages")
with st.form("simulation_form"):
    # Menu for simulation parameters
    n_scenarios = st.number_input(
        "Number of scenarios (for unknown parameters)",
        min_value=1,
        value=8,
        help="Number of random scenarios to generate for unknown parameters.",
    )
    replace_window_frames = st.checkbox(
        "Replace window frames?",
        value=False,
        help="If checked, frames will be changed alongside glazing, which significantly increases cost.",
    )
    max_rm_per_package = st.number_input(
        "Maximum number of renovation measures per package",
        min_value=1,
        value=5,
        help="The maximum number of renovation measures to combine in a single package.",
    )

    # Button to run the simulation
    run_simulation_button = st.form_submit_button("Run Simulation")

if run_simulation_button:
    with st.spinner("Running simulations... This may take a few minutes."):
        st.session_state.unknown_params = unknown_params
        try:
            clean_pre_renov_config = st.session_state.pre_renov_config
            pre_renov_config = get_raw_config(clean_pre_renov_config)
            st.session_state.df = query_surrogate_models(
                pre_renov_config,
                unknown_params,
                N_scenarios=n_scenarios,
                replace_window_frames=replace_window_frames,
                max_rm_per_package=max_rm_per_package,
            )
            st.success("Simulation complete!")
        except Exception as e:
            st.error(f"An error occurred during simulation: {e}")

# Optimization section
st.header("🔍 3. Find optimal renovation packages")
with st.form("optimization_form"):
    # Multiple checkbox to select KPIs for optimization
    kpi_to_optimize = st.multiselect(
        "Select KPIs to optimize",
        options=kpis,
        default=[],
        help="Select the indicators (KPIs) to optimize. for the renovation packages. If several KPIs are selected, the.",
    )
    requirements = {}
    for kpi in ["Renovation cost [€]", "Overheating [h]", "CO2 excess [h]"]:
        if val := st.text_input(f"Maximum allowed {kpi}"):
            requirements[kpi] = int(val)

    robustness_indicator = st.selectbox(
        "Select robustness indicator", options=["mean", "max_regret"]
    )
    n_top = st.number_input("Number of top packages to return", min_value=1, value=10)
    # Button to run the optimization
    run_optimization_button = st.form_submit_button("Run Optimization")

    if run_optimization_button:
        with st.spinner("Finding optimal packages..."):
            try:
                if "df" not in st.session_state:
                    raise ValueError(
                        "No simulation data found. Please run the simulation first (step 2)."
                    )
                df_opt_raw = find_optimal_packages(
                    st.session_state.df,
                    unknown_params=list(unknown_params.keys()),
                    kpis=kpi_to_optimize,
                    requirements=requirements,
                    robustness_indicator=robustness_indicator,
                    N_top=n_top,
                )
                pre_renov_config = get_raw_config(st.session_state.pre_renov_config)
                st.session_state.df_opt = clean_df_opt(df_opt_raw, pre_renov_config)
                st.success("Optimization complete!")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown(
    """
    <hr style="border: none; height: 6px; background-color: #333;" />
    """,
    unsafe_allow_html=True,
)

# Display results section
st.header("📊 4. Results")
# Display the DataFrame
if "df_opt" in st.session_state:
    st.dataframe(st.session_state.df_opt)
