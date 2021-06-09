"""
Módulo que contiene un sin número de constantes útiles para todo el proyecto.
"""

import os
import datetime

from django.utils.translation import gettext_lazy as _
from django.conf import settings



UNOLET = "Unolet"

MSG_ERROR_400 = "%s %s" % (UNOLET, _("no pudo entener su solicitud."))
MSG_ERROR_403 = _("Permiso denegado.")
MSG_ERROR_404 = _("Página no encontrada.")
MSG_ERROR_500 = _("Ha ocurrido un error en el servidor.")

