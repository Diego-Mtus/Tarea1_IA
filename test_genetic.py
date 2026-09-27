from genetic import GeneticAlgorithm

def main():
    print("=== TEST INDIVIDUAL: ALGORITMO GENÉTICO GENERAL ===")
    ga = GeneticAlgorithm(filepath="mapa1.txt", pop_size=100, generations=100, k_fire_turns=3)
    best_policy, stats = ga.run(verbose=True)

    print("\n--- RESULTADOS OBTENIDOS ---")
    print(f"Evacuados con éxito: {stats['evacuados']} / {stats['total_agentes']}")
    print(f"Fallecidos por fuego: {stats['fallecidos']}")
    print(f"Turnos de despeje: {stats['turnos_despeje']}")
    print(f"Tasa de supervivencia: {stats['tasa_supervivencia']:.2f}%")

if __name__ == "__main__":
    main()