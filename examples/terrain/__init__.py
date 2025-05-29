import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from grafica.terreno_fractal import diamond_square_algorithm
import click


def visualize_diamond_square_steps():
    """
    Visualiza paso a paso el algoritmo Diamond-Square.
    """
    size = 9  # 2^3 + 1
    heights = np.zeros((size, size))
    
    # Inicializar esquinas con valores aleatorios
    np.random.seed(42)
    heights[0, 0] = np.random.uniform(-0.5, 0.5)
    heights[0, size-1] = np.random.uniform(-0.5, 0.5)
    heights[size-1, 0] = np.random.uniform(-0.5, 0.5)
    heights[size-1, size-1] = np.random.uniform(-0.5, 0.5)
    
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    fig.suptitle('Algoritmo Diamond-Square: Pasos', fontsize=16)
    axes = axes.flatten()
    
    # Paso 0: Solo esquinas
    ax = axes[0]
    ax.imshow(heights, cmap='terrain', vmin=-1, vmax=1)
    ax.set_title('Inicio: 4 esquinas')
    ax.grid(True, alpha=0.3)
    
    # Ejecutar algoritmo paso a paso
    step_size = size - 1
    scale = 0.5
    step = 1
    
    while step_size > 1 and step < 4:
        half_step = step_size // 2
        
        # Paso Diamond (centros de cuadrados)
        for y in range(half_step, size - half_step, step_size):
            for x in range(half_step, size - half_step, step_size):
                avg = (heights[y - half_step, x - half_step] +
                       heights[y - half_step, x + half_step] +
                       heights[y + half_step, x - half_step] +
                       heights[y + half_step, x + half_step]) / 4.0
                heights[y, x] = avg + np.random.uniform(-scale, scale)
        
        # Paso Square (centros de diamantes)
        for y in range(0, size, half_step):
            for x in range((y + half_step) % step_size, size, step_size):
                total = 0
                count = 0
                
                # Promediar vecinos válidos
                for dy, dx in [(-half_step, 0), (half_step, 0), 
                              (0, -half_step), (0, half_step)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < size and 0 <= nx < size:
                        total += heights[ny, nx]
                        count += 1
                
                heights[y, x] = total / count + np.random.uniform(-scale, scale)
        
        # Visualizar
        ax = axes[step]
        ax.imshow(heights, cmap='terrain', vmin=-1, vmax=1)
        ax.set_title(f'Paso {step}: Subdivisión {step_size}→{half_step}')
        ax.grid(True, alpha=0.3)
        
        step_size //= 2
        scale *= 0.5
        step += 1
    
    plt.tight_layout()
    plt.show()


def compare_mesh_representations():
    """
    Compara Triangle Soup vs. Estructura Indexada.
    """
    # Generar datos simples
    heights = [[0.1, 0.2, 0.15],
                [0.3, 0.5, 0.4],
                [0.2, 0.3, 0.25]]
    
    fig = plt.figure(figsize=(14, 6))
    
    # Triangle Soup
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.set_title('Triangle Soup\n(48 valores almacenados)', fontsize=14)
    
    # Cada triángulo guarda sus propios vértices
    triangles_soup = []
    triangle_count = 0
    
    for i in range(2):
        for j in range(2):
            # Primer triángulo del cuadrado
            v1 = [i*0.4, j*0.4, heights[i][j]]
            v2 = [i*0.4, (j+1)*0.4, heights[i][j+1]]
            v3 = [(i+1)*0.4, j*0.4, heights[i+1][j]]
            triangles_soup.append([v1, v2, v3])
            
            # Anotar vértices del triángulo
            for k, v in enumerate([v1, v2, v3]):
                ax1.text(v[0], v[1], v[2]+0.05, f'T{triangle_count}:V{k}', 
                        fontsize=8, color='darkred')
            triangle_count += 1
            
            # Segundo triángulo
            v1 = [(i+1)*0.4, (j+1)*0.4, heights[i+1][j+1]]
            triangles_soup.append([v2, v1, v3])
            triangle_count += 1
    
    # Dibujar triángulos
    for tri in triangles_soup:
        poly = [[tuple(v) for v in tri]]
        collection = Poly3DCollection(poly, facecolors='lightblue', 
                                     edgecolors='black', linewidths=2, alpha=0.5)
        ax1.add_collection3d(collection)
    
    # Estructura Indexada
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.set_title('Estructura Indexada\n(9 vértices + 24 índices)', fontsize=14)
    
    # Lista de vértices únicos
    vertices = []
    for i in range(3):
        for j in range(3):
            vertices.append([i*0.4, j*0.4, heights[i][j]])
    
    # Dibujar vértices y numerarlos
    for idx, v in enumerate(vertices):
        ax2.scatter(v[0], v[1], v[2], c='red', s=100, edgecolors='black')
        ax2.text(v[0]+0.02, v[1]+0.02, v[2]+0.05, f'{idx}', 
                fontsize=10, color='darkred', weight='bold')
    
    # Índices para los triángulos
    indices = []
    for i in range(2):
        for j in range(2):
            idx1 = i * 3 + j
            idx2 = i * 3 + j + 1
            idx3 = (i + 1) * 3 + j
            idx4 = (i + 1) * 3 + j + 1
            
            indices.extend([[idx1, idx2, idx3], [idx2, idx4, idx3]])
    
    # Dibujar triángulos usando índices
    for tri_indices in indices:
        tri = [vertices[i] for i in tri_indices]
        poly = [[tuple(v) for v in tri]]
        collection = Poly3DCollection(poly, facecolors='lightcoral', 
                                     edgecolors='black', linewidths=1, alpha=0.5)
        ax2.add_collection3d(collection)
    
    # Configurar ejes
    for ax in [ax1, ax2]:
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Altura')
        ax.set_xlim(0, 0.8)
        ax.set_ylim(0, 0.8)
        ax.set_zlim(0, 0.6)
    
    plt.tight_layout()
    plt.show()


def demonstrate_mesh_operations():
    """
    Demuestra el concepto de one-ring neighborhood y análisis básico.
    """
    # Crear malla simple 5x5
    size = 5
    positions = []
    for i in range(size):
        for j in range(size):
            positions.append([i/(size-1), j/(size-1), 0])
    positions = np.array(positions)
    
    # Crear índices
    indices = []
    for i in range(size-1):
        for j in range(size-1):
            idx = i * size + j
            indices.extend([
                [idx, idx+1, idx+size],
                [idx+1, idx+size+1, idx+size]
            ])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. One-ring neighborhood
    ax1.set_title('One-ring Neighborhood', fontsize=14)
    ax1.set_aspect('equal')
    
    # Dibujar todos los vértices
    ax1.scatter(positions[:, 0], positions[:, 1], c='lightgray', s=50)
    
    # Vértice central (índice 12 = centro de grilla 5x5)
    center_idx = 12
    center = positions[center_idx]
    ax1.scatter(center[0], center[1], c='red', s=300, 
               edgecolors='black', linewidths=2, zorder=5)
    ax1.text(center[0]+0.05, center[1]+0.05, 'Centro', fontsize=12, weight='bold')
    
    # Encontrar y dibujar vecinos
    neighbors = set()
    for tri in indices:
        if center_idx in tri:
            # Dibujar triángulo
            triangle = positions[tri]
            for i in range(3):
                p1 = triangle[i]
                p2 = triangle[(i+1)%3]
                ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', linewidth=2, alpha=0.5)
            
            # Agregar vecinos
            for idx in tri:
                if idx != center_idx:
                    neighbors.add(idx)
    
    # Resaltar vecinos
    for n_idx in neighbors:
        pos = positions[n_idx]
        ax1.scatter(pos[0], pos[1], c='blue', s=150, 
                   edgecolors='black', linewidths=1, zorder=4)
    
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribución de grados
    ax2.set_title('Grado de los Vértices', fontsize=14)
    
    # Calcular grados
    degrees = np.zeros(len(positions))
    for tri in indices:
        for v in tri:
            degrees[v] += 1
    
    # Histograma
    unique_degrees, counts = np.unique(degrees, return_counts=True)
    bars = ax2.bar(unique_degrees, counts, color='green', alpha=0.7, edgecolor='black')
    
    # Marcar el grado ideal
    ax2.axvline(6, color='red', linestyle='--', linewidth=2, label='Grado ideal = 6')
    ax2.text(6.1, max(counts)*0.8, 'Ideal', color='red', fontsize=12)
    
    ax2.set_xlabel('Grado (número de triángulos incidentes)')
    ax2.set_ylabel('Número de vértices')
    ax2.set_xticks(unique_degrees)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Anotar barras con el tipo de vértice
    labels = {3: 'Esquina', 4: 'Borde', 6: 'Interior'}
    for bar, deg in zip(bars, unique_degrees):
        if deg in labels:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    labels[deg], ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.show()


def visualize_lod_hierarchy():
    """
    Muestra el concepto de niveles de detalle (LOD).
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Niveles de Detalle (LOD)', fontsize=16)
    
    resolutions = [5, 9, 17]
    labels = ['Baja (LOD 2)', 'Media (LOD 1)', 'Alta (LOD 0)']
    
    for ax, res, label in zip(axes, resolutions, labels):
        # Generar terreno
        heights = diamond_square_algorithm(res, roughness=0.6, seed=42)
        
        # Visualizar
        x = np.linspace(0, 1, res)
        y = np.linspace(0, 1, res)
        X, Y = np.meshgrid(x, y)
        
        # Mostrar superficie 3D simple
        ax = plt.subplot(1, 3, axes.tolist().index(ax) + 1, projection='3d')
        surf = ax.plot_surface(X, Y, heights, cmap='terrain', 
                              linewidth=0.5, edgecolors='black', alpha=0.8)
        
        # Información
        n_vertices = res * res
        n_triangles = 2 * (res - 1) * (res - 1)
        
        ax.set_title(f'{label}\n{n_vertices} vértices, {n_triangles} triángulos')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Altura')
        ax.view_init(elev=30, azim=45)
    
    plt.tight_layout()
    plt.show()


def analyze_terrain_properties():
    """
    Analiza propiedades básicas del terreno generado.
    """
    # Generar terreno
    size = 33
    heights = diamond_square_algorithm(size, roughness=0.6, seed=42)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Análisis de Terreno Generado', fontsize=16)
    
    # 1. Mapa de alturas
    ax = axes[0]
    im = ax.imshow(heights, cmap='terrain')
    plt.colorbar(im, ax=ax, label='Altura')
    ax.set_title('Mapa de Alturas')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    
    # 2. Vista 3D
    ax = plt.subplot(1, 3, 2, projection='3d')
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)
    
    surf = ax.plot_surface(X, Y, heights, cmap='terrain', 
                          linewidth=0, antialiased=True)
    ax.set_title('Vista 3D')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Altura')
    ax.view_init(elev=30, azim=45)
    
    # 3. Histograma de alturas
    ax = axes[2]
    ax.hist(heights.flatten(), bins=30, color='brown', alpha=0.7, 
            edgecolor='black')
    ax.set_title('Distribución de Alturas')
    ax.set_xlabel('Altura')
    ax.set_ylabel('Frecuencia')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Estadísticas básicas
    print("\n=== Estadísticas del Terreno ===")
    print(f"Altura mínima: {heights.min():.3f}")
    print(f"Altura máxima: {heights.max():.3f}")
    print(f"Altura promedio: {heights.mean():.3f}")
    print(f"Desviación estándar: {heights.std():.3f}")


@click.command("terrain_generation", short_help="Ejemplo de generación de terrenos")
def terrain_generation():
    """Ejemplos educativos sobre mallas y generación procedural."""
    
    while True:
        print("\n=== Ejemplos de Mallas y Generación Procedural ===")
        print("\n1. Algoritmo Diamond-Square paso a paso")
        print("2. Triangle Soup vs. Estructura Indexada")
        print("3. Conectividad y One-ring Neighborhood")
        print("4. Niveles de Detalle (LOD)")
        print("5. Análisis de terreno generado")
        print("6. Salir")
        
        choice = input("\nElige una opción (1-6): ")
        
        if choice == '1':
            print("\n→ Mostrando pasos del algoritmo Diamond-Square...")
            visualize_diamond_square_steps()
        elif choice == '2':
            print("\n→ Comparando representaciones de mallas...")
            compare_mesh_representations()
        elif choice == '3':
            print("\n→ Analizando conectividad de la malla...")
            demonstrate_mesh_operations()
        elif choice == '4':
            print("\n→ Mostrando concepto de LOD...")
            visualize_lod_hierarchy()
        elif choice == '5':
            print("\n→ Analizando propiedades del terreno...")
            analyze_terrain_properties()
        elif choice == '6':
            print("\n¡Chao, pescao!")
            break
        else:
            print("\nOpción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    terrain_generation()