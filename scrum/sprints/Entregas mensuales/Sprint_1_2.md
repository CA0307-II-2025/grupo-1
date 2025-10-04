---
output:
  pdf_document:
    latex_engine: xelatex
  html_document: default
---

# Sprint 1

##  Planificación

###   Objetivo del Sprint
Tener una propuesta de base de datos para usar en el proyecto, así como potenciales temas de investigación, y dejar la estructura inicial del repositorio lista con scripts y documentos básicos.

###   Historias de usuario

Nota del SCRUM master: la numeración de las notas están desordenadas porque, al estar en un periodo de aprendizaje, se cometieron errores que no se podían eliminar

- HU4 - "Como equipo, queremos encontrar una base de datos que podamos usar para la investigación" (Estimación: 8 pts) – *Criterios de aceptación confirmados.*
- HU6 - "Como equipo, queremos proponer diferentes enfoques y temas para la investigación que se respalden en la base" (Estimación: 5 pts) – *Criterios de aceptación confirmados.*
- HU7 - "Como científico de datos, quiero generar scripts de carga y limpieza de la base de datos" (Estimación: 3 pts) – *Criterios de aceptación pendientes.*
- HU8 - "Como científico de datos, quiero generar scripts de creación de gráficos y tablas" (Estimación: 3 pts) – *Criterios de aceptación pendientes.*
- HU9 - "Como científico de datos, quiero generar una primera instancia del dashboard en Python" (Estimación: 1 pts) – *Criterios de aceptación confirmados.*
- HU10 - "Como investigador, quiero encontrar artículos relacionados con temas potenciales para la investigación" (Estimación: 5 pts) – *Criterios de aceptación confirmados.*
- HU11 - "Como investigador, quiero generar una primera versión del trabajo escrito" (Estimación: 1 pts) – *Criterios de aceptación confirmados.*

---

###   Plan de alto nivel
- *Semana 1:* Investigar sobre metodologías posibles, indagar sobre bases de datos y proponer temas iniciales.
- *Semana 2:* Cargar la base de datos al repositorio, crear primera versión del escrito y del dashboard básico.

---

###   Criterios de aceptación del Sprint
- [ ] _Todas las historias listadas completadas y aceptadas por el profesor._
- [ ] _La base de datos seleccionada se encuentra en `data/raw`._
- [ ] _El dashboard básico se ejecuta desde la carpeta `app`._
- [ ] _El documento escrito preliminar se encuentra en la carpeta `docs`._



###   Asignación de tareas inicial
- *Todos*: Historia 4 y 6
- *Paola:* Historia 7 y 9
- *Paula:* Historia 11
- *Julián:* Historia 10
- *José Carlos:* Historia 7 y 8 y documentación SCRUM

### Posibles bloqueos o impedimentos conocidos

- **Bloqueo:** Poca idea de cómo implementar una metodología estadística sólida en el estudio.
- **Solución** Investigar y basarse fuertemente en trabajos de otros autores, así como consultar con el profesor.


## Daily

###  Fecha: 2025-08-18

#### Julián Soto Montoya
- **¿Qué hice ayer?**: Lectura del artículo "Bayesian spatial modeling of childhood overweight and obesity prevalence in Costa Rica".
- **¿Qué haré hoy?**: Presentar las ideas encontradas durante la lectura del artículo, a los compañeros de trabajo.
- **¿Hay algo que me está bloqueando?**:  -

#### Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Busqué posibles bases de datos para el proyecto.
- **¿Qué haré hoy?**: Explorar distintas alternativas para el desarrollo del dashboard.
- **¿Hay algo que me está bloqueando?**: No tenemos definida la metodología que podemos aplicar.

#### José Carlos:
- **¿Qué hice ayer?**: Consulté una base relacionada con el Covid-19 que podríamos usar
- **¿Qué haré hoy?**: Exploraré otras alternativas propuestas por mis compañeros
- **¿Hay algo que me está bloqueando?**: -

###  Fecha: 2025-08-20

#### Julián Soto Montoya:
- **¿Qué hice ayer?**: Lectura del artículo "Species Distribution Modeling using Spatial Point Processes: a Case Study of Sloths in Costa Rica"
- **¿Qué haré hoy?**: Divulgar las ideas encontradas con los compañeros, en la reunión acordada.
- **¿Hay algo que me está bloqueando?**: Dificultades en la utilización de git.

#### María Paula:
- **¿Qué hice ayer?**: Revisé los articulos y bases de datos proporcionados por mis compañeros.
- **¿Qué haré hoy?**: Ir comenzando una presentación en canva del proyecto para presentarla el viernes.
- **¿Hay algo que me está bloqueando?**: Estoy teniendo problemas con el manejo de git.

#### Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Investigué opciones para el desarrollo del dashboard y elaboré una versión inicial.
- **¿Qué haré hoy?**: Analizaré las bases de datos propuestas y revisaré posibles artículos a replicar.
- **¿Hay algo que me está bloqueando?**: La falta de certeza sobre el tema y la base de datos a utilizar.

#### José Carlos:
- **¿Qué hice ayer?**: Investigué sobre diferentes opciones de bases de datos y consulté sobre artículos compartidos por mis compañeros
- **¿Qué haré hoy?**: le escribiré al profe sobre nuestras propuestas de base de datos y organizaré la documentación del SCRUM de mejor manera
- **¿Hay algo que me está bloqueando?**: no estoy seguro de como implementaremos la metodología, pero eso es para etapas posteriores



##  Revisión en clase (Fecha: 2025-08-22)

### Resultado mostrado

- *Funcionalidad A:* Selección de base de datos final (con validación del coordinador).
- *Funcionalidad B:* Exploración inicial de temas de investigación vinculados a la base de datos.
- *Funcionalidad C:* Primera versión del documento preliminar del proyecto ubicada en `docs`.
- *Funcionalidad D:* Dashboard básico en Python ejecutado desde la carpeta `app`.

### Retroalimentación

- **Profesor**: en cada commit es recomendable mencionar, cuando corresponda, la historia de usuario/issue que se resuelve.
- **Compañeros:** falta definir un plan más claro en las reuniones para no divagar en discusiones sin rumbo.

###  Criterios de aceptación cumplidos:
- [x] HU4 – Base de datos seleccionada (ubicada en `data/raw`).
- [ ] HU6 – Temas explorados, pero el ranking comparativo aún está pendiente.
- [ ] HU7 – Scripts de carga y limpieza de datos no finalizados.
- [ ] HU8 – Scripts de gráficos/tablas no implementados.
- [x] HU9 – Dashboard inicial ejecutable desde `app`.
- [ ] HU10 – Algunas referencias encontradas, pero falta ampliar investigación académica.
- [x] HU11 – Documento preliminar del proyecto en `docs`.

---

##  Retrospective – Fecha: 2025-08-22

### Qué salió bien
1. Seleccionamos la base de datos final de forma consensuada y validada con el coordinador.
2. Se generó un primer dashboard básico en Python.
3. Se logró una primera versión del documento escrito, lo que da estructura al trabajo.

### Qué podría mejorar
- A veces nos desviamos del tema en las reuniones y no llegábamos a conclusiones claras.
- La organización del backlog no fue del todo clara debido a la inexperiencia, lo que retrasó la secuencia de tareas.
- Falta de avance en referencias y scripts técnicos (limpieza de datos y visualizaciones).

###  Acciones concretas para el próximo sprint
1. **Plan previo para cada reunión** – Definir una mini-agenda con 2–3 puntos clave para evitar divagar y asegurar decisiones rápidas.
2. **Commits vinculados a issues** – Al hacer commits, incluir referencia al issue/HU correspondiente cuando aplique.
3. **Refinamiento de backlog** – Dedicar una sesión corta a clarificar dependencias entre historias y qué significa “done” en cada caso.
4. **Avance incremental en tareas técnicas** – No esperar a tener todo listo: scripts de limpieza y gráficos deben avanzar en etapas pequeñas y revisables.
6. **Bibliografía semanal** – Cada miembro debe traer al menos 1 referencia académica nueva en el próximo sprint para reforzar HU10.

# Sprint 2

##    Planificación

###    Objetivo del Sprint:

Definir el tema del proyecto, y un objetivo tentativo. Realizar la limpieza de datos y un análisis descriptivo inicial.

###    Historias de usuario

- HU#29 - "Como analista/investigador quiero definir y delimitar el tema del proyecto y establecer sus objetivos para tener claridad sobre el enfoque de trabajo" (Estimación: 3 pts) – *Criterios de aceptación confirmados.*
- HU#1 - "Como científico de datos quiero cargar datos crudos desde la fuente cruda (CSV) para crear mi base de datos limpia." (Estimación: 2 pts) – *Criterios de aceptación confirmados.*
- HU#7 - "Como cientifico de datos, quiero generar scripts de carga y limpieza de la base de datos" (Estimación: 5 pts) – *Criterios de aceptación confirmados.*
- HU#23 - "Como analista/investigador quiero recopilar y revisar literatura relevante para contar con fuentes confiables que sustenten el proyecto." (Estimación: 3 pts) – *Criterios de aceptación confirmados.*
- HU#8 - "Como cientifico de datos, quiero generar scripts de creación de gráficos y tablas" (Estimación: 3 pts) – *Criterios de aceptación confirmados.*
- HU#28 - "Como analista/investigador quiero redactar el marco teórico y enlazar la bibliografía para sustentar el proyecto con evidencia científica." (Estimación: 3 pts) – *Criterios de aceptación confirmados.*
- HU#20 - "Como analista quiero generar un informe de calidad de datos para identificar problemas y asegurar la confiabilidad del dataset." (Estimación: 3 pts) – *Criterios de aceptación confirmados.*
- HU#32 - "Como analista quiero actualizar el dashboard del proyecto para reflejar la información más reciente generada por las demás tareas del proyecto." (Estimación: 2 pts) – *Criterios de aceptación confirmados.*
- HU#37 - "Como analista de datos, quiero preparar y presentar los resultados de los Sprints #1 y #2 para comunicar de manera clara los hallazgos, avances y resultados a los stakeholders del proyecto." (Estimación: 3 pts) – *Criterios de aceptación confirmados.*


###    Plan de alto nivel:
- *Semana 1:* _Limpieza de datos e investigación metodológica_
- *Semana 2:* _Análisis descriptivo, redacción de metodología y presentación_


###   Criterios de aceptación del Sprint:
- [ ] _El tema del proyecto está definido y delimitado, con objetivos claros (HU#29)._
- [ ] _La revisión de literatura está realizada y documentada, con fuentes confiables y actualizadas (HU#23)._
- [ ] _El marco teórico está redactado y enlaza correctamente la bibliografía (HU#28)._
- [ ] _La base de datos cruda en CSV se carga y se transforma en un dataset limpio en formato parquet (HU#1, HU#7)._
- [ ] _El código limpia automáticamente la base de datos, imputando o eliminando valores faltantes según reglas establecidas (HU#7)._
- [ ] _Existe un informe de calidad de datos documentado (HU#20)._
- [ ] _Se generan scripts para gráficos y tablas en la carpeta `src/viz`, que al ejecutarse producen al menos un gráfico y una tabla guardados en `res` (HU#8)._
- [ ] _El dashboard refleja la información más reciente del proyecto (HU#32)._
- [ ] _La presentación de resultados de los Sprints #1 y #2 está lista con gráficos y análisis textual (HU#37)._



###    Asignación de tareas inicial
- *José Carlos Quintero:* Limpieza y análisis descriptivo
- *Paola Espinoza Hernández:* Descripción de datos y dashboard
- *Julián Soto:* investigación, redacción de metodología
- *Paula Jiménez:* investigación y presentación

###  Posibles bloqueos o impedimentos conocidos

- **Bloqueo:** _Falta de claridad en la definición del tema y objetivos del proyecto._
- **Solución:** _Completar la HU#29 y validarla con el profesor antes de avanzar._

##  Daily

###   Fecha: 2025-08-26

####  Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Asigné las tareas a cada integrante del equipo e investigué la estructura y características de nuestra base de datos.
- **¿Qué haré hoy?**: Terminar la revisión de la base de datos y comenzaré con el proceso de limpieza.
- **¿Hay algo que me está bloqueando?**:  Debemos definir y acordar las reglas de imputación antes de continuar con la limpieza.

####  José Carlos Quintero:
- **¿Qué hice ayer?**: investigué sobre los datos y la metodología del artículo base del proyecto
- **¿Qué haré hoy?**: comenzar con la limpieza y descripción de los datos
- **¿Hay algo que me está bloqueando?**: falta de claridad en enfoque de investigacion

####  Julián Soto:
- **¿Qué hice ayer?**: conversar con los integrantes del grupo acerca las tareas propuestas para el sprint2
- **¿Qué haré hoy?**: iniciar con el análisis de la metodología del artículo de referencia.
- **¿Hay algo que me está bloqueando?**:  -

####  María Paula Jiménez:
- **¿Qué hice ayer?**: reunirme con mis compañeros para discutir la dinámica del sprint siguiente.
- **¿Qué haré hoy?**: investigaré sobre antecedentes y conceptos
- **¿Hay algo que me está bloqueando?**: no

###   Fecha: 2025-08-28

####  Paola Espinoza Hernández:
- **¿Qué hice ayer?**: Comencé el proceso de limpieza
- **¿Qué haré hoy?**: Terminar con el proceso de limpieza.
- **¿Hay algo que me está bloqueando?**:  Los pull-request

####  José Carlos Quintero:
- **¿Qué hice ayer?**: comenzar limpieza de datos
- **¿Qué haré hoy?**: completar módulo de limpieza de datos y el script de limpieza de la base, comenzar con el módulo de graficacion
- **¿Hay algo que me está bloqueando?**: graficacion en Python

####  Julián Soto:
- **¿Qué hice ayer?**: delimitación del análisis metodológico para modelos tipo CAR (conditional autoregressive models)
- **¿Qué haré hoy?**: continuación de la lectura de bibliografía sobre modelos CAR
- **¿Hay algo que me está bloqueando?**: falta de familiarización con modelos estadísticos autoregresivos

####  Paula:
- **¿Qué hice ayer?**: busqué varios artículos relacionados con nuestro tema
- **¿Qué haré hoy?**: de los artículos que guardé, voy a elegir los 3 o 4 que considere más relevantes y útiles para nuestro trabajo.
- **¿Hay algo que me está bloqueando?**: no

###   Fecha: 2025-08-31

####  Paola Espinoza Hernández:
- *¿Qué hice ayer?*: Asigné nuevas tareas a cada integrante, realicé la descripción de las variables a utilizar. Aprendí a hacer pull requests.
- *¿Qué haré hoy?*: Revisar el análisis descriptivo, continuar con la descripción de la base
- *¿Hay algo que me está bloqueando?*:  no

####  José Carlos Quintero:
- *¿Qué hice ayer?*: trabajar en la creación de un modulo de creación de gráficos en python.
- *¿Qué haré hoy?*: completer dicho modulo y generar un script para generar graficos de prueba
- *¿Hay algo que me está bloqueando?*: no

####  Julián Soto:
- *¿Qué hice ayer?*: revisión de las tareas asignadas a mi persona, para el sprint 2.
- *¿Qué haré hoy?*: continuar con la revisión de la literatura seleccionada.
- *¿Hay algo que me está bloqueando?*: no

####  María Paula Jiménez:
- *¿Qué hice ayer?*: meditar sobre las tareas a realizar
- *¿Qué haré hoy?*: planeo empezar a escribir los antecedentes
- *¿Hay algo que me está bloqueando?*: no

###   Fecha: 2025-09-03

####  Paola Espinoza Hernández:
- *¿Qué hice ayer?*: Revisé artículos y planteé posibles temas, junto con sus respectivas preguntas y objetivos.
- *¿Qué haré hoy?*: Tendremos una reunión de equipo para definir el tema, la pregunta de investigación y los detalles finales de la presentación de los sprints 1 y 2. Además, trabajaré en mejorar la estética del dashboard, dejándolo listo para la eventual inclusión de resultados.
- *¿Hay algo que me está bloqueando?*:  No

####  José Carlos Quintero:
- *¿Qué hice ayer?*: investigar posibles temas para enfocar la investigacion
- *¿Qué haré hoy?*: trabajar en elaborar un informe de calidad de los datos
- *¿Hay algo que me está bloqueando?*: -

####  Julián Soto:
- *¿Qué hice ayer?*: Recopilación de la información bibliográfica consultada.
- *¿Qué haré hoy?*: asistir a la reunión de equipo en la que se definirá el tema de la investigación, así como los objetivos. También, incluiré la revisión bibliográfica realizada.
- *¿Hay algo que me está bloqueando?*: no.

####  María Paula Jiménez:
-⁠  ⁠*¿Qué hice ayer?*: hacer un borrador de la estructura que quiero para los antecedentes
-⁠  ⁠*¿Qué haré hoy?*: asistir a la reunión del grupo para escoger el tema de la investigación y objetivos. Resumir los artículos bibliográficos y poner en el documento escrito una introducción de los antecedentes
-⁠  ⁠*¿Hay algo que me está bloqueando? *:no

##   Revisión en clase (Fecha: 2025-09-05)

###  Resultado mostrado

- *Funcionalidad A:* Tema del proyecto definido y objetivos establecidos.
- *Funcionalidad B:* Revisión de literatura completada con lista de referencias confiables y actualizadas.
- *Funcionalidad C:* Marco teórico redactado e integrado con bibliografía en formato APA.
- *Funcionalidad D:* Dataset crudo cargado desde CSV y transformado en un archivo limpio.
- *Funcionalidad E:* Base de datos limpiada con valores faltantes imputados o eliminados según reglas establecidas.
- *Funcionalidad F:* Informe de calidad de datos generado y documentado.
- *Funcionalidad G:* Scripts de gráficos y tablas creados en `src/viz`, que producen al menos un gráfico y una tabla guardados en `res`.
- *Funcionalidad H:* Dashboard actualizado con la información más reciente del proyecto.
- *Funcionalidad I:* Presentación de resultados de los Sprints #1 y #2 preparada con gráficos y análisis textual.


###   Retroalimentación

- **Profesor**: Seleccionar una metodología más sencilla.
- **Compañeros**: La realización constante de dailys ayuda a mantener el repositorio actualizado y recordar tanto las tareas a realizar como el tiempo límite para hacerlas.


### Criterios de aceptación cumplidos:
- [x] _El tema del proyecto está definido y delimitado, con objetivos claros (HU#29)._
- [x] _La revisión de literatura está realizada y documentada, con fuentes confiables y actualizadas (HU#23)._
- [x] _El marco teórico está redactado y enlaza correctamente la bibliografía (HU#28)._
- [x] _La base de datos cruda en CSV se carga y se transforma en un dataset limpio en formato parquet (HU#1, HU#7)._
- [x] _El código limpia automáticamente la base de datos, imputando o eliminando valores faltantes según reglas establecidas (HU#7)._
- [x] _Existe un informe de calidad de datos documentado (HU#20)._
- [x] _Se generan scripts para gráficos y tablas en la carpeta `src/viz`, que al ejecutarse producen al menos un gráfico y una tabla guardados en `res` (HU#8)._
- [x] _El dashboard refleja la información más reciente del proyecto (HU#32)._
- [x] _La presentación de resultados de los Sprints #1 y #2 está lista con gráficos y análisis textual (HU#37)._

##   Retrospective – Fecha: 2025-09-05

###  Qué salió bien
1. _Colaboración en el equipo:_ logramos terminar el sprint a tiempo.
2. _Documentación actualizada:_ se mantuvo día a día, lo que evitó retrabajo.
3. _Revisión de literatura y marco teórico:_ se completaron con fuentes confiables y se integraron correctamente.
4. _Dashboard y scripts:_ quedaron implementados y listos para incorporar resultados futuros.
5. _Daily meetings constantes:_ ayudaron a recordar tareas y deadlines.

###  Qué podría mejorar
- _Claridad de criterios de aceptación:_ en algunas historias no estaba claro cómo validar la finalización.
- _Distribución de carga:_ algunas historias concentraron demasiado trabajo en una sola persona.
- _Uso de commits convencionales:_ hubo un commit no convencional que rompió el estándar.
- _Definición de metodología:_ se eligió una demasiado compleja inicialmente; fue necesario replantearla en clase.

###  Acciones concretas para el próximo sprint
1. **Refinar historias en refinamiento semanal** – agregar criterios de aceptación más detallados.
2. **Balancear asignación de tareas** – mejorar la estimación de puntos y equilibrar la carga de cada integrante.
3. **Estandarizar commits** – reforzar uso de commits convencionales.
4. **Simplificar metodología** – acordar una estrategia más sencilla.
