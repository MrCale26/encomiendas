from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import EncomiendaForm
from .models import Empleado, Encomienda


class EncomiendaListView(LoginRequiredMixin, ListView):
    model = Encomienda
    template_name = 'index/lista.html'
    context_object_name = 'encomiendas'
    paginate_by = 15

    def get_queryset(self):
        qs = Encomienda.objects.con_relaciones()
        estado = self.request.GET.get('estado', '')
        q = self.request.GET.get('q', '')

        if estado:
            qs = qs.filter(estado=estado)
        if q:
            qs = qs.filter(
                Q(codigo__icontains=q)
                | Q(remitente__apellidos__icontains=q)
                | Q(destinatario__apellidos__icontains=q)
            )
        return qs


class EncomiendaDetailView(LoginRequiredMixin, DetailView):
    model = Encomienda
    template_name = 'index/detalle.html'
    context_object_name = 'encomienda'

    def get_queryset(self):
        return Encomienda.objects.con_relaciones()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historial'] = self.object.historial.select_related('empleado')
        return context


class EncomiendaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Encomienda
    form_class = EncomiendaForm
    template_name = 'index/form.html'
    success_message = 'Encomienda %(codigo)s creada correctamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva Encomienda'
        return context

    def form_valid(self, form):
        empleado = Empleado.objects.filter(email=self.request.user.email).first()
        if not empleado:
            empleado = Empleado.objects.filter(estado=1).first()
        form.instance.empleado_registro = empleado
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('encomienda_detalle', kwargs={'pk': self.object.pk})
