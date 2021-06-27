"""
Módulo para obtener iconos en formato .svg desde el directorio static de la app.
"""
import datetime
import warnings
import re
from pathlib import Path
from django.conf import settings
from django.utils.html import format_html



ICON_DIR = Path(__file__).resolve().parent.parent / 'static/icons'
STATIC_URL = settings.STATIC_URL
DATA = {} # Todos los íconos cargados aquí al iniciar el servidor.
DEFAULT = "DEFAULT"
RAISE_EXCEPTION = "RAISE_EXCEPTION"
DEFAULT_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
    'fill="currentColor" class="bi bi-circle-fill" viewBox="0 0 16 16">'
    '<circle cx="8" cy="8" r="8"/></svg>')


class IconError(Exception):
    pass


def populate():
    """Carga los íconos en la variable 'DATA'."""
    for path in ICON_DIR.iterdir():
        try:
            DATA[path.name] = {
                "path": path, 
                "url": STATIC_URL + "icons/" + path.name,
                "data": open(path, "r").read(),
            }
        except (IOError) as e:
            warnings.warn(e)

def get_url(name: str, override: bool=True) -> str:
    """
    Obtiene la url definitiva para el archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.
    """
    if not ".svg" in name:
        name += ".svg"
    return get_data(name, override=override)["url"]
    
def get_data(name: str, override: bool=True) -> str:
    """
    Obtiene el contenido del archivo SVG que coincida con el nombre.

    Si override es False, se lanzará una excepción en caso de no encontrar el 
    archivo con el nombre indicado.
    """
    if "/" in name:
        name = name.split("/")[-1]
    if not ".svg" in name:
        name += ".svg"

    override = bool(override)
    if override == False:
        #return open(ICON_DIR / name, "r").read() # Lanzará una excepción...
        return DATA[name]
    return DATA.get(name, {"url": "", "path": "", "data": ""})

def svg(name: str, size: str=None, fill: str=None, id: str=None, 
    on_error=RAISE_EXCEPTION) -> dict:
    """
    Retorna un diccionario con el contenido del archivo SVG con el nombre 
    indicado, y resto de parámetros pasados.

    Nota: retorna el contenido, no la ruta, en un archivo .SVG.

    Parameters:
        filename (str): Nombre del archivo o ruta. Si se indica el nombre del 
        archivo, buscará dentro de los directorios static/img/* predeterminados.
        Si se indica una ruta, tendrá que empezar por /static/*

        size (str): El size se pasará a las opciones CSS (width, height) tal y 
        como se especifiquen, por lo cual es conveniente indicar su tipo de 
        medida (ejemplos '32px', '2rem', etc.).

        fill (str): CSS color que se pasará a la opción fill para pintar la 
        imagen.
    """
    fill = fill or 'currentColor'

    try:
        svg = get_data(name, override=False)["data"]
    except (BaseException) as e:
        if on_error == RAISE_EXCEPTION:
            raise IconError(e) from e
        if on_error == DEFAULT:
            svg = DEFAULT_SVG
        else:
            svg = ""
        return {"svg": svg, "size": size, "fill": fill, "name": name, "id": id}

    # Eliminamos los saltos de línea y espacios extras.
    svg = " ".join(svg.replace("\n", " ").split())

    # if not id:
    #     id = f"id-svg-{name}-fill-{fill}-size-{size}-{datetime.datetime.today()}"
    #     id = text.Text.FormatCodename(id)

    if size in ("", "none", "null", "auto"):
        if (" width=" in svg):
            svg = re.sub(r'\swidth=(["\']).*?["\']\s', '', svg, count=1)
        
        if (" height=" in svg):
            svg = re.sub(r'\sheight=(["\']).*?["\']\s', '', svg, count=1)
    elif size:
        if (not " width=" in svg):
            svg = re.sub(r'<svg\s', f'<svg width="{size}" ', svg, count=1)
        else:
            svg = re.sub(r'\swidth=(["\']).*?["\']\s', f' width="{size}" ', 
            svg, count=1)
    
        if (not " height=" in svg):
            svg = re.sub(r'<svg\s', f'<svg height="{size}" ', svg, count=1)
        else:
            svg = re.sub(r'\sheight=(["\']).*?["\']\s', f' height="{size}" ', 
            svg, count=1)
    if (not " fill=" in svg):
        svg = re.sub(r'<svg\s', f'<svg fill="{fill}" ', svg, count=1)
    else:
        svg = re.sub(r'\sfill=(["\']).*?["\']\s', f' fill="{fill}" ', svg, 
        count=1)
    return {"svg": svg, "size": size, "fill": fill, "name": name, "id": id}


# Al iniciar el servidor, se cargarán los iconos en la variable DATA.
populate()