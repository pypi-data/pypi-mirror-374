#!/bin/bash
set -e

echo "=============================="
echo "  🚀 Crear y subir imagen a ECR"
echo "=============================="

# ================================
# Entrada del usuario
# ================================
read -p "👉 Ingresa la región AWS (ej: us-east-1): " AWS_REGION
read -p "👉 Ingresa el ID de la cuenta AWS (ej: 123456789012): " AWS_ACCOUNT_ID
read -p "👉 Ingresa el nombre del repositorio ECR (ej: hello-docker-image): " REPO_NAME
read -p "👉 Ingresa la ruta de la carpeta donde está el Dockerfile (ej: ../dockerfiles): " DOCKERFILE_PATH
read -p "👉 Ingresa el nombre del Dockerfile (ej: app.Dockerfile): " DOCKERFILE
read -p "👉 Ingresa el tag de la imagen (ej: v1.0.0): " IMAGE_TAG

# ================================
# Validación mínima
# ================================
if [ -z "$AWS_REGION" ] || [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$REPO_NAME" ] || [ -z "$DOCKERFILE_PATH" ] || [ -z "$DOCKERFILE" ] || [ -z "$IMAGE_TAG" ]; then
    echo "❌ Todos los campos son obligatorios"
    exit 1
fi

# ================================
# Construcción de la imagen
# ================================
echo "📦 Construyendo imagen desde $DOCKERFILE_PATH/$DOCKERFILE ..."
docker build -f "$DOCKERFILE_PATH/$DOCKERFILE" -t $REPO_NAME:$IMAGE_TAG $DOCKERFILE_PATH

echo "✅ Imagen construida localmente: $REPO_NAME:$IMAGE_TAG"

# ================================
# Login en ECR
# ================================
echo "🔑 Logueando en Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# ================================
# Verificar repositorio (crear si no existe)
# ================================
if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION >/dev/null 2>&1; then
    echo "📂 Repositorio $REPO_NAME no existe, creando..."
    aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION
    echo "✅ Repositorio creado."
fi

# ================================
# Push a ECR
# ================================
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG"

echo "🏷️ Etiquetando imagen como $IMAGE_URI"
docker tag $REPO_NAME:$IMAGE_TAG $IMAGE_URI

echo "🚀 Subiendo imagen a ECR..."
docker push $IMAGE_URI

echo "✅ Imagen subida exitosamente: $IMAGE_URI"
