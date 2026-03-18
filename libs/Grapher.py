# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 15:40:17 2026

@author: a056346

Follow Princess syntax below for full control
{
    "x": "Time",
    "y": "Accel",
    "title": "Acceleration vs Time",
    "x_title": "Time (s)",
    "y_title": "Acceleration (m/s²)",

    # Primary trace styles (optional)
    "line_styles": {
        "mode": "lines",        # default: "lines"
        "color": "#1f77b4",     # default: random or ColorManager
        "width": 2,             # default: 2
        "opacity": 1.0,         # default: 1.0
        "marker_size": 8        # default: 8
    },

    # Extra axis
    "y2": {
        "y": "SteeringAngle",
        "y_title": "SWA (°)",
        "line_styles": {
            "mode": "lines",    # default: "lines"
            "color": "#ff7f0e",
            "width": 2,
            "dash": "solid"
        }
    },

    # Perpendicular reference lines
    "x_perp": ["acc_metrics.t_signal_90", "acc_metrics.t_signal_max"],
    "x_perp_styles": {
        "acc_metrics.t_signal_90": {"color": "#00FF00", "dash": "dash"},
        "acc_metrics.t_signal_max": {"color": "#FF0000", "dash": "dot"}
    },

    "y_perp": [0.0],
    "y_perp_styles": {
        "0.0": {"color": "#000000", "dash": "solid"}
    }
}


bare minimum syntax
{
    "x": "Time",
    "y": "Accel",
    "title": "Acceleration vs Time",
    "x_title": "Time (s)",
    "y_title": "Acceleration (m/s²)",

    # Optional second axis
    "y2": {
        "y": "SteeringAngle",
        "y_title": "SWA (°)"
        # line_styles is optional; defaults will be filled automatically
    },

    # Optional perpendicular reference lines
    "x_perp": ["acc_metrics.t_signal_90"],
    "y_perp": [0.0]

    # x_perp_styles / y_perp_styles are optional;
    # if omitted, defaults (color, dash, marker) are filled in automatically
}

"""
def roundabout_specs():
    return [
        # --- Trajectory ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_OGR0x",
            "y": "DAVIDChassisSensorIcon01.sensorcha_OGR0y",
            "title": "Trajectory",
            "x_title": "X (m)",
            "y_title": "Y (m)"
        },

        # --- Front slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw",
            "title": "Front slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "front slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "rear slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Yaw rate vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
            "title": "Yaw rate & SWA",
            "x_title": "time (s)",
            "y_title": "yaw rate (°/s)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "rear slip angle (°)"
        },

        # --- Understeer vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "diff_derive",
            "title": "Understeer vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "Understeer"
        },

        # --- CIR vs time ---
        {
            "x": "Time",
            "y": "CIR_x",
            "title": "CIRX vs time",
            "x_title": "Time (s)",
            "y_title": "CIR_x (m)",
            #"y_range": [-10, 10]
        },
        # --- CIR vs time ---
        {
            "x": "Time",
            "y": "CIR_y",
            "title": "CIRY vs time",
            "x_title": "Time (s)",
            "y_title": "CIR_y (m)",
            #"y_range": [-10, 10]
        },
        # --- LR vs time ---
        {
            "x": "Time",
            "y": "lr",
            "title": "Lr vs time",
            "x_title": "Time (s)",
            "y_title": "CIR (m)",
            #"y_range": [-10, 10]
        },
    ]


def uturn_specs():
    return [
        # --- Trajectory ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_OGR0x",
            "y": "DAVIDChassisSensorIcon01.sensorcha_OGR0y",
            "title": "Trajectory",
            "x_title": "X (m)",
            "y_title": "Y (m)"
        },

        # --- Front slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw",
            "title": "Front slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "front slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "rear slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Yaw rate vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
            "title": "Yaw rate & SWA",
            "x_title": "time (s)",
            "y_title": "yaw rate (°/s)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "rear slip angle (°)"
        },

        # --- Understeer vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "diff_derive",
            "title": "Understeer vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "Understeer"
        },
    ]

def stepsteer_specs():
    return [
        # --- Trajectory ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_OGR0x",
            "y": "DAVIDChassisSensorIcon01.sensorcha_OGR0y",
            "title": "Trajectory",
            "x_title": "X (m)",
            "y_title": "Y (m)"
        },

        # --- Front slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw",
            "title": "Front slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "front slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "rear slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Yaw rate vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
            "title": "Yaw rate & SWA",
            "x_title": "time (s)",
            "y_title": "yaw rate (°/s)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "rear slip angle (°)"
        },

        # --- Understeer vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "diff_derive",
            "title": "Understeer vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "Understeer"
        },
        
        # --- lateral acceleration vs Time ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            },
            "y3": {
                "y": "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
                "y_title": "Yaw Rate (°/s)"
            },
            "title": "lateral acceleration vs Time",
            "x_title": "Time (s)",
            "y_title": "lateral acceleration (m/s²)",
            "x_perp" : ["acc_metrics.t_signal_90","yaw_metrics.t_signal_90","acc_metrics.t_signal_max","yaw_metrics.t_signal_max"],
        },
    ]

def dlc_specs():
    return [
        # --- Trajectory ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_OGR0x",
            "y": "DAVIDChassisSensorIcon01.sensorcha_OGR0y",
            "title": "Trajectory",
            "x_title": "X (m)",
            "y_title": "Y (m)"
        },

        # --- Front slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw",
            "title": "Front slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "front slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle & SWA",
            "x_title": "time (s)",
            "y_title": "rear slip angle (°)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Yaw rate vs time + SWA ---
        {
            "x": "Time",
            "y": "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
            "title": "Yaw rate & SWA",
            "x_title": "time (s)",
            "y_title": "yaw rate (°/s)",
            "y2": {
                "y": "STR_system.STR_Passive.str_pas_RotAngstrwh",
                "y_title": "SWA (°)"
            }
        },

        # --- Rear slip angle vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
            "title": "Rear slip angle vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "rear slip angle (°)"
        },

        # --- Understeer vs lateral acceleration ---
        {
            "x": "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
            "y": "diff_derive",
            "title": "Understeer vs lateral acceleration",
            "x_title": "lateral acceleration (m/s²)",
            "y_title": "Understeer"
        },
    ]
