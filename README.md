# T2_automatas_celulares


### 1. Observe sus comportamientos en la casa, en la universidad y en el medio de transporte que utiliza.Encuentre, para cada uno de estos escenarios sus reglas básicas.

 - **casa:** En el entorno hogar, el ente busca mantener estabilidad y orden.
    - Si detecta desorden después de usar un espacio, lo restaura a su estado inicial.
    - Si su nivel de energía es bajo, prioriza alimentarse o descansar.
    - Si existen tareas pendientes, les asigna prioridad antes de actividades recreativas.
    - Si identifica posibles conflictos o estímulos que alteren la estabilidad, reduce la interacción.

 - **universidad:** En el entorno académico, el ente optimiza el uso del tiempo.
    - Permanece en reposo hasta que el tiempo restante para clase alcanza el margen mínimo necesario para desplazarse.
    - Durante la clase, mantiene estado de atención; al finalizar, se retira si no hay otra actividad inmediata.
    - Si existe un intervalo amplio entre clases, utiliza ese tiempo para trabajo productivo (tareas o trabajo).
    - Ante la necesidad de alimentarse, evalúa el entorno: si el recurso inmediato es eficiente lo utiliza; si no, busca una alternativa (Si la cafeteria esta muy llena busco alguna chaza de almuerzos).
    - Al terminar el ciclo académico del día, retorna a su punto base (casa).

Aquí domina la eficiencia temporal y la asignación racional de recursos.
 - **transporte:** En el entorno de movilidad, el ente prioriza desplazamiento rápido y adaptación social.
    - Al detectar un medio de transporte disponible, lo utiliza sin evaluar condiciones secundarias.
    - Si existe asiento disponible y el contexto no indica alta demanda social, lo ocupa; de lo contrario, permanece de pie.
    - Busca ubicarse estratégicamente para facilitar la salida y reducir fricción en el descenso.
    - Cuando el destino se aproxima, anticipa la acción y se posiciona para ejecutarla sin obstáculo.
 
### 2. Suponga una enfermedad, o un incendio forestal, o una moda, desarrolle un modelo de difusión usando ACs probabilísticos. O simule un robot con dos ruedas que evite obstáculos.

### 3. Simule el comportamiento de un robot con tres sensores de distancia, que recorre un espacio bidimensional, donde hay 4 objetos distribuidos aleatoriamente, que no se choca con esos objetos.

En el documento robot_turtle.py se encuentra la simulación del robot con tres sensores de distancia, que recorre un espacio bidimensional, donde hay 4 objetos distribuidos aleatoriamente, que no se choca con esos objetos, adicionalmente se le ha añadido un pequeño porcentaje de aleatoriedad para que no se quede atascado en un ciclo, se uso la libreria turtle para la simulación del robot y los obstáculos, los obstaculos se ubican de forma aleatoria en el espacio bidimensional.

### 4. Tome el plano de una ciudad pequeña y localice, por ejemplo, las droguerías, centros de atención de salud y colegios. Por cada concepto dibuje un diagrama de Voronoi. ¿Considera que puede faltar una droguería, o un centro de atención de salud o un colegio? ¿Hay alguna relación entre los diagramas?