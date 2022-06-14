from ctypes import c_void_p
import pyrr
import math
import numpy as np
import random

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from shader import Shader

class Object:
    def __init__(self, vertices, indices, vertex_file, fragment_file):


        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)
        self.colors = []
        for _ in range(len(self.vertices) // 3):
            self.colors.append(random.random())
            self.colors.append(random.random())
            self.colors.append(random.random())
        self.colors = np.array(self.colors, dtype=np.float32)
        
        shader_reader = Shader(vertex_file, fragment_file)

        self.shader = compileProgram(compileShader(shader_reader.vertex, GL_VERTEX_SHADER), compileShader(shader_reader.fragment, GL_FRAGMENT_SHADER))

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        self.cbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.cbo)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glBindVertexArray(0)
        
    def render(self):
        glBindVertexArray(self.vao)
        glUseProgram(self.shader)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glUseProgram(0)
