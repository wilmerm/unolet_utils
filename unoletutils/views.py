import copy
import functools
import warnings

from django.core.exceptions import FieldError
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.views import generic
from django.contrib import messages

try:
    from weasyprint import HTML as weasyprintHTML
    from weasyprint.fonts import FontConfiguration as weasyprintFontConfiguration
except (ImportError) as e:
    warnings.warn(f"Es necesario el paquete 'weasyprint' para poder imprimir en PDF. {e}.")
except (OSError) as e:
    pass # warnings.warn(str(e) + ". Por lo general este error se presenta en Windows por falta de la librería 'cairo'.")
except (BaseException) as e:
    warnings.warn(str(e))



class ViewError(Exception):
    pass


class ObjectCapsule:
    """
    Encapsula una instancia de un models.Model para poder llamar a métodos 
    declarados en la vista mediante el atributo de clase 'list_display'.
    """

    def __init__(self, view, obj):
        self._view = view

        if isinstance(obj, ObjectCapsule):
            obj = obj._obj
        self._obj = obj 

    def __str__(self):
        return str(self._obj)

    def __bool__(self):
        return bool(self._obj)

    def __getattribute__(self, name):
        errors = []
        try:
            return getattr(super().__getattribute__("_view"), name)
        except (AttributeError) as e:
            errors.append(str(e))
        try:
            return getattr(super().__getattribute__("_obj"), name)
        except (AttributeError) as e:
            errors.append(str(e))
        try:
            return super().__getattribute__(name)
        except (AttributeError) as e:
            errors.append(str(e))

        raise AttributeError(". ".join(errors))

    def get_values(self):
        """Obtiene los valores de los campos declarados en list_display. """
        return {
            e[0]: {"value": self._obj.getattr(e[0]), 
                "cssclass": self.get_list_display_cssclass().get(e[0], "")} 
            for e in self._view.get_list_display()}


class QuerysetCapsule:
    """
    Encapsula un objeto Queryset para poder recorrer cada uno de sus elementos 
    de forma encapsulada con ObjectCapsule.
    """

    def __init__(self, view, queryset):
        self._view = view 
        self._queryset = queryset 

    def __iter__(self):
        for obj in self._queryset:
            yield ObjectCapsule(self._view, obj)

    def __len__(self):
        return len(self._queryset)

    def __getitem__(self, index):
        if isinstance(index, int):
            return ObjectCapsule(self._view, self._queryset[index])
        return QuerysetCapsule(self._view, self._queryset[index])

    def __getattribute__(self, name):
        if name in ("_view", "_queryset", "__iter__"):
            return object.__getattribute__(self, name)
        return getattr(self._queryset, name)


class BaseView():
    """Clase base de las cuales heredarán nuestras vistas."""

    # Nombre del campo en el modelo que contiene el valor de la empresa.
    # Por ejemplo, el modelo Document no tiene un campo para la empresa, sino
    # que este se obtiene de su campo relacionado 'doctype' que si tiene uno.
    # Entonces para la vista de documentos este campo deberá ser como sigue:
    # company_field = 'doctype__company'.
    company_field = "company"
    # Nombre del valor de la empresa en la url.
    # Ej. .../<int:company>/... company_in_url = 'company'
    company_in_url = "company" 
    # Nombre del campo en el modelo que contiene el valor pk.
    pk_field = "pk" 
    # Nombre con el cual está identificado el valor pk en la url 
    # Ej. ../<int:item>/.. pk_in_url = 'item'.
    pk_in_url = "pk" 
    # Lista de errores al procesar esta view, 
    # si hay errores devolverá una respuesta con código de error.
    error_list = [] 
    # Persmisos requeridos (str or iter).
    company_permission_required = None 
    # Título a mostrar en la página.
    title = ""
    # Módulo actual.
    module = None 

    def get_title(self):
        """Obtiene el valor del título que se mostrará en la página."""
        try:
            vnp = str(getattr(self.model._meta, "verbose_name_plural", "")).title()
        except (AttributeError):
            vnp = ""
        return str(self.title or self.get_object() or vnp)

    def get_company(self):
        """Obtiene la instancia de la empresa actual."""
        try:
            company = self.request.company
        except (AttributeError):
            try:
                company = self.get_context_data()["company"]
            except (AttributeError, KeyError):
                company = get_object_or_404(Company, pk=kwargs[self.company_in_url])
        return company

    def get_object(self, queryset=None):
        """
        Método Django que obtiene el objeto actual.
        Se hicieron algunas modificaciones para asegurarnos de que el objeto 
        devuelto pertenezca a la empresa actual. (no se puede mostrar un 
        registro de una empresa en otra.)
        """
        company = self.get_company()
        company_pk = self.kwargs.get(self.company_in_url)
        pk = self.kwargs.get(self.pk_in_url)
        
        if company_pk and pk:
            if self.model is None:
                raise ValueError("El valor del atributo 'model' no puede ser None.")
            filters = {self.company_field: company_pk, self.pk_field: pk}
            obj = get_object_or_404(self.model, **filters)
        else:
            obj = None
            
        # La objeto debe pertenecer a la misma empresa obtenida por url.
        if obj:
            obj_company = obj.getattr(self.company_field)
            if obj_company != company:
                raise Http404(f"La empresa {company} no es la misma empresa "
                    f"del objeto {obj_company}")
        
        # La empresa debe estar activa.
        if not company.is_active:
            raise Http404(f"La empresa {company} no está activa.")

        # El usuario debe tener acceso a esta empresa.
        if not company.user_has_access(self.request.user):
            raise Http404(
                f"El usuario {self.request.user} no pertenece a {company}")
        return obj

    def dispatch(self, request, *args, **kwargs):
        """
        Mismo método dispatch Django, en este caso validamos los permisos
        requeridos en la vista y los permisos del usuario.
        """
        if self.error_list:
            raise ViewError(". ".join(error_list))
        if self.company_permission_required:
            if not request.user.has_company_permission(
                company=self.get_company(), 
                permission=self.company_permission_required):
                raise PermissionDenied(
                    "Acceso denegado. No cuenta con permisos suficientes.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company = self.get_company()
        # Permisos y grupos que posee y pertenece el usuario actual.
        context["user_company_permissions"] = user.get_company_permissions(company)
        context["user_company_groups"] = user.get_company_groups(company)
        return context


class BaseList(BaseView):

    VALUES_FOR_PAGINATE_BY = (20, 40, 60, 80, 100)
    list_display = [("__str__", _l("nombre"))]
    list_display_cssclass = {}
    list_display_links = ["__str__"]
    #search_form_class = SearchForm *---------------------------------------------------------

    def get_search_form(self):
        if self.search_form_class:
            return self.search_form_class(self.request.GET)

    def get_queryset(self):
        # Establecemos el valor al atributo 'paginate_by' si se especifica en la
        # URL. Devolvemos el valor predeterminado si el valor no es válido.
        try:
            paginate_by = int(self.request.GET.get("paginate_by") or 
                self.paginate_by)
        except (ValueError, TypeError):
            paginate_by = self.VALUES_FOR_PAGINATE_BY[0]
        
        if not paginate_by in self.VALUES_FOR_PAGINATE_BY:
            paginate_by = self.VALUES_FOR_PAGINATE_BY[0]
            
        self.paginate_by = paginate_by
        qs = self.queryset_filter(super().get_queryset())
        return QuerysetCapsule(view=self, queryset=qs)

    def queryset_filter(self, queryset):
        """
        Filtra el queryset de acuerdo al los valores del diccionario pasado.
        Las claves del diccionario deben ser nombres de campos válidos del 
        modelo Ej. {'name': 'Unolet'} or {'name__contains': 'Uno'}
        Las claves no válidas serán obviadas.
        """
        form = self.get_search_form()
        if form.is_valid():
            for key in form.cleaned_data:
                value = form.cleaned_data[key]
                print(key, value, type(value))
                if value == "":
                    continue
                try:
                    queryset = queryset.filter(**{key: value})
                except (FieldError) as e:
                    print(e)
                    continue 
        return queryset

    def get_list_display(self):
        return self.list_display or [("__str__", _l("nombre"))]

    def get_list_display_cssclass(self):
        return self.list_display_cssclass or {}
    

class BaseForm(BaseView):

    def get_form_kwargs(self):
        """Incluimos la instancia 'company' a los argumentos del formulario."""
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.get_company()
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        company = self.get_company()

        if not form.instance.pk:
            try:
                form.instance.create_user = user
            except (AttributeError):
                pass
            try:
                form.instance.company = company
            except (AttributeError):
                pass

            messages.success(self.request, 
                (f"¡{form.instance.verbose_name.capitalize()} "
                f"'{form.instance}' {_('creado correctamente')}!"))
        else:
            messages.success(self.request, 
                (f"¡{form.instance.verbose_name.capitalize()} "
                f"'{form.instance}' {_('modificado correctamente')}!"))
            
        return super().form_valid(form)


class ListView(BaseList, generic.ListView):
    pass


class DetailView(BaseView, generic.DetailView):

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return ObjectCapsule(self, obj)


class CreateView(BaseForm, generic.CreateView):
    pass


class UpdateView(BaseForm, generic.UpdateView):
    pass


class DeleteView(BaseView, generic.DeleteView):
    template_name = "base/confirm_delete.html"

    def get_success_url(self):
        return self.get_object().get_list_url()


class TemplateView(BaseView, generic.TemplateView):
    pass


class PrintView(TemplateView):
    """Plantilla base de impresión heredada de TemplateView."""
    pass 


class DetailPrintView(DetailView):
    """Vista base para impresión heredada de DatailView."""
    
    def get_template_names(self):
        template_names = super().get_template_names()
        return [n.replace("detail.html", "print.html") for n in template_names]

    def dispatch(self, request, *args, **kwargs):
        # Al imprimir se guarda un registro en el historial de cambios.
        obj = self.get_object()
        if hasattr(obj, "history"):
            if bool(getattr(obj, "is_printed", False)):
                obj._change_reason = _("Re-imprimió")
            else:
                obj._change_reason = _("Imprimió")
            if request.user.is_staff:
                obj._change_reason += _(" (prueba)")
            obj.is_printed = True
            obj.save()
            history = obj.history.order_by("history_date").last()
            # Los tipos predefinidos de simple-history son (+), (-) y (~), hemos 
            # agregado uno más (p) para identificar los de la impresión.
            history.history_type = "p" 
            history.save()
        return super().dispatch(request, *args, **kwargs)


class JsonResponseMixin:
    """
    Mixin to add JSON support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.accepts('text/html'):
            return response
        else:
            data = {'pk': self.object.pk}
            return JsonResponse(data)


@login_required
def render_to_pdf(request, context: dict = {}, 
template_name: str = None) -> HttpResponse:
    """
    Obtiene el nombre de una plantilla html, la renderiza en PDF y retorna 
    el objeto response con el PDF renderizado.
    
    Parameters:
    - template_name (str): nombre de la plantilla a renderizar.
    """
    template_name = request.GET.get("template_name") or template_name
    try:
        HTML = weasyprintHTML
        FontConfiguration = weasyprintFontConfiguration
    except (NameError):
        warnings.warn("No se puede renderizar el HTML como un PDF porque la "
            "libería externa weasyprint no está instalada.")
        return render(request, template_name, context)
    try:
        html = render_to_string(template_name, context)
    except (BaseException) as e:
        raise Http404(f"Error obteniendo la plantilla: {e}")
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; report.pdf"
    font_config = weasyprintFontConfiguration()
    weasyprintHTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response, font_config=font_config)
    return response