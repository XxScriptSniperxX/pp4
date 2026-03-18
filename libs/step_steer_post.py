# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 10:38:20 2026

@tag: Xx_ScriptSniper_xX
@author: Albin
"""
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# -----------------------------
# Curve fitting helpers
# -----------------------------
def exp_decay(t, a, b, c):
    return a * np.exp(-b * t) + c

def fit_curve(time, values, fit_method="", upsample_factor=10):
    time = np.asarray(time)
    values = np.asarray(values)
    t_dense = np.linspace(time.min(), time.max(), len(time)*upsample_factor)

    if fit_method == "spline":
        spline = UnivariateSpline(time, values, s=len(time)*0.001)
        fitted = spline(t_dense)
    elif fit_method == "poly":
        coeffs = np.polyfit(time, values, 3)
        fitted = np.polyval(coeffs, t_dense)
    elif fit_method == "exp":
        try:
            popt, _ = curve_fit(exp_decay, time, values,
                                p0=(np.max(values), 0.1, np.min(values)))
            fitted = exp_decay(t_dense, *popt)
        except RuntimeError:
            fitted = np.interp(t_dense, time, values)
    else:
        fitted = np.interp(t_dense, time, values)

    return t_dense, fitted

# -----------------------------
# Signal analysis
# -----------------------------
def analyze_signal(signal_fit, steering_fit, t_dense, t0, delta=100, tol=1e-5):
    ii = 1
    max_len = len(t_dense)

    while ii * delta < max_len:
        seg_signal = signal_fit[-ii*delta : -(ii-1)*delta] if ii > 1 else signal_fit[-ii*delta:]
        seg_steer  = steering_fit[-ii*delta : -(ii-1)*delta] if ii > 1 else steering_fit[-ii*delta:]
        if len(seg_signal) < 2 or len(seg_steer) < 2:
            break
        if (np.abs(np.mean(np.diff(seg_signal))) < tol and
            np.abs(np.mean(np.diff(seg_steer))) < tol):
            ii += 1
        else:
            break

    stab_index = max(0, min(max_len-1, max_len - (ii-2)*delta))
    t_ss = t_dense[stab_index]
    signal_ss = signal_fit[stab_index]

    # --- Find max signal ---
    idx_max_signal = np.argmax(np.abs(signal_fit))
    t_signal_max = t_dense[idx_max_signal]
    delta_t_signal_max = t_signal_max - t0

    # --- 90% crossing ---
    signal_90p = 0.9 * signal_ss

    # Left side: search only up to the max index
    idx_90_left = np.argmax(signal_fit[:idx_max_signal] > signal_90p)
    t_signal_90_left = t_dense[idx_90_left]
    delta_t_signal_90_left = t_signal_90_left - t0

    # Right side: your original logic
    idx_90_right = np.argmax(signal_fit > signal_90p)
    t_signal_90_right = t_dense[idx_90_right]
    delta_t_signal_90_right = t_signal_90_right - t0

    return {
        "t_ss": t_ss,
        "signal_ss": signal_ss,
        "t_signal_max": t_signal_max,
        "delta_t_signal_max": delta_t_signal_max,
        "signal_90p": signal_90p,
        "t_signal_90_right": t_signal_90_right,
        "delta_t_signal_90_right": delta_t_signal_90_right,
        "t_signal_90": t_signal_90_left,
        "delta_t_signal_90_right": delta_t_signal_90_right,
    }


def analyze_vehicle_response(df, time_col, steering_col, acc_col, yaw_col,
                             fit_method="", upsample_factor=10,
                             delta=100, tol=1e-5):
    time = time_col.to_numpy()
    steering = steering_col.to_numpy()
    acc = acc_col.to_numpy()
    yaw = yaw_col.to_numpy()

    t_dense, steering_fit = fit_curve(time, steering, fit_method, upsample_factor)
    _, acc_fit = fit_curve(time, acc, fit_method, upsample_factor)
    _, yaw_fit = fit_curve(time, yaw, fit_method, upsample_factor)

    str_max = np.max(np.abs(steering_fit))
    target_val = 0.5 * str_max
    idx_50 = np.argmin(np.abs(np.abs(steering_fit) - target_val))
    t0 = t_dense[idx_50]
    str_50p = steering_fit[idx_50]

    acc_metrics = analyze_signal(acc_fit, steering_fit, t_dense, t0, delta, tol)
    yaw_metrics = analyze_signal(yaw_fit, steering_fit, t_dense, t0, delta, tol)

    return {
        "t0": t0,
        "str_50p": str_50p,
        "acc_metrics": acc_metrics,
        "yaw_metrics": yaw_metrics,
        "t_dense": t_dense,
        "steering_fit": steering_fit,
        "acc_fit": acc_fit,
        "yaw_fit": yaw_fit,
    }

# -----------------------------
# Plotting helper
# -----------------------------
def plot_signal(time, raw, t_dense, fitted, label, t0=None, t90=None, t_peak=None):
    plt.figure(figsize=(10,5))
    plt.plot(time, raw, 'o', alpha=0.4, label=f"{label} raw")
    plt.plot(t_dense, fitted, '-', linewidth=2, label=f"{label} fitted")
    if t0 is not None:
        plt.axvline(t0, color='g', linestyle='--', label="t0 (steering 50%)")
    if t90 is not None:
        plt.axvline(t90, color='r', linestyle='--', label="90% response")
    if t_peak is not None:
        plt.axvline(t_peak, color='m', linestyle='--', label="peak")
    plt.xlabel("Time [s]")
    plt.ylabel(label)
    plt.title(f"{label} vs Time")
    plt.legend()
    plt.grid(True)
    plt.show()

# -----------------------------
# Run analysis + plots
# -----------------------------
# df = pd.read_excel(r"C:\project files\script_scratch\workspace\mada_test_dir\PROJECT\smartvmc_stepsteer\ISO7401_step\combined_data.xlsx")

# results = analyze_vehicle_response(
    # df,
    # time_col="Time",
    # steering_col="Steering wheel angle",
    # acc_col="y - Acc. chassis COG (B1)",
    # yaw_col="Vehicle yaw velocity"
# )

# print("Steering 50% time:", results["t0"])
# print("Steering 50% angle:", results["str_50p"])
# print("\nLateral Acceleration Metrics:")
# for k, v in results["acc_metrics"].items():
#     print(f"  {k}: {v:.3f}")
# print("\nYaw Velocity Metrics:")
# for k, v in results["yaw_metrics"].items():
#     print(f"  {k}: {v:.3f}")

# # Plot steering
# plot_signal(df["Time"], df["Steering wheel angle"],
#             results["t_dense"], results["steering_fit"],
#             "Steering", t0=results["t0"])

# # Plot lateral acceleration
# plot_signal(df["Time"], df["y - Acc. chassis COG (B1)"],
#             results["t_dense"], results["acc_fit"],
#             "Lateral Accel",
#             t0=results["t0"],
#             t90=results["acc_metrics"]["t_signal_90"],
#             t_peak=results["acc_metrics"]["t_signal_max"])

# # Plot yaw velocity
# plot_signal(df["Time"], df["Vehicle yaw velocity"],
#             results["t_dense"], results["yaw_fit"],
#             "Yaw Velocity",
#             t0=results["t0"],
#             t90=results["yaw_metrics"]["t_signal_90"],
#             t_peak=results["yaw_metrics"]["t_signal_max"])
