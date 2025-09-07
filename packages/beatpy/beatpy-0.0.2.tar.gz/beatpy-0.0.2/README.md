
### Sistema Spleeter
1. Descarga la canción dado un `youtube_id`.
2. Separa la canción en pistas `(.wav)` con los instrumentos: `Vocals / drums / bass / piano / other`.
3. Se convierte `.wav -> .png` para bajar el peso.
4. Se calcula el espectrograma para cada separación.
- Ejemplo: [Joy Division - Isolation](https://www.youtube.com/watch?v=5ViMA_qDKTU)
![Spectrogram - Song: [Joy Division - Isolation]](plots/spleeter_5ViMA_qDKTU.png)

## Quickstart (Backend)
- Crear entorno virtual.
```bash
cd /path/to/project
python3 -m venv env
```

- Activar el entorno.
```bash
source env/bin/activate
```

- Instalar dependencias.
```bash
pip install -r requirements.txt
```

- Run.
```bash
python3 main.py
```

## Audio Tool
- https://github.com/deezer/spleeter
- https://hub.docker.com/r/deezer/spleeter
- Funciona con `numpy<2` y `python3.10.x`.

- Instala python3.10.16 y crea el entorno.
```bash
sudo ./install_python_spleeter.sh
```

## Doc API
- `Con el backend ejecutando:` http://127.0.0.1:8000/redoc


## Youtube
- `https://github.com/yt-dlp/yt-dlp`


## Datasets
- https://www.kaggle.com/datasets/anubhavchhabra/drum-kit-sound-samples/data


## Probar
- https://github.com/sigsep/open-unmix-pytorch
- https://github.com/adefossez/demucs/tree/main
- https://github.com/adefossez/demucs/blob/main/environment-cuda.yml
- https://github.com/adefossez/demucs/blob/main/environment-cpu.yml
- https://github.com/sigsep/open-unmix-pytorch
