from pymongo import MongoClient
import random
import os
import csv
import json
import shutil
from datetime import datetime
import re

URI = "mongodb+srv://lcarolinagomez_db_user:CxEsL4pu6VbX0IVu@cluster0.d4noy6p.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(URI)
db = client["taller_3"]
coleccion = db["signos_vitales"]

# --- 1. GENERACIÓN Y ORDENAMIENTO DE DATOS ---
def datos_aleatorios(can_d=50):
    pacientes = []
    for i in range(1, can_d + 1):
        ID = f"ID-{i:03d}"
        fr = f"{random.randint(18, 99)} Años"
        fc_valor = random.randint(1, 300)
        fc = f"{fc_valor:03d}ppm"
        spo2 = f"{random.randint(0, 100)}%"
        paciente = {"id": ID, "fr": fr, "fc": fc, "spo2": spo2}
        pacientes.append(paciente)
    return pacientes

def ordenar_datos(pacientes):
    return sorted(pacientes, key=lambda x: int(x["fc"].replace("ppm", "")))

# --- 2 y 3. ARCHIVOS, CARPETAS Y LOG ---
def guardar_log(mensaje):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(f"[{hora}] {mensaje}\n")

def crear_carpetas():
    for ruta in ["data/txt", "data/csv", "data/json"]:
        os.makedirs(ruta, exist_ok=True)
    guardar_log("Carpetas /data/txt, /data/csv y /data/json creadas.")

def guardar_archivos(pacientes):
    try:
        crear_carpetas()

        with open("datos.txt", "w", encoding="utf-8") as f_txt:
            for p in pacientes:
                f_txt.write(f"{p['id']} | {p['fr']} | {p['fc']} | {p['spo2']}\n")
        shutil.move("datos.txt", "data/txt/datos.txt")
        guardar_log("Archivo datos.txt guardado y movido.")

        with open("datos.csv", "w", newline="", encoding="utf-8") as f_csv:
            escritor = csv.DictWriter(f_csv, fieldnames=["id", "fr", "fc", "spo2"])
            escritor.writeheader()
            escritor.writerows(pacientes)
        shutil.move("datos.csv", "data/csv/datos.csv")
        guardar_log("Archivo datos.csv guardado y movido.")

        with open("datos.json", "w", encoding="utf-8") as f_json:
            json.dump(pacientes, f_json, indent=4, ensure_ascii=False)
        shutil.move("datos.json", "data/json/datos.json")
        guardar_log("Archivo datos.json exportado y movido.")

        print("Archivos guardados y organizados correctamente.")
    except Exception as e:
        guardar_log(f"ERROR en archivos: {e}")
        print(f"Error al guardar archivos: {e}")

def leer_json(ruta="data/json/datos.json"):
    try:
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No existe {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            pacientes = json.load(f)
        guardar_log(f"Datos importados desde {ruta}.")
        return pacientes
    except Exception as e:
        guardar_log(f"ERROR al leer JSON: {e}")
        print(f"Error al importar JSON: {e}")
        return []

# --- 4. VALIDACIÓN CON EXPRESIONES REGULARES ---
def validar_dato(paciente):
    ok_id = bool(re.fullmatch(r"^ID-\d{3}$", str(paciente.get("id", ""))))
    ok_fr = bool(re.fullmatch(r"^\d{1,3} Años$", str(paciente.get("fr", ""))))
    ok_fc = bool(re.fullmatch(r"^\d{3}ppm$", str(paciente.get("fc", ""))))
    ok_spo2 = bool(re.fullmatch(r"^\d{1,3}%$", str(paciente.get("spo2", ""))))
    return ok_id and ok_fr and ok_fc and ok_spo2

def filtrar_datos(pacientes):
    validos = []
    for p in pacientes:
        if validar_dato(p):
            validos.append(p)
        else:
            guardar_log(f"Registro inválido descartado: {p}")
    guardar_log(f"Validación completada: {len(validos)} de {len(pacientes)} válidos.")
    return validos

# --- 5. BASE DE DATOS MONGODB ATLAS ---
def subir_mongo(pacientes):
    try:
        if not pacientes:
            print("No hay datos válidos para subir.")
            return
        coleccion.delete_many({})
        copia = [p.copy() for p in pacientes]
        res = coleccion.insert_many(copia)
        guardar_log(f"Insertados {len(res.inserted_ids)} registros en MongoDB.")
        print(f"Se insertaron {len(res.inserted_ids)} registros en MongoDB Atlas.")
    except Exception as e:
        guardar_log(f"ERROR al subir a MongoDB: {e}")
        print(f"Error al insertar en MongoDB: {e}")

def consultar_mongo():
    try:
        docs = list(coleccion.find({}, {"_id": 0}))
        if not docs:
            print("La colección está vacía.")
            return

        valores_fc = [int(d["fc"].replace("ppm", "")) for d in docs]
        promedio_fc = round(sum(valores_fc) / len(valores_fc), 2)
        spo2_bajo = [d for d in docs if int(d["spo2"].replace("%", "")) < 94]

        resultados = {
            "promedio_frecuencia_cardiaca_ppm": promedio_fc,
            "total_documentos_spo2_menor_94": len(spo2_bajo),
            "documentos_spo2_menor_94": spo2_bajo
        }

        with open("resultados_mongo.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)

        guardar_log("Consultas MongoDB exportadas a resultados_mongo.json.")
        print(f"Promedio FC: {promedio_fc} ppm")
        print(f"Pacientes con SpO2 < 94%: {len(spo2_bajo)}")
        print("Resultados exportados a 'resultados_mongo.json'.")
    except Exception as e:
        guardar_log(f"ERROR en consultas MongoDB: {e}")
        print(f"Error al consultar MongoDB: {e}")
def buscar_por_id(id_buscar):
    try:
        paciente = coleccion.find_one({"id": id_buscar}, {"_id": 0})
        if paciente:
            print("Paciente encontrado en MongoDB:", paciente)
            guardar_log(f"Consulta por ID exitosa: {id_buscar}")
        else:
            print(f"No se encontró ningún paciente con ID '{id_buscar}'.")
    except Exception as e:
        guardar_log(f"ERROR al buscar ID {id_buscar}: {e}")
        print(f"Error en consulta: {e}")
def menu():
    pacientes = []
    pacientes_validos = []

    while True:
        print("\n=== SISTEMA DE SIGNOS VITALES ===")
        print("1. Generar 50 pacientes aleatorios y ordenarlos")
        print("2. Ingresar un paciente manualmente")
        print("3. Exportar archivos (TXT, CSV, JSON)")
        print("4. Importar datos desde JSON")
        print("5. Validar datos con Regex")
        print("6. Subir datos validados a MongoDB Atlas")
        print("7. Ejecutar consultas generales en MongoDB (Promedio FC y SpO2 < 94)")
        print("8. Buscar paciente en MongoDB por ID")
        print("0. Salir")

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            datos = datos_aleatorios()
            pacientes = ordenar_datos(datos)
            print(f"Se generaron y ordenaron {len(pacientes)} pacientes.")

        elif opcion == "2":
            nuevo = {
                "id": input("ID (ej. ID-051): ").strip(),
                "fr": input("Edad/FR (ej. 25 Años): ").strip(),
                "fc": input("Frecuencia cardiaca (ej. 085ppm): ").strip(),
                "spo2": input("SpO2 (ej. 98%): ").strip()
            }
            if validar_dato(nuevo):
                pacientes.append(nuevo)
                pacientes = ordenar_datos(pacientes)
                guardar_log(f"Paciente manual agregado: {nuevo['id']}")
                print("Paciente válido agregado y lista reordenada.")
            else:
                print("Formato inválido. Revisa los patrones (ID-000, 00 Años, 000ppm, 00%).")

        elif opcion == "3":
            if not pacientes:
                print("Primero genera o importa pacientes (opción 1 o 4).")
            else:
                guardar_archivos(pacientes)

        elif opcion == "4":
            pacientes = leer_json()
            print(f"Se importaron {len(pacientes)} registros desde JSON.")

        elif opcion == "5":
            if not pacientes:
                print("No hay datos cargados para validar.")
            else:
                pacientes_validos = filtrar_datos(pacientes)
                print(f"Registros válidos listos: {len(pacientes_validos)}")

        elif opcion == "6":
            if not pacientes_validos:
                print("Primero valida los datos en la opción 5.")
            else:
                subir_mongo(pacientes_validos)

        elif opcion == "7":
            consultar_mongo()

        elif opcion == "8":
            id_buscado = input("Ingresa el ID a consultar (ej. ID-001): ").strip()
            buscar_por_id(id_buscado)

        elif opcion == "0":
            guardar_log("Programa finalizado por el usuario.")
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    menu()
