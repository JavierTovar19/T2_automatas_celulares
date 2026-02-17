import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

# Definición de Estados
ESTADO_MUESTA = 0       # 'm' (vacío/muerta)
ESTADO_VIVA = 1         # 'v' (célula móvil)
ESTADO_OBSTACULO = 2    # 'x' (caja)
ESTADO_INHABITABLE = 3  # Vecino de 'x' (zona prohibida)

# Configuración del mapa
PERIODO = 0.01
N_FILAS = 30
N_COLUMNAS = 30
N_OBSTACULOS = 50  # Número de cajas aleatorias

def crear_mapa():
    """Inicializa la grilla con cajas, zonas prohibidas y una célula."""
    grilla = np.zeros((N_FILAS, N_COLUMNAS), dtype=int)

    # 1. Colocar Obstáculos (x)
    for _ in range(N_OBSTACULOS):
        # Evitamos los bordes extremos para simplificar
        r = random.randint(2, N_FILAS - 3)
        c = random.randint(2, N_COLUMNAS - 3)
        grilla[r, c] = ESTADO_OBSTACULO

    # 2. Marcar zonas inhabitables (vecinos de x)
    # Copiamos para no iterar sobre lo que estamos marcando
    temp_grilla = grilla.copy()
    direcciones = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]

    for r in range(N_FILAS):
        for c in range(N_COLUMNAS):
            if grilla[r, c] == ESTADO_OBSTACULO:
                # Marcar vecinos como inhabitables si son 0
                for dr, dc in direcciones:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < N_FILAS and 0 <= nc < N_COLUMNAS:
                        if temp_grilla[nr, nc] == ESTADO_MUESTA:
                            temp_grilla[nr, nc] = ESTADO_INHABITABLE
    
    grilla = temp_grilla

    # 3. Colocar la Célula Viva (v)
    # Buscamos una posición libre (que sea 0)
    libres = []
    for r in range(N_FILAS):
        for c in range(N_COLUMNAS):
            if grilla[r, c] == ESTADO_MUESTA:
                libres.append((r, c))
    
    if libres:
        vr, vc = random.choice(libres)
        grilla[vr, vc] = ESTADO_VIVA
    else:
        # Fallback por si está muy lleno (poco probable)
        grilla[N_FILAS//2, N_COLUMNAS//2] = ESTADO_VIVA

    return grilla

def actualizar(grilla):
    """
    Aplica las reglas de transición:
    - Identifica la célula 'v'.
    - Busca vecinos elegibles ('m').
    - Selecciona uno aleatoriamente (simulando 1/n).
    - Mueve la célula.
    """
    # Buscar coordenadas de la célula viva
    coords_v = np.argwhere(grilla == ESTADO_VIVA)
    if len(coords_v) == 0:
        return grilla  # No hay célula viva
    
    # Asumimos una sola célula viva por regla
    r, c = coords_v[0]
    
    # Regla 1: Si la célula esta v, pasa a estado m (al moverse).
    # (Se aplica al final junto con el nacimiento en la nueva posición)

    # Identificar vecinos candidatos (m)
    direcciones = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]
    
    vecinos_validos = []
    
    # Analizamos los 8 vecinos
    for dr, dc in direcciones:
        nr, nc = r + dr, c + dc
        
        # Verificar límites
        if 0 <= nr < N_FILAS and 0 <= nc < N_COLUMNAS:
            # Regla: Las casillas vecinas a x son inhabitables (ya marcadas con 3)
            # Regla: Solo puede moverse a 'm' (0)
            neighbor_state = grilla[nr, nc]
            
            if neighbor_state == ESTADO_MUESTA:
                vecinos_validos.append((nr, nc))
    
    # Regla de Probabilidad: "Su posibilidad de pasar a v... es 1/n..."
    # Interpretación: Elegimos UNO de los vecinos candidatos al azar.
    # Si hay 3 vecinos válidos, n efectivo sería el número de candidatos.
    # El usuario especifica un algoritmo de selección secuencial (1/8, 1/7...).
    # Matemáticamente, esto equivale a elegir uniformemente de la lista de candidatos disponibles
    # si procesamos solo los válidos, o elegir de los 8 direcciones si procesamos todas.
    # Aquí, para garantizar movimiento fluido, elegimos uniformemente entre los VÁLIDOS.
    
    if len(vecinos_validos) > 0:
        # Selección aleatoria
        nuevo_r, nuevo_c = random.choice(vecinos_validos)
        
        # Actualizar grilla
        grilla[r, c] = ESTADO_MUESTA      # La vieja posición muere
        grilla[nuevo_r, nuevo_c] = ESTADO_VIVA  # La nueva nace
        
    # Si no hay vecinos válidos, la célula se queda donde está (regla implícita/bloqueo)

    return grilla

my_cmap = mcolors.ListedColormap(['white', 'green', 'black', 'lightgray'])
bounds = [0, 1, 2, 3, 4]
norm = mcolors.BoundaryNorm(bounds, my_cmap.N)

# --- Ejecución ---
def main():
    grilla = crear_mapa()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Dibujo inicial
    img = ax.imshow(grilla, cmap=my_cmap, norm=norm, origin='upper')
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=0.1)
    ax.set_xticks(np.arange(-0.5, N_COLUMNAS, 1));
    ax.set_yticks(np.arange(-0.5, N_FILAS, 1));
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_title("Simulación Autómata Celular: Célula (Verde) vs Cajas (Negro)")
    
    # Barra de color para referencia
    cbar = plt.colorbar(img, ticks=[0.5, 1.5, 2.5, 3.5], boundaries=bounds)
    cbar.ax.set_yticklabels(['Muerta', 'Viva', 'Caja', 'Inhabitable'])
    
    try:
        # Bucle de animación
        while True:
            actualizar(grilla)
            img.set_data(grilla)
            plt.draw()
            plt.pause(PERIODO)  # Velocidad de actualización
    except KeyboardInterrupt:
        print("Simulación terminada.")
    finally:
        plt.show()

if __name__ == "__main__":
    main()
