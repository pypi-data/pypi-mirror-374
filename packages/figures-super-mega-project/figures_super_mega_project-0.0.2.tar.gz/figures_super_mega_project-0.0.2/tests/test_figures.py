import pytest
from figures_super_mega_project import FigureFactory, Circle, Triangle, Figure


class TestCircle:
    def test_circle_area_calculation(self):
        circle = FigureFactory.create("circle", {"radius": 5})
        assert circle.calculate_area() == 78.54

    def test_circle_area_calculation_zero_radius(self):
        circle = FigureFactory.create("circle", {"radius": 0})
        assert circle.calculate_area() == 0.0

    def test_circle_invalid_radius_type(self):
        with pytest.raises(ValueError, match='Радиус должен быть числом!'):
            FigureFactory.create("circle", {"radius": "abc"})

    def test_circle_negative_radius(self):
        with pytest.raises(ValueError, match='Радиус не может быть отрицательным!'):
            FigureFactory.create("circle", {"radius": -5})


class TestTriangle:
    def test_triangle_area_calculation_right_triangle(self):
        triangle = FigureFactory.create("triangle", {"a": 3, "b": 4, "c": 5})
        assert triangle.calculate_area() == 6.0

    def test_triangle_area_calculation_equilateral_triangle(self):
        triangle = FigureFactory.create("triangle", {"a": 2, "b": 2, "c": 2})
        assert triangle.calculate_area() == 1.732

    def test_triangle_invalid_side_type(self):
        with pytest.raises(ValueError, match='Все стороны должны быть числами!'):
            FigureFactory.create("triangle", {"a": 3, "b": "x", "c": 5})

    def test_triangle_inequality(self):
        with pytest.raises(ValueError, match='Сумма длин двух сторон любого треугольника должна быть больше длины третьей стороны'):
            FigureFactory.create("triangle", {"a": 1, "b": 2, "c": 5})

    def test_triangle_negative_side(self):
        with pytest.raises(ValueError, match='Сторона не может быть отрицательной!'):
            FigureFactory.create("triangle", {"a": 3, "b": 4, "c": -5}) 


class TestFigureFactory:
    def test_register_figure(self):
        class Square(Figure):
            def __init__(self, side: float) -> None:
                self.side = side

            def calculate_area(self) -> float:
                return self.side**2

        FigureFactory.register("square")(Square)
        assert "square" in FigureFactory.registry

    def test_register_non_string_figure_name(self):
        with pytest.raises(ValueError, match='Имя фигуры должно быть строкой!'):
            @FigureFactory.register(123)
            class InvalidFigure(Figure):
                pass

    def test_create_non_dict_params(self):
        with pytest.raises(ValueError, match='Параметры для создания объекта должны быть словарём!'):
            FigureFactory.create("circle", "not_a_dict")

    def test_create_unknown_figure(self):
        with pytest.raises(ValueError, match="Неизвестный тип фигуры: unknown_figure"):
            FigureFactory.create("unknown_figure", {"param": 1})

    def test_create_circle_success(self):
        circle = FigureFactory.create("circle", {"radius": 10})
        assert isinstance(circle, Circle)
        assert circle.radius == 10

    def test_create_triangle_success(self):
        triangle = FigureFactory.create("triangle", {"a": 3, "b": 4, "c": 5})
        assert isinstance(triangle, Triangle)
        assert triangle.a == 3
        assert triangle.b == 4
        assert triangle.c == 5 