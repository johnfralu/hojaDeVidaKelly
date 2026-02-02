from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from cloudinary.models import CloudinaryField

class DatosPersonales(models.Model):
    SEXO_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
    ]
    
    idperfil = models.AutoField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.IntegerField(default=1)
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)
    fechanacimiento = models.DateField()
    numerocedula = models.CharField(max_length=10, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    foto_perfil = CloudinaryField('image', folder='perfil', blank=True, null=True, help_text='Imagen cuadrada de mínimo 400x400 px')
    
    class Meta:
        verbose_name = 'Dato Personal'
        verbose_name_plural = 'Datos Personales'
        db_table = 'datospersonales'
    
    def clean(self):
        # Validar que la fecha de nacimiento no sea futura
        if self.fechanacimiento and self.fechanacimiento > timezone.now().date():
            raise ValidationError({'fechanacimiento': 'La fecha de nacimiento no puede ser futura.'})
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class ExperienciaLaboral(models.Model):
    idexperiencialaboral = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    cargodesempenado = models.CharField(max_length=100)
    nombreempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50, blank=True, null=True)
    emailempresa = models.CharField(max_length=100, blank=True, null=True)
    sitiowebempresa = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoempresarial = models.CharField(max_length=60, blank=True, null=True)
    fechainiciogestion = models.DateField()
    fechafingestion = models.DateField(blank=True, null=True)
    descripcionfunciones = models.TextField(blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('archivo', resource_type = 'raw', folder = 'certificados/experiencia/', null = True, blank = True, help_text='Certificado en PDF')
    
    class Meta:
        verbose_name = 'Experiencia Laboral'
        verbose_name_plural = 'Experiencias Laborales'
        db_table = 'experiencialaboral'
        ordering = ['-fechainiciogestion']
    
    def clean(self):
        # Validar que fecha de inicio no sea posterior a fecha fin
        if self.fechafingestion and self.fechainiciogestion > self.fechafingestion:
            raise ValidationError({
                'fechafingestion': 'La fecha de finalización no puede ser anterior a la fecha de inicio.'
            })
        
        # Validar que las fechas no sean futuras
        if self.fechainiciogestion > timezone.now().date():
            raise ValidationError({'fechainiciogestion': 'La fecha de inicio no puede ser futura.'})
        
        if self.fechafingestion and self.fechafingestion > timezone.now().date():
            raise ValidationError({'fechafingestion': 'La fecha de finalización no puede ser futura.'})
    
    def __str__(self):
        return f"{self.cargodesempenado} - {self.nombreempresa}"


class Reconocimientos(models.Model):
    TIPO_CHOICES = [
        ('Académico', 'Académico'),
        ('Público', 'Público'),
        ('Privado', 'Privado'),
    ]
    
    idreconocimiento = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES)
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.TextField()
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('archivo', resource_type = 'raw', folder = 'certificados/reconocimientos/', null = True, blank = True, help_text='Certificado en PDF')
    
    class Meta:
        verbose_name = 'Reconocimiento'
        verbose_name_plural = 'Reconocimientos'
        db_table = 'reconocimientos'
        ordering = ['-fechareconocimiento']
    
    def clean(self):
        if self.fechareconocimiento > timezone.now().date():
            raise ValidationError({'fechareconocimiento': 'La fecha de reconocimiento no puede ser futura.'})
    
    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.descripcionreconocimiento[:50]}"


class CursosRealizados(models.Model):
    idcursorealizado = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    totalhoras = models.IntegerField()
    descripcioncurso = models.TextField(blank=True, null=True)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = CloudinaryField('archivo', resource_type = 'raw', folder = 'certificados/cursos/', null = True, blank = True, help_text='Certificado en PDF')
    
    class Meta:
        verbose_name = 'Curso Realizado'
        verbose_name_plural = 'Cursos Realizados'
        db_table = 'cursosrealizados'
        ordering = ['-fechainicio']
    
    def clean(self):
        if self.fechafin and self.fechainicio > self.fechafin:
            raise ValidationError({
                'fechafin': 'La fecha de finalización no puede ser anterior a la fecha de inicio.'
            })
        
        if self.totalhoras and self.totalhoras < 0:
            raise ValidationError({'totalhoras': 'Las horas totales no pueden ser negativas.'})
        
        if self.fechafin and self.fechafin > timezone.now().date():
            raise ValidationError({'fechafin': 'La fecha de finalización no puede ser futura.'})
    
    def __str__(self):
        return self.nombrecurso


class ProductosAcademicos(models.Model):
    idproductoacademico = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombrerecurso = models.CharField(max_length=100)
    clasificador = models.CharField(max_length=100)
    descripcion = models.TextField()
    activarparaqueseveaenfront = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto Académico'
        verbose_name_plural = 'Productos Académicos'
        db_table = 'productosacademicos'
    
    def __str__(self):
        return self.nombrerecurso


class ProductosLaborales(models.Model):
    idproductolaboral = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombreproducto = models.CharField(max_length=100)
    fechaproducto = models.DateField()
    descripcion = models.TextField()
    activarparaqueseveaenfront = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto Laboral'
        verbose_name_plural = 'Productos Laborales'
        db_table = 'productoslaborales'
        ordering = ['-fechaproducto']
    
    def clean(self):
        if self.fechaproducto > timezone.now().date():
            raise ValidationError({'fechaproducto': 'La fecha del producto no puede ser futura.'})
    
    def __str__(self):
        return self.nombreproducto


class VentaGarage(models.Model):
    ESTADO_CHOICES = [
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
    ]
    
    idventagarage = models.AutoField(primary_key=True)
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombreproducto = models.CharField(max_length=100)
    estadoproducto = models.CharField(max_length=40, choices=ESTADO_CHOICES)
    descripcion = models.TextField()
    valordelbien = models.DecimalField(max_digits=7, decimal_places=2)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    imagen_producto = CloudinaryField('image', folder='garage', blank=True, null=True, help_text='Imagen del producto en venta')
    
    class Meta:
        verbose_name = 'Venta Garage'
        verbose_name_plural = 'Ventas Garage'
        db_table = 'ventagarage'
    
    def clean(self):
        if self.valordelbien and self.valordelbien < 0:
            raise ValidationError({'valordelbien': 'El valor del bien no puede ser negativo.'})
    
    def __str__(self):
        return self.nombreproducto


class ConfiguracionSecciones(models.Model):
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE)
    mostrar_perfil = models.BooleanField(default=True, verbose_name='Mostrar Perfil Profesional')
    mostrar_experiencia = models.BooleanField(default=True, verbose_name='Mostrar Experiencia Laboral')
    mostrar_reconocimientos = models.BooleanField(default=True, verbose_name='Mostrar Reconocimientos')
    mostrar_cursos = models.BooleanField(default=True, verbose_name='Mostrar Cursos Realizados')
    mostrar_productos_academicos = models.BooleanField(default=True, verbose_name='Mostrar Productos Académicos')
    mostrar_productos_laborales = models.BooleanField(default=True, verbose_name='Mostrar Productos Laborales')
    mostrar_venta_garage = models.BooleanField(default=True, verbose_name='Mostrar Venta Garage')
    
    class Meta:
        verbose_name = 'Configuración de Secciones'
        verbose_name_plural = 'Configuraciones de Secciones'
    
    def __str__(self):
        return f"Configuración de {self.perfil}"