#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== INICIO DEL BUILD ==="

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsu

# Verificar Cloudinary
echo ""
echo "=== VERIFICANDO CLOUDINARY ==="
echo "CLOUDINARY_CLOUD_NAME: ${CLOUDINARY_CLOUD_NAME:-'NO CONFIGURADO'}"
echo "CLOUDINARY_API_KEY: ${CLOUDINARY_API_KEY:0:10}..."
echo "CLOUDINARY_API_SECRET: ${CLOUDINARY_API_SECRET:0:10}..."

if [ -z "$CLOUDINARY_CLOUD_NAME" ]; then
    echo "❌ ERROR: CLOUDINARY_CLOUD_NAME no está configurado"
else
    echo "✅ CLOUDINARY_CLOUD_NAME está configurado"
fi

if [ -z "$CLOUDINARY_API_KEY" ]; then
    echo "❌ ERROR: CLOUDINARY_API_KEY no está configurado"
else
    echo "✅ CLOUDINARY_API_KEY está configurado"
fi

if [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "❌ ERROR: CLOUDINARY_API_SECRET no está configurado"
else
    echo "✅ CLOUDINARY_API_SECRET está configurado"
fi

echo "==========================="
echo ""
echo "=== FIN DEL BUILD ==="