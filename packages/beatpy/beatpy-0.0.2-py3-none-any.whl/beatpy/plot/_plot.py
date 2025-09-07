from typing import List, cast

import librosa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from beatpy.audio import Audio
from beatpy.const import path_extracted, COLOR_BACKGROUND, COLOR_TEXT

COLOR_BACKGROUND = "#212167"
COLOR_TEXT = "#9696f6"


def plot_wave(
        *,
        ax: Axes,
        y: np.ndarray,
        sr: float,
        title: str = "Wave"
) -> None:
    librosa.display.waveshow(y, ax=ax, sr=sr)
    ax.set_title(title)

def plot_spectrogram(
    *,
    ax: Axes,
    sr: float,
    S_db: np.ndarray,
    title: str = "Spectrogram",
    ylabel: str = "Frequency [Hz]",
    cmap: str = "magma",
    vmin: float = None,
    vmax: float = None,
    color_xaxis: str = "black"
) -> None:
    """Plotea un espectrograma con escala logarítmica de frecuencia en el eje especificado, 
    usando una escala de color definida por vmin y vmax."""
    img = librosa.display.specshow(
        S_db, ax=ax, sr=sr,
        x_axis="time", y_axis="log",
        cmap=cmap, vmin=vmin, vmax=vmax
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)

    # Cambiar el color del texto del eje horizontal (Time)
    ax.xaxis.label.set_color(color_xaxis)  # Color claro para el eje X (Tiempo)

    # Agregar barra de color con valores en dB
    plt.colorbar(img, ax=ax, format="%+2.0f dB")

def plot_spectrograms_by_youtube(*, youtube_id: str) -> None:
    youtube = Youtube(youtube_id=youtube_id, path_root=path_extracted)
    
    # Se levantan todos los audios.
    beats: List[Audio] = [Audio(path_audio=p) for p in youtube.paths.iter_spleeter_output()]
    if len(beats) != 6:
        raise ValueError("TODO: Manejar bien el plot.")
    
    # Se calcula el valor minimo y máximo de dB en los distintos audios.
    mins_dB, maxs_dB = [], []
    for beat in beats:
        mins_dB.append(beat.S_dD.min())
        maxs_dB.append(beat.S_dD.max())
    vmin, vmax = min(mins_dB), max(maxs_dB)

    # Crear figura y ejes
    fig, axes = plt.subplots(2, 3, figsize=(30, 10))

    # Cambiar el color de fondo de la figura
    fig.patch.set_facecolor(COLOR_BACKGROUND)

    k = 0
    for i in range(len(axes)):
        for j in range(len(axes[0])):
            beat = beats[k]
            k += 1
            ax = cast(Axes, axes[i, j])

            # Se grafican los espectrogramas.
            beat.plot_spectrogram(ax=ax, vmin=vmin, vmax=vmax, color_xaxis=COLOR_TEXT)
            ax.set_title(f"{beat.name}", color=COLOR_TEXT)  # Títulos en color claro
            ax.set_ylabel('Frequency [Hz]', color=COLOR_TEXT)      # Etiqueta de Y

            # Cambiar color a la barra, y fondo de los ejes.
            # Cambiar color de fondo de cada eje
            ax.set_facecolor(COLOR_BACKGROUND)
            ax.tick_params(axis='both', colors=COLOR_TEXT)
            cbar = ax.collections[0].colorbar
            cbar.ax.tick_params(labelcolor=COLOR_TEXT)

    # Ajustar espacio para el título
    plt.subplots_adjust(top=0.92)
    fig.suptitle('Spectrogram - Song: [Joy Division - Isolation]', fontsize=16, color=COLOR_TEXT)  # Título en color claro

    path_plots = youtube.paths.folder / "plots"
    path_plots.mkdir(exist_ok=True)
    
    # Guardar la figura
    fig.savefig(path_plots / f"spleeter_{youtube_id}.png", bbox_inches='tight')
    del fig
