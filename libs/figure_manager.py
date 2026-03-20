# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 11:21:06 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import uuid
import plotly.graph_objects as go
from collections import defaultdict
from plotly.subplots import make_subplots
import json,os
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import matplotlib as mpl



STYLE_CONFIG = {
    "font_family": "DejaVu Sans",
    "page_title_size": 15,
    "subgraph_title_size": 14,
    "legend_size": 12,
    "axis_label_size": 12,
    "tick_label_size": 11
}

mpl.rcParams.update({
    "font.size": STYLE_CONFIG["tick_label_size"],
    "legend.fontsize": STYLE_CONFIG["legend_size"],
    "figure.dpi": 1920,
    "font.family": STYLE_CONFIG["font_family"]
})

from collections import defaultdict
import os, json

class ManageData:
    def __init__(self, color_manager=None):
        self.color_manager = color_manager
    
    def load_format_json(self, format_file: str) -> dict:
        with open(format_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def MapdeMap(self, format_json: dict, data_files: list[dict]) -> dict:
        pages_output = {}
        for page_name, page_content in format_json.items():
            page_result = {"title": page_content.get("title", ""), "subgraphs": []}
            for subgraph in page_content.get("subgraphs", []):
                subgraph_result = dict(subgraph)

                if "criteria_id_list" in subgraph_result:
                    flat_values = [data.get(cid) for cid in subgraph_result["criteria_id_list"] for data in data_files]
                    subgraph_result["criteria_id_list"] = flat_values
                    subgraph_result["vehicle_count"] = len(flat_values)

                if "spline_criteria" in subgraph_result:
                    spline = dict(subgraph_result["spline_criteria"])
                    cid = spline.get("id")
                    spline["id"] = [data.get(cid) for data in data_files]
                    subgraph_result["spline_criteria"] = spline
                    subgraph_result["vehicle_count"] = len(spline["id"])

                subgraph_result.setdefault("vehicle_count", 1)
                page_result["subgraphs"].append(subgraph_result)

            pages_output[page_name] = page_result
        return pages_output

    def process_data(self, data_inputs, format_map: dict, format_folder: str = ".", aliases: dict = None):
        classified_outputs = {}
        impostors = {}
        stowaways = {}  # ⭐ fun name for scalar attributes
        grouped = defaultdict(list)

        # Group by Maneuver_ID
        for data in data_inputs:
            maneuver_id = data.get("Maneuver_ID", "Unknown_Maneuver")
            grouped[maneuver_id].append(data)

        for maneuver_id, files in grouped.items():
            if maneuver_id in format_map:
                format_file = os.path.join(format_folder, format_map[maneuver_id])
                format_json = self.load_format_json(format_file)
                classified_outputs[maneuver_id] = self.MapdeMap(format_json, files)

                # impostors logic unchanged
                impostors[maneuver_id] = {}
                for page_idx, (page_name, page_data) in enumerate(classified_outputs[maneuver_id].items(), start=1):
                    impostors[maneuver_id][page_name] = []
                    for data in files:
                        vehicle_id = data.get("Vehicle_ID", "Unknown_Vehicle")
                        file_name = data.get("__file_name__", vehicle_id)
                        alias_val = aliases.get(file_name, "") if aliases else ""
                        alias_name = alias_val if alias_val else vehicle_id
                        impostors[maneuver_id][page_name].append(alias_name)

                # ⭐ collect scalar attributes in flipped structure
                stowaways[maneuver_id] = {}
                for data in files:
                    vehicle_id = data.get("Vehicle_ID", "Unknown_Vehicle")
                    for key, val in data.items():
                        if key in ("Maneuver_ID", "Vehicle_ID", "__file_name__"):
                            continue
                        if not isinstance(val, (list, dict)):
                            if key not in stowaways[maneuver_id]:
                                stowaways[maneuver_id][key] = {}
                            stowaways[maneuver_id][key][vehicle_id] = val
            else:
                classified_outputs[maneuver_id] = {"error": f"No format file found for {maneuver_id}"}

        return classified_outputs, impostors, stowaways

class FigureData:
    def __init__(self, page_data, color_manager=None):
        self.page_data = page_data
        self.color_manager = color_manager

    def build_spec(self):
        page_data = self.page_data

        # Inject global style values
        if self.color_manager:
            page_data["axis_title_color"] = self.color_manager.axis_title_color
            page_data["tick_label_color"] = self.color_manager.tick_label_color
            page_data["legend_text_color"] = self.color_manager.legend_text_color
            page_data["plot_title_color"] = self.color_manager.plot_title_color
            page_data["plot_bgcolor"] = self.color_manager.plot_bgcolor
            page_data["grid_color"] = self.color_manager.grid_color
        else:
            page_data["axis_title_color"] = "black"
            page_data["tick_label_color"] = "black"
            page_data["legend_text_color"] = "black"
            page_data["plot_title_color"] = "black"
            page_data["plot_bgcolor"] = "white"
            page_data["grid_color"] = "#DDDDDD"

        # Reset color index per subgraph
        for subgraph in page_data.get("subgraphs", []):
            color_index = 0  # start fresh for each subgraph

            subgraph.setdefault("line_mode", "lines")
            subgraph.setdefault("line_width", 2)
            subgraph.setdefault("opacity", 1.0)
            subgraph.setdefault("marker_size", 15)

            # Assign colors per vehicle group
            vehicle_colors = []
            vehicle_count = subgraph.get("vehicle_count", 1)
            if self.color_manager:
                palette = self.color_manager.line_palette
                for v_idx in range(vehicle_count):
                    trace_color = palette[v_idx] if v_idx < len(palette) else self.color_manager.get_trace_color(v_idx)
                    vehicle_colors.append(trace_color)
            else:
                vehicle_colors = ["#0072B2"] * vehicle_count

            subgraph["vehicle_colors"] = vehicle_colors

        return page_data

    def compute_autoscale(self, values):
        if not values:
            return [0, 1], 0.1

        min_val, max_val = min(values), max(values)

        # Handle identical values
        if min_val == max_val:
            min_val -= 0.5
            max_val += 0.5

        # Add padding
        pad = 0.05 * (max_val - min_val)
        axis_range = [min_val - pad, max_val + pad]

        # Adaptive tick step
        raw_step = (axis_range[1] - axis_range[0]) / 10.0
        tick_step = self._nice_number(raw_step)

        return axis_range, tick_step

    def _nice_number(self, value):
        """Round value to a 'nice' tick step (1, 2, 5 × 10^n)."""
        import math
        exp = math.floor(math.log10(value))
        f = value / 10**exp
        if f < 1.5:
            nice = 1
        elif f < 3:
            nice = 2
        elif f < 7:
            nice = 5
        else:
            nice = 10
        return nice * 10**exp


    def render_page(self, page_data=None, vehicle_labels=None,
                    use_autoscale=True, fig_width=12, fig_height=None,
                    tick_angle=0, cutfactor_1d=1.4, cutfactor_2d=7.5):
        if page_data is None:
            page_data = self.build_spec()

        subgraphs = page_data.get("subgraphs", [])
        rows = len(subgraphs)

        one_d_count = sum(1 for sg in subgraphs if sg.get("subgraph_type") == "1DHorizontalCriteria")
        two_d_count = sum(1 for sg in subgraphs if sg.get("subgraph_type") == "twoDimGraph")

        # --- 1D branch (Matplotlib) ---
        if two_d_count == 0:
            if fig_height is None:
                fig_height = 1.2 * one_d_count
            fig, axes = plt.subplots(rows, 1, figsize=(fig_width, fig_height))
            if rows == 1:
                axes = [axes]

            for i, (sg, ax) in enumerate(zip(subgraphs, axes), start=1):
                values = sg.get("criteria_id_list", [])
                if use_autoscale:
                    axis_range, tick_step = self.compute_autoscale(values)
                else:
                    axis_range = sg.get("xAxis_scale_range")
                    if not axis_range or len(axis_range) < 2:
                        axis_range = [min(values) - 0.05, max(values) + 0.05] if values else [0, 1]
                    tick_step = sg.get("xAxis_scale_major_tick_step", 0.05)

                if not tick_step or tick_step <= 0:
                    tick_step = (axis_range[1] - axis_range[0]) / 10.0

                labels = [
                    vehicle_labels[v_idx] if vehicle_labels and v_idx < len(vehicle_labels)
                    else f"Vehicle {v_idx+1}"
                    for v_idx in range(len(values))
                ]
                colors = sg.get("vehicle_colors", [])
                marker_size = sg.get("marker_size", 40)

                y_position = 0
                ax.axhline(y_position, color=page_data["axis_title_color"], lw=2)

                for v_idx, val in enumerate(values):
                    label = labels[v_idx]
                    color = colors[v_idx] if v_idx < len(colors) else "black"
                    ax.plot(val, y_position, 'o', color=color, markersize=marker_size, label=label)

                ax.set_xlim(axis_range[0], axis_range[1])
                ax.set_ylim(-0.5, 0.5)
                ticks = np.arange(axis_range[0], axis_range[1] + tick_step, tick_step)
                ax.set_xticks(ticks)
                ax.set_yticks([])
                ax.spines['left'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['bottom'].set_position(('data', y_position))
                ax.tick_params(axis='x', colors=page_data["tick_label_color"], rotation=tick_angle)
                ax.grid(color=page_data["grid_color"], linestyle='--', linewidth=0.5)
                ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))

                ax.set_title(
                    sg.get("subgraph_title", ""),
                    fontsize=STYLE_CONFIG["subgraph_title_size"],
                    fontweight="bold",
                    fontfamily=STYLE_CONFIG["font_family"],
                    loc="left",
                    color=page_data["axis_title_color"]
                )

            handles, _ = axes[0].get_legend_handles_labels()
            fig.legend(
                handles, vehicle_labels,
                loc="center left",
                labelspacing=1.2,
                bbox_to_anchor=(1.0, 0.5),
                fontsize=STYLE_CONFIG["legend_size"],
                frameon=True,                      # <-- show bounding box
                facecolor=page_data["plot_bgcolor"],                 # <-- background color
                edgecolor=page_data["legend_text_color"],  # <-- border color
                framealpha=1.0,                   # <-- opacity of box
                ncol=1
            )

            fig.suptitle(
                page_data.get("title", ""),
                color=page_data["plot_title_color"],
                fontsize=STYLE_CONFIG["page_title_size"],
                fontweight="bold",
                fontfamily=STYLE_CONFIG["font_family"]
            )
            fig.tight_layout()

            # --- calculate split ratio ---
            split_ratio = 0.8  # default
            if fig.legends:
                fig.canvas.draw()
                bbox = fig.legends[0].get_window_extent()
                bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
                legend_width_px = int(bbox.width * fig.dpi) / cutfactor_1d
                w_px = fig.get_size_inches()[0] * fig.dpi

                # enforce minimum width for small legends
                legend_width_px = max(legend_width_px, 150)

                # compute ratio with clamp
                split_ratio = (w_px - legend_width_px) / w_px
                split_ratio = max(min(split_ratio, 0.9), 0.6)

                # fallback for very small legends (≤ 3 labels)
                if len(fig.legends[0].texts) <= 3:
                    split_ratio = 0.8

            return fig, split_ratio



        # --- 2D branch (Plotly) ---
        else:
            if fig_height is None:
                fig_height = 6

            fig = make_subplots(
                rows=rows,
                cols=1,
                shared_xaxes=False,
                vertical_spacing=min(0.2, 1.0/(rows-1) if rows > 1 else 1.0),
                subplot_titles=[sg.get("subgraph_title", "") for sg in subgraphs]
            )

            for i, sg in enumerate(subgraphs, start=1):
                if i-1 < len(fig.layout.annotations):
                    fig.layout.annotations[i-1].update(
                        text=f"<b>{sg.get('subgraph_title', '')}</b>",
                        font=dict(
                            size=STYLE_CONFIG["subgraph_title_size"],
                            family=STYLE_CONFIG["font_family"],
                            color=page_data["axis_title_color"]
                        ),
                        x=0,
                        xanchor="left"
                    )
                sg_type = sg.get("subgraph_type", "1DHorizontalCriteria")
                if sg_type == "twoDimGraph":
                    spline = sg.get("spline_criteria", {})
                    x_index = spline.get("x_value", 0)
                    y_indexes = spline.get("y_values_list", [])
                    vehicles = spline.get("id", [])
                    for v_idx, vehicle_curves in enumerate(vehicles):
                        label = vehicle_labels[v_idx] if vehicle_labels and v_idx < len(vehicle_labels) else f"Vehicle {v_idx+1}"
                        x_vals = vehicle_curves[x_index]
                        for y_idx in y_indexes:
                            y_vals = vehicle_curves[y_idx]
                            if not hasattr(x_vals, "__iter__") or isinstance(x_vals, (str, bytes)):
                                x_vals = [x_vals]
                            if not hasattr(y_vals, "__iter__") or isinstance(y_vals, (str, bytes)):
                                y_vals = [y_vals]
                            fig.add_trace(go.Scatter(
                                x=x_vals,
                                y=y_vals,
                                mode="lines",
                                name=label,
                                legendgroup=label,
                                line=dict(color=sg["vehicle_colors"][v_idx], width=sg["line_width"]),
                                showlegend=(i == 1)
                            ), row=i, col=1)

                    fig.update_xaxes(
                        title=dict(text=sg.get("xAxisTitle", ""), 
                            font=dict(color=page_data["axis_title_color"],
                            size=STYLE_CONFIG['axis_label_size'],
                            family=STYLE_CONFIG["font_family"],)
                            ),
                        type="log" if sg.get("x_axis_log_scale", False) else "linear",
                        tickangle=tick_angle,
                        tickfont=dict(color=page_data["tick_label_color"]),
                        gridcolor=page_data["grid_color"],
                        autorange=True,
                        showline=True,                      # <-- add this
                        linecolor=page_data["axis_title_color"],  # <-- axis line color
                        linewidth=2,                        # <-- thickness
                        row=i, col=1
                    )
                    fig.update_yaxes(
                        title=dict(text=sg.get("yAxisTitle", ""), 
                            font=dict(color=page_data["axis_title_color"],
                            size=STYLE_CONFIG['axis_label_size'],
                            family=STYLE_CONFIG["font_family"],)
                            ),
                        tickfont=dict(color=page_data["tick_label_color"]),
                        gridcolor=page_data["grid_color"],
                        autorange=True,
                        showline=True,                      # <-- add this
                        linecolor=page_data["axis_title_color"],  # <-- axis line color
                        linewidth=2,                        # <-- thickness
                        row=i, col=1
                    )
            #
            fig.update_layout(
                title=dict(
                    text=f"<b>{page_data.get('title', '')}</b>",
                    font=dict(
                        size=STYLE_CONFIG["page_title_size"],
                        family=STYLE_CONFIG["font_family"],
                        color=page_data["plot_title_color"],
                    ),
                    x=0.5,
                    xanchor="center",
                    xref="paper"
                ),
                #margin=dict(r=80),
                legend=dict(
                    font=dict(
                        size=STYLE_CONFIG["legend_size"],
                        family=STYLE_CONFIG["font_family"],
                        color=page_data["legend_text_color"]
                    ),
                    x=1.02, y=0.5,
                    xanchor="left", yanchor="middle",
                    bgcolor=page_data["plot_bgcolor"],   # background for bounding box
                    bordercolor=page_data["legend_text_color"],               # border color
                    borderwidth=2                      # thickness of border
                ),
                plot_bgcolor=page_data["plot_bgcolor"],
                paper_bgcolor=page_data["plot_bgcolor"],
                width=int(fig_width * 100),
                height=int(fig_height * 100),
            )


            # crude estimate based on longest label length
            max_label_len = max(len(lbl) for lbl in vehicle_labels) if vehicle_labels else 10
            legend_width_px = max_label_len * cutfactor_2d + 50
            w_px = fig_width * 100
            split_ratio = max(0.5, (w_px - legend_width_px) / w_px)

            return fig, split_ratio
