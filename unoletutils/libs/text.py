"""
Módulo con herramientas útiles para el manejo de cadenas de textos.
"""

import re
import unicodedata
import itertools

from . import number, number_letter


class TextError(Exception):
    pass


class Text(number.Number):
    """
    Realiza operaciones con textos mediante algunos métodos útiles.
    """

    @classmethod
    def number_to_letter(cls, number, in_moneda: bool=True, 
        moneda: str="dop") -> str:
        """Convierte un número en un texto leíble."""
        if in_moneda is True:
            return number_letter.numero_a_moneda(number, moneda=moneda)
        return number_letter.numero_a_letras(number)

    @classmethod
    def normalize(cls, string: str, lower: bool=True) -> str:
        """
        Remplaza el texto por uno similiar sin tíldes ni caracteres especiales
        como eñes, ni espacios extras, ni comillas y en minuscula si es indicado.

        Parameters:
            string (str): texto a formatear.
            lower (bool): si es True, el resultado será en minúscula.
        """
        if (string is None) or (string is False) or (string is True):
            return ""

        string = str(string).replace("'", "").replace('"', '')

        out = ''.join((c for c in unicodedata.normalize('NFD', string)
            if unicodedata.category(c) != 'Mn'))

        out = " ".join(out.split()).strip()
        if lower:
            out = out.lower()
        return out

    @classmethod
    def get_tag(cls, text, combinate=False, allow=None) -> str:
        """
        Obtiene un texto pre-formateado sin tíldes, ni comillas, ni slash...,
        ideal para campo de búsqueda.

        Se eliminan las tíldes y se establece todo en minúsculas.

        Parameters:
            text (str): texto que se desea formatear.

            combinate (bool): si el parámetro 'combinate' es True, retornará un
            texto más extenso, como resultado de todas las posibles combinaciones
            de sus palabras.

            allow (str): una cadena de caracteres que le indicarán a este método
            que los caracteres que en 'allow' no se especifiquen, serán excluidos
            del resultado.
        """
        t = cls.normalize(text, lower=False)

        if allow:
            if not isinstance(allow, str):
                raise TextError(f"El parámetro 'allow' debe ser de \
                     tipo str, pero se indicó {type(allow)}.")

            # Solo se permitirán estos caracteres.
            # El resto será excluido del resultado.
            regexp = "[^" + allow + "]" # Expresión Regular.
            t = re.sub(regexp, "", t)

        # De ninguna forma están permitidos estos caráctes que eliminaremos.
        # Esto es porque podría causar problemas utilizandolo dentro de otros
        # strings, consultas SQL y/o otros lenguales de programación.
        t = " ".join(t.split())
        t = t.replace("/", " ").replace("\\", " ").replace("'", "")
        t = t.replace('"', '').replace("$", "").replace("\n", " ")

        t = t.lower()
        # Combinaciones.
        if (combinate == True):
            return cls.permutations(t).strip()
        return t

    @classmethod
    def __gettagsclean(cls, text) -> str:
        if isinstance(text, (tuple, list)):
            text = cls.get_tags(text, combinate=False)
        return cls.normalize(text, lower=True)

    @classmethod
    def get_tags(cls, *args, **kwargs) -> str:
        """
        Obtiene una cadena de texto a partir de los valores pasados (*args).

        Se eliminan las tíldes y se establece todo en minúsculas.

        Keyword parameters:
            *args (tuple) lista de string.

            combinate (bool): si el parámetro 'combinate' es True, retornará un
            texto más extenso, como resultado de todas las posibles combinaciones
            de sus palabras.

            comb (bool): igual a combinate.

            allow (str): una cadena de caracteres que le indicarán a este método
            que los caracteres que en 'allow' no se especifiquen, serán 
            excluidos del resultado.
        """
        combinate = kwargs.get("combinate") or kwargs.get("comb", False)
        allow = kwargs.get("allow")

        if len(args) == 1:
            args = args[0]

        if isinstance(args, (list, tuple)):
            args = " ".join([cls.normalize(x) for x in args])
        else:
            args = cls.normalize(args)

        if (combinate):
            args = cls.permutations(args)

        if allow:
            if not isinstance(allow, str):
                raise TextError(f"El parámetro 'allow' debe ser de tipo str, "
                    f"pero se indicó {type(allow)}.")

            # Solo se permitirán estos caracteres.
            # El resto será excluido del resultado.
            regexp = "[^ " + allow + "]" # Expresión Regular.
            args = re.sub(regexp, "", args)

        # De ninguna forma están permitidos estos caráctes que eliminaremos.
        # Esto es porque podría causar problemas utilizandolo dentro de otros
        # strings, consultas SQL y/o otros lenguales de programación.
        args = args.replace("/", " ").replace("\\", " ").replace("'", "")
        args = args.replace('"', '').replace("$", "").replace("\n", " ")

        return args.strip()

    @classmethod
    def format_codename(cls, string: str, remplace: str="", lower: bool=True, 
        allowed: str="") -> str:
        """
        Formatea el texto dejando solo los caracteres en el rango de a-Z y 0-9.

        El texto retorna sin la ñ ni tíldes. Si se indica el remplace, se
        remplazan los caracteres no permitidos por el indicado. de lo contrario
        se eliminará.

        Parameters:
            string (str): texto a formatear
            remplace (str): texto que remplazará los carácteres no permitidos
            lower (bool): si es True, la salida será en minúscula
            allowed (bool): caracteres adicional que se desean permitir
        """
        if not remplace:
            remplace = ""

        permited = ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789" + allowed)
        out = ""

        for char in string:
            if not char in permited:
                char = remplace
            out += char

        if lower:
            return out.lower()

        return out

    @classmethod
    def permutations(cls, iterable: iter, r: int=2, split: str=" ") -> str:
        """
        Devuelve permutaciones de longitud r sucesivas de elementos en el 
        iterable.

        Si r no se especifica o lo está None, entonces r toma por defecto la
        longitud del iterable y se generan todas las posibles permutaciones de
        longitud completa.

        Las tuplas de permutación se emiten en orden lexicográfico según el
        orden de la entrada iterable . Entonces, si la entrada iterable está
        ordenada, las tuplas de combinación se producirán en orden ordenado.

        Los elementos se tratan como únicos en función de su posición, no de su
        valor. Entonces, si los elementos de entrada son únicos, no habrá
        valores repetidos en cada permutación.

        https://docs.python.org/3/library/itertools.html#itertools.permutations

        Si en 'iterable' se especifica un string y no un iterable, se tomará
        el valor del parámetro 'split' para dividir los elementos del string.

        Returns:
            str: Una cadena de texto separada por el valor del parámetro 'split'.
        """
        if isinstance(iterable, str):
            if split != " ":
                iterable = iterable.split(split)
            else:
                iterable = iterable.split()

        # Cuando r es mayor a la longitud del iterable, la función
        # itertools.permutations(iterable, r), retorna una lista vacia. 
        # Evitamos esto ajustando el valor de r a la longitud del iterable.
        if (len(iterable) < r):
            r = len(iterable)

        permutations = itertools.permutations(iterable, r)
        return split.join([split.join(x) for x in  permutations])

    @classmethod
    def truncatechars(cls, text: str, length: int, end: str="...") -> str:
        """
        Corta el texto según la longitud indicada.

        Parameters:
            text (str): texto a cortar.
            length (int): longitud del texto resultante, desde el inicio.
            end (str): texto final que se añadirá a la cadena.

        Returns:
            str: text[:length] + end
        """
        text = str(text)
        length = int(length)
        lent = len(text)
        end = str(end)

        if (length >= lent):
            return text

        if (not length):
            return ""

        return f"{text[:length - len(end)]}{end}"

    @classmethod
    def truncatechars_center(cls, text: str, length: int) -> str:
        """
        Corta el texto según la longitud indicada, quitando solo el texto 
        central.

        Ejemplo:
            TruncateCharsCenter('La chispa adecuada - Heroes Del Silencio', 30)
            --> 'La chispa adec/es Del Silencio'

        Parameters:
            text (str): texto a cortar.
            length (int): longitud del texto resultante.
        """
        text = str(text)
        length = int(length)
        lent = len(text)

        if (length >= lent):
            return text

        if (not length):
            return ""

        mid = int(length / 2) # Cantidad de caracteres en ambos extremos.
        res = int(lent - length) # Cantidad de caracteres que se van a suprimir.
        a1, a2 = (0, mid) # texto inicial
        b1, b2 = (lent - mid, lent) # texto final
        # Si el espacio en blanco más próximo está cerca del corte,
        # entonces cortamos por en el espacio más próximo.
        if (mid >= 5):
            idx = text.find(" ", a2 - 5, a2 + 5)
            if (idx != -1):
                a2 = idx
                b1 = a2 + res + 1
            else:
                idx = text.find(" ", b1 - 5, b1 + 5)
                if (idx != -1):
                    b1 = idx + 1
                    a2 = b1 - res - 1

        t1 = text[a1: a2]
        t2 = text[b1: b2]
        return f"{t1}/{t2}"

    @classmethod
    def is_possible_name(cls, text: str) -> bool:
        """Comprueba si el texto indicado puede ser un nombre."""
        numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for n in numbers:
            if str(n) in text:
                return False
        return True

    @classmethod
    def is_possible_full_name(cls, text: str) -> bool:
        """Comprueba si el texto indicado puede ser un nombre completo."""
        if len(text.split(" ")) < 2:
            return False
        return cls.is_possible_name(text)

    @classmethod
    def set_coin(cls, numero, simbolo: str="$", ndec: int=2) -> str:
        """Convierte el número en una cadena de texto con formato moneda."""
        return f"{simbolo}{round(numero, 2):,}"

    @classmethod
    def strip(cls, text: str) -> str:
        """
        Elimina los espacios extras del texto indicado.

        >> ' '.join('   Hello   World  '.split()).strip() -> 'Hello World'
        """
        return " ".join(text.split()).strip()

    @classmethod
    def validate_identification(cls, text, div: str="-", length: int=11, 
        allowed: str="0123456789") -> str:
        """
        Valida que el texto introduccido esté acorde al formato del ID indicado.

        Formato:
            Cédula: xxx-xxxxxxx-x (lenght=11)
            RNC: xxx-xxxxx-x (length=9)

        Parameters:
            text (str): identificación a evaluar.
            div (str): divisor de dígitos.
            length (int): longitud permitida 11 (cédula), 9 (RNC), None (otros).
        """
        text = "".join(text.split()).replace("-", "")
        if length != None:
            if len(text) != length:
                raise TextError(f"La identificación debe contener "
                f"exactamente {length} caracteres, la indicada tiene "
                f"{len(text)} '{text}'.")
        # Caracteres permitidos.
        if allowed != None:
            for c in text:
                if not c in allowed:
                    raise TextError(f"El caracter '{c}' no es válido. "
                    f"Los carácteres permitos son: '{allowed}'.")
        return f"{text[:3]}{div}{text[3:-1]}{div}{text[-1]}"

    @classmethod
    def validate_RNC(cls, text: str, div: str="-") -> str:
        """
        Valida que el texto introduccido esté acorde al formato del RNC indicado.

        Returns:
            str: self.validate_identification(text=text, div=div, length=9)
        """
        return cls.validate_identification(text=text, div=div, length=9)

    @classmethod
    def clean_person_name(cls, text: str) -> str:
        """Valida el texto para utilizarlo como nombre válido de persona."""
        out = cls.strip(text).title()
        if not cls.is_possible_name(out):
            raise TextError("El texto indicado no parece ser el nombre válido "
                "de una persona.")
        return out

    @classmethod
    def clean_phone(cls, text: str) -> str:
        """
        Valida y limpia el texto tenga un formato de número telefónico correcto.
        Y retorna una nueva cadena con el número correctamente dividido.

        Returns:
            str:
                cls.clean_phone('8299259531') -> '(829) 925-9531'
                cls.clean_phone('18299259531') -> '1 (829) 925-9531'
        """
        if not text:
            return ""
        text = str(text)
        text = "".join(text.split()).replace("-", "").replace(".", "")
        text = text.replace("_", "").replace(",", "").replace(";", "")
        if not text.isdigit():
            raise TextError(f"{text} tiene caracteres no numéricos.")
        if len(text) <= 4:
            return text # 0000
        elif len(text) <= 7:
            return f"{text[:-4]}-{text[-4:]}" # 000-0000
        elif len(text) <= 10:
            return f"({text[:-7]}) {cls.clean_phone(text[-7:])}" # (000) 000-0000
        elif len(text) <= 13:
            return f"{text[:-10]} {cls.clean_phone(text[-10:])}" # 0 (000) 000-0000
        else:
            # Varios números separados por coma (,).
            return (f"{cls.clean_phone(text[:-10])}, "
                f"{cls.clean_phone(text[-10:])}")
