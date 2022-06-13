import os
import numpy as np

MODELS_DIR = os.getcwd() + "/models"

class ObjectReader:
    def __init__(self, filename):

        print(MODELS_DIR + "/" + filename)

        self.f = open(MODELS_DIR + "/" + filename, 'r')

        self.vertices   = []
        self.textures   = []
        self.normals    = []

        self.indices            = []
        self.textures_indices   = []
        self.normals_indices    = []

        self.lines = self.f.readlines()

        print(self.lines)

        self.f.close()

    def parse(self):

        for line in self.lines:

            tokens = line.split()
            if tokens == []:
                continue

            if tokens[0] == 'v':
                print(tokens[1:])
                for token in tokens[1:]:
                    self.vertices.append(float(token))

            elif tokens[0] == 'vt':

                for token in tokens[1:]:
                    self.textures.append(float(token))

            elif tokens[0] == 'vn':

                for token in tokens[1:]:
                    self.normals.append(float(token))

            elif tokens[0] == 'f':
                toks = tokens[1:]

                if toks[0].count('/') > 0:
                    if toks[0].count('/') == 2:
                        for i in range(3):
                            l = toks[i].split('/')
                            self.indices.append(int(l[0]) - 1)
                            self.textures_indices.append(int(l[1]) - 1)
                            self.normals_indices.append(int(l[2]) - 1)

                    continue

                if len(toks) == 4:
                    t1 = [int(toks[0]) - 1, int(toks[2]) - 1, int(toks[1]) - 1]
                    t2 = [int(toks[0]) - 1, int(toks[2]) - 1, int(toks[3]) - 1]

                    for t in t1:
                        self.indices.append(t)
                    for t in t2:
                        self.indices.append(t)

                elif len(toks) == 3:
                    self.indices.append(int(toks[0]) - 1)
                    self.indices.append(int(toks[1]) - 1)
                    self.indices.append(int(toks[2]) - 1)

                else:
                    print('invalid indice')



            elif tokens[0] == 's':
                print('smooth shading')
                pass
            elif tokens[0] == 'usemtl':
                print('material')
                pass
            elif tokens[0] == 'g':
                print('group')
                pass
            elif tokens[0] == 'o':
                print('object')
                pass
            elif tokens[0] == 'mtllib':
                print('material lib')
                pass
            elif tokens[0] == '#':
                print('comment')

        print(self.vertices)

    def combine_data(self, *args):

        data = []

        i, rl, C, R, A = 0, 0, [], [], []

        while i <= len(args) // 2:
            C.append(len(args[i + 1]) // args[i])
            A.append(args[i + 1])
            R.append(args[i])
            rl += args[i]
            i += 2

        for i in range(max(C)):
            k, cr, t = 0, R[0], 0
            for j in range(rl):
                if j > cr - 1:
                    k += 1
                    cr += R[k]
                    t = 0

                ci = (i * R[k] + t) % 16;

                data.append(A[k][ci])

                print(f"k: {k}, cr: {cr}, t: {t}, R[k]: {R[k]}, A[k]: {A[k]}, ci: {(i * R[k] + t) % 16}, Al: {len(A[k])}")
                t += 1

        return np.array(data, dtype=np.float32)
