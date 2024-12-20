
# Proyecto Base con FastAPI

Este proyecto es una estructura base para una aplicación web desarrollada con **FastAPI**, organizada en módulos y con soporte para Docker y CI/CD.

## Características

- Base de datos FAISS, que es una base de datos vectorial de alta precisión y eficiencia.
- Spacy, un motor de procesamiento de lenguaje natural.
- Langchain, una biblioteca de inteligencia artificial.
- FastAPI, una herramienta de desarrollo rápido y sencilla para Python.
- PyPDF2, una biblioteca de Python para trabajar con archivos PDF.
- Streamlit, una herramienta de desarrollo de interfaces de usuario.

## Funcionalidades

**Reading and Processing PDF Files**
PDF Reader
La primera función principal de nuestra aplicación está diseñada para leer archivos PDF. Cuando un usuario carga uno o más archivos PDF, la aplicación procesa cada página del documento y extrae el texto, combinándolo en una única cadena de texto continua.

**Text Splitter**
Una vez que se extrae el texto, se divide en fragmentos manejables para facilitar su procesamiento y análisis. Utilizando la biblioteca LangChain, el texto se segmenta en fragmentos de 1000 caracteres cada uno. Esta segmentación ayuda a optimizar el rendimiento durante el procesamiento y permite una búsqueda más eficiente en el contenido.

**Creating a Searchable Text Database and Making Embeddings**
Para hacer que el texto sea fácilmente consultable, la aplicación convierte los fragmentos de texto en representaciones vectoriales. Esta transformación permite realizar búsquedas rápidas y precisas dentro del contenido del PDF.

**Vector Store**: Se utiliza la biblioteca FAISS para convertir los fragmentos de texto en vectores y almacenarlos localmente. Esta operación es esencial para permitir búsquedas eficientes dentro del conjunto de datos.
Setting Up the Conversational AI
El núcleo de la aplicación es una inteligencia artificial conversacional que emplea los modelos avanzados de OpenAI. Esta IA puede responder preguntas basadas en el contenido extraído de los PDFs.

**Conversation Chain**: La IA utiliza una serie de prompts para entender el contexto y ofrecer respuestas precisas a las consultas de los usuarios. Si la respuesta a una pregunta no está disponible en el texto procesado, la IA responde con “answer is not available in the context”, asegurando que los usuarios no reciban información incorrecta.

Este proceso integral permite a la aplicación leer, procesar, almacenar y consultar eficazmente grandes volúmenes de información contenida en archivos PDF, facilitando la interacción con el contenido a través de una IA conversacional.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```
app/
    api/
    core/
    db/
    schemas/
    services/
    business/
migrations/
tests/
ci_cd/
docker/
main.py
```

### Carpetas principales:

- **`app/`**: Contiene la lógica de la aplicación, dividida en diferentes módulos como rutas (`api/`), configuración (`core/`), base de datos (`db/`), esquemas (`schemas/`) y servicios (`services/`).
- **`migrations/`**: Contiene los archivos de migración de base de datos (probablemente usando Alembic).
- **`tests/`**: Pruebas unitarias e integraciones de la aplicación.
- **`ci_cd/`**: Scripts y configuraciones para la integración y despliegue continuo.
- **`docker/`**: Configuraciones de Docker para los diferentes entornos (desarrollo, testing, producción).

## Requisitos Previos

- **Python 3.8+**
- **Docker** (opcional para entornos contenedorizados)
- **Poetry** o **pip** para la gestión de dependencias.

## Instalación y Configuración

### 1. Clonar el repositorio

Clona este repositorio en tu máquina local:

```bash
git clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

### 2. Crear el entorno virtual

Usa el siguiente comando para crear un entorno virtual:

```bash
python -m venv venv
```

Luego, activa el entorno virtual:

- En **Unix/MacOS**:
  ```bash
  source venv/bin/activate
  ```
- En **Windows**:
  ```bash
  venv\Scripts\activate
  ```

### 3. Instalar las dependencias

Una vez activado el entorno virtual, instala las dependencias:

```bash
pip install -r requirements.txt
```

### 4. Configurar el archivo `.env`

Crea un archivo `.env` en el directorio raíz del proyecto para gestionar variables de entorno (como claves API, credenciales de base de datos, etc.). Un ejemplo básico de `.env` podría ser:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=tu_clave_secreta
```

### 5. Usar Docker (Opcional)

Si deseas usar Docker para la ejecución del proyecto, hay tres entornos disponibles: desarrollo, testing, y producción. Para cada entorno puedes encontrar un `Dockerfile` y un archivo `docker-compose.yml` en el directorio `docker/`.

Ejemplo para desarrollo:

```bash
cd docker/develop
docker-compose up --build
```

## .gitignore

Este proyecto incluye un archivo `.gitignore` que asegura que no se suban archivos sensibles ni innecesarios al repositorio:

- **`venv/`**: El entorno virtual.
- **`.env`**: Archivo de configuración del entorno.
- **`__pycache__/`**: Archivos cacheados por Python.
- **Archivos de configuración de IDEs**: Para que las configuraciones locales no se incluyan en el repositorio.

## Ejecutar la aplicación

Una vez configurado el entorno, puedes ejecutar la aplicación localmente usando Uvicorn:

```bash
uvicorn main:app --reload
```

Esto iniciará el servidor de FastAPI y la aplicación estará disponible en `http://127.0.0.1:8000/`.

## Pruebas

Para ejecutar las pruebas unitarias y de integración, puedes usar `pytest`:

```bash
pytest
```

## Contribución

1. Haz un fork del repositorio.
2. Crea una nueva rama con tus cambios (`git checkout -b feature/nueva-feature`).
3. Realiza un commit de tus cambios (`git commit -am 'Añadir nueva feature'`).
4. Haz push a la rama (`git push origin feature/nueva-feature`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT).
