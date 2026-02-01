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

def get_perfil_activo():
    """Obtiene el perfil activo"""
    return DatosPersonales.objects.filter(perfilactivo=1).first()

def get_configuracion(perfil):
    """Obtiene o crea la configuración de secciones"""
    config, created = ConfiguracionSecciones.objects.get_or_create(perfil=perfil)
    return config

def perfil_profesional(request):
    perfil = DatosPersonales.objects.first()
    config = ConfiguracionSecciones.objects.first()
    
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

@require_POST
def actualizar_configuracion(request):
    """Actualiza la configuración de secciones visibles"""
    perfil = get_perfil_activo()
    if not perfil:
        return JsonResponse({'success': False, 'error': 'No hay perfil activo'})
    
    config = get_configuracion(perfil)
    data = json.loads(request.body)
    
    config.mostrar_perfil = data.get('mostrar_perfil', True)
    config.mostrar_experiencia = data.get('mostrar_experiencia', True)
    config.mostrar_reconocimientos = data.get('mostrar_reconocimientos', True)
    config.mostrar_cursos = data.get('mostrar_cursos', True)
    config.mostrar_productos_academicos = data.get('mostrar_productos_academicos', True)
    config.mostrar_productos_laborales = data.get('mostrar_productos_laborales', True)
    config.mostrar_venta_garage = data.get('mostrar_venta_garage', True)
    config.save()
    
    return JsonResponse({'success': True})

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
        self.setStrokeColor(colors.HexColor('#0d6efd'))
        self.setLineWidth(1)
        self.line(2*cm, 2*cm, A4[0] - 2*cm, 2*cm)
        
        # Número de página
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(A4[0] - 2*cm, 1.5*cm, f"Página {self._pageNumber} de {page_count}")
        
        # Fecha de generación
        self.drawString(2*cm, 1.5*cm, f"Generado: {datetime.now().strftime('%d/%m/%Y')}")

def generar_pdf(request):
    """Genera PDF con diseño premium en colores pasteles basado en tu estructura original"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        data = json.loads(request.body)
        secciones_seleccionadas = data.get('secciones', [])
        perfil = get_perfil_activo()
        
        if not perfil:
            return JsonResponse({'error': 'No hay perfil activo'}, status=400)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=2.5*cm
        )
        
        # --- PALETA DE COLORES PASTELES ---
        C_LAVANDA = colors.HexColor('#818cf8')  # Principal / Secciones
        C_MENTA = colors.HexColor('#10b981')    # Cursos
        C_SALMON = colors.HexColor('#fb7185')   # Laboral
        C_CIELO = colors.HexColor('#0ea5e9')    # Académico
        C_TEXT_DARK = colors.HexColor('#1e293b')
        C_TEXT_GRAY = colors.HexColor('#64748b')
        C_BG_LIGHT = colors.HexColor('#f8fafc')
        
        styles = getSampleStyleSheet()

        # --- RE-DEFINICIÓN DE ESTILOS PARA EVITAR KEYERROR ---
        def get_style(name, parent_style, **kwargs):
            if name in styles:
                return styles[name]
            new_style = ParagraphStyle(name=name, parent=styles[parent_style], **kwargs)
            styles.add(new_style)
            return new_style

        # Estilos personalizados
        title_style = get_style('CVTitlePremium', 'Normal', fontSize=26, fontName='Helvetica-Bold', textColor=C_TEXT_DARK, spaceAfter=2)
        header_mini = get_style('HeaderMini', 'Normal', fontSize=9, textColor=C_TEXT_GRAY, leading=11)
        section_style = get_style('SectionHeaderPremium', 'Normal', fontSize=14, fontName='Helvetica-Bold', textColor=C_LAVANDA, spaceBefore=15, spaceAfter=10)
        body_style = get_style('CustomBodyTextPremium', 'Normal', fontSize=10, alignment=TA_JUSTIFY, leading=14, textColor=C_TEXT_DARK)
        job_style = get_style('JobTitlePremium', 'Normal', fontSize=12, fontName='Helvetica-Bold', textColor=C_TEXT_DARK)
        small_gray = get_style('SmallGrayPremium', 'Normal', fontSize=9, textColor=C_TEXT_GRAY)

        story = []

        # ========== ENCABEZADO PREMIUM ==========
        foto_element = []
        if perfil.foto_perfil:
            try:
                response = requests.get(perfil.foto_perfil.url, timeout=5)
                img = PILImage.open(BytesIO(response.content))
                img_buffer = BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                # Foto elegante
                foto = RLImage(img_buffer, width=3.5*cm, height=3.5*cm)
                foto_element = [foto]
            except:
                foto_element = []

        info_header = [
            Paragraph(f"{perfil.nombres} {perfil.apellidos}", title_style),
            Paragraph(f"<font color='#818cf8'><b>ID:</b></font> {perfil.numerocedula} | 📍 {perfil.lugarnacimiento}", styles['Normal']),
            Spacer(1, 6),
            Paragraph(f"📧 {perfil.sitioweb if perfil.sitioweb else 'No especificado'}", header_mini),
            Paragraph(f"📱 {perfil.telefonoconvencional}", header_mini),
            Paragraph(f"🏠 {perfil.direcciondomiciliaria}", header_mini),
        ]

        header_table = Table([[foto_element, info_header]], colWidths=[4*cm, 14*cm])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
        story.append(header_table)
        
        # Línea decorativa Lavanda
        line_t = Table([['']], colWidths=[18*cm], rowHeights=[2])
        line_t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), C_LAVANDA)]))
        story.append(Spacer(1, 10))
        story.append(line_t)

        # ========== SECCIÓN: PERFIL ==========
        if 'perfil' in secciones_seleccionadas:
            story.append(Paragraph("SOBRE MÍ", section_style))
            story.append(Paragraph(perfil.descripcionperfil, body_style))
            
            # Cuadro de datos personales pastel
            p_data = [
                [Paragraph(f"<b>Nacimiento:</b> {perfil.fechanacimiento.strftime('%d/%m/%Y')}", header_mini),
                 Paragraph(f"<b>Nacionalidad:</b> {perfil.nacionalidad}", header_mini)],
                [Paragraph(f"<b>Estado Civil:</b> {perfil.estadocivil}", header_mini),
                 Paragraph(f"<b>Ubicación:</b> {perfil.lugarnacimiento}", header_mini)]
            ]
            t_p = Table(p_data, colWidths=[9*cm, 9*cm])
            t_p.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), C_BG_LIGHT),
                ('BOX', (0,0), (-1,-1), 0.5, colors.white),
                ('PADDING', (0,0), (-1,-1), 6)
            ]))
            story.append(Spacer(1, 8))
            story.append(t_p)

        # ========== SECCIÓN: EXPERIENCIA (SALMÓN) ==========
        if 'experiencia' in secciones_seleccionadas:
            exps = ExperienciaLaboral.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True).order_by('-fechainiciogestion')
            if exps.exists():
                story.append(Paragraph("<font color='#fb7185'>EXPERIENCIA LABORAL</font>", section_style))
                for exp in exps:
                    f_ini = exp.fechainiciogestion.strftime('%Y')
                    f_fin = exp.fechafingestion.strftime('%Y') if exp.fechafingestion else "Actual"
                    
                    data_exp = [[
                        Paragraph(f"<b>{exp.cargodesempenado}</b><br/><font color='#64748b'>{exp.nombreempresa}</font>", styles['Normal']),
                        Paragraph(f"{f_ini} - {f_fin}", small_gray)
                    ]]
                    t = Table(data_exp, colWidths=[14*cm, 4*cm])
                    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
                    story.append(t)
                    if exp.descripcionfunciones:
                        story.append(Paragraph(exp.descripcionfunciones, body_style))
                    story.append(Spacer(1, 6))

        # ========== SECCIÓN: RECONOCIMIENTOS ==========
        if 'reconocimientos' in secciones_seleccionadas:
            recs = Reconocimientos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
            if recs.exists():
                story.append(Paragraph("RECONOCIMIENTOS", section_style))
                for r in recs:
                    story.append(Paragraph(f"🏆 <b>{r.tiporeconocimiento}</b> - {r.entidadpatrocinadora}", styles['Normal']))
                    story.append(Paragraph(r.descripcionreconocimiento, body_style))
                    story.append(Spacer(1, 4))

        # ========== SECCIÓN: CURSOS (MENTA) ==========
        if 'cursos' in secciones_seleccionadas:
            cursos = CursosRealizados.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
            if cursos.exists():
                story.append(Paragraph("<font color='#10b981'>CURSOS Y CERTIFICACIONES</font>", section_style))
                for c in cursos:
                    story.append(Paragraph(f"✔ <b>{c.nombrecurso}</b> | {c.entidadpatrocinadora} ({c.totalhoras}h)", styles['Normal']))
                    story.append(Spacer(1, 4))

        # ========== SECCIÓN: PRODUCTOS (CIELO) ==========
        if 'productosacademicos' in secciones_seleccionadas:
            prods = ProductosAcademicos.objects.filter(idperfilconqueestaactivo=perfil, activarparaqueseveaenfront=True)
            if prods.exists():
                story.append(Paragraph("<font color='#0ea5e9'>PROYECTOS ACADÉMICOS</font>", section_style))
                for p in prods:
                    story.append(Paragraph(f"• <b>{p.nombrerecurso}</b>: {p.descripcion}", header_mini))
                    story.append(Spacer(1, 4))

        # CONSTRUCCIÓN FINAL
        doc.build(story, canvasmaker=FooterCanvas)
        buffer.seek(0)
        
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="CV_{slugify(perfil.nombres)}.pdf"'
        return response

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)