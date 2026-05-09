from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from config.choices import EstadoEnvio
from .forms import EncomiendaForm
from .models import Empleado, Encomienda


def _empleado_para_usuario(user):
    empleado = Empleado.objects.filter(email=user.email).first()
    if empleado:
        return empleado
    return Empleado.objects.filter(estado=1).first()


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    stats = [
        ('Activas', Encomienda.objects.activas().count(), 'primary', 'box'),
        ('En transito', Encomienda.objects.en_transito().count(), 'warning', 'truck'),
        ('Con retraso', Encomienda.objects.con_retraso().count(), 'danger', 'clock'),
        (
            'Entregadas hoy',
            Encomienda.objects.filter(
                estado=EstadoEnvio.ENTREGADO,
                fecha_entrega_real=hoy,
            ).count(),
            'success',
            'check-circle',
        ),
    ]
    context = {
        'stats': stats,
        'ultimas': Encomienda.objects.con_relaciones()[:5],
    }
    return render(request, 'index/dashboard.html', context)


@require_GET
@login_required
def encomienda_lista(request):
    qs = Encomienda.objects.con_relaciones()
    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')

    if estado:
        qs = qs.filter(estado=estado)
    if q:
        qs = qs.filter(
            Q(codigo__icontains=q)
            | Q(remitente__apellidos__icontains=q)
            | Q(remitente__nombres__icontains=q)
            | Q(destinatario__apellidos__icontains=q)
            | Q(destinatario__nombres__icontains=q)
            | Q(ruta__codigo__icontains=q)
        )

    paginator = Paginator(qs, 15)
    encomiendas = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'index/lista.html', {
        'encomiendas': encomiendas,
        'estado_actual': estado,
        'q': q,
        'estados': EstadoEnvio.choices,
    })


@login_required
def encomienda_detalle(request, pk):
    encomienda = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)
    historial = encomienda.historial.select_related('empleado')
    return render(request, 'index/detalle.html', {
        'encomienda': encomienda,
        'historial': historial,
        'estados': EstadoEnvio.choices,
    })


@login_required
def encomienda_crear(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            empleado = _empleado_para_usuario(request.user)
            if not empleado:
                messages.error(request, 'No existe un empleado activo para registrar la encomienda.')
                return render(request, 'index/form.html', {
                    'form': form,
                    'titulo': 'Nueva Encomienda',
                })

            encomienda = form.save(commit=False)
            encomienda.empleado_registro = empleado
            encomienda.save()
            messages.success(
                request,
                f'Encomienda {encomienda.codigo} registrada correctamente.',
            )
            return redirect('encomienda_detalle', pk=encomienda.pk)

        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = EncomiendaForm()

    return render(request, 'index/form.html', {
        'form': form,
        'titulo': 'Nueva Encomienda',
    })


@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    nuevo_estado = request.POST.get('estado')
    observacion = request.POST.get('observacion', '')
    estados_validos = {estado for estado, _label in EstadoEnvio.choices}

    if nuevo_estado not in estados_validos:
        messages.error(request, 'Estado no valido.')
        return redirect('encomienda_detalle', pk=pk)

    empleado = _empleado_para_usuario(request.user)
    if not empleado:
        messages.error(request, 'No existe un empleado activo para registrar el cambio.')
        return redirect('encomienda_detalle', pk=pk)

    try:
        encomienda.cambiar_estado(nuevo_estado, empleado, observacion)
        messages.success(
            request,
            f'Estado actualizado a: {encomienda.get_estado_display()}',
        )
    except ValueError as exc:
        messages.error(request, str(exc))

    return redirect('encomienda_detalle', pk=pk)


@require_GET
@login_required
def encomienda_estado_json(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    return JsonResponse({
        'codigo': encomienda.codigo,
        'estado': encomienda.estado,
        'display': encomienda.get_estado_display(),
        'retraso': encomienda.tiene_retraso,
        'dias': encomienda.dias_en_transito,
    })


@login_required
def encomienda_eliminar(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)

    if encomienda.estado != EstadoEnvio.PENDIENTE:
        raise PermissionDenied

    if request.method == 'POST':
        codigo = encomienda.codigo
        encomienda.delete()
        messages.success(request, f'Encomienda {codigo} eliminada.')
        return redirect('encomienda_lista')

    return render(request, 'index/confirmar_eliminar.html', {'encomienda': encomienda})


@require_GET
@login_required
def buscar_por_codigo(request, codigo):
    try:
        encomienda = Encomienda.objects.get(codigo=codigo.upper())
    except Encomienda.DoesNotExist as exc:
        raise Http404(f'No existe la encomienda {codigo}') from exc
    return redirect('encomienda_detalle', pk=encomienda.pk)
