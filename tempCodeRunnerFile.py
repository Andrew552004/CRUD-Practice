from flask import Flask, request, jsonify
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
Swagger(app)  # Agrega Swagger para la documentación

# Base de datos simulada
tareas = {
    "1": {"titulo": "Comprar leche", "completada": False, "fecha": "2025-04-05"},
    "2": {"titulo": "Hacer ejercicio", "completada": True, "fecha": "2025-04-04"}
}

# Función para validar la fecha
def validar_fecha(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hoy = datetime.today().date()
        if fecha < hoy:
            return False, "La fecha no puede ser anterior a hoy"
        return True, ""
    except ValueError:
        return False, "Formato de fecha inválido. Usa YYYY-MM-DD"

@app.route('/tarea', methods=['POST'])
def crear_tarea():
    """
    Crea una nueva tarea
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            titulo:
              type: string
            completada:
              type: boolean
            fecha:
              type: string
              format: date
    responses:
      201:
        description: Tarea creada exitosamente
    """
    if not request.is_json:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON"}), 415

    data = request.get_json()
    if not data or "titulo" not in data or "completada" not in data or "fecha" not in data:
        return jsonify({"error": "Datos inválidos, se requiere 'titulo', 'completada' y 'fecha'"}), 400

    es_valida, mensaje_error = validar_fecha(data["fecha"])
    if not es_valida:
        return jsonify({"error": mensaje_error}), 400

    nueva_id = str(len(tareas) + 1)
    tareas[nueva_id] = {
        "titulo": data["titulo"],
        "completada": data["completada"],
        "fecha": data["fecha"]
    }
    return jsonify({"mensaje": "Tarea creada", "id": nueva_id}), 201

@app.route('/tarea/<id>', methods=['GET'])
def obtener_tarea(id):
    """
    Obtener una tarea por ID
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Tarea encontrada
      404:
        description: Tarea no encontrada
    """
    if id in tareas:
        return jsonify(tareas[id])
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tarea/<id>', methods=['PUT'])
def actualizar_tarea(id):
    """
    Actualizar una tarea por ID
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            titulo:
              type: string
            completada:
              type: boolean
            fecha:
              type: string
              format: date
    responses:
      200:
        description: Tarea actualizada exitosamente
      400:
        description: Datos inválidos
      404:
        description: Tarea no encontrada
    """
    if not request.is_json:
        return jsonify({"error": "El cuerpo de la solicitud debe ser JSON"}), 415

    if id in tareas:
        nueva_data = request.get_json()
        if "fecha" in nueva_data:
            es_valida, mensaje_error = validar_fecha(nueva_data["fecha"])
            if not es_valida:
                return jsonify({"error": mensaje_error}), 400
        tareas[id].update(nueva_data)
        return jsonify({"mensaje": "Tarea actualizada"}), 200
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tarea/<id>', methods=['DELETE'])
def eliminar_tarea(id):
    """
    Eliminar una tarea por ID
    ---
    parameters:
      - name: id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Tarea eliminada exitosamente
      404:
        description: Tarea no encontrada
    """
    if id in tareas:
        del tareas[id]
        return jsonify({"mensaje": "Tarea eliminada"}), 200
    return jsonify({"error": "Tarea no encontrada"}), 404

@app.route('/tareas', methods=['GET'])
def listar_tareas():
    """
    Obtiene la lista de todas las tareas
    ---
    responses:
      200:
        description: Lista de tareas
    """
    return jsonify(tareas), 200

if __name__ == '__main__':
    app.run(debug=True)
