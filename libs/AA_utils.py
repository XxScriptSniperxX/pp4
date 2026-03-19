# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 16:46:45 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import json
import os
from collections import defaultdict
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import pickle
from datetime import datetime

PRESET_FILE = "presets.json"

def phunt(obj, directory=".", name=None):
    """
    Save any Python object as a pickle file.

    Parameters
    ----------
    obj : any
        The object to pickle (dict, list, custom class, etc.)
    directory : str, optional
        Directory to store the pickle file. Defaults to current directory.
    name : str, optional
        Specific filename (without extension). If not provided, a timestamp-based name is used.

    Returns
    -------
    str
        Full path to the saved pickle file.
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)

    # Build filename
    if name is None:
        name = f"phunt"#_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filename = f"{name}.pkl"

    # Full path
    filepath = os.path.join(directory, filename)

    # Save pickle
    with open(filepath, "wb") as f:
        pickle.dump(obj, f)

    return filepath

def update_presets_json(updates: dict):
    """
    Merge updates into the existing presets.json file.
    Only overwrites the keys provided in `updates`.
    """
    # Load existing data if file exists
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Merge updates
    data.update(updates)

    # Write back to file
    with open(PRESET_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_presets():
    """
    Read presets.json if available, otherwise return defaults.
    Returns a dict with app and plot presets plus selected/applied snapshots.
    """
    # Try to read file
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # --- Defaults ---
    default_app_presets = {
        "Preset 1": {"primary":"#E69F00","text":"#000000","background":"#FFFFFF","secondary":"#F0F0F0"},
        "Preset 2": {"primary":"#444444","text":"#FFFFFF","background":"#000000","secondary":"#222222"},
        "Preset 3": {"primary":"#FF0000","text":"#000000","background":"#FFFFFF","secondary":"#FFFF00"},
        "Preset 4": {"primary":"#0072B2","text":"#000000","background":"#FFFFFF","secondary":"#DDDDDD"}
    }

    default_plot_presets = {
        "Preset 1": {
            "axis_title":"#000000","tick_label":"#000000","legend_text":"#000000",
            "plot_bg":"#FFFFFF","grid":"#DDDDDD","line_color":"#0072B2",
            "palette":["#E69F00","#56B4E9","#009E73"],
            "use_palette": False   # NEW
        },
        "Preset 2": {
            "axis_title":"#444444","tick_label":"#FFFFFF","legend_text":"#FFFFFF",
            "plot_bg":"#000000","grid":"#555555","line_color":"#D55E00",
            "palette":["#0072B2","#D55E00","#CC79A7"],
            "use_palette": True    # NEW
        },
        "Preset 3": {
            "axis_title":"#FF0000","tick_label":"#000000","legend_text":"#000000",
            "plot_bg":"#FFFFFF","grid":"#AAAAAA","line_color":"#FF0000",
            "palette":["#FF0000","#00FF00","#0000FF"],
            "use_palette": False   # NEW
        },
        "Preset 4": {
            "axis_title":"#0072B2","tick_label":"#000000","legend_text":"#000000",
            "plot_bg":"#FFFFFF","grid":"#DDDDDD","line_color":"#0072B2",
            "palette":["#0072B2","#E69F00","#56B4E9"],
            "use_palette": True    # NEW
        }
    }

    # --- Build return dict ---
    app_presets = data.get("app_presets", default_app_presets)
    selected_app_preset = data.get("selected_app_preset", "Preset 1")
    applied_app_theme = data.get("applied_app_theme", app_presets.get(selected_app_preset, {}))

    plot_presets = data.get("plot_presets", default_plot_presets)
    selected_plot_preset = data.get("selected_plot_preset", "Preset 1")
    applied_plot_theme = data.get("applied_plot_theme", plot_presets.get(selected_plot_preset, {}))

    return {
        "app_presets": app_presets,
        "selected_app_preset": selected_app_preset,
        "applied_app_theme": applied_app_theme,
        "plot_presets": plot_presets,
        "selected_plot_preset": selected_plot_preset,
        "applied_plot_theme": applied_plot_theme
    }
