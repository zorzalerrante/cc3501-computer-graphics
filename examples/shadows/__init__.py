import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
import click
from pathlib import Path

from grafica.scenegraph import Scenegraph
from grafica.scenegraph_premade import rectangle_2d
import grafica.transformations as tr


@click.command(
    "shadow_mapping", short_help="Sombras mediante la técnica shadow mapping."
)
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def shadow_mapping(width, height):
    """
    Implementación de shadow mapping usando un grafo de escena.
    
    Parámetros:
    width -- Ancho de la ventana en píxeles
    height -- Alto de la ventana en píxeles
    """
    
    # -------------------------------------------------------------------------
    # 1. CONFIGURACIÓN INICIAL
    # -------------------------------------------------------------------------
    
    # Crear ventana de pyglet
    window = pyglet.window.Window(width, height)
    
    # Crear grafo de escena principal
    graph = Scenegraph("root")
    
    # -------------------------------------------------------------------------
    # 2. CARGAR MODELOS 3D
    # -------------------------------------------------------------------------
    
    # Cargar modelos para la escena
    graph.load_and_register_mesh("cornell_box", "assets/CornellBox_original.obj")
    graph.load_and_register_mesh("sphere", "assets/sphere.off")
    graph.load_and_register_mesh("squirtle", "assets/Squirtle.STL", force_color=np.array([255, 20, 160, 255]))

    
    # -------------------------------------------------------------------------
    # 3. CARGAR SHADERS
    # -------------------------------------------------------------------------
    
    # Shader para renderizar profundidad (shadow pass)
    graph.load_and_register_pipeline(
        "depth_shader",
        Path(os.path.dirname(__file__)) / "simple_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "simple_fragment_program.glsl",
    )
    
    # Shader principal para renderizado con iluminación
    graph.load_and_register_pipeline(
        "basic_shader",
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )
    
    # Shader para visualizar la bombilla (fuente de luz)
    graph.load_and_register_pipeline(
        "bulb_pipeline",
        Path(os.path.dirname(__file__)) / ".." / "disco_bunny" / "bulb_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / ".." / "disco_bunny" / "bulb_fragment_program.glsl",
    )
    
    # Configurar pipeline actual
    graph.register_pipeline("current_shader", graph.pipelines["basic_shader"])
    
    # -------------------------------------------------------------------------
    # 4. CONSTRUIR ESCENA
    # -------------------------------------------------------------------------
    
    # Agregar caja de Cornell como objeto principal
    graph.add_mesh_instance("main", "cornell_box", "current_shader")
    graph.add_edge("root", "main")
    
    # Agregar Squirtle a la escena
    graph.add_mesh_instance('pokemon', 'squirtle', 'current_shader', 
                           transform=tr.uniformScale(0.5))
    graph.add_edge('main', 'pokemon')
    
    # Crear representación visual de la luz como una esfera
    graph.add_mesh_instance(
        "bulb_mesh",
        "sphere",
        "bulb_pipeline",
        transform=tr.uniformScale(0.1),
        bulb_color=np.array([1.0, 0.3, 0.0]),
    )
    
    # -------------------------------------------------------------------------
    # 5. CONFIGURAR CÁMARAS
    # -------------------------------------------------------------------------
    
    # Parámetros de frustum
    near_plane = 0.1
    far_plane = 3.0
    
    # Cámara principal (vista del usuario)
    projection_camera = tr.perspective(
        45, float(width) / float(height), near_plane, far_plane
    )
    view_camera = tr.lookAt(
        np.array([0, 0, 2]),      # Posición de la cámara
        np.array([0, 0, 0]),      # Punto de mira
        np.array([0, 1, 0])       # Vector "arriba"
    )
    
    # Cámara de luz (para shadow mapping)
    light_pos = np.array([0.0, 0.55, -0.03])
    projection_light = tr.perspective(
        90, float(width) / float(height), near_plane, far_plane
    )
    view_light = tr.lookAt(
        np.array(light_pos),      # Posición de la luz
        np.array([0.0, 0.0, 0.0]), # Punto de mira
        np.array([0.0, 0.0, -1.0]) # Vector "arriba"
    )
    
    # Matriz combinada para transformar a espacio de luz
    light_transform = projection_light @ view_light
    
    # Registrar las transformaciones de vista en el grafo
    graph.register_view_transform(view_light, name="light_view")
    graph.register_view_transform(view_camera, name="camera_view")
    
    # -------------------------------------------------------------------------
    # 6. CONFIGURAR JERARQUÍA DE LA LUZ
    # -------------------------------------------------------------------------
    
    # Configurar nodos para la luz (permitiendo animación)
    graph.add_node("bulb", transform=tr.translate(*light_pos))
    graph.add_edge("root", "bulb")
    graph.add_edge("bulb", "bulb_perturbation")
    graph.add_edge("bulb_perturbation", "bulb_mesh")
    
    # -------------------------------------------------------------------------
    # 7. CONFIGURAR SHADOW MAPPING
    # -------------------------------------------------------------------------
    
    # Crear textura de color (no usada para shadow mapping)
    color_buffer = pyglet.image.Texture.create(
        width, height, min_filter=GL.GL_NEAREST, mag_filter=GL.GL_NEAREST
    )
    
    # Crear textura de profundidad (shadow map)
    depth_buffer = pyglet.image.Texture.create(
        width,
        height,
        internalformat=GL.GL_DEPTH_COMPONENT32,  # 32 bits para mayor precisión
        fmt=GL.GL_DEPTH_COMPONENT,
        min_filter=GL.GL_LINEAR,                # Filtrado lineal para mejorar calidad
        mag_filter=GL.GL_LINEAR,
    )
    
    # Configurar parámetros de textura para el shadow map
    GL.glBindTexture(GL.GL_TEXTURE_2D, depth_buffer.id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_BORDER)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_BORDER)
    border_color = [1.0, 1.0, 1.0, 1.0]  # Color blanco para bordes fuera del frustum
    GL.glTexParameterfv(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_BORDER_COLOR, (GL.GLfloat * 4)(*border_color))
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    
    # Crear y configurar framebuffer para renderizar a textura
    framebuffer = pyglet.image.Framebuffer()
    framebuffer.attach_texture(color_buffer, attachment=GL.GL_COLOR_ATTACHMENT0)
    framebuffer.attach_texture(depth_buffer, attachment=GL.GL_DEPTH_ATTACHMENT)
    
    # Verificar que el framebuffer esté completo
    framebuffer.bind()
    status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
    if status != GL.GL_FRAMEBUFFER_COMPLETE:
        print(f"Framebuffer incompleto: {status}")
    framebuffer.unbind()
    
    # Asociar textura de shadow map con nodos que necesitan proyectar sombras
    graph.add_texture_to_node('main', 'shadow_map', depth_buffer.id)
    graph.add_texture_to_node('pokemon', 'shadow_map', depth_buffer.id)
    
    # -------------------------------------------------------------------------
    # 8. CONFIGURAR VISUALIZACIÓN DE SHADOW MAP
    # -------------------------------------------------------------------------
    
    # Crear grafo para mostrar el shadow map en pantalla
    fbo_scene = Scenegraph("root")
    fbo_scene.load_and_register_pipeline(
        "quad_view",
        Path(os.path.dirname(__file__)) / "screen_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "screen_fragment_program.glsl",
    )
    fbo_scene.register_mesh("quad", rectangle_2d(texture=depth_buffer))
    fbo_scene.add_mesh_instance("screen", "quad", "quad_view")
    fbo_scene.add_edge("root", "screen")
    
    # Variables de estado
    light_pov = False  # Alternar entre vista de cámara y vista de la luz
    total_time = 0.0   # Tiempo total para animaciones
    
    # -------------------------------------------------------------------------
    # 9. HANDLERS DE EVENTOS
    # -------------------------------------------------------------------------
    
    @window.event
    def on_key_press(symbol, modifiers):
        """Cambiar entre vista normal y vista del shadow map con la barra espaciadora"""
        nonlocal light_pov
        if symbol == pyglet.window.key.SPACE:
            light_pov = not light_pov
    
    @window.event
    def on_draw():
        """Render loop principal"""
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)
        
        # PASO 1: Renderizar la escena desde el punto de vista de la luz
        # Esto genera el shadow map que se usa para calcular sombras
        framebuffer.bind()
        window.clear()
        graph.pipelines["current_shader"] = graph.pipelines["depth_shader"]
        graph.current_view = "light_view"
        graph.set_global_attributes(
            projection=projection_light
        )
        graph.render(recalculate_transforms=False)
        framebuffer.unbind()
        
        # PASO 2: Renderizar la escena final con sombras
        window.clear()
        
        if light_pov:
            # Modo debug: mostrar el shadow map en pantalla
            GL.glDisable(GL.GL_DEPTH_TEST)
            fbo_scene.render()
        else:
            # Modo normal: renderizar escena con iluminación y sombras
            graph.pipelines["current_shader"] = graph.pipelines["basic_shader"]
            graph.current_view = "camera_view"
            graph.set_global_attributes(
                projection=projection_camera,
                light_position=graph.get_global_position("bulb_perturbation"),
                light_transform=light_transform,
            )
            graph.render(recalculate_transforms=False)
    
    def update_world(dt, window):
        """Actualizar animaciones y estado del mundo"""
        nonlocal total_time, light_transform, view_light
        total_time += dt

        graph.nodes["pokemon"]["transform"] = tr.rotationY(total_time * 0.5)
        
        # Animar posición de la luz
        base = 0.01
        graph.nodes["bulb_perturbation"]["transform"] = tr.translate(
            base + 0.075 * np.sin(total_time * 5.0),
            0,
            base + 0.05 * np.sin(total_time * 3.7),
        )
        
        # Recalcular transformaciones globales
        graph.calculate_global_transforms()
        
        # Actualizar vista de luz para seguir la posición actual de la luz
        view_light = tr.lookAt(
            graph.get_global_position("bulb_perturbation"),
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, -1.0]),
        )
        light_transform = projection_light @ view_light
        graph.register_view_transform(
            view_light,
            name="light_view",
        )
    
    # -------------------------------------------------------------------------
    # 10. INICIAR LOOP PRINCIPAL
    # -------------------------------------------------------------------------
    
    # Programar actualización del mundo a 60 FPS
    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    
    # Iniciar el loop principal
    pyglet.app.run()