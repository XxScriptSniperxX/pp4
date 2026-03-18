# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 15:09:51 2026

@author: a056346

Modified on Mon Feb  9 15:41:51 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import numpy as np
import pandas as pd
from libs.step_steer_post import analyze_vehicle_response

import re

def data_cleanup(df):
    # Drop first row and reset index
    df = df.drop(df.index[0])
    df.reset_index(drop=True, inplace=True)

    # Normalize column names: convert "sensorcha_X@DAVID..." → "DAVID....sensorcha_X"
    def normalize(col):
        if "@" in col:
            base, prefix = col.split("@")
            return f"{prefix.replace('DAV_', '')}.{base}"
        return col

    df = df.rename(columns={c: normalize(c) for c in df.columns})

    # Canonical column list
    cols = [
        "Time",
        "DAVIDChassisSensorIcon01.sensorcha_OGR0x",
        "DAVIDChassisSensorIcon01.sensorcha_OGR0y",
        "DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw",
        "DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw",
        "DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw",
        "DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty",
        "DAVIDChassisSensorIcon01.sensorcha_SideslipGRyaw",
        "STR_system.STR_Passive.str_pas_RotAngstrwh",
        "DAVIDChassisSensorIcon01.sensorcha_ORraxleR0x",
        "DAVIDChassisSensorIcon01.sensorcha_ORraxleR0y",
    ]

    # Select and cast
    new_df = df[cols].astype(float)
    return new_df


def dataframe_modif(df, man=None, gparams=None):
    gparams=None
    lr_scalar = None
    df = data_cleanup(df)
    single = {}
    # -- Understeer gradient --
    df["diff_derive"] = (
        df["DAVIDChassisSensorIcon01.sensorcha_SideslipFraxleRyaw"]
        - df["DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw"]
    )
    if man=="Roundabout":
        # --- lr from gparams (scalar) ---
        if gparams is None:
            pass
        else:
            COGX = get_param_value(gparams, "sensorcha_distOgridG_x")
            RraxleX = get_param_value(gparams, "sensorcha_OgridRearaxle_x")
            if COGX is None or RraxleX is None:
                lr_scalar = 0.5
            else:
                lr_scalar = abs(COGX/1000 - RraxleX/1000)
        # -- CIR --
        # --- lr from dataframe (vector) ---
        df["lr"] = np.sqrt(
            (df["DAVIDChassisSensorIcon01.sensorcha_ORraxleR0x"] - df["DAVIDChassisSensorIcon01.sensorcha_OGR0x"])**2 +
            (df["DAVIDChassisSensorIcon01.sensorcha_ORraxleR0y"] - df["DAVIDChassisSensorIcon01.sensorcha_OGR0y"])**2
        )
        derive_ar = np.deg2rad(df["DAVIDChassisSensorIcon01.sensorcha_SideslipRraxleRyaw"])
        derive_g = np.deg2rad(df["DAVIDChassisSensorIcon01.sensorcha_SideslipGRyaw"])
        df["CIR_x"] = compute_cirX(lr_scalar if lr_scalar is not None else df["lr"],
                                derive_g, derive_ar)
        df["CIR_y"] = compute_cirY(lr_scalar if lr_scalar is not None else df["lr"],
                            derive_g, derive_ar)

    # -- Step_steer response times--
    if man=="Step Steer":
        results = analyze_vehicle_response(
        df,
        time_col=df["Time"],
        steering_col=df["STR_system.STR_Passive.str_pas_RotAngstrwh"],
        acc_col=df["DAVIDChassisSensorIcon01.sensorcha_AccelGRtgty"],
        yaw_col=df["DAVIDChassisSensorIcon01.sensorcha_EulerVelZyaw"]
        )
        single.update(results)
    
    return df, single


def compute_cirX(lr, derive_g, derive_ar, tol=1e-2):
    tg = np.tan(derive_g)
    tr = np.tan(derive_ar)
    denom = tr - tg

    mask_invalid = (~np.isfinite(tg)) | (~np.isfinite(tr)) | (np.isclose(denom, 0.0, atol=tol))

    # lr can be scalar or Series; broadcasting works
    result = (lr * tg) / denom
    result[mask_invalid] = 0
    return result

def compute_cirY(lr, derive_g, derive_ar, tol=1e-2):
    tg = np.tan(derive_g)
    tr = np.tan(derive_ar)
    denom = tr - tg

    mask_invalid = (~np.isfinite(tg)) | (~np.isfinite(tr)) | (np.isclose(denom, 0.0, atol=tol))

    # lr can be scalar or Series; broadcasting works
    result = (lr) / denom
    result[mask_invalid] = 0
    return result


def get_param_value(gparams, keyword, default=None):
    row = gparams[gparams["GlobalParameter"].str.contains(keyword, case=False)]
    if not row.empty:
        return float(row["Value"].iloc[0])
    return default

