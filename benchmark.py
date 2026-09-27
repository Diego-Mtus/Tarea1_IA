import csv
import numpy as np
from main import Simulation
from genetic import GeneticAlgorithm

def run_headless_benchmark():

    mapas = ["mapa1.txt", "mapa2.txt", "mapa3.txt"] 
    algoritmos = ["BFS", "Dijkstra", "A*", "Greedy", "Genetic"]
    num_iterations = 160  
    max_turns = 500
    k_fire_turns = 3
    
    csv_filename = "resultados_benchmark.csv"

    print("=== Iniciando Benchmark ===\n")

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Encabezados
        writer.writerow(["Mapa", "Algoritmo", "Iteracion", "Turnos_Despeje", "Evacuados", "Fallecidos", "Tasa_Supervivencia"])

        for mapa in mapas:
            for algo in algoritmos:
                print(f"Ejecutando {num_iterations} iteraciones -> Mapa: '{mapa}' | Algoritmo: '{algo}'...")
                
                turnos_list = []
                supervivencia_list = []

                for i in range(1, num_iterations + 1):

                    if algo == "Genetic":

                        ga = GeneticAlgorithm(
                            filepath=mapa, 
                            pop_size=60, 
                            chromosome_len=150, 
                            generations=80, 
                            k_fire_turns=k_fire_turns
                        )

                        ga.set_random_agents()


                        _, stats = ga.run(verbose=False)

                        turnos_despeje = stats["turnos_despeje"]
                        evacuados = stats["evacuados"]
                        fallecidos = stats["fallecidos"]
                        tasa_supervivencia = stats["tasa_supervivencia"]

                    else:
                        # BFS, Dijkstra, A*, Greedy
                        sim = Simulation(filepath=mapa, algorithm=algo, k_fire_turns=k_fire_turns)
                        sim.randomize_agents()

                        while sim.agents and sim.turn < max_turns:
                            sim.step()

                        turnos_despeje = sim.turn
                        evacuados = sim.escaped
                        fallecidos = sim.deaths
                        tasa_supervivencia = (sim.escaped / sim.total_agents * 100) if sim.total_agents > 0 else 0.0

                    # Guardar fila de resultados en el CSV
                    writer.writerow([
                        mapa, algo, i, 
                        turnos_despeje, 
                        evacuados, 
                        fallecidos, 
                        f"{tasa_supervivencia:.2f}"
                    ])

                    turnos_list.append(turnos_despeje)
                    supervivencia_list.append(tasa_supervivencia)

                    if i % 20 == 0:
                        print(f"  [Iteración {i}/{num_iterations} completada]")

                # Resumen
                print(f"--> Tasa Supervivencia Media ({algo}): {np.mean(supervivencia_list):.2f}%")
                print(f"--> Turnos Despeje -> Media: {np.mean(turnos_list):.2f} | Desv.Est: {np.std(turnos_list):.2f} | Mín: {np.min(turnos_list)} | Máx: {np.max(turnos_list)}\n")

    print(f"Benchmark finalizado. Todos los datos fueron exportados a '{csv_filename}'.")

if __name__ == "__main__":
    run_headless_benchmark()