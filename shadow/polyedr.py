from math import pi, sqrt
from functools import reduce
from operator import add
from common.r3 import R3


class Segment:
    """ Одномерный отрезок """

    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [
            Segment(self.beg,
                    self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)
        ]


class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    # Учёт тени от одной грани
    def shadow(self, facet):
        # «Вертикальная» грань не затеняет ничего
        if facet.is_vertical():
            return
        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(facet.vertexes[0],
                                            facet.h_normal()))
        if shade.is_degenerate():
            return
        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [s for s in reduce(add, gaps, []) if
                     not s.is_degenerate()]

    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = -f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)


class Facet:
    """ Грань полиэдра """

    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vertexes = vertexes

    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        n = (self.vertexes[1] - self.vertexes[0]).cross(self.vertexes[2] -
                                                        self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1]
                            - self.center()) < 0.0 else n

    # Центр грани
    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * \
            (1.0 / len(self.vertexes))


class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):

        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []

        # искомая характеристика
        self.output = 0.0

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    self.c = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    self.alpha, self.beta, self.gamma = (float(x) * pi / 180.0
                                                         for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(
                        R3(x, y, z).rz(self.alpha).ry(self.beta).rz(
                            self.gamma)
                        * self.c)
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                    # задание самой грани
                    self.facets.append(Facet(vertexes))

    # Подсчёт требуемой характеристики
    def count(self):
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            flag = 0
            for s in e.gaps:
                s.beg = round(s.beg, 12)
                s.fin = round(s.fin, 12)
                if (s.beg != 0 or s.fin != 1) and s.beg != s.fin:
                    begin = R3(e.r3(0).x, e.r3(0).y, e.r3(0).z)
                    begin_draw = R3(
                        e.r3(s.beg).x,
                        e.r3(s.beg).y,
                        e.r3(s.beg).z)
                    end = R3(e.r3(1).x, e.r3(1).y, e.r3(1).z)
                    end_draw = R3(e.r3(s.fin).x, e.r3(s.fin).y, e.r3(s.fin).z)
                    begin = begin.rz(-self.alpha).ry(-self.beta).rz(
                        -self.gamma) * (1 / self.c)
                    begin_draw = begin_draw.rz(-self.alpha).ry(-self.beta).rz(
                        -self.gamma) * (1 / self.c)
                    end = end.rz(-self.alpha).ry(-self.beta).rz(
                        -self.gamma) * (1 / self.c)
                    end_draw = end_draw.rz(-self.alpha).ry(-self.beta).rz(
                        -self.gamma) * (1 / self.c)
                    mid = (begin.y + end.y) / 2
                    if 1 < mid < 3:
                        if flag == 0:
                            flag = 1
                            self.output += sqrt((end.x - begin.x) ** 2 +
                                                (end.y - begin.y) ** 2)
                        self.output -= sqrt((end_draw.x - begin_draw.x) ** 2 +
                                            (end_draw.y - begin_draw.y) ** 2)

    # Метод изображения полиэдра
    def draw(self, tk):  # pragma: no cover
        tk.clean()
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
