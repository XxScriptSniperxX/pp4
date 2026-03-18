# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 11:52:39 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import streamlit as st

class SpecManager:
    def __init__(self, figdata):
        self.figdata = figdata
        self.spec = figdata.spec_out

    def build_ui(self):
        with st.expander(f"⚙️ Settings for {self.spec.get('title', self.figdata.name)}"):
            # --- Primary trace styling (includes titles now) ---
            self._primary_trace_ui()

            # --- Extra axes ---
            self._extra_axes_ui()

            # --- Reference lines ---
            self._reference_lines_ui()
            
            self._legend_settings_ui()

            # --- Update button ---
            # if st.button("Update", key=self.figdata.gen_key("update")):
                # self.apply_updates()

    def _primary_trace_ui(self):
        spec = self.spec
        figdata = self.figdata

        datasets = spec.get("datasets", {})
        palette = getattr(figdata.color_manager, "line_palette", [])
        color_index = 0

        # --- Row 0: Chart title + X axis title ---
        col1, col2 = st.columns([2, 2])

        title_key = figdata.gen_key("title")
        if title_key not in st.session_state:
            st.session_state[title_key] = spec.get("title", figdata.name)
        col1.text_input("Chart title", key=title_key)

        x_title_key = figdata.gen_key("x_title")
        if x_title_key not in st.session_state:
            st.session_state[x_title_key] = spec.get("x_title", "")
        col2.text_input("X axis title", key=x_title_key)

        # --- Row 1: Y axis title (common, not repeated) ---
        y_title_key = figdata.gen_key("y_title")
        if y_title_key not in st.session_state:
            st.session_state[y_title_key] = spec.get("y_title", "")
        st.text_input("Y axis title", key=y_title_key)
        st.markdown(f"### Y1 axis settings")
        # --- Row 2: Trace styling controls (repeat per dataset trace) ---
        for fname, trace in datasets.items():
            st.markdown(f"**Dataset: {fname}**")

            col5, col6, col7, col8 = st.columns(4)

            lw_key = figdata.gen_key(f"{fname}_line_width")
            if lw_key not in st.session_state:
                st.session_state[lw_key] = int(trace.get("line_width", 2))
            col5.number_input("Line width", min_value=1, max_value=10, step=1, key=lw_key)

            op_key = figdata.gen_key(f"{fname}_opacity")
            if op_key not in st.session_state:
                st.session_state[op_key] = float(trace.get("opacity", 1.0))
            col6.number_input("Opacity", min_value=0.1, max_value=1.0, step=0.1, format="%.1f", key=op_key)

            ms_key = figdata.gen_key(f"{fname}_marker_size")
            if ms_key not in st.session_state:
                st.session_state[ms_key] = int(trace.get("marker_size", 8))
            col7.number_input("Marker size", min_value=4, max_value=20, step=1, key=ms_key)

            color_key = figdata.gen_key(f"{fname}_color")
            if color_key not in st.session_state:
                if color_index < len(palette):
                    st.session_state[color_key] = palette[color_index]
                else:
                    st.session_state[color_key] = "#000000"
                color_index += 1
            col8.color_picker("Line color", key=color_key)


    def _extra_axes_ui(self):
        spec = self.spec
        figdata = self.figdata

        extra_axes = spec.get("extra_axes", {})
        palette = getattr(figdata.color_manager, "line_palette", [])

        # Count how many primary + secondary traces exist to offset the color index
        datasets = spec.get("datasets", {})
        primary_count = len(datasets)
        color_index = primary_count  # start after primaries
        # --- Group by axis key first ---
        # Collect all axis keys across files
        axis_keys = set()
        for axes in extra_axes.values():
            axis_keys.update(axes.keys())

        for axis_key in sorted(axis_keys):
            st.markdown(f"### {axis_key.upper()} axis settings")

            # Row 0: Axis title (shared across files, but you can decide if you want one global or per file)
            # If you want one global title per axis:
            axis_title_key = figdata.gen_key(f"{axis_key}_y_title")
            if axis_title_key not in st.session_state:
                # Default to the first file’s y_title
                for axes in extra_axes.values():
                    if axis_key in axes:
                        st.session_state[axis_title_key] = str(axes[axis_key].get("y_title", axis_key))
                        break
            st.text_input(f"{axis_key.upper()} axis title", key=axis_title_key)

            # Row 1: Styling controls per file
            for fname, axes in extra_axes.items():
                if axis_key not in axes:
                    continue
                y_spec = axes[axis_key]
                st.markdown(f"**File: {fname}**")

                col1, col2, col3, col4 = st.columns(4)

                lw_key = figdata.gen_key(f"{fname}_{axis_key}_line_width")
                if lw_key not in st.session_state:
                    st.session_state[lw_key] = int(y_spec.get("line_width", 2))
                col1.number_input("Line width", min_value=1, max_value=10, step=1, key=lw_key)

                op_key = figdata.gen_key(f"{fname}_{axis_key}_opacity")
                if op_key not in st.session_state:
                    st.session_state[op_key] = float(y_spec.get("opacity", 1.0))
                col2.number_input("Opacity", min_value=0.1, max_value=1.0, step=0.1, format="%.1f", key=op_key)

                ms_key = figdata.gen_key(f"{fname}_{axis_key}_marker_size")
                if ms_key not in st.session_state:
                    st.session_state[ms_key] = int(y_spec.get("marker_size", 8))
                col3.number_input("Marker size", min_value=4, max_value=20, step=1, key=ms_key)

                trace_color_key = figdata.gen_key(f"{fname}_{axis_key}_line_color")
                if trace_color_key not in st.session_state:
                    if color_index < len(palette):
                        st.session_state[trace_color_key] = palette[color_index]
                    else:
                        st.session_state[trace_color_key] = y_spec.get("line_color", "#000000")
                    color_index += 1
                col4.color_picker("Line color", key=trace_color_key)



    def _reference_lines_ui(self):
        spec = self.spec
        figdata = self.figdata

        # Count primaries + secondaries
        datasets = spec.get("datasets", {})
        primary_count = len(datasets)

        # Count extras
        extra_axes = spec.get("extra_axes", {})
        extras_count = sum(len(axes) for axes in extra_axes.values())

        # Start color index after primaries + extras
        color_index = primary_count + extras_count
        palette = getattr(figdata.color_manager, "line_palette", [])

        for perp_key in ["x_perp", "y_perp"]:
            perp_dict = spec.get(perp_key, {})
            if not perp_dict:
                continue

            # Flatten all reference lines across files
            ref_lines = []
            for fidx, (fname, values) in enumerate(perp_dict.items(), start=1):
                if not values:  # skip empty lists
                    continue
                for vidx, (val, label) in enumerate(values, start=1):
                    ref_lines.append((fidx, vidx, val, label))

            if not ref_lines:
                continue

            st.markdown(f"### {perp_key.upper()} reference lines")

            # Chunk into groups of 8
            for chunk_start in range(0, len(ref_lines), 8):
                chunk = ref_lines[chunk_start:chunk_start + 8]

                # Row 1: labels
                cols = st.columns(len(chunk))
                for idx, (fidx, vidx, val, label) in enumerate(chunk):
                    cols[idx].markdown(f"**file{fidx}_{perp_key}{vidx}**")

                # Row 2: colors
                cols = st.columns(len(chunk))
                for idx, (fidx, vidx, val, label) in enumerate(chunk):
                    color_key = figdata.gen_key(f"{label}_color")
                    if color_key not in st.session_state:
                        if color_index < len(palette):
                            st.session_state[color_key] = palette[color_index]
                        else:
                            st.session_state[color_key] = "#000000"
                        color_index += 1
                    cols[idx].color_picker("Color", key=color_key)

                # Row 3: dash styles
                cols = st.columns(len(chunk))
                for idx, (fidx, vidx, val, label) in enumerate(chunk):
                    dash_key = figdata.gen_key(f"{label}_dash")
                    if dash_key not in st.session_state:
                        st.session_state[dash_key] = "dash" if perp_key == "x_perp" else "dot"
                    cols[idx].selectbox("Dash", ["solid", "dash", "dot"], key=dash_key)

                # Row 4: marker styles
                cols = st.columns(len(chunk))
                for idx, (fidx, vidx, val, label) in enumerate(chunk):
                    marker_key = figdata.gen_key(f"{label}_marker")
                    if marker_key not in st.session_state:
                        st.session_state[marker_key] = "circle" if perp_key == "x_perp" else "square"
                    cols[idx].selectbox("Marker", ["circle", "square", "diamond"], key=marker_key)

    def _legend_settings_ui(self):
        st.markdown("**Legend Text Settings**")

        legend_map = self.spec.get("legend_labels", {})
        if not legend_map:
            return

        legend_items = list(legend_map.items())

        # Chunk into rows of up to 8 entries
        for chunk_start in range(0, len(legend_items), 8):
            chunk = legend_items[chunk_start:chunk_start + 8]
            cols = st.columns(len(chunk))

            for idx, (trace_key, label) in enumerate(chunk):
                legend_text_key = self.figdata.gen_key(f"{trace_key}_legend_text")

                # Initialize session state if missing
                if legend_text_key not in st.session_state:
                    st.session_state[legend_text_key] = label

                # Show trace key as caption
                cols[idx].caption(trace_key)

                # Editable text input with current label as value
                new_label = cols[idx].text_input(
                    "Legend text",
                    value=st.session_state.get(legend_text_key, label),
                    key=legend_text_key
                )

                # Update spec directly
                self.spec["legend_labels"][trace_key] = new_label.strip() or label

    def apply_updates(self):
        spec = self.spec
        figdata = self.figdata

        # --- Titles ---
        spec["title"] = st.session_state.get(figdata.gen_key("title"), spec.get("title", figdata.name))
        spec["x_title"] = st.session_state.get(figdata.gen_key("x_title"), spec.get("x_title", ""))
        spec["y_title"] = st.session_state.get(figdata.gen_key("y_title"), spec.get("y_title", ""))

        # --- Datasets ---
        for fname, trace in spec.get("datasets", {}).items():
            color_key = figdata.gen_key(f"{fname}_color")
            lw_key = figdata.gen_key(f"{fname}_line_width")
            op_key = figdata.gen_key(f"{fname}_opacity")
            ms_key = figdata.gen_key(f"{fname}_marker_size")

            trace["line_color"] = st.session_state.get(color_key, trace.get("line_color", "#0072B2"))
            trace["line_width"] = int(st.session_state.get(lw_key, trace.get("line_width", 2)))
            trace["opacity"] = float(st.session_state.get(op_key, trace.get("opacity", 1.0)))
            trace["marker_size"] = int(st.session_state.get(ms_key, trace.get("marker_size", 8)))


        # --- Palette slots for datasets ---
        palette_index = 0
        for fname, trace in spec.get("datasets", {}).items():
            if palette_index < len(figdata.color_manager.line_palette):
                figdata.color_manager.line_palette[palette_index] = trace["line_color"]
            palette_index += 1


        # --- Extra axes (grouped by axis key) ---
        axis_keys = set()
        for axes in spec.get("extra_axes", {}).values():
            axis_keys.update(axes.keys())

        for axis_key in axis_keys:
            # One title input per axis key
            axis_title_key = figdata.gen_key(f"{axis_key}_y_title")
            new_title = st.session_state.get(axis_title_key, axis_key)

            for fname, axes in spec.get("extra_axes", {}).items():
                if axis_key not in axes:
                    continue
                y_spec = axes[axis_key]

                # Apply same title to all files sharing this axis
                y_spec["y_title"] = new_title

                # Style controls per file
                trace_color_key = figdata.gen_key(f"{fname}_{axis_key}_line_color")
                lw_key = figdata.gen_key(f"{fname}_{axis_key}_line_width")
                op_key = figdata.gen_key(f"{fname}_{axis_key}_opacity")
                ms_key = figdata.gen_key(f"{fname}_{axis_key}_marker_size")

                y_spec["line_color"] = st.session_state.get(trace_color_key, y_spec.get("line_color", "#0072B2"))
                y_spec["line_width"] = int(st.session_state.get(lw_key, y_spec.get("line_width", 2)))
                y_spec["opacity"] = float(st.session_state.get(op_key, y_spec.get("opacity", 1.0)))
                y_spec["marker_size"] = int(st.session_state.get(ms_key, y_spec.get("marker_size", 8)))

                y_spec["dash"] = y_spec.get("dash", "solid")
                y_spec["line_mode"] = y_spec.get("line_mode", "lines")

                if palette_index < len(figdata.color_manager.line_palette):
                    figdata.color_manager.line_palette[palette_index] = y_spec["line_color"]
                palette_index += 1

        # --- Reference lines ---
        for perp_key in ["x_perp", "y_perp"]:
            perp_dict = spec.get(perp_key, {})
            styles = spec.get(f"{perp_key}_styles", {})
            for fname, values in perp_dict.items():
                if not values:
                    continue
                new_values = []
                for idx, (val, label) in enumerate(values):
                    color_key = figdata.gen_key(f"{label}_color")
                    dash_key = figdata.gen_key(f"{label}_dash")
                    marker_key = figdata.gen_key(f"{label}_marker")

                    color_val = st.session_state.get(color_key, styles.get(label, {}).get("color", "#000000"))
                    dash_val = st.session_state.get(dash_key, styles.get(label, {}).get("dash", "dash" if perp_key == "x_perp" else "dot"))
                    marker_val = st.session_state.get(marker_key, styles.get(label, {}).get("marker", "circle" if perp_key == "x_perp" else "square"))

                    new_values.append((val, label))
                    styles[label] = {"color": color_val, "dash": dash_val, "marker": marker_val}

                    if palette_index < len(figdata.color_manager.line_palette):
                        figdata.color_manager.line_palette[palette_index] = color_val
                    palette_index += 1

                perp_dict[fname] = new_values
            spec[f"{perp_key}_styles"] = styles

        # --- Legend settings ---
        legend_updates = {}
        for trace_key, label in spec.get("legend_labels", {}).items():
            legend_text_key = figdata.gen_key(f"{trace_key}_legend_text")
            if legend_text_key in st.session_state:
                new_label = st.session_state[legend_text_key].strip()
                if (new_label.startswith("(") and new_label.endswith(")")) or \
                   (new_label.startswith("[") and new_label.endswith("]")) or \
                   (new_label.startswith("{") and new_label.endswith("}")):
                    new_label = new_label[1:-1].strip()
                if not new_label:
                    new_label = label
                legend_updates[trace_key] = new_label

        for trace_key, new_label in legend_updates.items():
            spec["legend_labels"][trace_key] = new_label

        spec["legend_font_size"] = st.session_state.get(figdata.gen_key("legend_font_size"), spec.get("legend_font_size", 10))
        spec["legend_itemsizing"] = st.session_state.get(figdata.gen_key("legend_itemsizing"), spec.get("legend_itemsizing", "constant"))
        spec["legend_pos"] = st.session_state.get(figdata.gen_key("legend_pos"), spec.get("legend_pos", "top right"))
        spec["legend_show"] = st.session_state.get(figdata.gen_key("legend_show"), spec.get("legend_show", True))
