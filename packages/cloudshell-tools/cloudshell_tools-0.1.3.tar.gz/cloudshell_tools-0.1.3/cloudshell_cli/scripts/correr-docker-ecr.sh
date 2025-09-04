#!/bin/bash
set -euo pipefail

# ================================
# Función para detectar cuenta y región automáticamente
# ================================
detect_account_and_region() {
  AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
  AWS_REGION=$(echo ${AWS_REGION:-})

  if [ -z "$AWS_REGION" ]; then
    # Si la región no está configurada, usar la de CloudShell
    AWS_REGION=$(curl -s 169.254.169.254/latest/meta-data/placement/region)
  fi
}

# ================================
# Menú para elegir modo de cuenta/región
# ================================
echo "Selecciona cómo quieres configurar la cuenta y la región:"
echo "1) Detectar automáticamente (cuenta y región actuales)"
echo "2) Especificar manualmente"
read -p "Opción [1/2]: " ACCOUNT_OPTION

if [ "$ACCOUNT_OPTION" == "1" ]; then
  detect_account_and_region
  echo "✅ Cuenta detectada: $AWS_ACCOUNT_ID"
  echo "✅ Región detectada: $AWS_REGION"

elif [ "$ACCOUNT_OPTION" == "2" ]; then
  read -p "Ingresa el AWS Account ID: " AWS_ACCOUNT_ID
  read -p "Ingresa la región (ej: us-east-1): " AWS_REGION
  echo "✅ Cuenta ingresada: $AWS_ACCOUNT_ID"
  echo "✅ Región ingresada: $AWS_REGION"
else
  echo "❌ Opción inválida"
  exit 1
fi

# ================================
# Preguntar URI de la imagen
# ================================
read -p "Ingresa la URI de la imagen en ECR (ej: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/mi-repo:latest): " IMAGE_URI

# ================================
# Login en ECR
# ================================
echo "🔑 Haciendo login en ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# ================================
# Preguntar puerto
# ================================
read -p "¿Con qué puerto quieres mapear la aplicación localmente? (ej: 8080): " PORT

# ================================
# Menú de opciones de ejecución
# ================================
echo "Selecciona una opción:"
echo "1) Correr la imagen normalmente (docker run -p $PORT:$PORT)"
echo "2) Correr la imagen y entrar con docker exec"
read -p "Opción [1/2]: " OPTION

# Nombre del contenedor (para identificarlo en exec)
CONTAINER_NAME="ecr-container-test"

if [ "$OPTION" == "1" ]; then
    echo "🚀 Corriendo contenedor desde $IMAGE_URI ..."
    docker run --rm -p "$PORT:$PORT" --name "$CONTAINER_NAME" "$IMAGE_URI"

elif [ "$OPTION" == "2" ]; then
    echo "🚀 Corriendo contenedor en segundo plano..."
    docker run -d -p "$PORT:$PORT" --name "$CONTAINER_NAME" "$IMAGE_URI"

    echo "🔗 Entrando al contenedor con bash..."
    docker exec -it "$CONTAINER_NAME" /bin/bash

    echo "📌 Cuando termines, puedes salir con 'exit'."
    echo "🛑 Si quieres parar el contenedor después, ejecuta:"
    echo "    docker stop $CONTAINER_NAME"

else
    echo "❌ Opción inválida"
    exit 1
fi
