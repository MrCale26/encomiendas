from django.contrib import admin
from django.utils.html import format_html

from .models import Empleado, Encomienda, HistorialEstado


@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'remitente',
        'destinatario',
        'ruta',
        'estado_badge',
        'costo_envio',
        'fecha_registro',
    )
    list_filter = ('estado', 'ruta', 'fecha_registro')
    search_fields = (
        'codigo',
        'remitente__nro_doc',
        'remitente__apellidos',
        'destinatario__nro_doc',
        'destinatario__apellidos',
    )
    readonly_fields = ('fecha_registro',)
    fieldsets = (
        ('Identificacion', {
            'fields': ('codigo', 'descripcion', 'peso_kg', 'volumen_cm3')
        }),
        ('Relaciones', {
            'fields': ('remitente', 'destinatario', 'ruta', 'empleado_registro')
        }),
        ('Estado y fechas', {
            'fields': (
                'estado',
                'costo_envio',
                'fecha_registro',
                'fecha_entrega_est',
                'fecha_entrega_real',
            )
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        colors = {
            'PE': '#6c757d',
            'TR': '#ffc107',
            'DE': '#0dcaf0',
            'EN': '#198754',
            'DV': '#dc3545',
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:10px; font-weight:600;">{}</span>',
            color,
            obj.get_estado_display(),
        )


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'cargo', 'email', 'estado')
    list_filter = ('estado', 'cargo')
    search_fields = ('codigo', 'apellidos', 'nombres', 'email')


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = (
        'encomienda',
        'estado_anterior',
        'estado_nuevo',
        'empleado',
        'fecha_cambio',
    )
    readonly_fields = (
        'encomienda',
        'estado_anterior',
        'estado_nuevo',
        'empleado',
        'fecha_cambio',
    )
    list_filter = ('estado_nuevo',)
    ordering = ('-fecha_cambio',)
