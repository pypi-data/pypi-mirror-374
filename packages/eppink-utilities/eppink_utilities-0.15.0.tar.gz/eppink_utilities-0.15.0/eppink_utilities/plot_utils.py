import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import os

def rangeplot(data, labels, name, color_scheme="Set3", path=""):
    """
    Generates a high-resolution range plot and saves it as a PNG file.

    Parameters:
    - data: list of numerical values representing the pie chart slices.
    - labels: list of category names corresponding to each slice.
    - name: the name used to save the file (no extension, will be saved as '.png').
    - color_scheme: string representing the Matplotlib colormap to use (default is "Set3").
      Available color schemes include:
      - "Blues": Light to dark blue.
      - "Oranges": Light to dark orange.
      - "Greens": Light to dark green.
      - "Purples": Light to dark purple.
      - "coolwarm": Blue to red (diverging).
      - "PiYG": Pink to green (diverging).
      - "BrBG": Brown to blue-green (diverging).
      - "tab10": Ten distinct, vibrant colors (ideal for categorical data).
      - "tab20": Twenty distinct, vibrant colors (ideal for larger datasets).
      - "Set3": 12 pastel-style colors (ideal for presentations).
      - "Pastel1" / "Pastel2": Soft and light colors (ideal for subtle distinctions).
      - "Dark2": Darker, high-contrast colors (ideal for better visibility).
    - path: the directory where the plot image will be saved (default is the current directory).
    """
    if len(data) != len(labels):
        raise ValueError("Length of labels must match length of data")

    plt.style.use('_mpl-gallery-nogrid')

    # Calculate percentages
    total = sum(data)
    percentages = [(value / total) * 100 for value in data]
    labeled_percentages = [f"{label} ({pct:.1f}%)" for label, pct in zip(labels, percentages)]

    # Prepare color scheme based on the selected colormap
    # Using 'tab20' here to avoid color repetition
    colors = plt.get_cmap(color_scheme)(np.linspace(0.2, 0.8, len(data)))

    # Create plot
    fig, ax = plt.subplots()
    wedges, _ = ax.pie(data, colors=colors, radius=3, center=(4, 4),
                       wedgeprops={"linewidth": 1, "edgecolor": "black"}, frame=False)

    # Add legend on the right
    ax.legend(wedges, labeled_percentages,
              title="Categories",
              loc="center left",
              bbox_to_anchor=(1, 0.5))

    # Set limits but remove ticks
    ax.set(xlim=(0, 8), ylim=(0, 8))
    ax.set_xticks([])
    ax.set_yticks([])

    # Set default path to "Figs" if not provided
    if not path:
        path = os.path.join(".", "Figs")

    # Ensure the directory exists
    os.makedirs(path, exist_ok=True)

    # Sanitize filename
    safe_name = name.replace(" ", "_")
    filename = f"{safe_name}.png"
    full_path = os.path.join(path, filename)

    # Save the figure with higher resolution (e.g., dpi=300)
    plt.savefig(full_path, bbox_inches='tight', dpi=300)
    plt.close()

def piechart(data, labels, name, color_scheme="Set3", path="", ylabel=""):
    """
    Generates a high-resolution bar chart and saves it as a PNG file.

    Parameters:
    - data: list of lists, where each inner list contains the values (y-values) for a specific category on the x-axis.
    - labels: list of category names corresponding to each bar on the x-axis.
    - name: the name used to save the file (no extension, will be saved as '.png').
    - color_scheme: string representing the Matplotlib colormap to use (default is "Set3").
      Available color schemes include:
      - "Blues": Light to dark blue.
      - "Oranges": Light to dark orange.
      - "Greens": Light to dark green.
      - "Purples": Light to dark purple.
      - "coolwarm": Blue to red (diverging).
      - "PiYG": Pink to green (diverging).
      - "BrBG": Brown to blue-green (diverging).
      - "tab10": Ten distinct, vibrant colors (ideal for categorical data).
      - "tab20": Twenty distinct, vibrant colors (ideal for larger datasets).
      - "Set3": 12 pastel-style colors (ideal for presentations).
      - "Pastel1" / "Pastel2": Soft and light colors (ideal for subtle distinctions).
      - "Dark2": Darker, high-contrast colors (ideal for better visibility).
    - path: the directory where the plot image will be saved (default is the current directory).
    - ylabel: label for the y-axis (optional).
    """

    # Compute min and max per category
    mins = [min(d) for d in data]
    maxs = [max(d) for d in data]
    
    x = range(len(labels))
    
    # Set color scheme
    cmap = plt.get_cmap(color_scheme)
    colors = [cmap(i) for i in range(len(labels))]

    fig, ax = plt.subplots()

    bar_width = 0.2

    for i, (low, high) in enumerate(zip(mins, maxs)):
        height = high - low
        rect = Rectangle(
            (i - bar_width / 2, low),
            width=bar_width,
            height=height,
            facecolor=colors[i],
            edgecolor='black',
            linewidth=1,
            zorder=2
        )
        ax.add_patch(rect)

    # Add y-axis grid lines every 0.5 without adding extra ticks
    y_min = 0
    y_max = max(maxs) * 1.1
    grid_lines = np.arange(y_min, y_max, 0.5)
    for y in grid_lines:
        ax.axhline(y, color='gray', linestyle='--', linewidth=0.5, alpha=0.5, zorder=1)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.set_ylabel(ylabel)
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylim(y_min, y_max)
    plt.tight_layout()

    # Set default path to "Figs" if not provided
    if not path:
        path = os.path.join(".", "Figs")

    # Ensure the directory exists
    os.makedirs(path, exist_ok=True)

    # Sanitize filename
    safe_name = name.replace(" ", "_")
    filename = f"{safe_name}.png"
    full_path = os.path.join(path, filename)

    # Save the figure with higher resolution (e.g., dpi=300)
    plt.savefig(full_path, bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    # test rangeplot
    labels = ["Coal fired","Natural gas","Oil shale","Biomass","Waste-to-energy"]
    name = "CO2 flue gas concentration per power plant"
    color_scheme = "Dark2"
    data = [
        [15.7, 16.5, 12, 14.2, 14, 16],
        [3.6, 11.2, 6.6, 14.1, 9.9, 11.3, 4.2],
        [12.7],
        [2,16,14],
        [8, 11.3]
    ]
    ylabel = "Flue gas CO2 concentration (mass%)"
    path = "Figs"  # Set to "" if you just want to display the plot

    rangeplot(data, labels, name, color_scheme, path, ylabel)

    # test pychart
    data = [10.1, 3.2, 0.5, 9.1, 7.8, 3.1]
    labels = ["Power plants (coal)", "Power plants (gas)", "Power plants (oil)",  "Industry", "Transport", "Buildings"]
    name = "CO2 emission per industry"
    color_scheme = "Dark2"  # Selected color scheme to avoid color repetition
    piechart(data, labels, name, color_scheme)

