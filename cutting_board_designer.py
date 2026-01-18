import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import io
import copy
import numpy as np

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

def add_wood_grain_texture(ax, x, y, width, height, color, orientation='vertical'):
    """Add wood grain texture effect to a rectangle"""
    # Create grain lines
    num_lines = int(width * 5) if orientation == 'vertical' else int(height * 5)
    for _ in range(num_lines):
        if orientation == 'vertical':
            line_x = x + np.random.uniform(0, width)
            line_y_start = y + np.random.uniform(0, height * 0.2)
            line_y_end = y + np.random.uniform(height * 0.8, height)
            ax.plot([line_x, line_x], [line_y_start, line_y_end],
                   color='black', alpha=0.05, linewidth=0.5)
        else:
            line_y = y + np.random.uniform(0, height)
            line_x_start = x + np.random.uniform(0, width * 0.2)
            line_x_end = x + np.random.uniform(width * 0.8, width)
            ax.plot([line_x_start, line_x_end], [line_y, line_y],
                   color='black', alpha=0.05, linewidth=0.5)

def draw_board_preview(strips, board_width, board_length, show_grain=False, corner_radius=0):
    """Draw a visual preview of the cutting board"""
    fig, ax = plt.subplots(figsize=(12, 8))

    current_x = 0
    for i, strip in enumerate(strips):
        # Draw the wood strip with optional rounded corners
        if corner_radius > 0 and (i == 0 or i == len(strips) - 1):
            # Create rounded rectangle for edge strips
            from matplotlib.patches import FancyBboxPatch
            if i == 0:
                # Left edge - round left side
                rect = FancyBboxPatch(
                    (current_x, 0),
                    strip['width'],
                    board_length,
                    boxstyle=f"round,pad=0,rounding_size={corner_radius}",
                    linewidth=1,
                    edgecolor='black',
                    facecolor=strip['color']
                )
            else:
                # Right edge - round right side
                rect = FancyBboxPatch(
                    (current_x, 0),
                    strip['width'],
                    board_length,
                    boxstyle=f"round,pad=0,rounding_size={corner_radius}",
                    linewidth=1,
                    edgecolor='black',
                    facecolor=strip['color']
                )
        else:
            rect = patches.Rectangle(
                (current_x, 0),
                strip['width'],
                board_length,
                linewidth=1,
                edgecolor='black',
                facecolor=strip['color']
            )
        ax.add_patch(rect)

        # Add wood grain texture if enabled
        if show_grain:
            add_wood_grain_texture(ax, current_x, 0, strip['width'], board_length,
                                  strip['color'], orientation='vertical')

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
    ax.set_title('Cutting Board Preview - Edge Grain', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig

def draw_end_grain_preview(strips, board_width, board_length, show_grain=False):
    """Draw end grain pattern (rotated 90 degrees)"""
    fig, ax = plt.subplots(figsize=(12, 8))

    # For end grain, we show the strips as horizontal bands
    current_y = 0
    for i, strip in enumerate(strips):
        rect = patches.Rectangle(
            (0, current_y),
            board_length,  # Length becomes the horizontal dimension
            strip['width'],  # Width becomes the vertical dimension
            linewidth=1,
            edgecolor='black',
            facecolor=strip['color']
        )
        ax.add_patch(rect)

        # Add wood grain texture if enabled (horizontal for end grain)
        if show_grain:
            add_wood_grain_texture(ax, 0, current_y, board_length, strip['width'],
                                  strip['color'], orientation='horizontal')

        # Add wood type label
        ax.text(
            board_length/2,
            current_y + strip['width']/2,
            strip['wood_type'],
            ha='center',
            va='center',
            fontsize=10,
            rotation=0,
            fontweight='bold',
            color='white' if strip['wood_type'] in ['Walnut', 'Wenge', 'Purpleheart', 'Bloodwood'] else 'black'
        )

        current_y += strip['width']

    ax.set_xlim(0, board_length)
    ax.set_ylim(0, board_width)
    ax.set_aspect('equal')
    ax.set_xlabel('Length (inches)', fontsize=12)
    ax.set_ylabel('Width (inches)', fontsize=12)
    ax.set_title('Cutting Board Preview - End Grain', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig

def draw_3d_preview(strips, board_width, board_length, board_thickness=1.5):
    """Draw a 3D preview of the cutting board"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    current_x = 0
    for strip in strips:
        # Define the 6 faces of the rectangular strip
        x = current_x
        y = 0
        z = 0
        w = strip['width']
        l = board_length
        h = board_thickness

        # Vertices of the box
        vertices = [
            [x, y, z], [x+w, y, z], [x+w, y+l, z], [x, y+l, z],  # Bottom face
            [x, y, z+h], [x+w, y, z+h], [x+w, y+l, z+h], [x, y+l, z+h]  # Top face
        ]

        # Define the 6 faces using vertex indices
        faces = [
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # Right
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom
            [vertices[4], vertices[5], vertices[6], vertices[7]]   # Top
        ]

        # Create the 3D polygon collection
        face_collection = Poly3DCollection(faces, alpha=0.9, linewidths=1, edgecolors='black')
        face_collection.set_facecolor(strip['color'])
        ax.add_collection3d(face_collection)

        current_x += strip['width']

    # Set the aspect ratio and labels
    ax.set_xlim(0, board_width)
    ax.set_ylim(0, board_length)
    ax.set_zlim(0, board_thickness)
    ax.set_xlabel('Width (inches)', fontsize=10)
    ax.set_ylabel('Length (inches)', fontsize=10)
    ax.set_zlabel('Thickness (inches)', fontsize=10)
    ax.set_title(f'3D Preview - Thickness: {board_thickness}"', fontsize=14, fontweight='bold')

    # Set equal aspect ratio for realistic proportions
    ax.set_box_aspect([board_width, board_length, board_thickness])

    # Set viewing angle
    ax.view_init(elev=20, azim=45)

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
if 'design_name' not in st.session_state:
    st.session_state.design_name = "cutting_board_design"

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
        # Use the strip's unique ID to ensure stable widgets
        current_strip = st.session_state.strips[i]
        wood_type = st.selectbox(
            "Wood",
            options=list(WOOD_TYPES.keys()),
            key=f"wood_{i}_{id(current_strip)}",
            index=list(WOOD_TYPES.keys()).index(current_strip['wood_type'])
        )
        current_strip['wood_type'] = wood_type
        current_strip['color'] = WOOD_TYPES[wood_type]

    with col2:
        width = st.number_input(
            "Width (in)",
            min_value=0.25,
            max_value=float(board_width),
            value=float(current_strip['width']),
            step=0.25,
            key=f"width_{i}_{id(current_strip)}"
        )
        current_strip['width'] = width

    # Strip action buttons
    col_a, col_b, col_c, col_d = st.sidebar.columns(4)

    with col_a:
        if st.button("📋", key=f"duplicate_{i}_{id(current_strip)}", help="Duplicate this strip"):
            new_strip = copy.deepcopy(current_strip)
            st.session_state.strips.insert(i + 1, new_strip)
            st.rerun()

    with col_b:
        # Show button but disable if it's the first strip
        if st.button("⬆️", key=f"up_{i}_{id(current_strip)}", help="Move up", disabled=(i == 0)):
            # Swap with previous strip - create temp copy to avoid reference issues
            temp = st.session_state.strips[i-1]
            st.session_state.strips[i-1] = st.session_state.strips[i]
            st.session_state.strips[i] = temp
            st.rerun()

    with col_c:
        # Show button but disable if it's the last strip
        if st.button("⬇️", key=f"down_{i}_{id(current_strip)}", help="Move down", disabled=(i == num_strips - 1)):
            # Swap with next strip - create temp copy to avoid reference issues
            temp = st.session_state.strips[i+1]
            st.session_state.strips[i+1] = st.session_state.strips[i]
            st.session_state.strips[i] = temp
            st.rerun()

    with col_d:
        # Show button but disable if it's the only strip
        if st.button("🗑️", key=f"delete_{i}_{id(current_strip)}", help="Delete this strip", disabled=(num_strips == 1)):
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

# Design name input
design_name = st.sidebar.text_input(
    "Design Name",
    value=st.session_state.design_name,
    key="design_name_input",
    help="This name will be used as a prefix for all saved files"
)
st.session_state.design_name = design_name

# Export design as JSON
import json

design_data = {
    'design_name': design_name,
    'board_width': board_width,
    'board_length': board_length,
    'strips': st.session_state.strips
}

design_json = json.dumps(design_data, indent=2)
st.sidebar.download_button(
    label="💾 Save Design (JSON)",
    data=design_json,
    file_name=f"{design_name}.json",
    mime="application/json"
)

# Load design from JSON
uploaded_file = st.sidebar.file_uploader("📂 Load Design", type=['json'])
if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        st.session_state.strips = loaded_data.get('strips', st.session_state.strips)
        st.session_state.design_name = loaded_data.get('design_name', 'cutting_board_design')
        st.success("Design loaded successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error loading design: {e}")

# Visualization Options
st.subheader("Visualization Options")
col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)

with col_opt1:
    show_grain = st.checkbox("Show Wood Grain", value=False)

with col_opt2:
    corner_radius = st.slider("Corner Radius", min_value=0.0, max_value=2.0, value=0.0, step=0.1)

with col_opt3:
    board_thickness = st.slider("Board Thickness (in)", min_value=0.5, max_value=3.0, value=1.5, step=0.25)

with col_opt4:
    view_angle = st.selectbox("3D View Angle", ["Default (45°)", "Top (90°)", "Side (0°)", "Angled (30°)"])

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Edge Grain", "🔄 End Grain", "📦 3D View", "📐 Schematic"])

with tab1:
    st.subheader("Edge Grain Preview")
    if total_width <= board_width:
        fig_preview = draw_board_preview(st.session_state.strips, board_width, board_length,
                                         show_grain=show_grain, corner_radius=corner_radius)
        st.pyplot(fig_preview)

        # Download preview
        buf = io.BytesIO()
        fig_preview.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download Edge Grain Preview (PNG)",
            data=buf,
            file_name=f"{st.session_state.design_name}_edge_grain.png",
            mime="image/png"
        )
    else:
        st.error("Total width exceeds board width! Please adjust strip widths.")

with tab2:
    st.subheader("End Grain Preview")
    st.info("This shows how the board would look if cut and rotated 90° for an end grain pattern")
    if total_width <= board_width:
        fig_end_grain = draw_end_grain_preview(st.session_state.strips, board_width, board_length,
                                                show_grain=show_grain)
        st.pyplot(fig_end_grain)

        # Download end grain preview
        buf = io.BytesIO()
        fig_end_grain.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download End Grain Preview (PNG)",
            data=buf,
            file_name=f"{st.session_state.design_name}_end_grain.png",
            mime="image/png"
        )
    else:
        st.error("Total width exceeds board width! Please adjust strip widths.")

with tab3:
    st.subheader("3D Preview")
    if total_width <= board_width:
        fig_3d = draw_3d_preview(st.session_state.strips, board_width, board_length, board_thickness)

        # Adjust viewing angle based on selection
        ax_3d = fig_3d.axes[0]
        if view_angle == "Top (90°)":
            ax_3d.view_init(elev=90, azim=0)
        elif view_angle == "Side (0°)":
            ax_3d.view_init(elev=0, azim=0)
        elif view_angle == "Angled (30°)":
            ax_3d.view_init(elev=30, azim=60)
        else:  # Default
            ax_3d.view_init(elev=20, azim=45)

        st.pyplot(fig_3d)

        # Download 3D preview
        buf = io.BytesIO()
        fig_3d.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label="📥 Download 3D Preview (PNG)",
            data=buf,
            file_name=f"{st.session_state.design_name}_3d.png",
            mime="image/png"
        )
    else:
        st.error("Total width exceeds board width! Please adjust strip widths.")

with tab4:
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
            file_name=f"{st.session_state.design_name}_schematic.pdf",
            mime="application/pdf"
        )

        # Download schematic as PNG
        buf_png = io.BytesIO()
        fig_schematic.savefig(buf_png, format='png', dpi=300, bbox_inches='tight')
        buf_png.seek(0)
        st.download_button(
            label="📥 Download Schematic (PNG)",
            data=buf_png,
            file_name=f"{st.session_state.design_name}_schematic.png",
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
    7. **Adjust visualization options**:
       - Show Wood Grain for realistic texture
       - Corner Radius for rounded edges
       - Board Thickness for 3D view
       - 3D View Angle to see different perspectives
    8. **Monitor total width** - should not exceed your board width
    9. **Save your design** - download as JSON to reload later
    10. **Explore different views**:
        - 📊 Edge Grain - Traditional striped pattern
        - 🔄 End Grain - Rotated 90° checkerboard style
        - 📦 3D View - See thickness and depth
        - 📐 Schematic - Dimensioned cutting guide
    11. **Download** any view as PDF or PNG to print

    ### Visualization Features
    - **Edge Grain View**: Shows the board with vertical wood grain (traditional)
    - **End Grain View**: Shows how it would look rotated 90° for end grain patterns
    - **3D View**: Interactive 3D preview with adjustable thickness and viewing angles
    - **Wood Grain Texture**: Toggle realistic wood grain lines for better visualization
    - **Rounded Corners**: Preview boards with rounded edge profiles

    ### Quick Actions
    - **Duplicate Strip**: Click 📋 to copy a strip's settings
    - **Reorder Strips**: Use ⬆️⬇️ to change strip positions
    - **Bulk Edit**: Use the ⚙️ Bulk Edit tool to change all strips at once
    - **Save/Load**: Save your design and reload it anytime
    - **Unit Toggle**: Switch between inches, cm, and mm instantly
    - **View Angles**: Change 3D perspective from top, side, or angled views

    ### Tips
    - Use contrasting woods for visual appeal (light/dark alternating)
    - Common strip widths: 0.75", 1.0", 1.5", 2.0" (19mm, 25mm, 38mm, 51mm)
    - Popular combinations: Maple + Walnut, Cherry + Maple + Purpleheart
    - Standard thickness: 1.5" for cutting boards, 0.75" for serving boards
    - End grain boards are more durable but require more wood and labor
    - Enable wood grain texture to better visualize the final appearance
    - Remember to account for material loss from planing and sanding
    - Save your designs to build a library of patterns
    """)
