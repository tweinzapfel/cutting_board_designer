import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import io
import copy

# Wood type library with realistic colors
WOOD_TYPES = {
    "Maple": "#F5DEB3",
    "Walnut": "#5C4033",
    "Purpleheart": "#7D1B7E",
    "Cherry": "#C95A49",
    "Padauk": "#D2691E",
    "Wenge": "#3E2723",
    "Yellowheart": "#FFD700",
    "Mahogany": "#C04000",
    "Zebrawood": "#E8D4A0",
    "Bloodwood": "#8B0000",
    "White Oak": "#D2B48C",
    "Red Oak": "#C19A6B",
}

# Board size presets (width x length in inches)
BOARD_PRESETS = {
    "Small (8\" × 12\")": (8, 12),
    "Medium (10\" × 14\")": (10, 14),
    "Standard (12\" × 18\")": (12, 18),
    "Large (14\" × 20\")": (14, 20),
    "Extra Large (16\" × 24\")": (16, 24),
    "Custom": None
}

# Unit conversion
def inches_to_cm(inches):
    return inches * 2.54

def cm_to_inches(cm):
    return cm / 2.54

def inches_to_mm(inches):
    return inches * 25.4

def mm_to_inches(mm):
    return mm / 25.4

def calculate_total_width(strips):
    """Calculate total width"""
    total = sum(strip['width'] for strip in strips)
    return total

def draw_board_preview(strips, board_width, board_length):
    """Draw a visual preview of the cutting board"""
    fig, ax = plt.subplots(figsize=(12, 8))

    current_x = 0
    for i, strip in enumerate(strips):
        # Draw the wood strip
        rect = patches.Rectangle(
            (current_x, 0),
            strip['width'],
            board_length,
            linewidth=1,
            edgecolor='black',
            facecolor=strip['color']
        )
        ax.add_patch(rect)

        # Add wood type label
        ax.text(
            current_x + strip['width']/2,
            board_length/2,
            strip['wood_type'],
            ha='center',
            va='center',
            fontsize=10,
            rotation=90,
            fontweight='bold',
            color='white' if strip['wood_type'] in ['Walnut', 'Wenge', 'Purpleheart', 'Bloodwood'] else 'black'
        )

        current_x += strip['width']

    ax.set_xlim(0, board_width)
    ax.set_ylim(0, board_length)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (inches)', fontsize=12)
    ax.set_ylabel('Length (inches)', fontsize=12)
    ax.set_title('Cutting Board Preview', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig

def draw_schematic(strips, board_width, board_length):
    """Draw a dimensioned schematic for cutting"""
    fig, ax = plt.subplots(figsize=(14, 10))

    current_x = 0
    for i, strip in enumerate(strips):
        # Draw the strip outline
        rect = patches.Rectangle(
            (current_x, 0),
            strip['width'],
            board_length,
            linewidth=2,
            edgecolor='black',
            facecolor=strip['color'],
            alpha=0.7
        )
        ax.add_patch(rect)

        # Add wood type and width label inside strip
        ax.text(
            current_x + strip['width']/2,
            board_length/2,
            f"{strip['wood_type']}\n{strip['width']}\"",
            ha='center',
            va='center',
            fontsize=11,
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        # Add dimension line above
        dimension_y = board_length + 1
        ax.plot([current_x, current_x + strip['width']],
                [dimension_y, dimension_y], 'k-', linewidth=1.5)
        ax.plot([current_x, current_x],
                [dimension_y - 0.2, dimension_y + 0.2], 'k-', linewidth=1.5)
        ax.plot([current_x + strip['width'], current_x + strip['width']],
                [dimension_y - 0.2, dimension_y + 0.2], 'k-', linewidth=1.5)
        ax.text(current_x + strip['width']/2, dimension_y + 0.5,
                f'{strip["width"]}"', ha='center', fontsize=10, fontweight='bold')

        current_x += strip['width']

    # Add overall dimensions
    total_width = calculate_total_width(strips)

    # Right side dimension line
    ax.plot([total_width + 1, total_width + 1], [0, board_length], 'k-', linewidth=2)
    ax.plot([total_width + 0.8, total_width + 1.2], [0, 0], 'k-', linewidth=2)
    ax.plot([total_width + 0.8, total_width + 1.2], [board_length, board_length], 'k-', linewidth=2)
    ax.text(total_width + 1.5, board_length/2, f'{board_length}"',
            ha='left', va='center', fontsize=12, fontweight='bold', rotation=270)

    # Bottom dimension line
    ax.plot([0, total_width], [-1, -1], 'k-', linewidth=2)
    ax.plot([0, 0], [-1.2, -0.8], 'k-', linewidth=2)
    ax.plot([total_width, total_width], [-1.2, -0.8], 'k-', linewidth=2)
    ax.text(total_width/2, -1.5, f'Total: {total_width:.3f}"',
            ha='center', fontsize=12, fontweight='bold')

    ax.set_xlim(-2, board_width + 3)
    ax.set_ylim(-3, board_length + 3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Cutting Board Schematic with Dimensions', fontsize=16, fontweight='bold', pad=20)

    # Add cut list
    cut_list_y = -2.5
    ax.text(-1.5, cut_list_y, 'CUT LIST:', fontsize=11, fontweight='bold')
    for i, strip in enumerate(strips):
        ax.text(-1.5, cut_list_y - 0.5 * (i + 1),
                f'{i+1}. {strip["wood_type"]}: {strip["width"]}" × {board_length}"',
                fontsize=9)

    return fig

# Streamlit App
st.set_page_config(page_title="Cutting Board Designer", layout="wide")
st.title("🪵 Wood Cutting Board Designer")
st.markdown("Design your custom cutting board with different wood types and widths!")

# Sidebar for controls
st.sidebar.header("Design Controls")

# Initialize session state
if 'strips' not in st.session_state:
    st.session_state.strips = [
        {'wood_type': 'Maple', 'width': 2.0, 'color': WOOD_TYPES['Maple']},
        {'wood_type': 'Walnut', 'width': 1.5, 'color': WOOD_TYPES['Walnut']},
        {'wood_type': 'Maple', 'width': 2.0, 'color': WOOD_TYPES['Maple']},
    ]
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.history_index = -1
if 'unit' not in st.session_state:
    st.session_state.unit = "inches"

# Measurement unit selector
st.sidebar.subheader("Settings")
unit = st.sidebar.radio(
    "Measurement Units",
    options=["inches", "centimeters", "millimeters"],
    index=["inches", "centimeters", "millimeters"].index(st.session_state.unit),
    horizontal=True
)
st.session_state.unit = unit

# Unit display helper
def format_dimension(value_in_inches):
    if st.session_state.unit == "centimeters":
        return f"{inches_to_cm(value_in_inches):.2f} cm"
    elif st.session_state.unit == "millimeters":
        return f"{inches_to_mm(value_in_inches):.1f} mm"
    else:
        return f"{value_in_inches:.3f}\""

st.sidebar.markdown("---")

# Board size selection
st.sidebar.subheader("Board Size")
size_preset = st.sidebar.selectbox(
    "Size Preset",
    options=list(BOARD_PRESETS.keys()),
    index=2  # Default to "Standard (12" × 18")"
)

if BOARD_PRESETS[size_preset] is None:
    # Custom size
    col1, col2 = st.sidebar.columns(2)
    with col1:
        board_width = st.number_input(
            "Width (in)",
            min_value=4.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="custom_width"
        )
    with col2:
        board_length = st.number_input(
            "Length (in)",
            min_value=6.0,
            max_value=36.0,
            value=18.0,
            step=0.5,
            key="custom_length"
        )
else:
    # Use preset
    board_width, board_length = BOARD_PRESETS[size_preset]
    st.sidebar.info(f"Board: {board_width}\" × {board_length}\"")

st.sidebar.markdown("---")

# Number of strips
num_strips = st.sidebar.number_input(
    "Number of strips",
    min_value=1,
    max_value=20,
    value=len(st.session_state.strips)
)

# Adjust strips list if needed
while len(st.session_state.strips) < num_strips:
    st.session_state.strips.append({
        'wood_type': 'Maple',
        'width': 1.0,
        'color': WOOD_TYPES['Maple']
    })
while len(st.session_state.strips) > num_strips:
    st.session_state.strips.pop()

st.sidebar.markdown("---")
st.sidebar.subheader("Strip Tools")

# Bulk edit option
with st.sidebar.expander("⚙️ Bulk Edit"):
    bulk_width = st.number_input(
        "Set all widths to:",
        min_value=0.25,
        max_value=float(board_width),
        value=1.0,
        step=0.25,
        key="bulk_width"
    )
    if st.button("Apply to All Strips"):
        for strip in st.session_state.strips:
            strip['width'] = bulk_width
        st.rerun()

    bulk_wood = st.selectbox(
        "Set all wood types to:",
        options=list(WOOD_TYPES.keys()),
        key="bulk_wood"
    )
    if st.button("Apply Wood to All"):
        for strip in st.session_state.strips:
            strip['wood_type'] = bulk_wood
            strip['color'] = WOOD_TYPES[bulk_wood]
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Configure Each Strip")

# Configure each strip
for i in range(num_strips):
    st.sidebar.markdown(f"**Strip {i+1}**")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        wood_type = st.selectbox(
            "Wood",
            options=list(WOOD_TYPES.keys()),
            key=f"wood_{i}",
            index=list(WOOD_TYPES.keys()).index(st.session_state.strips[i]['wood_type'])
        )
        st.session_state.strips[i]['wood_type'] = wood_type
        st.session_state.strips[i]['color'] = WOOD_TYPES[wood_type]

    with col2:
        width = st.number_input(
            "Width (in)",
            min_value=0.25,
            max_value=float(board_width),
            value=float(st.session_state.strips[i]['width']),
            step=0.25,
            key=f"width_{i}"
        )
        st.session_state.strips[i]['width'] = width

    # Strip action buttons
    col_a, col_b, col_c, col_d = st.sidebar.columns(4)

    with col_a:
        if st.button("📋", key=f"duplicate_{i}", help="Duplicate this strip"):
            new_strip = copy.deepcopy(st.session_state.strips[i])
            st.session_state.strips.insert(i + 1, new_strip)
            st.rerun()

    with col_b:
        if i > 0 and st.button("⬆️", key=f"up_{i}", help="Move up"):
            st.session_state.strips[i], st.session_state.strips[i-1] = st.session_state.strips[i-1], st.session_state.strips[i]
            st.rerun()

    with col_c:
        if i < num_strips - 1 and st.button("⬇️", key=f"down_{i}", help="Move down"):
            st.session_state.strips[i], st.session_state.strips[i+1] = st.session_state.strips[i+1], st.session_state.strips[i]
            st.rerun()

    with col_d:
        if num_strips > 1 and st.button("🗑️", key=f"delete_{i}", help="Delete this strip"):
            st.session_state.strips.pop(i)
            st.rerun()

    st.sidebar.markdown("")

# Calculate total width
total_width = calculate_total_width(st.session_state.strips)
width_remaining = board_width - total_width

st.sidebar.markdown("---")
st.sidebar.subheader("Summary")
st.sidebar.metric("Total Width", format_dimension(total_width))
st.sidebar.metric("Remaining", format_dimension(width_remaining))
st.sidebar.metric("Board Size", f"{format_dimension(board_width)} × {format_dimension(board_length)}")

if width_remaining < 0:
    st.sidebar.error(f"⚠️ Board is {format_dimension(abs(width_remaining))} too wide!")
elif width_remaining > 0:
    st.sidebar.info(f"✓ {format_dimension(width_remaining)} of space remaining")
else:
    st.sidebar.success("✓ Perfect fit!")


# Save/Load Design
st.sidebar.markdown("---")
st.sidebar.subheader("Save/Load Design")

# Export design as JSON
import json

design_data = {
    'board_width': board_width,
    'board_length': board_length,
    'strips': st.session_state.strips
}

design_json = json.dumps(design_data, indent=2)
st.sidebar.download_button(
    label="💾 Save Design (JSON)",
    data=design_json,
    file_name="cutting_board_design.json",
    mime="application/json"
)

# Load design from JSON
uploaded_file = st.sidebar.file_uploader("📂 Load Design", type=['json'])
if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        st.session_state.strips = loaded_data.get('strips', st.session_state.strips)
        st.success("Design loaded successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error loading design: {e}")

# Main content area
tab1, tab2 = st.tabs(["📊 Preview", "📐 Schematic"])

with tab1:
    st.subheader("Board Preview")
    if total_width <= board_width:
        fig_preview = draw_board_preview(st.session_state.strips, board_width, board_length)
        st.pyplot(fig_preview)

        # Download preview
        buf = io.BytesIO()
        fig_preview.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download Preview (PNG)",
            data=buf,
            file_name="cutting_board_preview.png",
            mime="image/png"
        )
    else:
        st.error("Total width exceeds board width! Please adjust strip widths.")

with tab2:
    st.subheader("Dimensioned Schematic")
    if total_width <= board_width:
        fig_schematic = draw_schematic(st.session_state.strips, board_width, board_length)
        st.pyplot(fig_schematic)

        # Download schematic as PDF
        buf_pdf = io.BytesIO()
        fig_schematic.savefig(buf_pdf, format='pdf', bbox_inches='tight')
        buf_pdf.seek(0)
        st.download_button(
            label="📥 Download Schematic (PDF)",
            data=buf_pdf,
            file_name="cutting_board_schematic.pdf",
            mime="application/pdf"
        )

        # Download schematic as PNG
        buf_png = io.BytesIO()
        fig_schematic.savefig(buf_png, format='png', dpi=300, bbox_inches='tight')
        buf_png.seek(0)
        st.download_button(
            label="📥 Download Schematic (PNG)",
            data=buf_png,
            file_name="cutting_board_schematic.png",
            mime="image/png"
        )
    else:
        st.error("Total width exceeds board width! Please adjust strip widths.")

# Instructions
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    ### Instructions
    1. **Select measurement units** - choose inches, centimeters, or millimeters
    2. **Select board size** - choose from presets or use custom dimensions
    3. **Select number of strips** in the sidebar
    4. **Choose wood type** for each strip from the dropdown
    5. **Set width** for each strip
    6. **Use strip tools** for quick edits:
       - 📋 Duplicate a strip
       - ⬆️⬇️ Reorder strips
       - 🗑️ Delete a strip
       - ⚙️ Bulk Edit to change all strips at once
    7. **Monitor total width** - should not exceed your board width
    8. **Save your design** - download as JSON to reload later
    9. **View Preview** to see what your board will look like
    10. **View Schematic** to get dimensioned drawings for cutting
    11. **Download** the schematic as PDF or PNG to print

    ### Quick Actions
    - **Duplicate Strip**: Click 📋 to copy a strip's settings
    - **Reorder Strips**: Use ⬆️⬇️ to change strip positions
    - **Bulk Edit**: Use the ⚙️ Bulk Edit tool to change all strips at once
    - **Save/Load**: Save your design and reload it anytime
    - **Unit Toggle**: Switch between inches, cm, and mm instantly

    ### Tips
    - Use contrasting woods for visual appeal (light/dark alternating)
    - Common strip widths: 0.75", 1.0", 1.5", 2.0" (19mm, 25mm, 38mm, 51mm)
    - Popular combinations: Maple + Walnut, Cherry + Maple + Purpleheart
    - Remember to account for material loss from planing and sanding
    - Save your designs to build a library of patterns
    """)
