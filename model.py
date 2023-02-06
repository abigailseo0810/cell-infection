"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from random import random
from exercises.ex09 import constants
from math import sin, cos, pi
from math import sqrt


__author__ = "730577007"


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)

    def distance(self, other: Point) -> float:
        """Returns distance between the Point object and some other Point."""
        dist: float = sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)
        return dist


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Infected cells become immune after recovery period ticks."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
        if self.sickness > constants.RECOVERY_PERIOD:
            self.immunize()
        
    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_vulnerable():
            return "gray"
        if self.is_infected():
            return "red"
        if self.is_immune():
            return "green"
        return "none"
    
    def contract_disease(self) -> None:
        """Assigns the INFECTED constant to the sickness attribute of the Cell object."""
        self.sickness = constants.INFECTED

    def is_vulnerable(self) -> bool:
        """Return True if cell's sickness attribute == VULNERABLE, return False if otherwise."""
        if self.sickness == constants.VULNERABLE:
            return True
        else:
            return False

    def is_infected(self) -> bool:
        """Return True if cell's sickness attribute == INFECTED, return False if otherwise."""
        if self.sickness >= constants.INFECTED:
            return True
        else:
            return False

    def contact_with(self, other: Cell) -> None:
        """If either Cell objects is infected and other is vulnerable, then other becomes infected."""
        if self.is_infected() and other.is_vulnerable():
            other.contract_disease()
        elif other.is_infected() and self.is_vulnerable():
            self.contract_disease()
    
    def immunize(self) -> None:
        """Assigns the Immune constant to the sickness attribute."""
        self.sickness = constants.IMMUNE

    def is_immune(self) -> bool:
        """Return True when cell object's sickness attribute == IMMUNE constant."""
        if self.sickness == constants.IMMUNE:
            return True


class Model:
    """The state of the simulation."""

    population: list[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, infected: int, immune: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        if infected >= cells or infected <= 0:
            raise ValueError("Some number of the Cell objects must begin infected.")
        if immune >= cells or immune < 0:
            raise ValueError("There is an improper number of immune or infected cells in the call.")
        if immune + infected >= cells:
            raise ValueError("Incorrect number of starting cells.")
        for i in range(0, cells):
            start_location: Point = self.random_location()
            start_direction: Point = self.random_direction(speed)
            cell: Cell = Cell(start_location, start_direction)
            if i < infected:
                cell.contract_disease()
            elif i < immune + infected:
                cell.immunize()
            self.population.append(cell)
            
    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x: float = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y: float = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle: float = 2.0 * pi * random()
        direction_x: float = cos(random_angle) * speed
        direction_y: float = sin(random_angle) * speed
        return Point(direction_x, direction_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1.0
        if cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1.0
        if cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1.0
        if cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1.0

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        i: int = 0
        while i < len(self.population):
            if self.population[i].is_infected():
                return False
            i += 1
        return True

    def check_contacts(self) -> None:
        """Method to compare the distance between every two Cell objects' location attributes in population."""
        i: int = 0
        while i < len(self.population):
            i2: int = i + 1
            while i2 < len(self.population):
                if self.population[i2].location.distance(self.population[i].location) < constants.CELL_RADIUS:
                    self.population[i].contact_with(self.population[i2])
                i2 += 1
            i += 1
