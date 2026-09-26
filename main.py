import pygame
import random
import sys
import os
import heapq
from collections import deque
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Config
GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 28
MARGIN = 2

# Colores para el mapa
COLOR_BG = (20, 20, 20)
COLOR_EMPTY = (245, 245, 245)
COLOR_WALL = (50, 50, 50)
COLOR_FIRE = (230, 57, 70)
COLOR_EXIT = (42, 157, 143)
COLOR_AGENT = (29, 53, 87)
COLOR_TEXT = (255, 255, 255)
COLOR_PATH = (0, 150, 255)

# Estados de las celdas
EMPTY = 0
WALL = 1
FIRE = 2
EXIT = 3

# variables de pygame
screen = None
clock = None
font_weights = None
font_ui = None
title_font = None

# Se inicializa solo en el main
def init_pygame_gui():
    global screen, clock, font_weights, font_ui, title_font
    pygame.init()
    WINDOW_SIZE = (GRID_WIDTH * (CELL_SIZE + MARGIN) + MARGIN + 280, GRID_HEIGHT * (CELL_SIZE + MARGIN) + MARGIN)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tarea 1")
    clock = pygame.time.Clock()

    font_weights = pygame.font.SysFont("Arial", 9)
    font_ui = pygame.font.SysFont("Arial", 13)
    title_font = pygame.font.SysFont("Arial", 16, bold=True)


# Validación de las dimensiones (30x20), caracteres permitidos (F, P, E, 0-9)
# y existencia de al menos un punto de escape 'E'.
def validate_map_file(filepath):

    if not os.path.exists(filepath):
        return False, f"El archivo '{filepath}' no existe en la carpeta."

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) != GRID_HEIGHT:
            return False, f"El mapa debe tener exactamente {GRID_HEIGHT} filas (se encontraron {len(lines)})."

        has_exit = False
        allowed_chars = set("FPE0123456789")

        for r_idx, line in enumerate(lines):
            if len(line) != GRID_WIDTH:
                return False, f"La fila {r_idx + 1} debe tener exactamente {GRID_WIDTH} caracteres (tiene {len(line)})."

            for char in line:
                if char not in allowed_chars:
                    return False, f"Carácter no válido '{char}' encontrado en la fila {r_idx + 1}."
                if char == 'E':
                    has_exit = True

        if not has_exit:
            return False, "El mapa debe contener al menos un bloque de escape ('E')."

        return True, "OK"

    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"



# El selector de archivos, está en bucle en caso de errores.
def select_file_dialog():

    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilename(
            title="Seleccionar mapa (.txt)",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if not file_path:
            root.destroy()
            return None

        is_valid, error_msg = validate_map_file(file_path)

        if is_valid:
            root.destroy()
            return file_path
        else:
            messagebox.showwarning("Formato de Mapa Incorrecto", f"{error_msg}\n\nPor favor, selecciona otro archivo válido.")


# Abre el dialog para el valor K de propagación
def ask_fire_turns_dialog(current_k):
    """Abre una ventana emergente para consultar el valor K de propagación del fuego."""
    root = tk.Tk()
    root.withdraw()
    
    new_k = simpledialog.askinteger(
        "Propagación del Fuego",
        "Ingresa cada cuántos turnos se propaga el fuego:",
        initialvalue=current_k,
        minvalue=1,
        maxvalue=10
    )
    root.destroy()
    return new_k


# --- HEURÍSTICA Y COSTOS ---

# Es simplemente distancia manhattan por el mov ortogonal
def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# La función de costo es cuadrática respecto a la ocupación, para evitar aglomeraciones.
def get_cost(pos, density_map):
    occupancy = density_map.get(pos, 0)
    return 1.0 + 2.5 * (occupancy ** 2)

# Para los colores de congestión
# Poner en el informe de q las variables de colores fueron con asistencia de ia
def get_congestion_color(occupancy):
    if occupancy == 0:
        return COLOR_EMPTY
    elif occupancy == 1:
        return (255, 240, 180)  # Amarillo muy claro
    elif occupancy == 2:
        return (255, 210, 130)  # Amarillo cálido
    elif occupancy == 3:
        return (255, 180, 80)   # Naranja claro
    elif occupancy == 4:
        return (255, 140, 60)   # Naranja
    elif occupancy == 5:
        return (245, 100, 50)   # Naranja rojizo
    elif occupancy == 6:
        return (230, 70, 50)    # Rojo suave
    elif occupancy == 7:
        return (210, 40, 40)    # Rojo medio
    else:
        return (180, 20, 20)    # Rojo oscuro


# --- ALGORITMOS DE BÚSQUEDA ---


# BFS, visto en clases de estructuras de datos.
def solve_bfs(grid, start, goal):
    queue = deque([start])
    desde = {start: None} # from es palabra reservada:C

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                if grid[nr][nc] not in (WALL, FIRE) and neighbor not in desde:
                    desde[neighbor] = current
                    queue.append(neighbor)

    return reconstruct_path(desde, start, goal)

# También visto en estructuras de datos, con prioridad por costo acumulado.
def solve_dijkstra(grid, start, goal, density_map):
    pq = [(0, start)]
    desde = {start: None}
    cost = {start: 0}

    while pq:
        current_cost, current = heapq.heappop(pq)
        if current == goal: # llega a meta
            break

        if current_cost > cost[current]: # si el costo actual es mayor que el costo almacenado
            continue

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                if grid[nr][nc] not in (WALL, FIRE):
                    new_cost = cost[current] + get_cost(neighbor, density_map)
                    if neighbor not in cost or new_cost < cost[neighbor]:
                        cost[neighbor] = new_cost
                        desde[neighbor] = current
                        heapq.heappush(pq, (new_cost, neighbor))

    return reconstruct_path(desde, start, goal)

# A* es casi lo mismo que dijkstra pero con manhattan.
def solve_astar(grid, start, goal, density_map):
    pq = [(0, start)]
    desde = {start: None}
    g_score = {start: 0}

    while pq:
        _, current = heapq.heappop(pq)
        if current == goal:
            break

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                if grid[nr][nc] not in (WALL, FIRE):
                    tentative_g = g_score[current] + get_cost(neighbor, density_map)
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score = tentative_g + manhattan_distance(neighbor, goal)
                        desde[neighbor] = current
                        heapq.heappush(pq, (f_score, neighbor))

    return reconstruct_path(desde, start, goal)


# Casi lo mismo que A*, pero con la heurística solamente
def solve_greedy(grid, start, goal):
    pq = [(manhattan_distance(start, goal), start)]
    desde = {start: None}
    visited = {start}

    while pq:
        _, current = heapq.heappop(pq)
        if current == goal:
            break

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                if grid[nr][nc] not in (WALL, FIRE) and neighbor not in visited:
                    visited.add(neighbor)
                    desde[neighbor] = current
                    h = manhattan_distance(neighbor, goal)
                    heapq.heappush(pq, (h, neighbor))

    return reconstruct_path(desde, start, goal)


def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return []
    curr = goal
    path = []
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path


# Simulación principal

class Simulation:
    def __init__(self, filepath="mapa1.txt", algorithm="BFS", k_fire_turns=3):

        self.turn = 0
        self.k_fire_turns = k_fire_turns  # Valor de propagación
        self.algorithm = algorithm      
        self.filepath = filepath
        self.filename = os.path.basename(filepath) if filepath else "Sin Mapa"
        
        self.grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.agents = []
        self.exit_pos = None

        if filepath and os.path.exists(filepath):
            self.load_from_txt(filepath)

        self.total_agents = len(self.agents)
        self.escaped = 0
        self.deaths = 0
        self.active_paths = []
        self.planned_density = {}

    def load_from_txt(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for r in range(min(GRID_HEIGHT, len(lines))):
            line = lines[r]
            for c in range(min(GRID_WIDTH, len(line))):
                char = line[c]
                
                if char == 'P':
                    self.grid[r][c] = WALL
                elif char == 'F':
                    self.grid[r][c] = FIRE
                elif char == 'E':
                    self.grid[r][c] = EXIT
                    self.exit_pos = (r, c)
                elif char.isdigit():
                    num_agents = int(char)
                    for _ in range(num_agents):
                        self.agents.append((r, c))

    # Para propagar fuego, se revisa cada celda, si es fuego, sus vecinos ortogonales se convierten en fuego.
    def propagate_fire(self):
        new_fires = []
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c] == FIRE:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                            if self.grid[nr][nc] in (EMPTY, WALL):
                                new_fires.append((nr, nc))
        for r, c in new_fires:
            self.grid[r][c] = FIRE


    # Para el benchmark, que tengan posiciones aleatorias (no tiene sentido posiciones fijas ya que los resultados son determinísticos)
    def randomize_agents(self):
        if self.total_agents == 0:
            return

        # Busca vacías
        empty_cells = []
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid[r][c] == EMPTY:
                    empty_cells.append((r, c))

        # Asigna agentes a posiciones vacías aleatorias
        if empty_cells:
            self.agents = [random.choice(empty_cells) for _ in range(self.total_agents)]

    def step(self):
        if not self.agents or not self.exit_pos:
            return

        self.turn += 1
        self.planned_density = {}
        new_agents = []
        self.active_paths = []

        # Movimiento según algoritmo
        for agent in self.agents:
            if self.algorithm == "BFS":
                path = solve_bfs(self.grid, agent, self.exit_pos)
            elif self.algorithm == "Dijkstra":
                path = solve_dijkstra(self.grid, agent, self.exit_pos, self.planned_density)
            elif self.algorithm == "A*":
                path = solve_astar(self.grid, agent, self.exit_pos, self.planned_density)
            elif self.algorithm == "Greedy":
                path = solve_greedy(self.grid, agent, self.exit_pos)

            next_pos = path[0] if path else agent

            # Registrar reserva de tráfico para el siguiente agente en este turno
            self.planned_density[next_pos] = self.planned_density.get(next_pos, 0) + 1

            # Evaluar destino del movimiento
            if next_pos == self.exit_pos:
                self.escaped += 1  # Evacuado con éxito
            elif self.grid[next_pos[0]][next_pos[1]] == FIRE:
                self.deaths += 1   # Caminó directamente hacia el fuego
            else:
                self.active_paths.append([agent] + path)
                new_agents.append(next_pos) # Continúa en la torre

        self.agents = new_agents

        # Propagación de fuego cada K
        if self.turn % self.k_fire_turns == 0:
            self.propagate_fire()

        # Se revisa luego de propagación de fuego si algún agente quedó atrapado
        survivors = []
        for r, c in self.agents:
            if self.grid[r][c] == FIRE:
                self.deaths += 1   # Atrapado por la propagación del fuego
            else:
                survivors.append((r, c))
                
        self.agents = survivors

    def draw(self, surface):
        surface.fill(COLOR_BG)

        current_density = {}
        for pos in self.agents:
            current_density[pos] = current_density.get(pos, 0) + 1

        # GRILLA CON PESOS
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                cell = self.grid[r][c]
                occupancy = current_density.get((r, c), 0)
                
                if cell == WALL:
                    color = COLOR_WALL
                elif cell == FIRE:
                    color = COLOR_FIRE
                elif cell == EXIT:
                    color = COLOR_EXIT
                else:
                    color = get_congestion_color(occupancy) # Lo del mapeo de congestión

                rect = pygame.Rect(
                    c * (CELL_SIZE + MARGIN) + MARGIN,
                    r * (CELL_SIZE + MARGIN) + MARGIN,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(surface, color, rect)

                if cell not in (WALL, FIRE, EXIT):
                    cost_val = get_cost((r, c), current_density)
                    text_color = (0, 0, 0) if occupancy > 0 else (130, 130, 130)
                    weight_txt = font_weights.render(f"{cost_val:.1f}", True, text_color)
                    surface.blit(weight_txt, (rect.x + 1, rect.y + 1))

        # LINEA DE RUTAS
        for path in self.active_paths:
            if len(path) > 1:
                points = [
                    (
                        c * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2,
                        r * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                    )
                    for r, c in path
                ]
                pygame.draw.lines(surface, COLOR_PATH, False, points, 1)

        # AGENTES
        for pos, count in current_density.items():
            r, c = pos
            if self.grid[r][c] not in (FIRE, EXIT):
                cx = c * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                cy = r * (CELL_SIZE + MARGIN) + MARGIN + CELL_SIZE // 2
                
                pygame.draw.circle(surface, COLOR_AGENT, (cx, cy), CELL_SIZE // 3)
                
                if count > 1:
                    num_txt = font_ui.render(str(count), True, (255, 255, 255))
                    surface.blit(num_txt, (cx - 4, cy - 7))

        # 4. PANEL LATERAL
        px = GRID_WIDTH * (CELL_SIZE + MARGIN) + 15
        py = 15
        
        surface.blit(title_font.render("Panel de Control", True, COLOR_TEXT), (px, py))
        py += 25
        
        disp_name = self.filename if len(self.filename) <= 18 else self.filename[:15] + "..."
        surface.blit(font_ui.render(f"Archivo: {disp_name}", True, (0, 220, 255)), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Algoritmo: {self.algorithm}", True, (255, 215, 0)), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Propagación del Fuego: {self.k_fire_turns} turnos", True, (230, 100, 100)), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Turno: {self.turn}", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Agentes: {len(self.agents)} / {self.total_agents}", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Evacuados: {self.escaped}", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render(f"Fallecidos: {self.deaths}", True, COLOR_TEXT), (px, py))
        
        py += 25
        surface.blit(title_font.render("Configuración:", True, COLOR_TEXT), (px, py))
        py += 25
        surface.blit(font_ui.render("[C] Cargar Mapa (.txt)", True, (0, 255, 150)), (px, py))
        py += 20
        surface.blit(font_ui.render("[F] Cambiar Propagación del Fuego", True, (255, 150, 100)), (px, py))

        py += 25
        surface.blit(title_font.render("Algoritmos:", True, COLOR_TEXT), (px, py))
        py += 25
        surface.blit(font_ui.render("No Informados", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[1] BFS", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[2] Dijkstra", True, COLOR_TEXT), (px, py))
        py += 25
        surface.blit(font_ui.render("Informados:", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[3] A*", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[4] Greedy", True, COLOR_TEXT), (px, py))

        py += 30
        surface.blit(font_ui.render("[ESPACIO] Avanzar Turno", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[A] Modo Automático", True, COLOR_TEXT), (px, py))
        py += 20
        surface.blit(font_ui.render("[R] Reiniciar Estado", True, COLOR_TEXT), (px, py))


# loop main
def main():
    init_pygame_gui()
    sim = Simulation(filepath="mapa1.txt")
    auto = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Paso manual
                    sim.step()
                elif event.key == pygame.K_a: # Toggle de automatico
                    auto = not auto
                elif event.key == pygame.K_r and sim.filepath: # Reiniciar
                    sim = Simulation(
                        filepath=sim.filepath,
                        algorithm=sim.algorithm,
                        k_fire_turns=sim.k_fire_turns
                    )
                elif event.key == pygame.K_f: # Cambiar K de propagación
                    new_k = ask_fire_turns_dialog(sim.k_fire_turns)
                    if new_k is not None:
                        sim.k_fire_turns = new_k
                elif event.key == pygame.K_c: # Seleccionar nuevo mapa
                    selected_path = select_file_dialog()
                    if selected_path:
                        sim = Simulation(
                            filepath=selected_path,
                            algorithm=sim.algorithm,
                            k_fire_turns=sim.k_fire_turns
                        )
                elif event.key == pygame.K_1:
                    sim.algorithm = "BFS"
                elif event.key == pygame.K_2:
                    sim.algorithm = "Dijkstra"
                elif event.key == pygame.K_3:
                    sim.algorithm = "A*"
                elif event.key == pygame.K_4:
                    sim.algorithm = "Greedy"

        if auto and len(sim.agents) > 0:
            sim.step()
            pygame.time.delay(180)

        sim.draw(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()