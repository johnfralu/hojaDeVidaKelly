from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DatosPersonales, ExperienciaLaboral, Reconocimientos,
    CursosRealizados, ProductosAcademicos, ProductosLaborales, VentaGarage,
    ConfiguracionSecciones
)

@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'numerocedula', 'perfilactivo', 'preview_foto')
    search_fields = ('nombres', 'apellidos', 'numerocedula')
    list_filter = ('perfilactivo', 'sexo', 'nacionalidad')
    
    def preview_foto(self, obj):
        if obj.foto_perfil:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.foto_perfil.url)
        return "Sin foto"
    preview_foto.short_description = 'Foto'
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'numerocedula', 'sexo', 'fechanacimiento', 'lugarnacimiento', 'nacionalidad', 'foto_perfil')
        }),
        ('Perfil', {
            'fields': ('descripcionperfil', 'perfilactivo')
        }),
        ('Contacto', {
            'fields': ('telefonoconvencional', 'telefonofijo', 'direcciondomiciliaria', 'direcciontrabajo', 'sitioweb')
        }),
        ('Otros Datos', {
            'fields': ('estadocivil', 'licenciaconducir')
        }),
    )

@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = ('cargodesempenado', 'nombreempresa', 'fechainiciogestion', 'fechafingestion', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront', 'nombreempresa')
    search_fields = ('cargodesempenado', 'nombreempresa')
    date_hierarchy = 'fechainiciogestion'
    fieldsets = (
        ('Información del Cargo', {
            'fields': ('idperfilconqueestaactivo', 'cargodesempenado', 'descripcionfunciones')
        }),
        ('Información de la Empresa', {
            'fields': ('nombreempresa', 'lugarempresa', 'emailempresa', 'sitiowebempresa')
        }),
        ('Contacto Empresarial', {
            'fields': ('nombrecontactoempresarial', 'telefonocontactoempresarial')
        }),
        ('Fechas', {
            'fields': ('fechainiciogestion', 'fechafingestion')
        }),
        ('Opciones', {
            'fields': ('activarparaqueseveaenfront', 'rutacertificado')
        }),
    )

@admin.register(Reconocimientos)
class ReconocimientosAdmin(admin.ModelAdmin):
    list_display = ('tiporeconocimiento', 'descripcionreconocimiento', 'entidadpatrocinadora', 'fechareconocimiento', 'activarparaqueseveaenfront')
    list_filter = ('tiporeconocimiento', 'activarparaqueseveaenfront')
    search_fields = ('descripcionreconocimiento', 'entidadpatrocinadora')
    date_hierarchy = 'fechareconocimiento'

@admin.register(CursosRealizados)
class CursosRealizadosAdmin(admin.ModelAdmin):
    list_display = ('nombrecurso', 'entidadpatrocinadora', 'fechainicio', 'fechafin', 'totalhoras', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront', 'entidadpatrocinadora')
    search_fields = ('nombrecurso', 'entidadpatrocinadora')
    date_hierarchy = 'fechainicio'

@admin.register(ProductosAcademicos)
class ProductosAcademicosAdmin(admin.ModelAdmin):
    list_display = ('nombrerecurso', 'clasificador', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront', 'clasificador')
    search_fields = ('nombrerecurso', 'clasificador')

@admin.register(ProductosLaborales)
class ProductosLaboralesAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'fechaproducto', 'activarparaqueseveaenfront')
    list_filter = ('activarparaqueseveaenfront',)
    search_fields = ('nombreproducto',)
    date_hierarchy = 'fechaproducto'

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'estadoproducto', 'valordelbien', 'activarparaqueseveaenfront', 'preview_imagen')
    list_filter = ('estadoproducto', 'activarparaqueseveaenfront')
    search_fields = ('nombreproducto',)
    
    def preview_imagen(self, obj):
        if obj.imagen_producto:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen_producto.url)
        return "Sin imagen"
    preview_imagen.short_description = 'Imagen'

@admin.register(ConfiguracionSecciones)
class ConfiguracionSeccionesAdmin(admin.ModelAdmin):
    list_display = ('perfil', 'mostrar_perfil', 'mostrar_experiencia', 'mostrar_reconocimientos', 'mostrar_cursos')
    fieldsets = (
        ('Perfil', {
            'fields': ('perfil',)
        }),
        ('Secciones Visibles', {
            'fields': (
                'mostrar_perfil',
                'mostrar_experiencia',
                'mostrar_reconocimientos',
                'mostrar_cursos',
                'mostrar_productos_academicos',
                'mostrar_productos_laborales',
                'mostrar_venta_garage'
            )
        }),
    )