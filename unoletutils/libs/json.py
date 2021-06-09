"""
Trabajar con archivos Json, a traves del módulo Python 'json'.
"""

import os
import json


load = json.load
loads = json.loads
dump = json.dump
dumps = json.dumps


def clean(obj, remove: bool=True, raise_exception: bool=True):
    """
    Limpia el objeto de los items que no sean serializables a Json.

    Parameters:
        obj (object): Objeto que desea limpiar.

        remove (bool): Si es True, removerá aquellos items que no sean 
        json serializables. Si es False, pondrá en str aquellos 
        items que no sean serializables por json.

        raise_exception (bool): Determina si lanzará una exceptión al 
        encontrar errores.

    Returns:
        type(obj): El mismo objeto limpio de valores no serializables a Json.
    """
    if (isinstance(obj, dict)):
        return {clean(k, False): clean(v, remove, False) for k,v in obj.items()}
    elif (isinstance(obj, (list, tuple))):
        return [clean(e, remove, False) for e in obj]
    else:
        try:
            dumps(obj)
        except (TypeError) as e:
            if (raise_exception is True) and (remove is True):
                raise TypeError(e)
            return str(obj)
        return obj


def jsonbackup_clear(jsondata):
    """
    Convierte el objeto Json obtenido desde python manage.py dumpdata
    en un diccionario dispuesto de la siguiente manera:

    {
        model1: {
            'cols': [name1, name2, name3], 
            'vals': [
                [a1, a2, a3],
                [b1, b2, b3],
                [c1, c2, c3],
            ]},
        model2: {
            'cols': [name1, name2, name3], 
            'vals': [
                [a1, a2, a3],
                [b1, b2, b3],
                [c1, c2, c3],
            ]},
        ...
    }
    """
    out = {}

    # Suponiendo que el json tenta la siguiente disposición en primer lugar.
    # model | pk | fields (justo como lo genera manage.py dumpdata).
    for dic in jsondata:
        try:
            out[dic["model"]]
        except (KeyError):
            out[dic["model"]] = {"cols": [], "vals": []}

            # Ahora llenamos los nombres de las columnas desde el primer 
            # elemento. Ya que estas se repiten en cada elemento.
            out[dic["model"]]["cols"] = ["pk"] + list(dic["fields"].keys())

        # Ahora rellenamos con los valores.
        l = [dic["pk"]] + list(dic["fields"].values())
        out[dic["model"]]["vals"].append(l)

    return out