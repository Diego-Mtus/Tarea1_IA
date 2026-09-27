
### Integrantes
* Diego Matus Salas, 2023900249

### Requisitos Previos
* Python 3.13 o superior instalado.

### Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto de forma local:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com
   cd mi-proyecto-python
   ```

2. **Crear el entorno virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Activar el entorno virtual:**
   * **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   * **macOS / Linux:** `source .venv/bin/activate`

4. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

### Para utilizar el programa

El programa principal es una interfaz que ejecuta los algoritmos visualmente usando `pygame` como interfaz, este se abre mediante

   ```bash
      py main.py
   ```

Por otro lado, el benchmarking se ejecuta utilizando

   ```bash
      py benchmark.py
   ```

El cual realiza 160 iteraciones de cada prueba, y lo obtenido se almacena en `resultados_benchmark.csv`. Si se quiere graficar estos valores obtenidos, esto se puede hacer mediante

   ```bash
      py generar_graficos.py
   ```
