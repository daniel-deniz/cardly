# src/release_input_example.py

RELEASE_INPUT_EXAMPLE = {
    "version_name": "v1.8.0",
    "cards": [
        {
            "title": "BL Academy - Añadir evaluación por vídeo",
            "description": "Cada vídeo incluye un cuestionario para validar comprensión y guardar el resultado del usuario.",
            "type": "Funcionalidad",
            "customer_visible": True,
        },
        {
            "title": "Operaciones - Mostrar estado de envío de email automático",
            "description": "Se muestra si el email al cliente se envió, cuándo y motivos si no se envió.",
            "type": "Funcionalidad",
            "customer_visible": True,
        },
        {
            "title": "Presupuestos - PDF muestra solo adultos cuando hay niños",
            "description": "Al descargar a PDF, el campo de pasajeros no refleja correctamente los niños.",
            "type": "Bug/Corrección",
            "customer_visible": True,
        },
        {
            "title": "Infra - Refactor de logs de auditoría",
            "description": "Ajustes internos para mejorar trazabilidad y mantenimiento.",
            "type": "Funcionalidad",
            "customer_visible": False,
        },
        {
            "title": "Calendario conductores - Evaluar nueva librería",
            "description": "Spike para investigar una librería que permita gestionar jornadas laborales y eventos en bloque.",
            "type": "Funcionalidad",
            "customer_visible": False,
        },
    ],
}
