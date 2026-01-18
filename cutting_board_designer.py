import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import io

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

# Board dimensions
BOARD_LENGTH = 18  # inches
BOARD_WIDTH = 12   # inches
GLUE_LINE_LOSS = 0.0625  # 1/16 inch per glue joint

def calculate_total_width(strips):
    """Calculate total width including glue line losses"""
    total = sum(strip['width'] for strip in strips)
    # Add glue line losses (n-1 glue lines for n strips)
    if len(strips) > 1:
        total += (len(strips) - 1) * GLUE_LINE_LOSS
    return total

def draw_board_preview(strips):
    """Draw a visual preview of the cutting board"""
    fig, ax = plt.subplots(figsize=(12, 8))

    current_x = 0
    for i, strip in enumerate(strips):
        # Draw the wood strip
        rect = patches.Rectangle(
            (current_x, 0),
            strip['width'],
            BOARD_LENGTH,
            linewidth=1,
            edgecolor='black',
            facecolor=strip['color']
        )
        ax.add_patch(rect)

        # Add wood type label
        ax.text(
            current_x + strip['width']/2,
            BOARD_LENGTH/2,
            strip['wood_type'],
            ha='center',
            va='center',
            fontsize=10,
            rotation=90,
            fontweight='bold',
            color='white' if strip['wood_type'] in ['Walnut', 'Wenge', 'Purpleheart', 'Bloodwood'] else 'black'
        )

        current_x += strip['width']
        # Add glue line
        if i < len(strips) - 1:
            current_x += GLUE_LINE_LOSS

    ax.set_xlim(0, BOARD_WIDTH)
    ax.set_ylim(0, BOARD_LENGTH)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (inches)', fontsize=12)
    ax.set_ylabel('Length (inches)', fontsize=12)
    ax.set_title('Cutting Board Preview', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    return fig

def draw_schematic(strips):
    """Draw a dimensioned schematic for cutting"""
    fig, ax = plt.subplots(figsize=(14, 10))

    current_x = 0
    for i, strip in enumerate(strips):
        # Draw the strip outline
        rect = patches.Rectangle(
            (current_x, 0),
            strip['width'],
            BOARD_LENGTH,
            linewidth=2,
            edgecolor='black',
            facecolor=strip['color'],
            alpha=0.7
        )
        ax.add_patch(rect)

        # Add wood type and width label inside strip
        ax.text(
            current_x + strip['width']/2,
            BOARD_LENGTH/2,
            f"{strip['wood_type']}\n{strip['width']}\"",
            ha='center',
            va='center',
            fontsize=11,
            fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        # Add dimension line above
        dimension_y = BOARD_LENGTH + 1
        ax.plot([current_x, current_x + strip['width']],
                [dimension_y, dimension_y], 'k-', linewidth=1.5)
        ax.plot([current_x, current_x],
                [dimension_y - 0.2, dimension_y + 0.2], 'k-', linewidth=1.5)
        ax.plot([current_x + strip['width'], current_x + strip['width']],
                [dimension_y - 0.2, dimension_y + 0.2], 'k-', linewidth=1.5)
        ax.text(current_x + strip['width']/2, dimension_y + 0.5,
                f'{strip["width"]}"', ha='center', fontsize=10, fontweight='bold')

        current_x += strip['width']

        # Show glue line
        if i < len(strips) - 1:
            ax.plot([current_x, current_x], [0, BOARD_LENGTH],
                   'r--', linewidth=1, alpha=0.5, label='Glue line' if i == 0 else '')
            current_x += GLUE_LINE_LOSS

    # Add overall dimensions
    total_width = calculate_total_width(strips)

    # Right side dimension line
    ax.plot([total_width + 1, total_width + 1], [0, BOARD_LENGTH], 'k-', linewidth=2)
    ax.plot([total_width + 0.8, total_width + 1.2], [0, 0], 'k-', linewidth=2)
    ax.plot([total_width + 0.8, total_width + 1.2], [BOARD_LENGTH, BOARD_LENGTH], 'k-', linewidth=2)
    ax.text(total_width + 1.5, BOARD_LENGTH/2, f'{BOARD_LENGTH}"',
            ha='left', va='center', fontsize=12, fontweight='bold', rotation=270)

    # Bottom dimension line
    ax.plot([0, total_width], [-1, -1], 'k-', linewidth=2)
    ax.plot([0, 0], [-1.2, -0.8], 'k-', linewidth=2)
    ax.plot([total_width, total_width], [-1.2, -0.8], 'k-', linewidth=2)
    ax.text(total_width/2, -1.5, f'Total: {total_width:.3f}"',
            ha='center', fontsize=12, fontweight='bold')

    ax.set_xlim(-2, BOARD_WIDTH + 3)
    ax.set_ylim(-3, BOARD_LENGTH + 3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Cutting Board Schematic with Dimensions', fontsize=16, fontweight='bold', pad=20)

    # Add cut list
    cut_list_y = -2.5
    ax.text(-1.5, cut_list_y, 'CUT LIST:', fontsize=11, fontweight='bold')
    for i, strip in enumerate(strips):
        ax.text(-1.5, cut_list_y - 0.5 * (i + 1),
                f'{i+1}. {strip["wood_type"]}: {strip["width"]}" × {BOARD_LENGTH}"',
                fontsize=9)

    return fig

# Streamlit App
st.set_page_config(page_title="Cutting Board Designer", layout="wide")
st.title("🪵 Wood Cutting Board Designer")
st.markdown("Design your custom cutting board with different wood types and widths!")

# Sidebar for controls
st.sidebar.header("Design Controls")

# Initialize session state for strips
if 'strips' not in st.session_state:
    st.session_state.strips = [
        {'wood_type': 'Maple', 'width': 2.0, 'color': WOOD_TYPES['Maple']},
        {'wood_type': 'Walnut', 'width': 1.5, 'color': WOOD_TYPES['Walnut']},
        {'wood_type': 'Maple', 'width': 2.0, 'color': WOOD_TYPES['Maple']},
    ]

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
            max_value=12.0,
            value=float(st.session_state.strips[i]['width']),
            step=0.25,
            key=f"width_{i}"
        )
        st.session_state.strips[i]['width'] = width

    st.sidebar.markdown("")

# Calculate total width
total_width = calculate_total_width(st.session_state.strips)
width_remaining = BOARD_WIDTH - total_width

st.sidebar.markdown("---")
st.sidebar.subheader("Summary")
st.sidebar.metric("Total Width", f"{total_width:.3f}\"")
st.sidebar.metric("Remaining", f"{width_remaining:.3f}\"")

if width_remaining < 0:
    st.sidebar.error(f"⚠️ Board is {abs(width_remaining):.3f}\" too wide!")
elif width_remaining > 0:
    st.sidebar.info(f"✓ {width_remaining:.3f}\" of space remaining")
else:
    st.sidebar.success("✓ Perfect fit!")

st.sidebar.markdown(f"*Includes {len(st.session_state.strips) - 1} glue lines @ {GLUE_LINE_LOSS}\" each*")

# Main content area
tab1, tab2 = st.tabs(["📊 Preview", "📐 Schematic"])

with tab1:
    st.subheader("Board Preview")
    if total_width <= BOARD_WIDTH:
        fig_preview = draw_board_preview(st.session_state.strips)
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
    if total_width <= BOARD_WIDTH:
        fig_schematic = draw_schematic(st.session_state.strips)
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
    1. **Select number of strips** in the sidebar
    2. **Choose wood type** for each strip from the dropdown
    3. **Set width** for each strip (in inches)
    4. **Monitor total width** - should not exceed 12 inches
    5. **View Preview** to see what your board will look like
    6. **View Schematic** to get dimensioned drawings for cutting
    7. **Download** the schematic as PDF or PNG to print

    ### Tips
    - The app accounts for glue line losses (1/16" per joint)
    - Use contrasting woods for visual appeal (light/dark alternating)
    - Common strip widths: 0.75", 1.0", 1.5", 2.0"
    - Popular combinations: Maple + Walnut, Cherry + Maple + Purpleheart
    """)
