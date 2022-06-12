import glfw
import numpy as np
from math import sin, cos

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import pyrr

WIDTH = 1280
HEIGHT = 720

from shader import Shader
from reader import ObjectReader

def window_resize(window, width, height):
    glViewport(0, 0, width, height);


if not glfw.init():
    raise Exception("glfw init cannot be initialized!")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)


window = glfw.create_window(WIDTH, HEIGHT, "3D Model Viewer", None, None)

if not window:
    glfw.terminate()
    raise Exception('glfw window cannot be created!')

glfw.set_window_size_callback(window, window_resize)

glfw.make_context_current(window)

object_reader = ObjectReader("cube.obj")
object_reader.parse()
print(object_reader.vertices)
print(object_reader.indices)

vertices = [
     0.5,  0.5, 0.0, 1.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
    -0.5,  0.5, 0.0, 0.0, 0.0, 1.0,
    -0.5, -0.5, 0.0, 1.0, 0.0, 1.0
]

indices = [
    0, 1, 2,
    1, 2, 3
]

vertices = np.array(object_reader.vertices, dtype=np.float32)
indices = np.array(object_reader.indices, dtype=np.uint32)

shader_reader = Shader("rectangle.vert", "rectangle.frag")

shader = compileProgram(compileShader(shader_reader.vertex,
            GL_VERTEX_SHADER), compileShader(shader_reader.fragment, GL_FRAGMENT_SHADER))

model_loc = glGetUniformLocation(shader, "model")
view_loc = glGetUniformLocation(shader, "view")
proj_loc = glGetUniformLocation(shader, "projection")

model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -15.0]))
view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -5.0]))
projection = pyrr.matrix44.create_perspective_projection(45.0, WIDTH / HEIGHT, 0.1, 100)

VAO = glGenVertexArrays(1)
glBindVertexArray(VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

# glEnableVertexAttribArray(1)
# glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

glUseProgram(shader)
glBindVertexArray(0)

glClearColor(0.1, 0.2, 0.3, 1.0)
glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):

    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # camX = sin(glfw.get_time()) * 5
    # camZ = cos(glfw.get_time()) * 5

    # view = pyrr.matrix44.create_look_at(pyrr.Vector3([camX, 5.0, camZ]), pyrr.Vector3([0.0, 1.0, 0.0]), pyrr.Vector3([0.0, 1.0, 0.0]))

    # glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
    rot_y = pyrr.Matrix44.from_y_rotation(0.5 * glfw.get_time())

    model = pyrr.matrix44.multiply(rot_x, rot_y)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    glUseProgram(shader)
    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))

    glfw.swap_buffers(window)

glfw.terminate()
