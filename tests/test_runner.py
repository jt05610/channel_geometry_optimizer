from unittest import TestCase
import runner


class RunnerTest(TestCase):
    lattice_structure = (2, 1, 2, 3, 2, 1, 2, 3, 2, 1, 1)
    channel_spacing = 5
    channel_width = 0.5
    channel_height = 0.56

    def test_create_mesh(self):
        runner.create_mesh(
            lattice_structure=self.lattice_structure,
            channel_spacing=self.channel_spacing,
            channel_width=self.channel_width,
            channel_height=self.channel_height,
        )
