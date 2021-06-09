=====
Unolet Utils
=====

Unolet Utils es una aplicación Django con módulos, funciones, objetos, etc. 
útiles para cualquier proyecto con Django.

La documentación detallada se encuentra en el directorio "docs".

Inicio rápido
-----------

1. Agregue "unoletutils" a su configuración INSTALLED_APPS de esta manera:

     INSTALLED_APPS = (
         ...
         'unoletutils',
     )

2. Incluya la URLconf de unoletutils en su proyecto urls.py así:

     url (r'^unoletutils/', include('unoletutils.urls')),

3. Ejecute `python manage.py migrate` para crear los modelos de unoletutils.
