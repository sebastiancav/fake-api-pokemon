from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# 🔹 Estructura principal: cada alumno tiene su propia "base"
datos_alumnos = {}


def obtener_pokemon(nombre):
    """Obtiene datos desde la PokéAPI"""
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return {
            "nombre": data["name"].capitalize(),
            "nivel": data["base_experience"],
            "descripcion": f"Pokémon tipo {', '.join(t['type']['name'] for t in data['types'])}",
            "url_imagen": data["sprites"]["front_default"]
        }
    return None


def obtener_lista(alumno):
    """Devuelve la lista del alumno o crea una nueva si no existe"""
    if alumno not in datos_alumnos:
        datos_alumnos[alumno] = []
    return datos_alumnos[alumno]


# ✅ Obtener todos
@app.route('/<string:alumno>/pokemons', methods=['GET'])
def get_all(alumno):
    return jsonify(obtener_lista(alumno))


# 🔍 Obtener uno
@app.route('/<string:alumno>/pokemons/<string:nombre>', methods=['GET'])
def get_one(alumno, nombre):
    lista = obtener_lista(alumno)
    p = next((x for x in lista if x['nombre'].lower() == nombre.lower()), None)
    if p:
        return jsonify(p)
    return jsonify({"error": "No encontrado"}), 404


# ➕ Crear nuevo
@app.route('/<string:alumno>/pokemons', methods=['POST'])
def create(alumno):
    data = request.get_json()
    lista = obtener_lista(alumno)
    nombre = data.get('nombre')

    if nombre and not any(p['nombre'].lower() == nombre.lower() for p in lista):
        poke_data = obtener_pokemon(nombre)
        if poke_data:
            lista.append(poke_data)
            return jsonify(poke_data), 201

    nuevo = {
        "nombre": nombre,
        "nivel": data.get('nivel'),
        "descripcion": data.get('descripcion'),
        "url_imagen": data.get('url_imagen')
    }
    lista.append(nuevo)
    return jsonify(nuevo), 201


# ✏️ Actualizar
@app.route('/<string:alumno>/pokemons/<string:nombre>', methods=['PUT'])
def update(alumno, nombre):
    lista = obtener_lista(alumno)
    data = request.get_json()
    for p in lista:
        if p['nombre'].lower() == nombre.lower():
            p['nivel'] = data.get('nivel', p['nivel'])
            p['descripcion'] = data.get('descripcion', p['descripcion'])
            p['url_imagen'] = data.get('url_imagen', p['url_imagen'])
            return jsonify(p)
    return jsonify({"error": "No encontrado"}), 404


# 🗑️ Eliminar
@app.route('/<string:alumno>/pokemons/<string:nombre>', methods=['DELETE'])
def delete(alumno, nombre):
    lista = obtener_lista(alumno)
    nuevos = [p for p in lista if p['nombre'].lower() != nombre.lower()]
    datos_alumnos[alumno] = nuevos
    return jsonify({"mensaje": f"{nombre} eliminado del perfil {alumno}"})


# 🧹 Borrar todos los datos de un alumno (opcional)
@app.route('/<string:alumno>/reset', methods=['DELETE'])
def reset(alumno):
    datos_alumnos[alumno] = []
    return jsonify({"mensaje": f"Datos del alumno '{alumno}' reiniciados"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
