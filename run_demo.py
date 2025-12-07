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
STEPS_IN_SIMULATION = 5000
DURATION_OF_ANIMATION = STEPS_IN_SIMULATION / 10  # seconds
FRAMES_NUMBER = STEPS_IN_SIMULATION
DELAY_BETWEEN_FRAMES = 1000 * DURATION_OF_ANIMATION / FRAMES_NUMBER  # in milliseconds

FIGURE_SIZE = (8, 8)
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

fig = plt.figure(figsize=(8, 8), facecolor="black")
ax = plt.subplot(frameon=False)

ax.add_collection(lc_rays)

ax.add_collection(lc_emits)
ax.add_collection(lc_colls)

ax.autoscale()
ax.set_aspect("equal", "box")


# scatter = ax.scatter([], [], s=40, color="yellow")


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

    return lc_rays, lc_emits, lc_colls


animation = FuncAnimation(
    fig=fig,
    func=update_plot,
    frames=FRAMES_NUMBER,
    blit=True,
    interval=DELAY_BETWEEN_FRAMES,
    repeat=False,
)

fig.show()
