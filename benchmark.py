import csv
import numpy as np
from main import Simulation

# Esto va a ser para ejecutar el benchmark sin lo visual, para q sea más rápido.
def run_headless_benchmark():

    # Definir los mapas a evaluar
    mapas = ["mapa1.txt"] 
    algoritmos = ["BFS", "Dijkstra", "A*", "Greedy"]
    num_iterations = 200  
    max_turns = 500
    
    csv_filename = "resultados_benchmark.csv"

    print("= Iniciando benchmark=\n")

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Encabezados para las métricas obligatorias
        writer.writerow(["Mapa", "Algoritmo", "Iteracion", "Turnos_Despeje", "Evacuados", "Fallecidos", "Tasa_Supervivencia"])

        for mapa in mapas:
            for algo in algoritmos:
                print(f"Ejecutando {num_iterations} iteraciones -> Mapa: '{mapa}' | Algoritmo: '{algo}'...")
                
                turnos_list = []
                supervivencia_list = []

                for i in range(1, num_iterations + 1):

                    sim = Simulation(filepath=mapa, algorithm=algo, k_fire_turns=3)
                    sim.randomize_agents() # Aleatorizar posiciones
                    while sim.agents and sim.turn < max_turns:
                        sim.step() # Se hacen los pasos sin draw

                    # Metricas de supervivencia
                    tasa_supervivencia = (sim.escaped / sim.total_agents * 100) if sim.total_agents > 0 else 0.0

                    # Guardar resultados
                    writer.writerow([
                        mapa, algo, i, 
                        sim.turn, 
                        sim.escaped, 
                        sim.deaths, 
                        f"{tasa_supervivencia:.2f}"
                    ])

                    turnos_list.append(sim.turn)
                    supervivencia_list.append(tasa_supervivencia)

                    if i % 10 == 0:
                        print(f" [Iteración {i}/{num_iterations}]")


                print(f"Tasa Supervivencia Media: {np.mean(supervivencia_list):.2f}%")
                print(f"Turnos Despeje -> Media: {np.mean(turnos_list):.2f} | Desv.Est: {np.std(turnos_list):.2f} | Mín: {np.min(turnos_list)} | Máx: {np.max(turnos_list)}\n")

    print(f"Datos exportados a '{csv_filename}'.")

if __name__ == "__main__":
    run_headless_benchmark()