import numpy as np
from typing import List, Tuple, Any

class Rectangle:
    """Quadtree'nin sınırlarını temsil eden dikdörtgen sınıfı."""
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point: Tuple[float, float]) -> bool:
        """Bir noktanın bu dikdörtgenin içinde olup olmadığını kontrol eder."""
        px, py = point
        return (self.x - self.width / 2 <= px < self.x + self.width / 2 and
                self.y - self.height / 2 <= py < self.y + self.height / 2)

    def intersects(self, other: 'Rectangle') -> bool:
        """Bu dikdörtgenin başka bir dikdörtgenle kesişip kesişmediğini kontrol eder."""
        return not (other.x - other.width / 2 > self.x + self.width / 2 or
                    other.x + other.width / 2 < self.x - self.width / 2 or
                    other.y - other.height / 2 > self.y + self.height / 2 or
                    other.y + other.height / 2 < self.y - self.height / 2)


class Quadtree:
    """
    2D uzaydaki nesneleri verimli bir şekilde sorgulamak için kullanılan Quadtree veri yapısı.
    """
    def __init__(self, boundary: Rectangle, capacity: int):
        self.boundary = boundary
        self.capacity = capacity
        self.points = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        """Quadtree'yi dört alt bölgeye ayırır."""
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2

        nw = Rectangle(x - w / 2, y - h / 2, w, h)
        ne = Rectangle(x + w / 2, y - h / 2, w, h)
        sw = Rectangle(x - w / 2, y + h / 2, w, h)
        se = Rectangle(x + w / 2, y + h / 2, w, h)

        self.northwest = Quadtree(nw, self.capacity)
        self.northeast = Quadtree(ne, self.capacity)
        self.southwest = Quadtree(sw, self.capacity)
        self.southeast = Quadtree(se, self.capacity)
        self.divided = True

    def insert(self, point: Tuple[float, float, Any]) -> bool:
        """Quadtree'ye bir nokta (ve ilişkili veri) ekler."""
        if not self.boundary.contains((point[0], point[1])):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        
        if not self.divided:
            self.subdivide()

        # Alt bölgeler artık None olamaz, linter için assert ekleyebiliriz veya doğrudan kullanabiliriz.
        # Kodu daha güvenli hale getirelim.
        if self.northwest and self.northwest.insert(point): return True
        if self.northeast and self.northeast.insert(point): return True
        if self.southwest and self.southwest.insert(point): return True
        if self.southeast and self.southeast.insert(point): return True
        
        return False

    def query(self, range_rect: Rectangle) -> List[Any]:
        """Belirli bir aralıktaki tüm noktaları/verileri bulur."""
        found_points = []
        if not self.boundary.intersects(range_rect):
            return found_points

        for p in self.points:
            if range_rect.contains((p[0], p[1])):
                found_points.append(p[2])

        if self.divided:
            if self.northwest: found_points.extend(self.northwest.query(range_rect))
            if self.northeast: found_points.extend(self.northeast.query(range_rect))
            if self.southwest: found_points.extend(self.southwest.query(range_rect))
            if self.southeast: found_points.extend(self.southeast.query(range_rect))

        return found_points 