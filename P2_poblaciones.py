import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

# Definición de Estados
ESTADO_VACIO = 0
ESTADO_CONEJO = 1
ESTADO_ZORRO = 2
ESTADO_OBSTACULO = 3

# Configuración del mapa y simulación
ANCHO = 50
ALTO = 50
PORCENTAJE_OBSTACULOS = 0.0  # Eliminados
PORCENTAJE_CONEJOS = 0.2
PORCENTAJE_ZORROS = 0.05

# Parámetros biológicos (Wa-Tor)
EDAD_REPRODUCCION_CONEJO = 5
LIMITE_EDAD_CONEJO = 20  # Nuevo: Conejos mueren de viejos
EDAD_REPRODUCCION_ZORRO = 8
LIMITE_HAMBRE_ZORRO = 4

# Estructuras para almacenar el estado extendido
# grilla: Tipo de celda (0, 1, 2, 3)
# edad: Turnos vividos desde la última reproducción
# hambre: Turnos desde la última comida (solo zorros)

def crear_mapa():
    grilla = np.zeros((ALTO, ANCHO), dtype=int)
    edad = np.zeros((ALTO, ANCHO), dtype=int)
    hambre = np.zeros((ALTO, ANCHO), dtype=int)
    
    for r in range(ALTO):
        for c in range(ANCHO):
            rand = random.random()
            if rand < PORCENTAJE_CONEJOS:
                grilla[r, c] = ESTADO_CONEJO
            elif rand < PORCENTAJE_CONEJOS + PORCENTAJE_ZORROS:
                grilla[r, c] = ESTADO_ZORRO
                # Zorros empiezan alimentados
                hambre[r, c] = 0
            # El resto queda VACIO y Obstáculos eliminados
            
    return grilla, edad, hambre

def obtener_vecinos(r, c, grilla):
    """Retorna coordenadas de vecinos (arriba, abajo, izq, der)."""
    # Vecindad de Von Neumann (4 vecinos) o Moore (8)?
    # Wa-Tor suele usar Von Neumann, pero usaremos Moore (8) como P3_Robot para consistencia
    direcciones = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]
    
    vecinos = []
    for dr, dc in direcciones:
        nr, nc = (r + dr) % ALTO, (c + dc) % ANCHO # Mundo toroidal (pacman)
        # Opcional: Sin mundo toroidal (bordes sólidos)
        # nr, nc = r + dr, c + dc
        
        if 0 <= nr < ALTO and 0 <= nc < ANCHO:
            vecinos.append((nr, nc))
            
    return vecinos

def buscar_vecino_tipo(r, c, tipo, grilla):
    """Busca vecinos de un tipo específico. Retorna lista de coordenadas."""
    candidatos = []
    vecinos = obtener_vecinos(r, c, grilla)
    for nr, nc in vecinos:
        if grilla[nr, nc] == tipo:
            candidatos.append((nr, nc))
    return candidatos

def actualizar(grilla, edad, hambre):
    # Creamos copias para el siguiente estado (actualización síncrona visualmente, 
    # pero lógicamente secuencial aleatoria es mejor para evitar conflictos de movimiento)
    # Sin embargo, para simular Wa-Tor correctamente, necesitamos procesar los agentes 
    # uno por uno en orden aleatorio para evitar colisiones de destino.
    
    # Lista de coordenadas de todos los agentes
    agentes = []
    for r in range(ALTO):
        for c in range(ANCHO):
            if grilla[r, c] in [ESTADO_CONEJO, ESTADO_ZORRO]:
                agentes.append((r, c))
    
    # Mezclar orden de procesamiento
    random.shuffle(agentes)
    
    # Procesar movimientos
    # Nota: Usamos una máscara "procesado" para no mover el mismo agente dos veces en un turno
    # Pero como iteramos sobre una lista fija de coordenadas iniciales, si un agente se mueve
    # a una casilla (r', c') que estaba en la lista y aún no se procesó, podríamos tener problemas.
    # Solución simplificada: Iteramos la lista. Si en (r,c) ya no está el agente (porque murió o se movió otro ahí), saltar.
    # Pero cuidado: Si (r,c) tiene UN agente, ¿es el original o uno nuevo?
    # Para simplificar y evitar complejidad excesiva, usaremos arrays auxiliares 'moved' 
    # y asumiremos que si grilla[r,c] sigue siendo del tipo esperado, es el agente.
    
    ya_movido = np.zeros((ALTO, ANCHO), dtype=bool)

    nuevo_grilla = grilla.copy() # No usaremos esto directamente, modificaremos in-place con cuidado
    # En Wa-Tor clásico, se modifica la grilla paso a paso.
    
    for r, c in agentes:
        if ya_movido[r, c]: continue # Si ya se movió (era destino de otro), ignorar... espera, esto no aplica aquí
        # En realidad, 'agentes' tiene las posiciones ORIGINALES.
        # Verificamos si en la posición actual TODAVÍA está el agente del tipo esperado y NO ha sido marcado como 'procesado_en_este_turno'
        
        tipo = grilla[r, c]
        
        if tipo == ESTADO_VACIO or tipo == ESTADO_OBSTACULO: 
            continue # Ya no está (fue comido o algo)
            
        if ya_movido[r, c]:
            continue # Ya procesado (recién nacido o movido aquí? No, nacidos no están en 'agentes')

        # --- Lógica CONEJO ---
        if tipo == ESTADO_CONEJO:
            # 1. Intentar mover a una casilla vacía
            vecinos_vacios = buscar_vecino_tipo(r, c, ESTADO_VACIO, grilla)
            
            if vecinos_vacios:
                nr, nc = random.choice(vecinos_vacios)
                
                # Mover conejo
                grilla[nr, nc] = ESTADO_CONEJO
                edad[nr, nc] = edad[r, c] + 1
                ya_movido[nr, nc] = True # Marcar destino como procesado
                
                # Reproducción
                if edad[r, c] >= EDAD_REPRODUCCION_CONEJO:
                    grilla[r, c] = ESTADO_CONEJO # Deja un hijo
                    edad[r, c] = 0
                    edad[nr, nc] = 0 
                else:
                    grilla[r, c] = ESTADO_VACIO # Deja vacía la celda origen
                    
                ya_movido[r, c] = True # Origen procesado
            else:
                # No se mueve, solo envejece
                edad[r, c] += 1
            
            # Muerte por vejez (Conejos)
            # Verificamos la posición actual del conejo (sea nueva o vieja)
            curr_r, curr_c = (nr, nc) if vecinos_vacios else (r, c)
            
            if edad[curr_r, curr_c] >= LIMITE_EDAD_CONEJO:
                grilla[curr_r, curr_c] = ESTADO_VACIO
                ya_movido[curr_r, curr_c] = True
        
        # --- Lógica ZORRO ---
        elif tipo == ESTADO_ZORRO:
            # 1. Buscar Comida (Conejos)
            vecinos_conejos = buscar_vecino_tipo(r, c, ESTADO_CONEJO, grilla)
            
            nuevo_r, nuevo_c = r, c
            comio = False
            se_movio = False
            
            if vecinos_conejos:
                # Caza
                nr, nc = random.choice(vecinos_conejos)
                grilla[nr, nc] = ESTADO_ZORRO
                hambre[nr, nc] = 0 # Saciado
                edad[nr, nc] = edad[r, c] + 1
                ya_movido[nr, nc] = True
                comio = True
                se_movio = True
                nuevo_r, nuevo_c = nr, nc
                
                # El conejo en nr, nc muere (sobrescrito)
                
            else:
                # 2. Si no hay comida, intentar mover a vacío
                vecinos_vacios = buscar_vecino_tipo(r, c, ESTADO_VACIO, grilla)
                if vecinos_vacios:
                    nr, nc = random.choice(vecinos_vacios)
                    grilla[nr, nc] = ESTADO_ZORRO
                    hambre[nr, nc] = hambre[r, c] + 1
                    edad[nr, nc] = edad[r, c] + 1
                    ya_movido[nr, nc] = True
                    se_movio = True
                    nuevo_r, nuevo_c = nr, nc
                else:
                    # No se mueve
                    hambre[r, c] += 1
                    edad[r, c] += 1
            
            # Gestión de origen (r, c) después de moverse
            if se_movio:
                # Reproducción
                if edad[r, c] >= EDAD_REPRODUCCION_ZORRO: # Usamos edad PREVIA al movimiento para decidir
                    # Nota: edad ya se incrementó en destino.
                    # Si era apto para reproducirse antes de moverse:
                    grilla[r, c] = ESTADO_ZORRO # Deja hijo
                    edad[r, c] = 0
                    hambre[r, c] = 0 # Hijo nace saciado? O heredado? Normalmente 0.
                    
                    # Padre (en nuevo_r, nuevo_c) reinicia edad de reproducción? Wa-Tor dice que sí.
                    edad[nuevo_r, nuevo_c] = 0 
                else:
                    grilla[r, c] = ESTADO_VACIO
                    
            # Muerte por hambre (del zorro en su posición actual, sea nueva o vieja)
            # Si se movió, verificamos en nuevo_r, nuevo_c
            # Si no se movió, en r, c
            
            curr_r, curr_c = (nuevo_r, nuevo_c) if se_movio else (r, c)
            
            if hambre[curr_r, curr_c] >= LIMITE_HAMBRE_ZORRO:
                grilla[curr_r, curr_c] = ESTADO_VACIO
                ya_movido[curr_r, curr_c] = True # Marcar como procesado (muerto)

    return grilla, edad, hambre

# --- Visualización ---
# 0: Vacio (Negro o Blanco)
# 1: Conejo (Azul/Verde)
# 2: Zorro (Rojo)
# 3: Obstáculo (Gris)

my_cmap = mcolors.ListedColormap(['white', 'cyan', 'red', 'black'])
bounds = [0, 1, 2, 3, 4]
norm = mcolors.BoundaryNorm(bounds, my_cmap.N)

def main():
    grilla, edad, hambre = crear_mapa()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    img = ax.imshow(grilla, cmap=my_cmap, norm=norm, origin='upper', interpolation='nearest')
    ax.set_title("Simulación Depredador-Presa (Wa-Tor)\nConejos:Cyan, Zorros:Rojo (Sin Obstáculos)")
    ax.axis('off')
    
    # Barra de color
    cbar = plt.colorbar(img, ticks=[0.5, 1.5, 2.5], boundaries=bounds, fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels(['Vacío', 'Conejo', 'Zorro'])
    
    try:
        while True:
            actualizar(grilla, edad, hambre)
            img.set_data(grilla)
            plt.draw()
            plt.pause(0.05)
    except KeyboardInterrupt:
        print("Simulación terminada.")
    finally:
        plt.show()

if __name__ == "__main__":
    main()
