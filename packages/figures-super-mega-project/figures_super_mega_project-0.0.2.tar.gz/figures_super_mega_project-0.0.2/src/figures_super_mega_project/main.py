"""
Модуль, в котором задаются сущности библиотеки.
Для создания объектов геометрических фигур объявлен класс FigureFactory, который удовлетворяет DI(Dependency Injection).
Для соблюдения принципа OCP(Open/Closed Principle) SOLID в фабрике реализован декоратор FigureFactory.register,
который используется при объявлении классов геометрических фигур.
"""


import math
from abc import ABC, abstractmethod
from typing import Union


class Figure(ABC):
    """Общий абстрактный класс для геометрических фигур."""
    @abstractmethod
    def __init__(self) -> None:
        pass

    # Метод, используемый для расчёта площади геометрической фигуры.
    # Не требует знания типа фигуры(не принимает на вход никаких аргументов).
    @abstractmethod
    def calculate_area(self) -> float:
        pass


class FigureFactory:
    """
    Фабрика для создания объектов геометрических фигур. Использует реестр, 
    хранящий классы по их строковому имени.
    """
    registry = {}  # Реестр для хранения зарегистрированных типов геометрических фигур.

    # Декоратор, который используется при объявлении классов геометрических фигур. Принимает на вход строковое имя фигуры.
    @classmethod
    def register(cls, figure_name: str):
        def wrapper(figure_class):
            if type(figure_name) is not str:
                raise ValueError('Имя фигуры должно быть строкой!')
            
            cls.registry[figure_name] = figure_class
            return figure_class
        return wrapper

    # Метод для создания объектов геометрических фигур. Использует реестр.
    @classmethod
    def create(cls, figure_name: str, params: dict) -> Figure:        
        if type(params) is not dict:
            raise ValueError('Параметры для создания объекта должны быть словарём!')

        if figure_name not in cls.registry:
            raise ValueError(f"Неизвестный тип фигуры: {figure_name}")
        return cls.registry[figure_name](**params)


# Реализаця базовых геометрических фигур.
@FigureFactory.register("circle")
class Circle(Figure):
    """Это круг. Всё, чем он обладает - это радиус."""

    def __init__(self, radius: Union[float, int]) -> None:
        if type(radius) is not float and type(radius) is not int:
            raise ValueError('Радиус должен быть числом!')
        if radius < 0:
            raise ValueError('Радиус не может быть отрицательным!')
        self.radius = radius

    def calculate_area(self) -> float:
        return round(math.pi * self.radius**2, 3)  # Используем округление


@FigureFactory.register("triangle")
class Triangle(Figure):
    """Это треугольник. У него есть три стороны: a, b, c."""

    def __init__(self, a: Union[float, int], b: Union[float, int], c: Union[float, int]) -> None:
        for side in [a, b, c]:
            if type(side) is not float and type(side) is not int:
                raise ValueError('Все стороны должны быть числами!')
            if side < 0:
                raise ValueError('Сторона не может быть отрицательной!')
        self.a = a
        self.b = b
        self.c = c

        if ((self.a + self.b) <= self.c) or \
           ((self.a + self.c) <= self.b) or \
           ((self.b + self.c) <= self.a):
            raise ValueError(
                'Сумма длин двух сторон любого треугольника должна быть больше длины третьей стороны')

    def calculate_area(self) -> float:
        # Если треугольник прямоугольный, то расчёт происходит по-простому
        if (self.a**2 + self.b**2 == self.c**2):
            print('Найден прямоугольный треугольник!')
            return self.a * self.b / 2

        elif (self.a**2 + self.c**2 == self.b**2):
            print('Найден прямоугольный треугольник!')
            return self.a * self.c / 2

        elif (self.b**2 + self.c**2 == self.a**2):
            print('Найден прямоугольный треугольник!')
            return self.b * self.c / 2

        # Формула Герона
        half_perimeter = (self.a + self.b + self.c) / 2
        area = math.sqrt(half_perimeter * (half_perimeter - self.a)
                         * (half_perimeter - self.b) * (half_perimeter - self.c))
        return round(area, 3)  # Используем округление
