from django import template

register = template.Library()

@register.filter(name='cloudinary_raw')
def cloudinary_raw(value):
    """Convierte URL de Cloudinary de image/upload a raw/upload para PDFs"""
    if value and 'cloudinary.com' in str(value):
        return str(value).replace('/image/upload/', '/raw/upload/')
    return value