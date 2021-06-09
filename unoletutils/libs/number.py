"""
Módulo para trabajar con números.
"""

from decimal import Decimal



class Number:
    """
    Clase para trabajar con números.
    """

    @classmethod
    def Int(self, texto, intext=False, on_error_return="raise_exception"):
        """
        Obtiene un número entero a partir del texto introduccido, eliminando
        los caracteres que no sean númericos. Si hay un punto, los caracteres a
        la derecha del punto serán omitidos.
        Si 'intext' es True, retorna el número como un objeto string.
        Si 'on_error_return' retornará el valor que se le indique en caso de error.
        """
        if (not isinstance(texto, str)):
            try:
                return int(texto)
            except (BaseException) as e:
                if (on_error_return != "raise_exception"):
                    return on_error_return
                raise ValueError(e)

        n = ""
        for c in texto:
            if c == ".":
                break
            elif c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                n += c

        try:
            n = int(n)
        except (ValueError, TypeError) as e:
            if (on_error_return != "raise_exception"):
                return on_error_return
            raise ValueError(e)

        if intext:
            return str(int(n))
        return int(n)

    @classmethod
    def Float(self, texto, intext=False, on_error_return="raise_exception"):
        """
        Obtiene un número de coma flotante a partir del texto introduccido,
        eliminando los caracteres que no sean numéricos, exceptuando el punto.
        Si 'intext' es True, retorna el número como un objeto string.
        """
        if (not isinstance(texto, str)):
            try:
                return float(texto)
            except (BaseException) as e:
                if (on_error_return != "raise_exception"):
                    return on_error_return
                raise ValueError(e)

        n = ""
        for c in texto:
            if c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
                n += c

        try:
            n = float(n)
        except (ValueError, TypeError) as e:
            if (on_error_return != "raise_exception"):
                return on_error_return
            raise ValueError(e)

        if intext:
            return str(float(n))
        return float(n)

    @classmethod
    def Decimal(self, texto, intext=False, on_error_return="raise_exception"):
        """
        Obtiene un número Decimal a partir del texto introduccido,
        eliminado los carácteres que no sean numéricos, exceptuando el punto.
        Si 'intext' es True, retorna el número como un objeto string.
        """
        if (not isinstance(texto, str)):
            try:
                return Decimal(texto)
            except (BaseException) as e:
                if (on_error_return != "raise_exception"):
                    return on_error_return
                raise ValueError(e)

        if not texto:
            return Decimal()
        floatObj = self.Float(texto, intext)

        try:
            n = Decimal(floatObj)
        except (BaseException) as e:
            if (on_error_return != "raise_exception"):
                return on_error_return
            raise ValueError(e)

        if intext:
            return floatObj
        return Decimal(str(floatObj))

    @classmethod
    def MontoText(self, monto, moneda="", html=False):
        if not isinstance(moneda, str):
            moneda = ""
        if html == True:
            if monto < 0:
                return '<span style="color: red">{:,.2f} {}</span>'.format(monto, moneda)
            return '<span>{:,.2f} {}</span>'.format(monto, moneda)
        return "{:,.2f} {}".format(monto, moneda)

    @classmethod
    def MontoHtml(self, monto, moneda=""):
        return self.MontoText(monto, moneda, True)