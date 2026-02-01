from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
import json
import traceback
from PIL import Image as PILImage
import requests
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from .models import (
    DatosPersonales, ExperienciaLaboral, Reconocimientos,
    CursosRealizados, ProductosAcademicos, ProductosLaborales, VentaGarage,
    ConfiguracionSecciones
)
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def actualizar_configuracion(request):
    try:
        data = json.loads(request.body)
        # Guardamos en la sesión para que el usuario anónimo "recuerde" sus cambios
        request.session['config_pdf'] = data
        request.session.modified = True
        
        perfil = get_perfil_activo()
        # Solo intentamos guardar en DB si hay perfil y el usuario tiene permisos
        if perfil and request.user.is_authenticated:
            config, _ = ConfiguracionSecciones.objects.get_or_create(perfil=perfil)
            config.mostrar_perfil = data.get('mostrar_perfil', True)
            config.mostrar_experiencia = data.get('mostrar_experiencia', True)
            config.mostrar_reconocimientos = data.get('mostrar_reconocimientos', True)
            config.mostrar_cursos = data.get('mostrar_cursos', True)
            config.mostrar_productos_academicos = data.get('mostrar_productos_academicos', True)
            config.mostrar_productos_laborales = data.get('mostrar_productos_laborales', True)
            config.mostrar_venta_garage = data.get('mostrar_venta_garage', True)
            config.save()
            
        return JsonResponse({'success': True})
    except Exception as e:
        print(f"Error en actualizar_configuracion: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
def get_perfil_activo():
    """Obtiene el perfil marcado como activo o el primero disponible"""
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()
    if not perfil:
        perfil = DatosPersonales.objects.first() # Plan B: El primero de la lista
    return perfil

def get_configuracion(perfil):
    """Obtiene o crea la configuración de secciones"""
    config, created = ConfiguracionSecciones.objects.get_or_create(perfil=perfil)
    return config

def perfil_profesional(request):
    perfil = get_perfil_activo() # Mejor usar tu función helper
    config = get_configuracion(perfil)
    
    # Obtener previews de cada sección (solo los activos)
    experiencias = ExperienciaLaboral.objects.filter(activarparaqueseveaenfront=True).order_by('-fechainiciogestion')
    cursos = CursosRealizados.objects.filter(activarparaqueseveaenfront=True).order_by('-fechainicio')
    reconocimientos = Reconocimientos.objects.filter(activarparaqueseveaenfront=True).order_by('-fechareconocimiento')
    productos_academicos = ProductosAcademicos.objects.filter(activarparaqueseveaenfront=True).order_by('-idproductoacademico')
    productos_laborales = ProductosLaborales.objects.filter(activarparaqueseveaenfront=True).order_by('-fechaproducto')
    productos_garage = VentaGarage.objects.filter(activarparaqueseveaenfront=True).order_by('-idventagarage')
    
    context = {
        'perfil': perfil,
        'config': config,
        'experiencias': experiencias,
        'cursos': cursos,
        'reconocimientos': reconocimientos,
        'productos_academicos': productos_academicos,
        'productos_laborales': productos_laborales,
        'productos_garage': productos_garage,
    }
    
    return render(request, 'curriculum/perfil_profesional.html', context)

def experiencia_laboral(request):
    """Vista de Experiencia Laboral"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    experiencias = ExperienciaLaboral.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    ).order_by('-fechainiciogestion')
    
    context = {
        'perfil': perfil,
        'config': config,
        'experiencias': experiencias,
        'page_title': 'Experiencia Laboral'
    }
    return render(request, 'curriculum/experiencia_laboral.html', context)

def reconocimientos(request):
    """Vista de Reconocimientos"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    reconocimientos_list = Reconocimientos.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    ).order_by('-fechareconocimiento')
    
    context = {
        'perfil': perfil,
        'config': config,
        'reconocimientos': reconocimientos_list,
        'page_title': 'Reconocimientos'
    }
    return render(request, 'curriculum/reconocimientos.html', context)

def cursos_realizados(request):
    """Vista de Cursos Realizados"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    cursos = CursosRealizados.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    ).order_by('-fechainicio')
    
    context = {
        'perfil': perfil,
        'config': config,
        'cursos': cursos,
        'page_title': 'Cursos Realizados'
    }
    return render(request, 'curriculum/cursos_realizados.html', context)

def productos_academicos(request):
    """Vista de Productos Académicos"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    productos = ProductosAcademicos.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    )
    
    context = {
        'perfil': perfil,
        'config': config,
        'productos': productos,
        'page_title': 'Productos Académicos'
    }
    return render(request, 'curriculum/productos_academicos.html', context)

def productos_laborales(request):
    """Vista de Productos Laborales"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    productos = ProductosLaborales.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    ).order_by('-fechaproducto')
    
    context = {
        'perfil': perfil,
        'config': config,
        'productos': productos,
        'page_title': 'Productos Laborales'
    }
    return render(request, 'curriculum/productos_laborales.html', context)

def venta_garage(request):
    """Vista de Venta Garage"""
    perfil = get_perfil_activo()
    config = get_configuracion(perfil) if perfil else None
    productos = VentaGarage.objects.filter(
        idperfilconqueestaactivo=perfil,
        activarparaqueseveaenfront=True
    )
    
    context = {
        'perfil': perfil,
        'config': config,
        'productos': productos,
        'page_title': 'Venta Garage'
    }
    return render(request, 'curriculum/venta_garage.html', context)

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado para agregar número de página y encabezado"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(
            A4[0] - 72, 30,
            f"Página {self._pageNumber} de {page_count}"
        )

def fecha_en_espanol(fecha):
    """Convierte una fecha a formato: 26 de enero de 2026"""
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    dia = fecha.day
    mes = meses[fecha.month]
    anio = fecha.year
    return f"{dia} de {mes} de {anio}"

class FooterCanvas(canvas.Canvas):
    """Canvas con pie de página personalizado"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        # Línea superior del pie
        self.setStrokeColor(colors.HexColor('#A7C7E7'))
        self.setLineWidth(1)
        self.line(2*cm, 2*cm, A4[0] - 2*cm, 2*cm)
        
        # Número de página
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(A4[0] - 2*cm, 1.5*cm, f"Página {self._pageNumber} de {page_count}")
        
        # Fecha de generación
        self.drawString(2*cm, 1.5*cm, f"Generado: {datetime.now().strftime('%d/%m/%Y')}")

@csrf_exempt
def generar_pdf(request):
    """Genera PDF profesional de hoja de vida"""
    try:
        if request.method != 'POST':
            return HttpResponse({'error': 'Método no permitido'}, status=405)
        
        try:
            data = json.loads(request.body)
        except:
            # Si el JS envía mal los datos, tomamos todo por defecto
            data = {'secciones': ['perfil', 'experiencia', 'reconocimientos', 'cursos']}
        
        secciones_seleccionadas = data.get('secciones', [])
        
        if not secciones_seleccionadas:
            return HttpResponse({'error': 'No se seleccionaron secciones'}, status=400)
        
        perfil = get_perfil_activo()
        if not perfil:
            return HttpResponse({'error': 'No hay datos de perfil disponibles en el sistema.'}, status=404)
        
        config = get_configuracion(perfil)

        # Configurar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=1.5*cm,
            bottomMargin=2.5*cm,
            title=f"CV - {perfil.nombres} {perfil.apellidos}"
        )
        
        # Colores pasteles profesionales
        COLOR_PRIMARY = colors.HexColor('#A7C7E7')  # Azul pastel (Soft Blue)
        COLOR_DARK = colors.HexColor('#555555')     # Gris oscuro suave para texto
        COLOR_GRAY = colors.HexColor('#999999')     # Gris claro
        COLOR_LIGHT_BG = colors.HexColor('#F4F7F9') # Fondo azul grisáceo muy tenue
        # 1. DEFINIR COLORES (Estos son los que usas en tus estilos personalizados)
        color_primario = colors.HexColor('#A7C7E7')    # Azul pastel
        color_secundario = colors.HexColor('#B2B2B2')  # Gris suave
        color_fondo = colors.HexColor('#FAF9F6')       # Crema/Blanco roto

        # Estilos
        styles = getSampleStyleSheet()

        # Función auxiliar para añadir o actualizar estilos sin que explote
        def add_style(name, parent, **kwargs):
            if name in styles:
                # Si ya existe, lo modificamos
                for key, value in kwargs.items():
                    setattr(styles[name], key, value)
            else:
                # Si no existe, lo creamos
                styles.add(ParagraphStyle(name=name, parent=parent, **kwargs))

        # --- Definición de tus estilos personalizados ---
        
        # Título principal
        add_style('MainTitle', styles['Heading1'], fontSize=24, textColor=color_primario, 
                  alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6)
        
        # Título de sección (con fondo azul)
        add_style('SectionTitle', styles['Heading2'], fontSize=14, textColor=colors.white, 
                  backColor=color_primario, fontName='Helvetica-Bold', leftIndent=10, 
                  rightIndent=10, leading=20, spaceBefore=12, spaceAfter=12)

        # Texto Justificado (tu reemplazo para BodyText para evitar el KeyError)
        add_style('Justified', styles['Normal'], fontSize=10, alignment=TA_JUSTIFY, 
                  leading=16, spaceAfter=10)

        # EL QUE TE DA EL ERROR: SmallText
        add_style('SmallText', styles['Normal'], fontSize=9, textColor=color_secundario, 
                  leading=14)
        
        # EntryTitle
        add_style('EntryTitle', styles['Normal'], fontSize=12, textColor=color_primario, 
                  fontName='Helvetica-Bold', spaceAfter=4)
        
        styles.add(ParagraphStyle(
            name='CVTitle',
            parent=styles['Normal'],
            fontSize=24,
            leading=28,
            textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            alignment=TA_LEFT
        ))
        
        styles.add(ParagraphStyle(
            name='CVSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=COLOR_GRAY,
            fontName='Helvetica',
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Normal'],
            fontSize=16,
            textColor=COLOR_PRIMARY,
            fontName='Helvetica-Bold',
            spaceAfter=10,
            spaceBefore=15,
            borderPadding=(5, 5, 5, 5),
            borderColor=COLOR_PRIMARY,
            borderWidth=0,
            leftIndent=0
        ))
        
        styles.add(ParagraphStyle(
            name='JobTitle',
            parent=styles['Normal'],
            fontSize=13,
            textColor=COLOR_DARK,
            fontName='Helvetica-Bold',
            spaceAfter=3
        ))
        
        styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLOR_GRAY,
            fontName='Helvetica',
            leading=14,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            leading=16,
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='SmallGray',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLOR_GRAY,
            leading=12
        ))
        
        # Contenido
        story = []
        
        # ========== ENCABEZADO CON FOTO ==========
        header_table_data = []
        
        # Intentar cargar foto
        foto_col = []
        if perfil.foto_perfil:
            try:
                img_url = perfil.foto_perfil.url
                response = requests.get(img_url, timeout=10)
                
                if response.status_code == 200:
                    # Procesar imagen
                    img_data = BytesIO(response.content)
                    pil_img = PILImage.open(img_data)
                    
                    # Redimensionar manteniendo aspecto
                    img_width = 4*cm
                    img_height = 4*cm
                    
                    # Crear imagen para ReportLab
                    img_buffer = BytesIO()
                    pil_img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    foto = RLImage(img_buffer, width=img_width, height=img_height)
                    foto_col = [foto]
            except Exception as e:
                print(f"Error cargando foto: {e}")
                foto_col = [Paragraph("", styles['Normal'])]
        
        # Información del encabezado
        nombre_completo = f"{perfil.nombres} {perfil.apellidos}"
        
        info_col = []
        info_col.append(Paragraph(nombre_completo, styles['CVTitle']))
        # Combinamos Cédula y contacto en un solo Paragraph para mejor control
        contacto_linea = f"Cédula: {perfil.numerocedula}"
        contacto_datos = []
        if perfil.telefonoconvencional: contacto_datos.append(perfil.telefonoconvencional)
        if perfil.sitioweb: contacto_datos.append(perfil.sitioweb)
        
        datos_html = f"{contacto_linea}<br/>"
        if contacto_datos:
            datos_html += f"{' | '.join(contacto_datos)}<br/>"
        if perfil.direcciondomiciliaria:
            datos_html += f"{perfil.direcciondomiciliaria}"        
        info_col.append(Paragraph(f"Cédula: {perfil.numerocedula}", styles['CVSubtitle']))
        
        contacto_items = []
        if perfil.telefonoconvencional:
            contacto_items.append(f"📱 {perfil.telefonoconvencional}")
        if perfil.sitioweb:
            contacto_items.append(f"🌐 {perfil.sitioweb}")
        if perfil.direcciondomiciliaria:
            contacto_items.append(f"📍 {perfil.direcciondomiciliaria}")
        
        if contacto_items:
            info_col.append(Paragraph(" | ".join(contacto_items), styles['SmallGray']))
        
        # Tabla del encabezado
        if foto_col:
            header_table = Table([[foto_col, info_col]], colWidths=[5*cm, None])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(header_table)
        else:
            for item in info_col:
                story.append(item)
        
        # Línea separadora
        story.append(Spacer(1, 0.3*cm))
        sep_table = Table([['']], colWidths=[doc.width])
        sep_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, COLOR_PRIMARY)
        ]))
        story.append(sep_table)
        story.append(Spacer(1, 0.3*cm))
        
        # ========== PERFIL PROFESIONAL ==========
        if 'perfil' in secciones_seleccionadas:
            story.append(Paragraph("━━━ PERFIL PROFESIONAL", styles['SectionHeader']))
            
            # Sobre mí
            story.append(Paragraph(f"<b>Sobre mí:</b> {perfil.descripcionperfil}", styles['CustomBodyText']))
            
            # Tabla de información personal
            info_data = [
                [Paragraph('<b>Fecha de Nacimiento:</b>', styles['Normal']), 
                 Paragraph(perfil.fechanacimiento.strftime('%d/%m/%Y'), styles['Normal']),
                 Paragraph('<b>Nacionalidad:</b>', styles['Normal']),
                 Paragraph(perfil.nacionalidad, styles['Normal'])],
                
                [Paragraph('<b>Lugar de Nacimiento:</b>', styles['Normal']), 
                 Paragraph(perfil.lugarnacimiento, styles['Normal']),
                 Paragraph('<b>Estado Civil:</b>', styles['Normal']),
                 Paragraph(perfil.estadocivil, styles['Normal'])],
            ]
            # Justo antes de crear la tabla_info, asegúrate de que el estilo Normal tenga aire
            styles['Normal'].leading = 14

            tabla_info = Table(info_data, colWidths=[3.5*cm, 5*cm, 3*cm, 5*cm])
            tabla_info.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(tabla_info)
            story.append(Spacer(1, 0.5*cm))
        
        # ========== EXPERIENCIA LABORAL ==========
        if 'experiencia' in secciones_seleccionadas:
            experiencias = ExperienciaLaboral.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            ).order_by('-fechainiciogestion')
            
            if experiencias.exists():
                story.append(Paragraph("━━━ EXPERIENCIA LABORAL", styles['SectionHeader']))
                
                for exp in experiencias:
                    story.append(Paragraph(exp.cargodesempenado, styles['JobTitle']))
                    
                    fechas = f"{exp.fechainiciogestion.strftime('%b %Y')} - "
                    fechas += exp.fechafingestion.strftime('%b %Y') if exp.fechafingestion else "Actual"
                    
                    empresa = f"<b>{exp.nombreempresa}</b> • {fechas}"
                    if exp.lugarempresa:
                        empresa += f" • {exp.lugarempresa}"
                    
                    story.append(Paragraph(empresa, styles['CompanyInfo']))
                    
                    if exp.descripcionfunciones:
                        story.append(Paragraph(exp.descripcionfunciones, styles['CustomBodyText']))

                    if exp.rutacertificado:
                        cert_url = exp.rutacertificado.url
                        if '/image/upload/' in cert_url:
                            cert_url = cert_url.replace('/image/upload/', '/raw/upload/')
                        
                        # El timestamp evita que el navegador cargue un error 404 viejo
                        cert_url = f"{cert_url}?_={datetime.now().timestamp()}"
                        
                        story.append(Paragraph(
                            f'<a href="{cert_url}" color="blue"><i>Ver certificado</i></a>',
                            styles['SmallText']
                    ))
                        
                    story.append(Spacer(1, 0.4*cm))
        
        # ========== RECONOCIMIENTOS ==========
        if 'reconocimientos' in secciones_seleccionadas:
            reconocimientos = Reconocimientos.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            ).order_by('-fechareconocimiento')
            
            if reconocimientos.exists():
                story.append(Paragraph("━━━ RECONOCIMIENTOS", styles['SectionHeader']))
                
                for rec in reconocimientos:
                    titulo = f"<b>{rec.tiporeconocimiento}</b> • {rec.fechareconocimiento.strftime('%b %Y')}"
                    story.append(Paragraph(titulo, styles['JobTitle']))
                    story.append(Paragraph(rec.descripcionreconocimiento, styles['CustomBodyText']))
                    story.append(Paragraph(f"<i>Otorgado por: {rec.entidadpatrocinadora}</i>", styles['SmallGray']))
                    if rec.rutacertificado:
                        cert_url = rec.rutacertificado.url
                        if '/image/upload/' in cert_url:
                            cert_url = cert_url.replace('/image/upload/', '/raw/upload/')
                        
                        cert_url = f"{cert_url}?_={datetime.now().timestamp()}"
                        
                        story.append(Paragraph(
                            f'<a href="{cert_url}" color="blue"><i>Ver certificado</i></a>',
                            styles['SmallText']
                    ))
                    story.append(Spacer(1, 0.3*cm))
        # ========== CURSOS Y CERTIFICACIONES ==========
        if 'cursos' in secciones_seleccionadas:
            cursos = CursosRealizados.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            ).order_by('-fechainicio')
            
            if cursos.exists():
                story.append(Paragraph("━━━ CURSOS Y CERTIFICACIONES", styles['SectionHeader']))
                
                for curso in cursos:
                    story.append(Paragraph(curso.nombrecurso, styles['JobTitle']))
                    
                    fechas = f"{curso.fechainicio.strftime('%b %Y')} - {curso.fechafin.strftime('%b %Y')} • {curso.totalhoras} horas"
                    story.append(Paragraph(f"<b>{curso.entidadpatrocinadora}</b> • {fechas}", styles['CompanyInfo']))
                    
                    if curso.descripcioncurso:
                        story.append(Paragraph(curso.descripcioncurso, styles['CustomBodyText']))
                    if curso.rutacertificado:
                        cert_url = curso.rutacertificado.url
                        if '/image/upload/' in cert_url:
                            cert_url = cert_url.replace('/image/upload/', '/raw/upload/')
                        
                        cert_url = f"{cert_url}?_={datetime.now().timestamp()}"
                        
                        story.append(Paragraph(
                            f'<a href="{cert_url}" color="blue"><i>Ver certificado</i></a>',
                            styles['SmallText']
                        ))
                    story.append(Spacer(1, 0.3*cm))
        
        # ========== PRODUCTOS ACADÉMICOS ==========
        if 'productosacademicos' in secciones_seleccionadas:
            productos = ProductosAcademicos.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            )
            
            if productos.exists():
                story.append(Paragraph("━━━ PRODUCTOS ACADÉMICOS", styles['SectionHeader']))
                
                for prod in productos:
                    story.append(Paragraph(f"<b>{prod.nombrerecurso}</b> ({prod.clasificador})", styles['JobTitle']))
                    story.append(Paragraph(prod.descripcion, styles['CustomBodyText']))
                    story.append(Spacer(1, 0.2*cm))
        
        # ========== PRODUCTOS LABORALES ==========
        if 'productoslaborales' in secciones_seleccionadas:
            productos = ProductosLaborales.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            ).order_by('-fechaproducto')
            
            if productos.exists():
                story.append(Paragraph("━━━ PRODUCTOS LABORALES", styles['SectionHeader']))
                
                for prod in productos:
                    story.append(Paragraph(f"<b>{prod.nombreproducto}</b> • {prod.fechaproducto.strftime('%b %Y')}", styles['JobTitle']))
                    story.append(Paragraph(prod.descripcion, styles['CustomBodyText']))
                    story.append(Spacer(1, 0.2*cm))
        
        # ========== VENTA GARAGE ==========
        if 'ventagarage' in secciones_seleccionadas:
            productos = VentaGarage.objects.filter(
                idperfilconqueestaactivo=perfil,
                activarparaqueseveaenfront=True
            )
            
            if productos.exists():
                story.append(Paragraph("━━━ ARTÍCULOS EN VENTA", styles['SectionHeader']))
                
                for prod in productos:
                    # Intentar incluir imagen
                    if prod.imagen_producto:
                        try:
                            response = requests.get(prod.imagen_producto.url, timeout=10)
                            if response.status_code == 200:
                                img_buffer = BytesIO(response.content)
                                img = RLImage(img_buffer, width=3*cm, height=3*cm)
                                
                                info_text = f"""
                                <b>{prod.nombreproducto}</b><br/>
                                <font color='#6c757d'>Estado: {prod.estadoproducto}</font><br/>
                                <font size='12' color='#198754'><b>${prod.valordelbien}</b></font><br/>
                                <font size='9'>{prod.descripcion[:100]}</font>
                                """
                                
                                tabla_prod = Table([[img, Paragraph(info_text, styles['Normal'])]], colWidths=[3.5*cm, None])
                                tabla_prod.setStyle(TableStyle([
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                    ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
                                    ('PADDING', (0, 0), (-1, -1), 8),
                                ]))
                                story.append(tabla_prod)
                                story.append(Spacer(1, 0.3*cm))
                            else:
                                raise Exception("No se pudo cargar imagen")
                        except:
                            # Sin imagen
                            story.append(Paragraph(f"<b>{prod.nombreproducto}</b> • ${prod.valordelbien}", styles['JobTitle']))
                            story.append(Paragraph(f"Estado: {prod.estadoproducto}", styles['SmallGray']))
                            story.append(Paragraph(prod.descripcion, styles['CustomBodyText']))
                    else:
                        story.append(Paragraph(f"<b>{prod.nombreproducto}</b> • ${prod.valordelbien}", styles['JobTitle']))
                        story.append(Paragraph(f"Estado: {prod.estadoproducto}", styles['SmallGray']))
                        story.append(Paragraph(prod.descripcion, styles['CustomBodyText']))
                    
                    story.append(Spacer(1, 0.2*cm))
        
        # Generar PDF
        doc.build(story, canvasmaker=FooterCanvas)
        
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        filename = slugify(f"cv {perfil.nombres} {perfil.apellidos}")
        response['Content-Disposition'] = f'inline; filename="{filename}.pdf"'
        response['Content-Transfer-Encoding'] = 'binary'
        
        return response
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        print("ERROR AL GENERAR PDF:")
        print(error_traceback)
        return JsonResponse({'error': str(e), 'traceback': error_traceback}, status=500)