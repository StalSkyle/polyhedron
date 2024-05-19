import unittest
from unittest.mock import patch, mock_open

from shadow.polyedr import Polyedr


class TestPolyedr1(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """200.0    45.0    45.0    30.0
8       4       16
-0.5    -0.5    0.5
-0.5    0.5     0.5
0.5     0.5     0.5
0.5     -0.5    0.5
-0.5    -0.5    -0.5
-0.5    0.5     -0.5
0.5     0.5     -0.5
0.5     -0.5    -0.5
4       5    6    2    1
4       3    2    6    7
4       3    7    8    4
4       1    4    8    5"""
        fake_file_path = 'data/holey_box.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.assertEqual(len(self.polyedr.vertexes), 8)

    def test_num_facets(self):
        self.assertEqual(len(self.polyedr.facets), 4)

    def test_num_edges(self):
        self.assertAlmostEqual(len(self.polyedr.edges), 16)


# проверка на правильный поиск требуемой характеристики
class TestPolyedr2(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """40       5 0 0
8       2       8
0.0 0.0 0.0
5.0 0.0 0.0
5.0 5.0 0.0
0.0 5.0 0.0
1.0 1.0 3.0
6.0 1.0 3.0
6.0 6.0 3.0
1.0 6.0 3.0
4       1    2    3    4
4       5    6    7    8"""
        fake_file_path = 'data/ссс.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.polyedr.count()
        self.assertAlmostEqual(self.polyedr.output, 4.0)


# коэффициент гомотетии не влияет на ответ
class TestPolyedr3(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """120      5 0 0
8       2       8
0.0 0.0 0.0
5.0 0.0 0.0
5.0 5.0 0.0
0.0 5.0 0.0
1.0 1.0 3.0
6.0 1.0 3.0
6.0 6.0 3.0
1.0 6.0 3.0
4       1    2    3    4
4       5    6    7    8"""
        fake_file_path = 'data/ссс_modified.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.polyedr.count()
        self.assertAlmostEqual(self.polyedr.output, 4.0)


# у куба нет невидимых рёбер
class TestPolyedr4(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """80       40 -20 30
8       6       24
-0.5    -0.5    0.5
-0.5    0.5     0.5
0.5     0.5     0.5
0.5     -0.5    0.5
-0.5    -0.5    -0.5
-0.5    0.5     -0.5
0.5     0.5     -0.5
0.5     -0.5    -0.5
4       1    2    3    4
4       5    6    2    1
4       3    2    6    7
4       3    7    8    4
4       1    4    8    5
4       8    7    6    5"""
        fake_file_path = 'data/сube.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.polyedr.count()
        self.assertAlmostEqual(self.polyedr.output, 0.0)


# проверка собственного полиэдра
class TestPolyedr5(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        fake_file_content = """40       0 0 0
12 3 24
1.0 2.9 -0.5
5.0 2.9 -0.5
5.0 1.1 -0.5
1.0 1.1 -0.5
0 2.1 0.1
2 2.1 0.1
2 0.1 0.1
0 0.1 0.1
4 0.1 0.2
6 0.1 0.2
6 2.1 0.2
4 2.1 0.2
4       1    2    3    4
4       5    6    7    8
4 9 10 11 12"""
        fake_file_path = 'data/еркуу_здфтуы.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            self.polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

    def test_num_vertexes(self):
        self.polyedr.count()
        self.assertAlmostEqual(self.polyedr.output, 4.0)
