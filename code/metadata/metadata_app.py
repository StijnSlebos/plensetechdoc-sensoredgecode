import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path("C:/Users/MirandavanDuijn/OneDrive - Plense Technologies/Documents - Research & Development/Datasets/metadata_test")
DATA_DIR.mkdir(exist_ok=True)

# --- Utility functions ---
def list_object_files():
    return [f for f in DATA_DIR.glob("metadata_oid*.json")]

def load_object_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def save_object_data(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def get_all_keys(data_list):
    keys = set()
    for item in data_list:
        keys.update(item.keys())
    return sorted(list(keys))

def get_next_available_oid():
    existing = sorted([int(f.stem.replace("metadata_oid", "")) for f in list_object_files() if f.stem.replace("metadata_oid", "").isdigit()])
    next_id = 0
    while next_id in existing:
        next_id += 1
    return f"oid{next_id:06}"

# --- Streamlit layout ---
st.set_page_config(layout="wide")
tabs = st.tabs(["📋 Manage Metadata", "📊 Summary"])

with tabs[0]:
    st.title("🌱 Plense Object Metadata Manager")

    st.sidebar.header("Available Objects")
    object_files = list_object_files()
    object_display_options = []
    oid_to_file_map = {}

    for f in object_files:
        oid = f.stem.replace("metadata_", "")
        try:
            data = load_object_data(f)
            obj_type = data.get("object_metadata", {}).get("type", "unknown")
            display_str = f"{oid} — {obj_type}"
        except Exception as e:
            display_str = f"{oid} — <error reading type>"
        object_display_options.append(display_str)
        oid_to_file_map[display_str] = oid

    selected_display = st.sidebar.selectbox("Select an object to view/edit", object_display_options)
    selected_oid = oid_to_file_map[selected_display]

    if selected_oid:
        obj_path = DATA_DIR / f"metadata_{selected_oid}.json"
        obj_data = load_object_data(obj_path)

        st.header(f"Object: {selected_oid}")

        with st.expander("ℹ️ Object Metadata Overview"):
            object_metadata = obj_data.get("object_metadata", {})
            st.markdown("**Object-specific attributes (view/edit/delete):**")

            if "edit_meta_keys" not in st.session_state:
                st.session_state.edit_meta_keys = {}

            for i, (key, value) in enumerate(object_metadata.items()):
                edit_mode = st.session_state.edit_meta_keys.get(key, False)

                col1, col2, col3 = st.columns([4, 4, 2])

                if edit_mode:
                    with col1:
                        new_key = st.text_input(f"Attribute name {i+1}", value=key, key=f"meta_key_{i}")
                    with col2:
                        new_value = st.text_input(f"Value {i+1}", value=value, key=f"meta_val_{i}")
                    with col3:
                        if st.button("✅ Update", key=f"update_meta_{i}"):
                            # Special case: object_id
                            if key == "object_id":
                                if new_value != key:
                                    new_oid = new_value.strip()
                                    if not new_oid.startswith("oid") or not new_oid[3:].isdigit():
                                        st.error("Object ID must follow the format 'oid######'.")
                                    else:
                                        # Update the value in JSON
                                        object_metadata["object_id"] = new_oid
                                        obj_data["object_metadata"] = object_metadata
                                        # Save to new file
                                        new_path = DATA_DIR / f"metadata_{new_oid}.json"
                                        if new_path.exists():
                                            st.error(f"A file for object_id '{new_oid}' already exists.")
                                        else:
                                            save_object_data(new_path, obj_data)
                                            # Remove old file
                                            obj_path.unlink()
                                            st.success(f"Object ID updated and file renamed to: metadata_{new_oid}.json")
                                            st.session_state.edit_meta_keys = {}  # Clear all edit flags
                                            st.rerun()
                                else:
                                    st.info("Object ID unchanged.")
                            else:
                                # Normal metadata update
                                if new_key != key:
                                    object_metadata[new_key] = object_metadata.pop(key)
                                object_metadata[new_key] = new_value
                                obj_data["object_metadata"] = object_metadata
                                save_object_data(obj_path, obj_data)
                                st.success(f"Updated metadata: {new_key} = {new_value}")
                                st.session_state.edit_meta_keys[key] = False
                                st.rerun()

                        if st.button("🗑️ Delete", key=f"delete_meta_{i}"):
                            object_metadata.pop(key)
                            obj_data["object_metadata"] = object_metadata
                            save_object_data(obj_path, obj_data)
                            st.warning(f"Deleted metadata attribute: {key}")
                            st.rerun()
                else:
                    with col1:
                        st.markdown(f"**{key}**")
                    with col2:
                        st.markdown(f"{value}")
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_meta_{i}"):
                            st.session_state.edit_meta_keys[key] = True
                            st.rerun()

            st.markdown("*✏️ Add / Edit Object Metadata*")
            with st.form("edit_object_metadata"):
                key = st.text_input("New attribute name")
                value = st.text_input("Value")
                submitted = st.form_submit_button("Add to object metadata")
                if submitted:
                    obj_data.setdefault("object_metadata", {})[key] = value
                    save_object_data(obj_path, obj_data)
                    st.success(f"Added attribute '{key}' to object metadata.")

        st.subheader("➕ Add New Measurement")

        with st.expander("📌 Show measurement-specific attribute names used so far"):
            measurement_keys = get_all_keys(obj_data.get("measurements", []))
            if measurement_keys:
                st.write(measurement_keys)
            else:
                st.info("No measurement-specific attributes found yet.")

        flexible_fields = {}
        if "flex_field_count" not in st.session_state:
            st.session_state.flex_field_count = 0

        existing_measurement_keys = get_all_keys(obj_data.get("measurements", []))

        with st.form("add_measurement_form"):
            measurements = obj_data.get("measurements") or []
            mid = st.text_input("Measurement ID", value=f"mid{len(measurements)+1:03}")
            now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            ts_begin = st.text_input("Record Timestamp Begin (e.g. 2025-04-01T12:00:00Z)", value=now_iso)
            ts_end = st.text_input("Record Timestamp End (e.g. 2025-04-01T12:05:00Z)")

            for i in range(st.session_state.flex_field_count):
                col1, col2 = st.columns([1, 2])
                with col1:
                    flex_key = st.selectbox(
                        f"Attribute name {i+1}",
                        options=["<Manual input>"] + existing_measurement_keys,
                        key=f"flex_key_select_{i}"
                    )
                    if flex_key == "<Manual input>":
                        flex_key = st.text_input(f"Manual attribute name {i+1}", key=f"flex_key_manual_{i}")
                with col2:
                    flex_val = st.text_input(f"Attribute value {i+1}", key=f"flex_val_{i}")

                if flex_key:
                    flexible_fields[flex_key] = flex_val

            add_field = st.form_submit_button("+ Add another attribute")
            if add_field:
                st.session_state.flex_field_count += 1
                st.rerun()

            submit_measurement = st.form_submit_button("Add Measurement")
            if submit_measurement:
                if not ts_begin or not ts_end:
                    st.error("Timestamps are required.")
                else:
                    measurement = {
                        "measurement_id": mid,
                        "record_timestamp_begin": ts_begin,
                        "record_timestamp_end": ts_end
                    }
                    measurement.update(flexible_fields)
                    obj_data.setdefault("measurements", []).append(measurement)
                    save_object_data(obj_path, obj_data)
                    st.success(f"Measurement '{mid}' added.")

        st.subheader("📄 Existing Measurements")
        for i, m in enumerate(obj_data.get("measurements", [])):
            with st.expander(f"Measurement {m.get('measurement_id', f'# {i+1}')}"):
                st.json(m)
                col1, col2 = st.columns(2)
                if col1.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state[f"edit_mode_{i}"] = True
                if col2.button("🗑️ Delete", key=f"delete_{i}"):
                    obj_data["measurements"].pop(i)
                    save_object_data(obj_path, obj_data)
                    st.rerun()

        st.subheader("🗑️ Delete This Object")
        with st.expander("⚠️ Danger Zone"):
            st.warning("You are about to delete this object. This action cannot be undone.")
            summary_type = obj_data.get("object_metadata", {}).get("type", "unknown")
            num_measurements = len(obj_data.get("measurements", []))
            unique_keys = get_all_keys(obj_data.get("measurements", []))
            st.write(f"**Type:** {summary_type}")
            st.write(f"**Number of measurements:** {num_measurements}")
            st.write(f"**Unique measurement attribute names:** {unique_keys}")

            if st.button("Delete this object permanently"):
                os.remove(obj_path)
                st.success(f"Deleted object {selected_oid}")
                st.rerun()

with tabs[1]:
    st.title("📊 Data Summary")
    all_data = [load_object_data(p) for p in list_object_files()]
    type_counts = {}
    all_types = set()
    for entry in all_data:
        t = entry.get("object_metadata", {}).get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        all_types.add(t)
    df = pd.DataFrame({'type': list(type_counts.keys()), 'count': list(type_counts.values())}).set_index('type')
    st.table(df)

# Create a new object
st.sidebar.markdown("---")
st.sidebar.subheader("Create New Object")
with st.sidebar.form("create_new_object"):
    suggested_oid = get_next_available_oid()
    st.text(f"Suggested ID: {suggested_oid}")
    existing_types = sorted([t for t in all_types if t != "unknown"])
    new_type = st.selectbox("Select existing type or type a new one", existing_types + ["<Other - type manually>"])
    if new_type == "<Other - type manually>":
        new_type = st.text_input("New type")

    confirm = st.form_submit_button("OK to create")
    if confirm:
        if not new_type:
            st.sidebar.error("You must specify a type to create a new object.")
        else:
            new_path = DATA_DIR / f"metadata_{suggested_oid}.json"
            blank_data = {
                "object_metadata": {
                    "object_id": suggested_oid,
                    "type": new_type
                },
                "measurements": []
            }
            save_object_data(new_path, blank_data)
            st.sidebar.success(f"Created new object {suggested_oid}")
            st.rerun()
