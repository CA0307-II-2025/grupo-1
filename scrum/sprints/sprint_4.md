# 📆  Planificación

## 🎯  Objetivo del Sprint:

 Realizar una exploración inicial de distintos modelos estadísticos para el análisis de la prevalencia infantil de obesidad y sobrepeso en Costa Rica.

## 😃  Historias de usuario

- HU#71 - (Modelo Nacional Simplificado) Como investigador, quiero aplicar los algoritmos Metropolis-Hastings y muestreo de Gibs, para obtener una estimación de la prevalencia de la obesidad a nivel nacional (sin distinción de distritos). (Estimación: 3 pts)
- HU#73 - (Modelo distritial No Bayesiano) Como investigador, quiero aplicar un modelo de regresión a partir de variables sociodemográficas, para obtener una estimación de la prevalencia de la obesidad a nivel distrital. (Estimación: 5 pts)
- HU#74 - (Modelo distrital) Como investigador, quiero aplicar un modelo de regresión con covariables sociodemográficas y efectos provinciales, para estimar la prevalencia de la obesidad a nivel distrital. (Estimación: 8 pts)
- HU#75 -Como analista de datos, quiero preparar y presentar los resultados de los Sprints #3 y #4 para comunicar de manera clara los hallazgos, avances y resultados parciales del proyecto. (Estimación: 2 pts)


## 🔜  Plan de alto nivel:
- *Semana 1:* Delimitar los modelos estadísticos que se considerarán preliminarmente para el proyecto.
- *Semana 2:* Implementar los modelos estadísticos propuestos, así como también valorar su respectivo ajuste.


## 🥇  Criterios de aceptación del Sprint:
- [ ] Se cumplen todos los criterios para (UH#71), (UH#73), (UH#75). Además, se cumple parcialmente (UH#74).

- [ ] (UH#71) Implementación de los algoritmos Metropolis-Hastings y muestreo de Gibs, para este caso específico.
- [ ] (UH#71) Convergencia del algortimo con > 5000 iteraciones.
- [ ] (UH#71) Se reporta media, desviación estándar, IC95% para la distribución posterior de prevalencia de obesidad.
- [ ] (UH#71) Resultados se presentan en tabla resumen.

- [ ] (UH#73) Selección y calibración de un modelo de regresión para la prevalencia de obesidad, a partir de las covariables sociodemográficas distritales.
- [ ] (UH#73) Se presentan los diagnósticos de ajuste del modelo.
- [ ] (UH#73) Se presentan los resultados principales obtenidos del modelo.

- [ ] (UH#74) Se incluyen covariables demográficas validadas.
- [ ] (UH#74) Se presentan los diagnósticos del modelo.
- [ ] (UH#74) Se presenta: la media, desviación estándar, e IC95% para la distribución posterior de la prevalencia de obesidad, por distrito.

- [ ] (UH#75) Resumen de los principales resultados obtenidos en los sprints 3 - 4
- [ ] (UH#75) Preparación de una presentación divulgativa, donde se exponga dicho resumen, de forma clara y profesional.




## 📌  Asignación de tareas inicial
- José Carlos Quintero: HU#71, HU#74
- Paola Espinoza Hernández: HU#71, HU74#
- Julián Soto: HU#73, HU74#, HU#75
- Paula Jiménez: HU#73, HU#75


## 🚫 Posibles bloqueos o impedimentos conocidos

- **Bloqueo:** El principal bloqueo es la especficación e implementación del modelo jerárquico bayesiano.
- **Solución** Enfocar la búsqueda metodológica en este tipo de modelos, así como también, recibir retroalimentación por parte del profesor.


# ⏳  Daily

##  Fecha: 2025-09-26

### Paola Espinoza Hernández:
- *¿Qué hice ayer?*: revisar la implementación de la metodología
- *¿Qué haré hoy?*: Agregar la implemetación de metodología al documento escrito
- *¿Hay algo que me está bloqueando?*:  no

### José Carlos Quintero:
- *¿Qué hice ayer?*: comenzar la programación del modelo metrópolis hasting
- *¿Qué haré hoy?*: finalizar el modelo y crear gráficos
- *¿Hay algo que me está bloqueando?*: no sé en qué usar los componentes demográficos de la base de datos

### Julián Soto:
- *¿Qué hice ayer?*: finalizar la asignación de tareas para el sprint.
- *¿Qué haré hoy?*: ajuste del modelo de regresión simplificado.
- *¿Hay algo que me está bloqueando?*: No

### María Paula Jiménez:
•⁠  ⁠*¿Qué hice ayer?*: Empezar a estudiar la regresión logística.
•⁠  ⁠*¿Qué haré hoy?*: Avanzar con la entrega del reporte de los sprint 3 y 4.
•⁠  ⁠*¿Hay algo que me está bloqueando?*: no.

##  Fecha: 2025-09-30

### Paola Espinoza Hernández:
- *¿Qué hice ayer?*: agregar resultados a documento escrito.
- *¿Qué haré hoy?*: agregar resultados al dashboard.
- *¿Hay algo que me está bloqueando?*: no.

### José Carlos Quintero:
- *¿Qué hice ayer?*: desarrollo de modelo para encontrar la distribución del parámetro de prevalencia de obesidad y sobrepeso a nivel nacional.
- *¿Qué haré hoy?*: investigar sobre la mejor manera de realizar distribuciones a nivel regional.
- *¿Hay algo que me está bloqueando?*: no.

### Julián Soto:
- *¿Qué hice ayer?*: Revisión de modelos de regresión para datos agregados.
- *¿Qué haré hoy?*: ajuste de un modelo de regresión binomial con datos agregados.
- *¿Hay algo que me está bloqueando?*: no.

### María Paula Jiménez:
•⁠  ⁠*¿Qué hice ayer?*: Revisión de modelos de regresión para datos agregados.
•⁠  ⁠*¿Qué haré hoy?*: Empezar con la presentación.
•⁠  ⁠*¿Hay algo que me está bloqueando?*: no.

# 🔍   Revisión en clase (Fecha: 2025-10-03)

## 📈  Resultado mostrado

- *Funcionalidad A:* Distribución posterior de la prevalencia infantil de sobrepeso y obesidad, obtenida a través del algoritmo de Metrópolis Hastings.
- *Funcionalidad B:* Falta de ajuste del modelo de regresión binomial con covariables sociodemográficas a nivel distrital.
- *Funcionalidad C:* Especificación preliminar de un modelo de regresión jerárquico bayesiano, para modelar la prevalencia infantil de sobrepeso y obesidad a nivel distrital.


## :arrows_counterclockwise:  Retroalimentación

- **Profesor**: Profundizar en el estudio metodológico de la Teoría de Procesos Estocásticos, puntualmente, en el contexto de especificar distibuciones previas para la varianza de los efectos aleatóricos.
- **Compañeros:** NA


## ✔️  Criterios de aceptación cumplidos:
- [✔️] Se cumplen todos los criterios para (UH#71), (UH#73), (UH#75). Además, se cumple parcialmente (UH#74).

- [✔️] (UH#71) Implementación de los algoritmos Metropolis-Hastings y muestreo de Gibs, para este caso específico.
- [✔️] (UH#71) Convergencia del algortimo con > 5000 iteraciones.
- [✔️] (UH#71) Se reporta media, desviación estándar, IC95% para la distribución posterior de prevalencia de obesidad.
- [✔️] (UH#71) Resultados se presentan en tabla resumen.

- [✔️] (UH#73) Selección y calibración de un modelo de regresión para la prevalencia de obesidad, a partir de las covariables sociodemográficas distritales.
- [✔️] (UH#73) Se presentan los diagnósticos de ajuste del modelo.
- [✔️] (UH#73) Se presentan los resultados principales obtenidos del modelo.

- [✔️] (UH#74) Se incluyen covariables demográficas validadas.
- [X] (UH#74) Se presentan los diagnósticos del modelo.
- [X] (UH#74) Se presenta: la media, desviación estándar, e IC95% para la distribución posterior de la prevalencia de obesidad, por distrito.

- [✔️] (UH#75) Resumen de los principales resultados obtenidos en los sprints 3 - 4
- [✔️] (UH#75) Preparación de una presentación divulgativa, donde se exponga dicho resumen, de forma clara y profesional.

# 🔙  Retrospective – Fecha: 2025-10-03

## :white_check_mark: Qué salió bien
1. Colaboración en el equipo: las tareas asignadas se completaron de forma eficiente en subgrupos de trabajo.
2. Implementación de modelos: se ajustaron preliminarmente dos modelos estadísticos. Sus resultados proporcionaron una guía para proponer un modelo jerárquico bayesiano.
3. Delimitación del alcance: se terminó de delimitar el alcance del proyecto.
4. Equilibrio de asignaciones: las asignaciones se realizaron de forma equilibrada por persona (2), mientras que el scrum master se encargó de (3).



## :no_good: Qué podría mejorar

- _Falta de reuniones_: en el contexto del sprint, se sugiere al menos una reunión por sprint para compartir el avance en las tareas asignadas.

## :pencil: Acciones concretas  para el próximo sprint
1. **Timebox en Daily** – Reunión para determinar la especificación concreta del modelo.
