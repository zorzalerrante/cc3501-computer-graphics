from pyglet.math import Vec2

# based on https://github.com/Josephbakulikira/Cloth-Simulation-With-python---Verlet-Integration/
# no funciona completamente! por qué crees que sucede?

gravity = Vec2(0.0, -9.8)
damping = 0.01


def distance(v1, v2):
    return v1.distance(v2)


class Point:
    def __init__(self, position):
        self.position = position
        self.previousPosition = position
        self.force = gravity

    def bound(self, max_x, max_y):
        if self.position.x < 0:
            self.position.x = 0
            self.previousPosition.x = self.position.x
        if self.position.x > max_x:
            self.position.x = max_x
            self.previousPosition.x = self.position.x

        if self.position.y < 0:
            self.position.y = 0
            self.previousPosition.y = self.position.y
        if self.position.y > max_y:
            self.position.y = max_y
            self.previousPosition.y = self.position.y


class ClothSystem:
    def __init__(self, vertices, joints, static=[], bound_width=640, bound_height=480):
        self.vertices = vertices
        self.joints = joints
        self.static = static
        self.dists = [
            distance(self.vertices[i].position, self.vertices[j].position)
            for i, j in self.joints
        ]
        self.bound_width = bound_width
        self.bound_height = bound_height

    def update(self, dt, toggle=None, bSpace=None):
        for vertex in self.vertices:
            if not vertex in self.static:
                vertex.bound(self.bound_width, self.bound_height)
                vertex.force = gravity
            else:
                vertex.force = Vec2()
                vertex.position = vertex.previousPosition

        self._verlet_update(dt)
        self._apply_restrictions()

    def _verlet_update(self, dt):
        for vertex in self.vertices:
            if not vertex in self.static:
                curr_pos = vertex.position
                vertex.position = (
                    vertex.position
                    + (vertex.position - vertex.previousPosition)
                    + vertex.force * dt * dt
                )
                vertex.previousPosition = curr_pos

    def _apply_restrictions(self):
        for length, joint in zip(self.dists, self.joints):
            src = self.vertices[joint[0]]
            dst = self.vertices[joint[1]]

            if src in self.static and dst in self.static:
                continue

            current_dist = distance(src.position, dst.position)

            offset_distance = (current_dist - length) * 0.5

            dst_to_src = (dst.position - src.position) / current_dist

            if not src in self.static:
                src.position += (dst_to_src * offset_distance) * 0.9
            if not dst in self.static:
                dst.position -= (dst_to_src * offset_distance) * 0.9


def Cloth(
    width,
    height,
    position,
    horiz,
    vertiz,
    t,
    vertical=True,
    horizontal=True,
    Diagonal1=True,
    Diagonal2=True,
):
    x, y = position.x, position.y
    vertices = []
    for j in range(vertiz):
        for i in range(horiz):
            vertices.append(Point(Vec2(x + i * t, y + j * t)))

    joints = []

    # Horizontal connection
    if horizontal == True:
        for i in range(len(vertices) - 1):
            if i % horiz != horiz - 1:
                joints.append([i, i + 1])
    # Vertical connection
    if vertical == True:
        for i in range(len(vertices) - horiz):
            joints.append([i, i + horiz])

    # first diagonal connection
    if Diagonal1 == True:
        for i in range(len(vertices) - horiz - 1):
            if i % horiz != horiz - 1:
                joints.append([i, i + horiz + 1])
    # second diagonal connection
    if Diagonal2 == True:
        for i in range(len(vertices) - horiz):
            if i % horiz != 0:
                joints.append([i, i + horiz - 1])

    static = [vertices[0], vertices[horiz // 2], vertices[horiz - 1]]

    return ClothSystem(vertices, joints, static, width, height)
