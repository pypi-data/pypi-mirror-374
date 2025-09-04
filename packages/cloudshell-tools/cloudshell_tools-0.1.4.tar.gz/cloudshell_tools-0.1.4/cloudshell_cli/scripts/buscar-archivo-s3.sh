#!/bin/bash

# Pedir la palabra clave al usuario
read -p "Ingresa la palabra clave para buscar el archivo: " keyword

# Obtener lista de buckets
buckets=$(aws s3 ls | awk '{print $3}')

echo "🔎 Buscando archivos que coincidan con: '$keyword' ..."

# Recorrer cada bucket
for bucket in $buckets; do
    echo "📂 Revisando bucket: $bucket"
    
    # Buscar coincidencias en los objetos
    resultados=$(aws s3 ls s3://$bucket --recursive | grep "$keyword")

    if [ -n "$resultados" ]; then
        echo "✅ Coincidencias en $bucket:"
        echo "$resultados"
    else
        echo "❌ No se encontraron coincidencias en $bucket"
    fi
    echo "-----------------------------------"
done
