import random
import copy
import os
from collections import deque

ACTIONS = [0, 1, 2, 3, 4]
DIR_MAP = {
    0: (0, 0),   # Esperar
    1: (-1, 0),  # Arriba
    2: (1, 0),   # Abajo
    3: (0, -1),  # Izquierda
    4: (0, 1)    # Derecha
}

GRID_WIDTH = 30
GRID_HEIGHT = 20


# El cromosoma es la lista de instrucciones de movimiento para todo el grupo.
class GeneticAlgorithm:

    def __init__(self, filepath="mapa1.txt", pop_size=80, chromosome_len=150, generations=100, k_fire_turns=4):
        self.filepath = filepath
        self.pop_size = pop_size # Tamaño de la población
        self.chromosome_len = chromosome_len # Cantidad de turnos planificados
        self.generations = generations # Número de generaciones a evolucionar
        self.k_fire_turns = k_fire_turns # Cada cuántos turnos se propaga el fuego
        
        self.grid_template, self.initial_agents, self.exit_pos = self.load_map_data(filepath)
        self.total_agents = len(self.initial_agents)
        self.real_distance_map = self.bfs_distance_map()

    def load_map_data(self, filepath):
        grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        agents = []
        exit_pos = None

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"El archivo de mapa '{filepath}' no fue encontrado.")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for r in range(min(GRID_HEIGHT, len(lines))):
            line = lines[r]
            for c in range(min(GRID_WIDTH, len(line))):
                char = line[c]
                if char == 'P': grid[r][c] = 1   # Muro
                elif char == 'F': grid[r][c] = 2 # Fuego
                elif char == 'E': 
                    grid[r][c] = 3               # Salida
                    exit_pos = (r, c)
                elif char.isdigit():
                    for _ in range(int(char)):
                        agents.append((r, c))

        return grid, agents, exit_pos

    # Para el fitness, usamos bfs para calcular la distancia mínima a la salida desde cada celda
    # Porque manhattan no es suficiente en presencia de muros y fuego
    def bfs_distance_map(self):
        """Calcula la distancia mínima por pasillos libres a la salida."""
        dist_map = [[999 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        if not self.exit_pos:
            return dist_map

        queue = deque([(self.exit_pos[0], self.exit_pos[1], 0)])
        dist_map[self.exit_pos[0]][self.exit_pos[1]] = 0

        while queue:
            r, c, d = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH:
                    if self.grid_template[nr][nc] != 1 and dist_map[nr][nc] == 999:
                        dist_map[nr][nc] = d + 1
                        queue.append((nr, nc, d + 1))

        return dist_map

    # Para el benchmark, se aleatorizan los agentes para que no sea siempre la misma posición inicial
    def set_random_agents(self):
        empty_cells = []
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                if self.grid_template[r][c] == 0:
                    empty_cells.append((r, c))
        if empty_cells and self.total_agents > 0:
            self.initial_agents = [random.choice(empty_cells) for _ in range(self.total_agents)]

    # Genera movimientos aleatorios
    def create_individual(self):
        return [random.choice(ACTIONS) for _ in range(self.chromosome_len)]

    def evaluate_fitness(self, chromosome):
        grid = copy.deepcopy(self.grid_template)
        agents = list(self.initial_agents)
        escaped = 0
        deaths = 0
        turn = 0
        
        progress_score = 0

        for action in chromosome:
            turn += 1
            if not agents:
                break

            dr, dc = DIR_MAP[action]
            new_agents = []

            for r, c in agents:
                nr, nc = r + dr, c + dc
                
                # Si la instrucción del genoma choca con un muro o borde,
                # el simulador redirige la colisión hacia el paso libre con menor distancia BFS
                if not (0 <= nr < GRID_HEIGHT and 0 <= nc < GRID_WIDTH) or grid[nr][nc] == 1:
                    best_r, best_c = r, c
                    best_dist = self.real_distance_map[r][c]
                    for fdr, fdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        tr, tc = r + fdr, c + fdc
                        if 0 <= tr < GRID_HEIGHT and 0 <= tc < GRID_WIDTH and grid[tr][tc] != 1:
                            if self.real_distance_map[tr][tc] < best_dist:
                                best_dist = self.real_distance_map[tr][tc]
                                best_r, best_c = tr, tc
                    nr, nc = best_r, best_c

                if (nr, nc) == self.exit_pos:
                    escaped += 1
                elif grid[nr][nc] == 2: # Fuego
                    deaths += 1
                else:
                    new_agents.append((nr, nc))
                    prev_d = self.real_distance_map[r][c]
                    curr_d = self.real_distance_map[nr][nc]
                    if curr_d < prev_d:
                        progress_score += 200
                    elif curr_d > prev_d:
                        progress_score -= 100

            agents = new_agents

            # Propagación de fuego cada k turnos
            if turn % self.k_fire_turns == 0:
                new_fires = []
                for fr in range(GRID_HEIGHT):
                    for fc in range(GRID_WIDTH):
                        if grid[fr][fc] == 2:
                            for fdr, fdc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nfr, nfc = fr + fdr, fc + fdc
                                if 0 <= nfr < GRID_HEIGHT and 0 <= nfc < GRID_WIDTH and grid[nfr][nfc] in (0, 1):
                                    new_fires.append((nfr, nfc))
                for fr, fc in new_fires:
                    grid[fr][fc] = 2

            survivors = []
            for r, c in agents:
                if grid[r][c] == 2:
                    deaths += 1
                else:
                    survivors.append((r, c))
            agents = survivors

        final_dist_penalty = sum(self.real_distance_map[r][c] for r, c in agents)

        # Aptitud
        fitness = (escaped * 1000000) + progress_score - (deaths * 5000) - (final_dist_penalty * 100)
        return fitness, escaped, deaths, turn

    # Selección por torneo de 4 individuos.
    # El mejor de los 4 es elegido como padre.
    def selection(self, population, fitnesses):
 
        tournament = random.sample(list(zip(population, fitnesses)), k=4)
        tournament.sort(key=lambda x: x[1], reverse=True)
        return copy.deepcopy(tournament[0][0])

    # Se escoge un punto de cruce aleatorio y se intercambian los genes de los padres.
    def crossover(self, parent1, parent2):
        if random.random() < 0.85:
            point = random.randint(1, self.chromosome_len - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

    # Cada gen tiene una probabilidad de mutar a un movimiento aleatorio.
    def mutate(self, individual, mutation_rate=0.08):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = random.choice(ACTIONS)

    def run(self, verbose=False):
        population = [self.create_individual() for _ in range(self.pop_size)]
        best_overall = None
        best_fitness_overall = float('-inf')
        best_stats = None

        for gen in range(1, self.generations + 1):
            evaluations = [self.evaluate_fitness(ind) for ind in population]
            fitnesses = [e[0] for e in evaluations]

            max_fit_idx = fitnesses.index(max(fitnesses))
            if fitnesses[max_fit_idx] > best_fitness_overall:
                best_fitness_overall = fitnesses[max_fit_idx]
                best_overall = copy.deepcopy(population[max_fit_idx])
                best_stats = evaluations[max_fit_idx]

            # Elitismo
            new_population = [copy.deepcopy(best_overall)]

            # Torneo
            while len(new_population) < self.pop_size:
                # Elige dos padres mediante selección por torneo
                p1 = self.selection(population, fitnesses)
                p2 = self.selection(population, fitnesses)
                c1, c2 = self.crossover(p1, p2)
                self.mutate(c1)
                self.mutate(c2)
                new_population.extend([c1, c2])

            population = new_population[:self.pop_size]

            if verbose and (gen % 10 == 0 or gen == self.generations):
                print(f"  [Gen {gen}/{self.generations}] Fitness: {best_fitness_overall:.1f} | Evacuados: {best_stats[1]}/{self.total_agents} | Muertes: {best_stats[2]}")

        tasa_supervivencia = (best_stats[1] / self.total_agents * 100) if self.total_agents > 0 else 0.0
        return best_overall, {
            "turnos_despeje": best_stats[3],
            "evacuados": best_stats[1],
            "fallecidos": best_stats[2],
            "total_agentes": self.total_agents,
            "tasa_supervivencia": tasa_supervivencia
        }