import cloudinary
from django.conf import settings

def test_cloudinary():
    print("=== CLOUDINARY TEST ===")
    print(f"Cloud Name: {settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')}")
    print(f"API Key: {settings.CLOUDINARY_STORAGE.get('API_KEY')[:10]}...")
    print(f"Storage Backend: {settings.DEFAULT_FILE_STORAGE}")
    print("======================")