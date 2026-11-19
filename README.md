# Taller 3 - Sistema de Gestión de Signos Vitales

 Aplicación en Python para la generación, validación, almacenamiento local y gestión en la nube (MongoDB Atlas) de registros de signos vitales de pacientes.

## Estructura del Proyecto
- `main.py`: Programa principal con menú interactivo e integración completa.
- `data/txt/datos.txt`: Registros ordenados por frecuencia cardiaca en texto plano.
- `data/csv/datos.csv`: Registros exportados en formato tabular CSV.
- `data/json/datos.json`: Registros exportados e importados en formato JSON.
- `resultados_mongo.json`: Resultados de consultas analíticas (promedio de FC y pacientes con SpO2 < 94%).
- `log.txt`: Registro cronológico de acciones y errores del sistema.

## Requisitos e Instalación
1. Instalar dependencia de MongoDB:
   ```bash
   pip install pymongo
   ```
2. Ejecutar el programa principal:
   ```bash
   python main.py
   ```

## Funcionalidades Implementadas
1. **Generación y Ordenamiento:** Creación de 50 registros aleatorios (`ID-001` a `ID-050`) ordenados ascendentemente por frecuencia cardiaca (`fc`).
2. **Gestión de Archivos y Sistema:** Creación automática de directorios (`/data/txt`, `/data/csv`, `/data/json`), exportación/importación de archivos y bitácora en `log.txt`.
3. **Validación con Expresiones Regulares:** Verificación estricta de patrones en `id`, `fr`, `fc` y `spo2`.
4. **Base de Datos NoSQL (MongoDB Atlas):** Inserción de documentos validados en la colección `signos_vitales`, cálculo de promedio de frecuencia cardiaca, filtrado de SpO2 < 94% y búsqueda por `ID`.