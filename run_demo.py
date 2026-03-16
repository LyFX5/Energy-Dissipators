import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import PatchCollection
from matplotlib.animation import FuncAnimation

from model import Grid


# utils
def segments_to_arrows(segments, style, color):
    patches = []
    for (x1, y1), (x2, y2) in segments:
        patches.append(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle=f"fancy,head_length=0.001,head_width=0.001,tail_width=0.003",
                hatch="*",
                # mutation_scale=1,
                # shrinkA=0,
                # shrinkB=0,
                color=color,
                linewidth=0.01,
            )
        )
    return patches


# init constants
STEPS_IN_SIMULATION = 1000
DURATION_OF_ANIMATION = STEPS_IN_SIMULATION / 10  # seconds
FRAMES_NUMBER = STEPS_IN_SIMULATION
DELAY_BETWEEN_FRAMES = 1000 * DURATION_OF_ANIMATION / FRAMES_NUMBER  # in milliseconds

FIGURE_SIZE = (16, 8)  # Wider figure to accommodate two subplots
SCENE_WIDTH = FIGURE_SIZE[1]
SCENE_HEIGHT = FIGURE_SIZE[0]
SCATTER_SIZE = 5

SIMULATION_NAME = "Mutating Self-organizing Energy Dissipator"


# init model
grid = Grid(m=8, n=8, s=0.01, init_energy=8 * 8)

rays = grid.rays
emits = grid.emitters()
colls = grid.collectors()


# build animation
lc_rays = LineCollection(rays, linewidths=1, colors="white")

"""
patches_emits = segments_to_arrows(emits, "->", "blue")
patches_colls = segments_to_arrows(colls, "]-", "red")

pc_emits = PatchCollection(patches_emits, match_original=True)
pc_colls = PatchCollection(patches_colls, match_original=True)
"""

lc_emits = LineCollection(emits, linewidths=1, colors="white")
lc_colls = LineCollection(colls, linewidths=1, colors="white")

fig = plt.figure(figsize=FIGURE_SIZE, facecolor="black")
ax = fig.add_subplot(1, 2, 1, frameon=False)  # Left subplot for main animation
ax2 = fig.add_subplot(
    1, 2, 2, facecolor="black"
)  # Right subplot for numerical readings
ax2.set_facecolor("black")

ax.add_collection(lc_rays)

ax.add_collection(lc_emits)
ax.add_collection(lc_colls)

ax.autoscale()
ax.set_aspect("equal", "box")


# scatter = ax.scatter([], [], s=40, color="yellow")

# Initialize data storage for tracking metrics
time_steps = []
total_energies = []
num_rays = []
num_alive_rotors = []
avg_energy = []

# Initialize right subplot
ax2.set_xlim(0, STEPS_IN_SIMULATION)
ax2.set_ylim(0, 100)
ax2.set_xlabel("Time Step", color="white", fontsize=10)
ax2.set_ylabel("Value", color="white", fontsize=10)
ax2.set_title("", color="white", fontsize=12, pad=10)
ax2.tick_params(colors="white", labelsize=8)
ax2.spines["bottom"].set_color("white")
ax2.spines["top"].set_color("white")
ax2.spines["right"].set_color("white")
ax2.spines["left"].set_color("white")
ax2.grid(True, alpha=0.3, color="gray")

# Create line plots for metrics
(line_total_energy,) = ax2.plot([], [], "y-", label="Total Energy", linewidth=1.5)
(line_num_rays,) = ax2.plot([], [], "c-", label="Active Rays", linewidth=1.5)
(line_avg_energy,) = ax2.plot([], [], "m-", label="Avg Energy", linewidth=1.5)
ax2.legend(
    loc="upper left",
    facecolor="black",
    edgecolor="white",
    labelcolor="white",
    fontsize=8,
)

# Text display for current readings (positioned to not overlap with legend)
text_display = ax2.text(
    0.05,
    0.65,
    "",
    transform=ax2.transAxes,
    fontsize=9,
    color="white",
    verticalalignment="top",
    family="monospace",
    bbox=dict(boxstyle="round", facecolor="black", alpha=0.7),
)

# Adjust layout to prevent overlap
plt.tight_layout()


def update_plot(frame):
    grid.step()
    rays = grid.rays
    emits = grid.emitters()
    colls = grid.collectors()

    lc_rays.set_segments(rays)

    """
    patches_emits = segments_to_arrows(emits, "->", "blue")
    patches_colls = segments_to_arrows(colls, "]-", "red")

    pc_emits.set_paths(patches_emits)
    pc_colls.set_paths(patches_colls)
    """

    lc_emits.set_segments(emits)
    lc_colls.set_segments(colls)

    # scatter.set_offsets(grid.scatter_of_rotors)

    # Calculate and store metrics
    total_energy = sum(rotor.E for rotor in grid.rotors if rotor.alive)
    num_active_rays = len(rays)
    alive_rotors = sum(1 for rotor in grid.rotors if rotor.alive)
    avg_energy_per_rotor = total_energy / alive_rotors if alive_rotors > 0 else 0

    time_steps.append(frame)
    total_energies.append(total_energy)
    num_rays.append(num_active_rays)
    num_alive_rotors.append(alive_rotors)
    avg_energy.append(avg_energy_per_rotor)

    # Update plots
    line_total_energy.set_data(time_steps, total_energies)
    line_num_rays.set_data(time_steps, num_rays)
    line_avg_energy.set_data(time_steps, avg_energy)

    # Auto-scale y-axis based on current data (update every 10 frames to reduce overhead)
    if total_energies and frame % 10 == 0:
        max_val = max(
            max(total_energies),
            max(num_rays) if num_rays else 0,
            max(avg_energy) if avg_energy else 0,
        )
        if max_val > 0:
            ax2.set_ylim(0, max(max_val * 1.2, 10))

    # Update x-axis to show current window (last 1000 steps or all if less)
    if len(time_steps) > 1000:
        ax2.set_xlim(max(0, frame - 1000), frame + 100)
    else:
        ax2.set_xlim(0, max(frame + 100, STEPS_IN_SIMULATION))

    # Update text display with current readings
    text_info = f"Step: {frame}/{STEPS_IN_SIMULATION}\n"
    text_info += f"Total Energy: {total_energy:.3f}\n"
    text_info += f"Active Rays: {num_active_rays}\n"
    text_info += f"Alive Rotors: {alive_rotors}/{grid.rotors_number}\n"
    text_info += f"Avg Energy: {avg_energy_per_rotor:.3f}\n"
    # Show energy matrix in compact form
    energy_matrix = grid.energies()
    text_info += f"Energy Range: [{energy_matrix.min():.2f}, {energy_matrix.max():.2f}]"
    text_display.set_text(text_info)

    return (
        lc_rays,
        lc_emits,
        lc_colls,
        line_total_energy,
        line_num_rays,
        line_avg_energy,
        text_display,
    )


animation = FuncAnimation(
    fig=fig,
    func=update_plot,
    frames=FRAMES_NUMBER,
    blit=True,
    interval=DELAY_BETWEEN_FRAMES,
    repeat=False,
)

fig.show()

plt.show(block=True)
