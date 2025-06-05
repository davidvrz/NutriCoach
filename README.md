# NutriCoach

NutriCoach es una aplicación web moderna para nutricionistas que permite gestionar planes alimenticios de sus clientes. Desarrollada con Flask y Bootstrap para una interfaz de usuario elegante y responsiva.

## Configuración del entorno

### 0. Requisitos previos

- Python 3.8 o superior
- Redis (base de datos en memoria)

### 1. Clonar el repositorio

```bash
git clone https://github.com/davidvrz/NutriCoach.git
cd NutriCoach
```

### 2. Crear un entorno virtual e instalar dependencias

```bash
# Windows
python -m venv venv # o py -m venv venv
venv\Scripts\Activate.ps1 
pip install -r requirements.txt

# Linux/macOS
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Redis

Redis es necesario para el funcionamiento de Sirope (ORM utilizado en la aplicación).

#### Windows (WSL)

1. Si no tienes WSL instalado, instala Ubuntu desde Microsoft Store o ejecuta:
   ```
   wsl --install -d Ubuntu
   ```

2. Dentro de WSL, instala Redis:
   ```
   sudo apt update
   sudo apt install redis-server
   ```

3. Inicia el servidor Redis:
   ```
   sudo service redis-server start
   ```

#### Linux/macOS

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# macOS (con Homebrew)
brew install redis
brew services start redis
```

### 4. Inicializar datos de ejemplo (Opcional)

Para cargar datos de ejemplo y facilitar las pruebas, ejecuta:

```bash
python init_data.py
```

Esto creará un coach y varios clientes con datos de ejemplo.

## Ejecución de la aplicación

### Método 1 (recomendado): Python directo

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

### Método 2: Con Flask CLI

```bash
export FLASK_APP=app.py  # En Windows: set FLASK_APP=app.py
export FLASK_ENV=development  # Para modo desarrollo (opcional)
flask run
```

## Credenciales de acceso (después de inicializar datos)

- **Email**: coach@example.com
- **Contraseña**: password

## Estructura del proyecto

```
NutriCoach/
├── app.py              # Punto de entrada principal de la aplicación
├── requirements.txt    # Dependencias del proyecto
├── init_data.py        # Script para inicializar datos de ejemplo
├── controllers/        # Controladores de la aplicación (rutas)
├── models/             # Modelos de datos
├── static/             # Estilos de la aplicación (Bootstrap)
└── templates/          # Plantillas HTML (Jinja2)
```

## Funcionalidades principales

- Gestión de clientes
- Creación de planes alimenticios diarios
- Seguimiento semanal nutricional
- Planes predefinidos reutilizables
### Si Redis no se conecta:

1. Verifica que el servicio Redis esté en ejecución:
   ```
   # Windows (WSL)
   wsl -d Ubuntu -u root service redis-server status
   
   # Linux/macOS
   systemctl status redis-server
   ```

2. Si no está activo, inicia el servicio:
   ```
   # Windows (WSL)
   wsl -d Ubuntu -u root service redis-server start
   
   # Linux/macOS
   sudo systemctl start redis-server
   ```

3. Para limpiar por completo la base de datos Redis (si es necesario):
   ```
   redis-cli flushall
   ```

### Si aparece el error "ModuleNotFoundError":

Asegúrate de que el entorno virtual está activado y todas las dependencias están instaladas:
```
pip install -r requirements.txt
```

## Tecnologías utilizadas

- Flask (Framework web)
- Sirope (ORM para Redis)
- Bootstrap 5 (Framework CSS)
- Redis (Base de datos)