"""
Conjunto de utilidades.
"""
import copy
import warnings
import sys
from io import BytesIO
import datetime
from decimal import Decimal
import warnings
import functools
try:
    import barcode
    from barcode.writer import SVGWriter, ImageWriter
except (ImportError) as e:
    pass #warnings.warn(e)
try:
    from django.contrib.sites.models import Site
except (ImportError, RuntimeError) as e:
    pass #warnings.warn(e)

from . import text, json, icons


def valuecallable(obj):
    """Intentará invocar el objeto --> obj() y retorna su valor."""
    try:
        return obj()
    except (TypeError):
        return obj

def parse_bool(value) -> bool:
    """
    Devuelve False si el valor (string) está en:
        ('false', 'False', '0', '0.0', 'none', 'None', 'null', 'Null', 'off').
    De lo contrario devoverá el resultado de bool(value).
    """
    if value in ('false', 'False', '0', '0.0', 'none', 'None', 'null', 'Null', 'off'):
        return False
    return bool(value)

def supergetattr(obj, name, default="", get_display_name=True):
    """
    Una función getattr con super poderes.

    Si el nombre 'name' contiene puntos (.) se asume que son varios Nombres
    uno es un método del otro en el mismo orden.

    Parameters:

        obj (object): Cualquier objeto.

        name (str):

    >> supergetattr(obj, 'a.b.c', False)
    a = obj.a() or obj.a
    b = a.b() or a.b
    c = b.c() or b.c

    >> supergetattr(obj, 'a.b')
    a = obj.a() or obj.a
    b = a.get_display_b() or a.get_display_b or a.b() or a.b

    >> supergetattr(obj, 'a')
    a = obj.get_a_display() or obj.get_a_display or obj.a() or obj.a
    """
    names = name.split(".")
    if get_display_name:
        name_end = names[-1]
        names[-1] = f"get_{names[-1]}_display"

    attr = obj
    for nam in names:
        try:
            attr = valuecallable(getattr(attr, nam))
        except (AttributeError):
            if get_display_name:
                attr = valuecallable(getattr(attr, name_end, default))
    return attr


def get_barcode(code: str, strtype: str="code128", render: bool=True, 
    options: dict=None):
    """
    Obtiene el código de barras con python-barcode.

    https://python-barcode.readthedocs.io/en/latest/
    https://pypi.org/project/python-barcode/

    Parameters:
        code (str): Código en string del barcode a obtener.

        strtype (str): 'code39', 'code128', 'ean', 'ean13', 'ean8', 'gs1',
        'gtin','isbn', 'isbn10', 'isbn13', 'issn', 'jan', 'pzn', 'upc', 'upca'

        render (bool): (default=True) le aplica el método 'render()' a la 
        salida, obteniendo así el contenido en string del SVG

        options (dict): (default={compress=True}) opciones que se pasarán al 
        render.

    Returns:
        barcode (object): barcode.get_barcode_class(strtype)(str(code)).render()
    """
    c = barcode.get_barcode_class(strtype)(str(code), writer=SVGWriter())
    if (render is True):
        opt = dict(compress=True)
        opt.update(options or {})
        return c.render(opt).decode("utf-8")
    return c


def upload_file_on_site(instance, filename):
    """
    Función para ser utilizada en campos de subida de archivo, para guardar el 
    archivo en una ruta ideal que contiene el nombre del site, aplicación y 
    modelo. 
    Ejemplo: 'www.misite.com/miapp/mimodel/filename'.
    """
    site = getattr(instance, "site", Site.objects.get_current())
    return "/".join([site.domain, instance.__class__._meta.app_label, 
        instance.__class__._meta.model_name, filename])


def upload_file_on_company(instance, filename):
    """
    Función para ser utilizada en campos de subida de archivos, para guardar el
    archivo en una ruta ideal que contiene el nombre del site, empresa, 
    aplicación y modelo. 
    Ejemplo: 'www.misite.com/company/miapp/mimodel/filename'.
    """
    site = getattr(instance, "site", Site.objects.get_current())
    company = getattr(instance.get_company(), "id", 0)
    return "/".join([site.domain, company, instance.__class__._meta.app_label, 
        instance.__class__._meta.model_name, filename])


