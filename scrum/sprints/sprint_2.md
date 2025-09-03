# 📆  Planificación

## 🎯  Objetivo del Sprint:

Definir el tema del proyecto, y un objetivo tentativo. Realizar la limpieza de datos y un análisis descriptivo inicial.

## 😃  Historias de usuario

- HU#29 - Como analista/investigador quiero definir y delimitar el tema del proyecto y establecer sus objetivos para tener claridad sobre el enfoque de trabajo – Dado un área general de interés, cuando identifico un tema específico y establezco los objetivos principales y secundarios, entonces cuento con un tema claro y delimitado, y objetivos concretos que guían todas las actividades del proyecto
- HU#1 - Como científico de datos quiero cargar datos crudos desde la fuente cruda (CSV) para crear mi base de datos limpia. - Dado un archivo de datos en formato CSV en la carpeta data/raw, cuando ejecuto el script de limpieza en src, entonces los datos se leen correctamente y se guarda un archivo consolidado en data/clean/dataset.parquet listo para su uso.
- HU#7 - Como cientifico de datos, quiero generar scripts de carga y limpieza de la base de datos - Dado que existe un conjunto de datos crudo con valores faltantes y posibles inconsistencias, cuando cargo los datos, reviso su integridad, defino criterios de imputación y aplico el proceso de limpieza, entonces obtengo una base de datos limpia, con los valores imputados o eliminados según reglas establecidas, y la guardo en un formato procesado listo para análisis.
- HU#23 - Como analista/investigador quiero recopilar y revisar literatura relevante para contar con fuentes confiables que sustenten el proyecto. - Dado que se conoce el tema y los objetivos del proyecto, cuando busco, selecciono y reviso artículos, libros, papers y reportes relevantes, entonces genero una lista de referencias confiables y actualizadas, con notas resumidas de cada fuente, que servirán de base para redactar el marco teórico
- HU#8 - Como cientifico de datos, quiero generar scripts de creación de gráficos y tablas - Dado que el equipo necesita generar visualizaciones y tablas organizadas, cuando se creen y guarden los scripts en el repositorio,, entonces deberán existir en la carpeta src/viz un script para gráficos y otro para tablas (en el mismo lenguaje), que al ejecutarse generen al menos un gráfico y una tabla básicos guardados como imágenes en la carpeta res.
- HU#28 - Como analista/investigador quiero redactar el marco teórico y enlazar la bibliografía para sustentar el proyecto con evidencia científica. - Dado que se tiene la revisión de literatura y fuentes relevantes
Cuando redacto los apartados del marco teórico, integrando conceptos, definiciones y resultados previos
Entonces genero un documento coherente que presenta el marco conceptual del proyecto y enlaza correctamente las referencias bibliográficas según el estilo definido (APA)
- HU#20 - Como analista quiero generar un informe de calidad de datos para identificar problemas y asegurar la confiabilidad del dataset. - Dado el dataset procesado final, cuando reviso cada columna, identifico valores faltantes, duplicados, valores atípicos y tipos de datos incorrectos, entonces genero un informe de calidad de datos que incluye en la documentación, mostrando claramente cómo se manejaron los datos
- HU#32 - Como analista quiero actualizar el dashboard del proyecto para reflejar la información más reciente generada por las demás tareas del proyecto. - Dado que se han completado tareas de carga y limpieza de datos, documentación de variables y revisión de literatura, cuando integro los datos procesados y la información relevante en el dashboard, entonces el dashboard muestra información actualizada
- HU#37 - Como analista de datos, quiero preparar y presentar los resultados de los Sprints #1 y #2 para comunicar de manera clara los hallazgos, avances y resultados a los stakeholders del proyecto. - Dado que los resultados y análisis de los Sprints 1 y 2 están disponibles, cuando preparo la presentación con tablas, gráficas y análisis textual, entonces obtengo una presentación lista para exponer que resuma los sprints, incluyendo las estadísticas descriptivas de las variables relevantes y los hallazgos principales, de forma clara y profesional.


## 🔜  Plan de alto nivel:
- *Semana 1:* _Limpieza de datos e investigación metodológica_
- *Semana 2:* _Análisis descriptivo, redacción de metodología y presentación_


## 🥇 Criterios de aceptación del Sprint:
- [ ] _El tema del proyecto está definido y delimitado, con objetivos claros (HU#29)._
- [ ] _La revisión de literatura está realizada y documentada, con fuentes confiables y actualizadas (HU#23)._
- [ ] _El marco teórico está redactado y enlaza correctamente la bibliografía (HU#28)._
- [ ] _La base de datos cruda en CSV se carga y se transforma en un dataset limpio en formato parquet (HU#1, HU#7)._
- [ ] _El código limpia automáticamente la base de datos, imputando o eliminando valores faltantes según reglas establecidas (HU#7)._
- [ ] _Existe un informe de calidad de datos documentado (HU#20)._
- [ ] _Se generan scripts para gráficos y tablas en la carpeta `src/viz`, que al ejecutarse producen al menos un gráfico y una tabla guardados en `res` (HU#8)._
- [ ] _El dashboard refleja la información más reciente del proyecto (HU#32)._
- [ ] _La presentación de resultados de los Sprints #1 y #2 está lista con gráficos y análisis textual (HU#37)._



## 📌  Asignación de tareas inicial
- *José Carlos Quintero:* Limpieza y análisis descriptivo
- *Paola Espinoza Hernández:* Descripción de datos y dashboard
- *Julián Soto:* investigación, redacción de metodología
- *Paula Jiménez:* investigación y presentación

## 🚫 Posibles bloqueos o impedimentos conocidos

- **Bloqueo:** _Falta de claridad en la definición del tema y objetivos del proyecto._
  **Solución:** _Completar la HU#29 y validarla con el profesor antes de avanzar._

# ⏳  Daily

##  Fecha: 2025-08-26

### Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Asigné las tareas a cada integrante del equipo e investigué la estructura y características de nuestra base de datos.
- **¿Qué haré hoy?**: Terminar la revisión de la base de datos y comenzaré con el proceso de limpieza.
- **¿Hay algo que me está bloqueando?**:  Debemos definir y acordar las reglas de imputación antes de continuar con la limpieza.

### José Carlos Quintero:
- **¿Qué hice ayer?**:
- **¿Qué haré hoy?**:
- **¿Hay algo que me está bloqueando?**:

### Julián Soto:
- **¿Qué hice ayer?**: conversar con los integrantes del grupo acerca las tareas propuestas para el sprint2
- **¿Qué haré hoy?**: iniciar con el análisis de la metodología del artículo de referencia.
- **¿Hay algo que me está bloqueando?**:  -

### María Paula Jiménez:
- **¿Qué hice ayer?**: reunirme con mis compañeros para discutir la dinámica del sprint siguiente.
- **¿Qué haré hoy?**: investigaré sobre antecedentes y conceptos
- **¿Hay algo que me está bloqueando?**: no

##  Fecha: 2025-08-28

### Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Comencé el proceso de limpieza
- **¿Qué haré hoy?**: Terminar con el proceso de limpieza.
- **¿Hay algo que me está bloqueando?**:  Los pull-request

### José Carlos Quintero:
- **¿Qué hice ayer?**: comenzar limpieza de datos
- **¿Qué haré hoy?**: completar módulo de limpieza de datos y el script de limpieza de la base, comenzar con el módulo de graficacion
- **¿Hay algo que me está bloqueando?**: graficacion en Python

### Julián Soto:
- **¿Qué hice ayer?**: delimitación del análisis metodológico para modelos tipo CAR (conditional autoregressive models)
- **¿Qué haré hoy?**: continuación de la lectura de bibliografía sobre modelos CAR
- **¿Hay algo que me está bloqueando?**: falta de familiarización con modelos estadísticos autoregresivos

### Paula:
- **¿Qué hice ayer?**: busqué varios artículos relacionados con nuestro tema
- **¿Qué haré hoy?**: de los artículos que guardé, voy a elegir los 3 o 4 que considere más relevantes y útiles para nuestro trabajo.
- **¿Hay algo que me está bloqueando?**: no

##  Fecha: 2025-08-31

### Paola Espinoza Hernández:
- *¿Qué hice ayer?*: Asigné nuevas tareas a cada integrante, realicé la descripción de las variables a utilizar. Aprendí a hacer pull requests.
- *¿Qué haré hoy?*: Revisar el análisis descriptivo, continuar con la descripción de la base
- *¿Hay algo que me está bloqueando?*:  no

### José Carlos Quintero:
- *¿Qué hice ayer?*: trabajar en la creación de un modulo de creación de gráficos en python.
- *¿Qué haré hoy?*: completer dicho modulo y generar un script para generar graficos de prueba
- *¿Hay algo que me está bloqueando?*: no

### Julián Soto:
- *¿Qué hice ayer?*: revisión de las tareas asignadas a mi persona, para el sprint 2.
- *¿Qué haré hoy?*: continuar con la revisión de la literatura seleccionada.
- *¿Hay algo que me está bloqueando?*: no

### María Paula Jiménez:
- *¿Qué hice ayer?*: meditar sobre las tareas a realizar
- *¿Qué haré hoy?*: planeo empezar a escribir los antecedentes
- *¿Hay algo que me está bloqueando?*: no



# 🔍   Revisión en clase (Fecha: YYYY-MM-DD)



## 📈 Resultado mostrado

- *Funcionalidad A:* Tema del proyecto definido y objetivos establecidos.
- *Funcionalidad B:* Revisión de literatura completada con lista de referencias confiables y actualizadas.
- *Funcionalidad C:* Marco teórico redactado e integrado con bibliografía en formato APA.
- *Funcionalidad D:* Dataset crudo cargado desde CSV y transformado en un archivo limpio en formato Parquet.
- *Funcionalidad E:* Base de datos limpiada con valores faltantes imputados o eliminados según reglas establecidas.
- *Funcionalidad F:* Informe de calidad de datos generado y documentado.
- *Funcionalidad G:* Scripts de gráficos y tablas creados en `src/viz`, que producen al menos un gráfico y una tabla guardados en `res`.
- *Funcionalidad H:* Dashboard actualizado con la información más reciente del proyecto.
- *Funcionalidad I:* Presentación de resultados de los Sprints #1 y #2 preparada con gráficos y análisis textual.


## :arrows_counterclockwise:  Retroalimentación

- **Profesor**:
- **Compañeros:**


## ✔️  Criterios de aceptación cumplidos:
- [] _Historias 1, 2, 3. completadas. Falta la historia 4.
- [x] Carga automática de la base de datos.


# 🔙  Retrospective – Fecha: YYYY-MM-DD

## :white_check_mark: Qué salió bien
1.  _Colaboración en el equipo_ Logramos terminar el sprint a tiempo.
1.  _Usamos commits convencionales correctamente y no hubo errores_
1.  Documentación actualizada al día evitó retrabajo luego.



## :no_good: Qué podría mejorar

- _Gestión de tiempo en Daily:_ a veces se extendieron a 20 min discutiendo detalles innecesarios.
- _Claridad de criterios de aceptación:_ En HU2 inicialmente no estaba claro cómo validar "datos limpios". Mejoraremos definición de *Done* para tareas de datos.
- _Distribución de carga:_ Persona A quedó sobrecargada con 3 historias. El próximo sprint se equilibrará asignación más temprano.


## :pencil: Acciones concretas  para el próximo sprint
1. **Timebox en Daily** – SM usará temporizador de 15 min y cortará discusiones largas, anotándolas para after.
2. **Refinar historias en refinamiento semanal** – Agregar criterios de aceptación más detallados, especialmente para historias técnicas (como limpieza de datos).
3. **Balancear asignación tareas** – Implementar mini-plan al inicio del sprint donde cada dev toma carga similar; SM monitoreará que nadie tenga >40% de tareas.
