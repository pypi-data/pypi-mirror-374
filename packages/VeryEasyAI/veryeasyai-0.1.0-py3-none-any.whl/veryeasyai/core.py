import random

class ArrayInterno:
    """Array interno que escolhe a melhor forma de armazenar os dados"""
    def __init__(self, dados):
        # Se os dados forem muito grandes, usa numpy
        try:
            import numpy as np
            if len(dados) > 50:
                self.data = np.array(dados)
                self.tipo = "numpy"
            else:
                self.data = list(dados)
                self.tipo = "list"
        except ImportError:
            # fallback se numpy não existir
            self.data = list(dados)
            self.tipo = "list"

    def get(self):
        return self.data


class CriarModelo:
    def __init__(self, tipo="regressao"):
        self.tipo = tipo
        self.peso = random.random()
        self.sesgo = random.random()

    def treinar(self, dados, taxa=0.01, epocas=1000):
        entradas = ArrayInterno(dados["entradas"]).get()
        saidas   = ArrayInterno(dados["saidas"]).get()

        for _ in range(epocas):
            for x, y in zip(entradas, saidas):
                y_pred = self.peso * x + self.sesgo
                erro = y - y_pred
                self.peso += taxa * erro * x
                self.sesgo += taxa * erro

    def prever(self, x):
        return self.peso * x + self.sesgo
