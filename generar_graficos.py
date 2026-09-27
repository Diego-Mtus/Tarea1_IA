import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Generador de gráficos realizado con IA.
def generate_benchmark_charts(csv_file="resultados_benchmark.csv"):
    if not os.path.exists(csv_file):
        print(f"Error: No se encontró el archivo '{csv_file}'. Ejecuta primero el benchmarking.")
        return

    # Cargar los datos exportados
    df = pd.read_csv(csv_file)
    print(f"Cargados {len(df)} registros desde '{csv_file}'. Generando gráficos...")

    # Configuración de estilo visual para gráficos de informe académico
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 11, 'font.family': 'sans-serif'})
    palette = sns.color_palette("Set2")

    # ==========================================
    # GRÁFICO 1: Tasa de Supervivencia Promedio
    # ==========================================
    plt.figure(figsize=(9, 5))
    survival_df = df.groupby("Algoritmo")["Tasa_Supervivencia"].mean().reset_index()
    survival_df = survival_df.sort_values(by="Tasa_Supervivencia", ascending=False)

    ax1 = sns.barplot(
        data=survival_df, 
        x="Algoritmo", 
        y="Tasa_Supervivencia", 
        palette="viridis"
    )
    plt.title("Tasa Promedio de Supervivencia por Algoritmo", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Algoritmo de Búsqueda", labelpad=10)
    plt.ylabel("Supervivencia (%)", labelpad=10)
    plt.ylim(0, 110)

    # Añadir las etiquetas con el valor numérico exacto sobre cada barra
    for p in ax1.patches:
        val = p.get_height()
        ax1.annotate(f'{val:.1f}%', 
                     (p.get_x() + p.get_width() / 2., val), 
                     ha='center', va='center', 
                     xytext=(0, 7), 
                     textcoords='offset points',
                     fontweight='bold')

    plt.tight_layout()
    chart1_path = "grafico_tasa_supervivencia.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f" Guardado: {chart1_path}")

    # ==========================================
    # GRÁFICO 2: Distribución de Turnos de Despeje (Boxplot)
    # ==========================================
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=df, 
        x="Algoritmo", 
        y="Turnos_Despeje", 
        palette="Set2",
        width=0.4,
        boxprops=dict(alpha=0.8)
    )
    plt.title("Distribución de Turnos de Despeje", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Algoritmo de Búsqueda", labelpad=10)
    plt.ylabel("Turnos de Despeje", labelpad=10)

    plt.tight_layout()
    chart2_path = "grafico_distribucion_turnos.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f" Guardado: {chart2_path}")

    # ==========================================
    # GRÁFICO 3: Evacuados vs. Fallecidos Promedio
    # ==========================================
    summary_df = df.groupby("Algoritmo")[["Evacuados", "Fallecidos"]].mean().reset_index()
    summary_melted = pd.melt(summary_df, id_vars=["Algoritmo"], value_vars=["Evacuados", "Fallecidos"], 
                             var_name="Resultado", value_name="Cantidad")

    plt.figure(figsize=(10, 5))
    ax3 = sns.barplot(
        data=summary_melted, 
        x="Algoritmo", 
        y="Cantidad", 
        hue="Resultado", 
        palette=["#2a9d8f", "#e76f51"]
    )
    plt.title("Promedio de Evacuados vs. Fallecidos", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Algoritmo de Búsqueda", labelpad=10)
    plt.ylabel("Número Promedio de Agentes", labelpad=10)

    for p in ax3.patches:
        val = p.get_height()
        if val > 0:
            ax3.annotate(f'{val:.1f}', 
                         (p.get_x() + p.get_width() / 2., val), 
                         ha='center', va='center', 
                         xytext=(0, 6), 
                         textcoords='offset points',
                         fontsize=9)

    plt.legend(title="Resultado")
    plt.tight_layout()
    chart3_path = "grafico_evacuados_vs_fallecidos.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f" Guardado: {chart3_path}")

    # ==========================================
    # TABLA ESTADÍSTICA: Descriptivos de Turnos de Despeje
    # ==========================================

    stats_df = df.groupby(["Mapa", "Algoritmo"])["Turnos_Despeje"].agg(
        Media='mean',
        Desviacion_Estandar='std',
        Minimo='min',
        Maximo='max'
    ).reset_index()

    # Redondear números
    stats_df['Media'] = stats_df['Media'].round(2)
    stats_df['Desviacion_Estandar'] = stats_df['Desviacion_Estandar'].round(2)

    # Crear figura para renderizar la tabla visual
    fig, ax = plt.subplots(figsize=(10, len(stats_df) * 0.45 + 1.5))
    ax.axis('tight')
    ax.axis('off')

    # Encabezados limpios para la imagen
    headers = ["Mapa", "Algoritmo", "Media (Turnos)", "Desv. Estándar", "Mínimo", "Máximo"]
    
    # Dibujar la tabla
    table = ax.table(
        cellText=stats_df.values, 
        colLabels=headers, 
        cellLoc='center', 
        loc='center'
    )

    # Estilo estético para la tabla
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    # Formato de colores (Encabezados oscuros, filas alternadas)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#2B3A42')
            cell.set_text_props(color='white', fontweight='bold')
        else:
            if row % 2 == 0:
                cell.set_facecolor('#F0F4F8')
            else:
                cell.set_facecolor('#FFFFFF')

    plt.title("Estadísticos Descriptivos", fontsize=12, fontweight="bold", pad=10)
    
    table_img_path = "tabla_estadisticas_turnos.png"
    plt.savefig(table_img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" Guardado: {table_img_path}")
    print("\nLos gráficos han sido generados exitosamente.")

if __name__ == "__main__":
    generate_benchmark_charts()