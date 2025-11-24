# Prevalencia de obesidad y sobrepeso infantil en Costa Rica

Repositorio del proyecto del curso **CA0307 – Estadística II (II-2025, UCR)**.  
El objetivo es estimar la prevalencia de sobrepeso y obesidad infantil en Costa Rica utilizando el **Primer Censo Escolar de Peso/Talla 2016** y un modelo **binomial con enlace logit** bajo un enfoque **bayesiano**, además de presentar los resultados en un **informe reproducible** y en un **dashboard interactivo** (Dash).


## Estructura del repositorio

- `app/`  
  Código de la aplicación web (Dash) para explorar los resultados de prevalencia por provincia y cantón.

- `data/`  
  Datos crudos necesarios para el análisis (por ejemplo, tablas del censo y archivos GeoJSON).

- `docs/`  
  Archivos de documentación e informes. Aquí se encuentra el **informe principal en R Markdown** (por ejemplo, `docs/Reporte_final.Rmd`) y el PDF generado.

- `res/`  
  Resultados intermedios del análisis: tablas `.csv` (por ejemplo, `summary_prevalence_by_province.csv`, `summary_prevalence_by_canton.csv`) y gráficos `.png` que se usan en el informe y en el dashboard.

- `src/`  
  Código Python de apoyo (funciones para cargar datos, limpieza, modelos, etc.).

- `scrum/`  
  Documentos de gestión del proyecto (sprints, tareas, etc.).

- Archivos de configuración:
  - `pyproject.toml`, `uv.lock`: configuración del entorno de Python.
  - `.python-version`: versión recomendada de Python.
  - `.pre-commit-config.yaml`: hooks de calidad de código.
  - `LICENSE`: licencia del proyecto.
  - `README.md`: este archivo.


## Requisitos previos

1. **Python**
   - Versión recomendada: **Python 3.11**.
   - Paquetes principales (se instalan automáticamente con el método recomendado):
     - `pandas`
     - `numpy`
     - `plotly`
     - `dash`
     - `dash-bootstrap-components`

2. **R**
   - Versión recomendada: **R ≥ 4.2**.
   - Paquetes R necesarios para knit del informe:
     - `rmarkdown`
     - `knitr`
     - `tidyverse` (o al menos `dplyr`, `readr`, `ggplot2`)
   - Se recomienda usar **RStudio**, aunque no es obligatorio.

3. **Herramientas adicionales (opcionales)**
   - [`uv`](https://github.com/astral-sh/uv) para manejar el entorno de Python a partir de `pyproject.toml` y `uv.lock`.
   - Git para clonar el repositorio.


### 2.a Instalación usando `uv` (recomendado)

Si tienes `uv` instalado:

    uv sync

Esto creará un entorno virtual (por defecto `.venv/`) e instalará todas las dependencias definidas en `pyproject.toml` y `uv.lock`.

Para activar el entorno virtual (solo si no usas `uv run`):

- En Linux/macOS:

      source .venv/bin/activate

- En Windows (PowerShell):

      .venv\Scripts\Activate.ps1

### 2.b Instalación usando `pip` (alternativa)

Si no usas `uv`, puedes crear un entorno virtual manualmente:

- En Linux/macOS:

      python -m venv .venv
      source .venv/bin/activate

- En Windows (PowerShell):

      python -m venv .venv
      .venv\Scripts\Activate.ps1

Luego instala las dependencias listadas anteriormente, o bien utiliza:

    pip install -r requirements.txt

## Ejecución de la aplicación web local

La aplicación web (Dash) se encuentra en la carpeta `app/` en el archivo `app.py`. Asegúrate de tener el entorno virtual activo o usa `uv run`.

Con `uv`:

    uv run python app/app.py

Con entorno activado y `python` directamente:

    python app/app.py

Por defecto, la aplicación se ejecuta en:

- URL: `http://127.0.0.1:8050`

Abre esa dirección en el navegador para explorar:

- Distribuciones posteriores de prevalencia por provincia y cantón.
- Gráficos de bosque (forest plots) de medias e intervalos de credibilidad.
- Visualizaciones de densidades y comparaciones entre grupos.

## Reproducción del análisis estadístico

### Scripts de Python en `src/`

En la carpeta `src/` se encuentran los scripts que automatizan el proceso de:

- Preparar las bases de datos.
- Seleccionar covariables mediante AIC.
- Ajustar el modelo logit–binomial con priors débiles.
- Guardar tablas de resumen en `res/csv/` y figuras en `res/graficos/`.

Ejemplos de ejecución:

    # Selección de covariables (AIC)
    uv run python src/seleccion_aic.py

    # Ajuste del modelo logit–binomial con NUTS
    uv run python src/modelo_jerarquico.py

Si no usa `uv`, omita el prefijo `uv run` y asegúrese de tener el entorno activado:

    python src/seleccion_aic.py
    python src/modelo_jerarquico.py

Estos comandos regeneran las tablas `summary_prevalence_by_province.csv` y `summary_prevalence_by_canton.csv` dentro de `res/csv/`, que son utilizadas tanto en el informe como en la aplicación web.

## Regenerar el informe (R Markdown)

El informe principal se encuentra en la carpeta `docs/` como un archivo `.Rmd`, llamado `docs/Reporte_final.Rmd`.

Para regenerar el informe desde R (con RStudio):

1. Abrir el archivo `.Rmd` dentro de `docs/`.
2. Ejecutar el botón `Knit` y elegir el formato deseado (PDF o HTML).

Desde la línea de comando:

    Rscript -e "rmarkdown::render('docs/Reporte_final.Rmd', output_format = 'pdf_document')"

o para generar HTML:

    Rscript -e 'rmarkdown::render("docs/Reporte_final.Rmd", output_format = "html_document")'

El documento generado se guardará en la misma carpeta `docs/`.

El informe utiliza los resultados almacenados en `res/csv/` y las figuras en `res/graficos/`. Si se desea rehacer todo desde cero:

1. Ejecuta los scripts de análisis en `src/` para regenerar las tablas y gráficos.
2. Vuelve a compilar el `.Rmd` siguiendo los pasos anteriores.

## Flujo completo de reproducción

1. Clonar el repositorio y entrar a la carpeta raíz.
2. Crear y sincronizar el entorno (idealmente con `uv sync`).
3. Ejecutar los scripts de análisis en `src/` para regenerar resultados en `res/`.
4. Compilar el informe en `docs/` con R/RStudio o desde la terminal.
5. (Opcional) Lanzar la aplicación web con `uv run python app/app.py` para explorar interactiva y visualmente los resultados.

## Contacto

Para dudas sobre el código o el análisis:

- Paola Espinoza; paomariespher@gmail.com
- José Carlos Quintero  
- Julián Soto Montoya
- María Paula Jiménez Torres

El enlace oficial del repositorio es:

    https://github.com/CA0307-II-2025/grupo-1
