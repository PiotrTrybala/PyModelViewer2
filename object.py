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
        
        self.shader_reader = Shader(vertex_file, fragment_file)

        self.shader = compileProgram(compileShader(self.shader_reader.vertex, GL_VERTEX_SHADER), compileShader(self.shader_reader.fragment, GL_FRAGMENT_SHADER))

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
    
    def applyTransform(self, translation=None, model=None, view=None, projection=None, scale=None):

        model_loc = glGetUniformLocation(self.shader, "model")
        translation_loc = glGetUniformLocation(self.shader, "translation")
        view_loc = glGetUniformLocation(self.shader, "view")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        scale_loc = glGetUniformLocation(self.shader, "scale")

        glUseProgram(self.shader)

        if model is not None:
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

        if translation is not None:
            glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        if view is not None:
            glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        
        if projection is not None:
            glUniformMatrix4fv(translation_loc, 1, GL_FALSE, translation)
        
        if scale is not None:
            glUniformMatrix4fv(scale_loc, 1, GL_FALSE, scale)
        glUseProgram(0)

    def render(self):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glUseProgram(self.shader)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glUseProgram(0)
