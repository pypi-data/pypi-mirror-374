
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from collections import namedtuple
import numpy as np

def convert_fig_to_html_img(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # style = "width: 80%; height: auto; @media only screen and (max-width: 390px) { img {width: 100px;} }"
    # return f"<img src='data:image/png;base64,{data}' style={style}>"
    img = f'<img src="data:image/png;base64,{data}" style="width: clamp(300px, 75vw, 1000px); height: auto;">'
    return img


def module_plot(test_name: str, pos_0, pos_1, pos_2, pos_3, vmin=None, vmax=None) -> Figure:
    fig, axs = plt.subplots(2, 2, figsize=(20, 16), gridspec_kw={'wspace': 0.2, 'hspace': 0.2})

    Position = namedtuple("Position", ["pos", "matrix", "invert_x", "invert_y", "ax"])
    positions = [
        Position(pos='3', matrix=pos_3, invert_x=True,  invert_y=True,  ax=axs[0, 0]),
        Position(pos='1', matrix=pos_1, invert_x=True,  invert_y=True,  ax=axs[0, 1]),
        Position(pos='2', matrix=pos_2, invert_x=False, invert_y=False, ax=axs[1, 0]),
        Position(pos='0', matrix=pos_0, invert_x=False, invert_y=False, ax=axs[1, 1]),
    ]
    images = []
    for pos, matrix, invert_x, invert_y, ax in positions:
        if matrix is not None:
            matrix = np.array(matrix)
            im = ax.matshow(matrix, vmin=vmin, vmax=vmax)
            images.append(im)
            for row in range(16):
                for col in range(16):
                    #       x,   y
                    ax.text(col, row, int(matrix[row,col]), ha="center", va="center", color="w", fontsize=10)
            
            ax.set_xlabel('Column')
            ax.set_ylabel('Row')
            if invert_x:
                ax.invert_xaxis()
            if invert_y:
                ax.invert_yaxis()

            ax.minorticks_off()
            ax.xaxis.set_ticks_position('bottom')
            ax.xaxis.set_label_position('bottom')
            ax.text(0.0, 1.01, pos, 
                    ha="left", 
                    va="bottom", 
                    transform=ax.transAxes, 
                    fontsize=18, 
                    fontweight = "bold")
            ax.text(0.1, 1.01, 
                    fr"$<\mu>$ = {np.round(np.mean(matrix), 2)}, $\sigma$ = {np.round(np.std(matrix), 2)} ", 
                    ha="left", 
                    va="bottom", 
                    transform=ax.transAxes, 
                    fontsize=18)

        else:
            # Handle the case where matrix is None
            ax.set_title(f'{pos} (No Data)', fontsize=18, fontweight='bold')
            ax.text(0.5, 0.5, 'No Data Available', ha='center', va='center', 
                    transform=ax.transAxes, fontsize=16, color='gray')
            ax.set_xlim(0, 15)
            ax.set_ylim(0, 15)
            ax.set_xticks([])
            ax.set_yticks([])
    
    cbar = fig.colorbar(images[0], ax=axs) # first position
    cbar.set_label(test_name.capitalize(), fontsize = 34)

    fig.text(0.08, 0.92, "CMS", fontsize=42, ha="left", va="bottom", fontweight='bold')
    fig.text(0.155, 0.924, "ETL Preliminary", fontsize=34, ha="left", va="bottom", style='italic')
    
    # Add black triangle to top right corner as overlay (after layout is finalized)
    offset = 0.1
    size = 0.05
    # Top-right corner, rotated 90 degrees (counter-clockwise)
    triangle_x = [0.95  - offset, 0.95  - offset, 0.95  - offset - size]
    triangle_y = [0.95        , 0.95  - size,   0.95       ]
    
    triangle = Polygon(list(zip(triangle_x, triangle_y)), 
                        closed=True, 
                        transform=fig.transFigure, 
                        facecolor='black', 
                        edgecolor='black',
                        zorder=1000,
                        clip_on=False)
    fig.add_artist(triangle)
    fig.suptitle(f"Orientation: sensor side up, you are looking on the sensors", 
                    fontsize=18, fontweight='bold', y=0.04)
    return fig