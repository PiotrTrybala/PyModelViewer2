import os
from sys import exit

class Shader:
    def __init__(self, vertex_file, fragment_file):
        self.vertex = self.readShader(vertex_file)
        self.fragment = self.readShader(fragment_file)

    def readShader(self, filename):
        filepath = f"{os.getcwd()}/shaders/{filename}"
        try:
            f = open(filepath, 'r')
            out = ''.join(f.readlines())
            f.close()
            return out
        except Exception as e:
            print(f"this file does not exist: {filename}")
            exit(1)
