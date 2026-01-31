from cloudinary_storage.storage import RawMediaCloudinaryStorage

class PublicRawMediaCloudinaryStorage(RawMediaCloudinaryStorage):
    """Storage personalizado para archivos raw públicos en Cloudinary"""
    
    def url(self, name):
        """Genera URL pública para archivos raw"""
        try:
            # Obtener la URL base
            url = super().url(name)
            # Asegurarse de que use el tipo 'raw' y sea público
            if 'image/upload' in url:
                url = url.replace('/image/upload/', '/raw/upload/')
            return url
        except:
            return name