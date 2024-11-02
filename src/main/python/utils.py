import os

import matplotlib.lines as mlines
import matplotlib.collections as mcollections
import matplotlib.patches as mpatches

from PyQt5.QtWidgets import (QMessageBox)

def copy_axes(old_ax, new_ax):
    # Copy lines
    for line in old_ax.get_lines():
        new_line = mlines.Line2D(
            line.get_xdata(),
            line.get_ydata(),
            label=line.get_label(),
            color=line.get_color(),
            linestyle=line.get_linestyle(),
            linewidth=line.get_linewidth(),
            marker=line.get_marker(),
            markerfacecolor=line.get_markerfacecolor(),
            markersize=line.get_markersize(),
        )
        new_ax.add_line(new_line)

    # Copy collections (e.g., scatter plots, quad meshes)
    for collection in old_ax.collections:
        if isinstance(collection, mcollections.QuadMesh):
            new_collection = mcollections.QuadMesh(
                collection.get_coordinates(),
                antialiased=collection.get_antialiased(),
                facecolor=collection.get_facecolor(),
                edgecolor=collection.get_edgecolor(),
                linewidths=collection.get_linewidths()
            )
            new_ax.add_collection(new_collection)

    # Copy patches (e.g., rectangles, circles, polygons)
    for patch in old_ax.patches:
        if isinstance(patch, mpatches.Rectangle):
            new_patch = mpatches.Rectangle(
                patch.get_xy(),
                patch.get_width(),
                patch.get_height(),
                angle=patch.get_angle(),
                facecolor=patch.get_facecolor(),
                edgecolor=patch.get_edgecolor(),
                linewidth=patch.get_linewidth()
            )
        elif isinstance(patch, mpatches.Polygon):
            new_patch = mpatches.Polygon(
                patch.get_xy(),
                closed=True,
                facecolor=patch.get_facecolor(),
                edgecolor=patch.get_edgecolor(),
                linewidth=patch.get_linewidth()
            )
        
        new_ax.add_patch(new_patch)

    # Copy titles, labels, limits, and legend
    new_ax.set_title(old_ax.get_title())
    new_ax.set_xlabel(old_ax.get_xlabel())
    new_ax.set_ylabel(old_ax.get_ylabel())
    new_ax.set_xlim(old_ax.get_xlim())
    new_ax.set_ylim(old_ax.get_ylim())

    # Copy over the legend if it exists
    if old_ax.get_legend():
        new_ax.legend()

def flatten_2d(l):
    return [e for row in l for e in row]

def show_message(message, msg_type='error'):
    msg = QMessageBox()
    
    if msg_type == 'error':
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
    elif msg_type == 'success':
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
    
    msg.setText(message)
    msg.exec_()

def get_file_extension(file_name):
    _, extension = os.path.splitext(file_name)
    return extension[1:]

def has_second_channel(audio):
    if audio.ndim == 1:
        return False
    elif audio.ndim == 2 and audio.shape[1] == 2:
        return True
    
def process_audio(audio):
    if audio.ndim == 1:
        # Type 1 audio (shape: (n,))
        return audio
    elif audio.ndim == 2 and audio.shape[1] == 2:
        # Type 2 audio (shape: (n, 2))
        # Take only the first channel
        return audio[:, 0]
    else:
        # Invalid audio format
        raise ValueError("Invalid audio format")