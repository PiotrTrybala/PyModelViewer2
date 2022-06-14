import glfw
import numpy as np
from sys import exit
from math import sin, cos, radians
import random

import sys

filename = None


try:
    filename = sys.argv[1]
except:
    pass

if not filename:
    print('nie można znaleźć wartości dla zmiennej \'filename\'')
    sys.exit(1)

print(f"Plik obiektu (.obj): {filename}")


from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import pyrr

WIDTH = 1280
HEIGHT = 720

from shader import Shader
from reader import ObjectReader

camera_pos = pyrr.Vector3([0.0, 0.0, 0.0])
camera_front = pyrr.Vector3([0.0, 0.0, -1.0])
camera_move_front = pyrr.Vector3([0.0, 0.0, -1.0])
camera_up = pyrr.Vector3([0.0, 1.0, 0.0])

def window_resize(window, width, height):
    glViewport(0, 0, width, height);

delta_time = 0.0
last_frame = 0.0

def process_input(window):
    global delta_time, camera_pos, camera_front, camera_move_front, camera_up

    camera_speed = 20.0 * delta_time

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += camera_speed * camera_move_front
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= camera_speed * camera_move_front
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= pyrr.vector3.cross(camera_move_front, camera_up) * camera_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += pyrr.vector3.cross(camera_move_front, camera_up) * camera_speed
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        camera_pos += camera_up * camera_speed
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        camera_pos -= camera_up * camera_speed
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        exit(1)

yaw = -90.0
pitch = 0.0
last_x, last_y = 400, 400
first_mouse = True

def mouse_callback(window, xpos, ypos):
    global yaw, pitch, last_x, last_y, camera_front, camera_move_front, first_mouse

    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False


    direction = pyrr.Vector3([0.0, 0.0, 0.0])

    xoffset = xpos - last_x
    yoffset = last_y - ypos

    last_x = xpos
    last_y = ypos

    sensitivity = 0.1

    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset

    if pitch > 89.0:
        pitch = 89.0
    if pitch < -89.0:
        pitch = -89.0

    direction.x = cos(radians(yaw)) * cos(radians(pitch))
    direction.y = sin(radians(pitch))
    direction.z = sin(radians(yaw)) * cos(radians(pitch))

    camera_move_front = pyrr.vector3.normalise(pyrr.Vector3([direction.x, 0, direction.z]))

    camera_front = pyrr.vector3.normalise(direction)

fov = 60.0


def scroll(window, xoffset, yoffset):
    global fov

    fov -= yoffset

    if fov < 20.0:
        fov = 20.0
    if fov > 90.0:
        fov = 90.0

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
glfw.set_cursor_pos_callback(window, mouse_callback)
glfw.set_scroll_callback(window, scroll)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

glfw.make_context_current(window)

object_reader = ObjectReader(filename)
object_reader.parse()

colors = []

for i in range(len(object_reader.vertices) // 3):
    colors.append(random.random()) # wartość czerwonego w kolorze wyjściowym
    colors.append(random.random()) # wartość niebieskiego w kolorze wyjściowym
    colors.append(random.random()) # wartość zielonego w kolorze wyjściowym



vertices = np.array(object_reader.vertices, dtype=np.float32)
indices = np.array(object_reader.indices, dtype=np.uint32)
colors = np.array(colors, dtype=np.float32)

shader_reader = Shader("rectangle.vert", "rectangle.frag")

shader = compileProgram(compileShader(shader_reader.vertex,
            GL_VERTEX_SHADER), compileShader(shader_reader.fragment, GL_FRAGMENT_SHADER))

model_loc = glGetUniformLocation(shader, "model")
view_loc = glGetUniformLocation(shader, "view")
proj_loc = glGetUniformLocation(shader, "projection")

model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -5.0]))
view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -15.0]))
projection = pyrr.matrix44.create_perspective_projection(60.0, WIDTH / HEIGHT, 0.1, 100)


VAO = glGenVertexArrays(1)
glBindVertexArray(VAO)

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

CBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, CBO)
glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glBindBuffer(GL_ARRAY_BUFFER, CBO)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

glUseProgram(shader)
glBindVertexArray(0)

glClearColor(0.1, 0.2, 0.3, 1.0)
glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):

    glfw.poll_events()

    current_frame = glfw.get_time()
    delta_time = current_frame - last_frame
    last_frame = current_frame

    process_input(window)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # camX = sin(glfw.get_time()) * 15
    # camZ = cos(glfw.get_time()) * 15

    view = pyrr.matrix44.create_look_at(camera_pos, camera_pos + camera_front, camera_up)

    projection = pyrr.matrix44.create_perspective_projection(fov, WIDTH / HEIGHT, 0.1, 100)

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
    # rot_y = pyrr.Matrix44.from_y_rotation(0.5 * glfw.get_time())

    # model = pyrr.matrix44.multiply(rot_x, rot_y)

    # glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    glUseProgram(shader)
    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))

    glfw.swap_buffers(window)

glfw.terminate()
