from abc import ABC, abstractmethod
from geometry import Point, Line, NamedLine, Lattice


class DesignInterface(ABC):
    @abstractmethod
    def add_point(self, point: Point):
        raise NotImplementedError

    def add_line(
        self,
        line: Line,
    ):
        raise NotImplementedError

    @abstractmethod
    def create_geometry(self, lattice: Lattice, extrusion_height: float):
        raise NotImplementedError

    @staticmethod
    def named_faces(lattice: Lattice):
        def inlet_gen():
            for i, channel in enumerate(lattice.channel_layers[0]):
                if i % 2 == 0:
                    name = f"aqueous_inlet_{(i / 2) + 1:n}"
                else:
                    name = f"organic_inlet"
                yield NamedLine(
                    line=lattice.channel_layers[0].channels[i].bottom_wall,
                    name=name,
                )

        outlet = NamedLine(
            line=lattice.channel_layers[-1].channels[0].top_wall, name="outlet"
        )
        return tuple(inlet_gen()) + (outlet,)

    def exclude_points(self, lattice: Lattice):
        for f in self.named_faces(lattice):
            yield from f.line
