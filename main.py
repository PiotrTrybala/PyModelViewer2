import glfw
import numpy as np
from sys import exit
from math import sin, cos, radians
import random

import sys

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import pyrr

from shader import Shader
from reader import ObjectReader
from object import Object

filename = None
WIDTH = 1280
HEIGHT = 720

camera_pos = pyrr.Vector3([0.0, 0.0, 0.0])
camera_front = pyrr.Vector3([0.0, 0.0, -1.0])
camera_move_front = pyrr.Vector3([0.0, 0.0, -1.0])
camera_up = pyrr.Vector3([0.0, 1.0, 0.0])

delta_time = 0.0
last_frame = 0.0

fov = 60.0
yaw = -90.0
pitch = 0.0
last_x, last_y = 400, 400
first_mouse = True

path_to_font = None
font = None

position = [0.0, 0.0, 0.0]
rotation = [0.0, 0.0, 0.0]
scale = 1.0

# python3 main.py filename p1 p2 p3 r1 r2 r3 s1

# pobieranie nazwy pliku do wczytania z wiersza poleceń
try:
    filename = sys.argv[1]
except:
    pass

# pobieranie pozycji z wiersza poleceń

try:
    position[0] = float(sys.argv[2])
    position[1] = float(sys.argv[3])
    position[2] = float(sys.argv[4])
except:
    position = [0.0, 0.0, 0.0]

# pobieranie rotacji z wiersza poleceń

try:
    rotation[0] = radians(float(sys.argv[5]))
    rotation[1] = radians(float(sys.argv[6]))
    rotation[2] = radians(float(sys.argv[7]))

except:
    rotation = [0.0, 0.0, 0.0]

try:
    scale = int(sys.argv[8])
except:
    scale = 1.0


print("data input:")
print(f"position: {position}")
print(f"rotation: {rotation}")


if not filename:
    print('nie można znaleźć wartości dla zmiennej \'filename\'')
    sys.exit(1)

print(f"Plik obiektu (.obj): {filename}")


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


def process_input(window):
    global delta_time, camera_pos, camera_front, camera_move_front, camera_up

    camera_speed = 20.0 * delta_time

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += camera_speed * camera_move_front
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= camera_speed * camera_move_front
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= pyrr.vector3.cross(camera_move_front,
                                         camera_up) * camera_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += pyrr.vector3.cross(camera_move_front,
                                         camera_up) * camera_speed
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        camera_pos += camera_up * camera_speed
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        camera_pos -= camera_up * camera_speed
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        exit(1)


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

    camera_move_front = pyrr.vector3.normalise(
        pyrr.Vector3([direction.x, 0, direction.z]))

    camera_front = pyrr.vector3.normalise(direction)


def scroll(window, xoffset, yoffset):
    global fov

    fov -= yoffset

    if fov < 20.0:
        fov = 20.0
    if fov > 90.0:
        fov = 90.0


object_reader = ObjectReader(filename)
object_reader.parse()

vertices = np.array(object_reader.vertices, dtype=np.float32)
indices = np.array(object_reader.indices, dtype=np.uint32)

objr = ObjectReader("humanoid.obj");
objr.parse()


plane_vertices = [
     5.0,  0.6,  5.0,
     5.0,  0.6, -5.0,
    -5.0,  0.6,  5.0,
    -5.0,  0.6, -5.0,
]

plane_indices = [
    0, 1, 2, 
    1, 2, 3,
]

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

boat = Object(vertices, indices, "rectangle.vert", "rectangle.frag")
plane = Object(plane_vertices, plane_vertices, "plane.vert", "plane.frag")

model = pyrr.matrix44.create_from_translation(pyrr.Vector3(position))

rotation_x = pyrr.Matrix44.from_x_rotation(rotation[0])
rotation_y = pyrr.Matrix44.from_x_rotation(rotation[1])
rotation_z = pyrr.Matrix44.from_x_rotation(rotation[2])

rotation_xy = pyrr.matrix44.multiply(rotation_x, rotation_y)
rotation_xyz = pyrr.matrix44.multiply(rotation_xy, rotation_z)

scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([scale, scale, scale]))
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3(position))
model = pyrr.matrix44.multiply(rotation_xyz, model)
view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -15.0]))
projection = pyrr.matrix44.create_perspective_projection(
    60.0, WIDTH / HEIGHT, 0.1, 100)

glClearColor(0.1, 0.2, 0.3, 1.0)
glEnable(GL_DEPTH_TEST)

while not glfw.window_should_close(window):

    glfw.poll_events()

    current_frame = glfw.get_time()
    delta_time = current_frame - last_frame
    last_frame = current_frame

    process_input(window)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    view = pyrr.matrix44.create_look_at(
        camera_pos, camera_pos + camera_front, camera_up)

    projection = pyrr.matrix44.create_perspective_projection(
        fov, WIDTH / HEIGHT, 0.1, 100)

    boat.applyTransform(translation=translation, model=model, view=view, projection=projection, scale=scale)
    plane.applyTransform(translation=translation, model=model, view=view, projection=projection, scale=scale)

    boat.render()
    plane.render()

    glfw.swap_buffers(window)

glfw.terminate()
