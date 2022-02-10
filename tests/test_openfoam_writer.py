import unittest
import openfoam_writer


class MyTestCase(unittest.TestCase):
    experiment_variables = (
        openfoam_writer.ExperimentVariable(
            type="$walls",
            name="walls",
            fields=openfoam_writer.VariableFields(
                U=None,
                p_rgh=None,
                alpha=None,
                field_box=None,
                nu=None,
                rho=None,
            ),
        ),
        openfoam_writer.ExperimentVariable(
            type="$inlet",
            name="aqueous_inlet_1",
            fields=openfoam_writer.VariableFields(
                U=openfoam_writer.ChannelVelocity(
                    flow_rate=15, height=0.56, width=0.5, channel_angle=45
                ),
                p_rgh=None,
                alpha=1,
                field_box=None,
                nu=8.926e-07,
                rho=1000,
            ),
        ),
        openfoam_writer.ExperimentVariable(
            type="$inlet",
            name="aqueous_inlet_2",
            fields=openfoam_writer.VariableFields(
                U=openfoam_writer.ChannelVelocity(
                    flow_rate=15, height=0.56, width=0.5, channel_angle=135
                ),
                p_rgh=None,
                alpha=1,
                field_box=None,
                nu=8.926e-07,
                rho=1000,
            ),
        ),
        openfoam_writer.ExperimentVariable(
            type="$inlet",
            name="organic_inlet",
            fields=openfoam_writer.VariableFields(
                U=openfoam_writer.ChannelVelocity(
                    flow_rate=3, height=0.56, width=0.5, channel_angle=90
                ),
                p_rgh=None,
                alpha=0,
                field_box=openfoam_writer.BoundingBox(
                    x1=-0.0003,
                    y1=-0.0005,
                    z1=0,
                    x2=0.0003,
                    y2=0.0025,
                    z2=0.0006,
                ),
                nu=1.796e-06,
                rho=1095,
            ),
        ),
        openfoam_writer.ExperimentVariable(
            type="$outlet",
            name="outlet",
            fields=openfoam_writer.VariableFields(
                U=None,
                p_rgh=None,
                alpha=None,
                field_box=None,
                nu=None,
                rho=None,
            ),
        ),
    )

    def test_calculate_velocity(self):
        result = openfoam_writer.calculate_velocity(
            flow_rate=30, height=0.56, width=0.5, channel_angle=45
        )
        self.assertEqual(
            openfoam_writer.Velocity(x=1.2627, y=1.2627, z=0), result
        )
        result = openfoam_writer.calculate_velocity(
            flow_rate=3, height=0.56, width=0.5, channel_angle=135
        )
        self.assertEqual(
            openfoam_writer.Velocity(x=-0.1263, y=0.1263, z=0), result
        )

    def test_get_object_template(self):
        template = openfoam_writer.get_template(
            openfoam_writer.OpenFoamObject.U
        )
        self.assertEqual(25, len(template))

    def test_foam_string(self):
        vel = openfoam_writer.Velocity(1, 2, 3)
        expected = "uniform (1 2 3)"
        self.assertEqual(expected, openfoam_writer.foam_string(vel))

    def test_parse_component(self):
        template_components = tuple(
            openfoam_writer.parse_template_components("U")
        )
        self.assertEqual(3, len(template_components))
        self.assertTrue(
            all(map(lambda x: x.lines[-1] == "}\n", template_components))
        )

    def test_parse_component_variables(self):
        template_components = tuple(
            openfoam_writer.parse_template_components("U")
        )
        component_variables = tuple(
            openfoam_writer.parse_component_variables(c)
            for c in template_components
        )
        res = tuple(component_variables[1])
        self.assertEqual(3, len(component_variables))
        self.assertEqual(1, len(res))
        self.assertEqual("inlet_value", res[0])

    def test_insert_experiment_variable_flow_rate(self):
        variable = openfoam_writer.ExperimentVariable(
            type="$inlet",
            name="aqueous_inlet_1",
            fields=openfoam_writer.VariableFields(
                U=openfoam_writer.ChannelVelocity(
                    flow_rate=30, height=0.56, width=0.5, channel_angle=45
                ),
                p_rgh=None,
                alpha=1,
                field_box=None,
                nu=None,
                rho=None,
            ),
        )
        component = openfoam_writer.insert_experiment_variable("U", variable)
        self.assertEqual("aqueous_inlet_1\n", component.lines[0])
        self.assertEqual(
            "    value           uniform (1.2627 1.2627 0);\n",
            component.lines[3],
        )

    def test_insert_experiment_variable_walls(self):
        variable = openfoam_writer.ExperimentVariable(
            type="$walls",
            name="walls",
            fields=openfoam_writer.VariableFields(
                U=None,
                p_rgh=None,
                alpha=None,
                field_box=None,
                nu=None,
                rho=None,
            ),
        )
        component = openfoam_writer.insert_experiment_variable("U", variable)
        self.assertEqual("walls\n", component.lines[0])

    def test_insert_experiment_variables_transport(self):
        variable = self.experiment_variables[1]
        component = openfoam_writer.insert_experiment_variable(
            "transportProperties", variable
        )
        self.assertEqual("aqueous\n", component.lines[0])

    def test_components_start(self):
        template = openfoam_writer.get_template("U")
        component_start = openfoam_writer.get_component_start(template)
        self.assertEqual(22, component_start)

    def test_replace_variables(self):
        res = openfoam_writer.replace_variables("U", self.experiment_variables)
        self.assertEqual(47, len(res))

    def test_create_case(self):
        case = openfoam_writer.Case(
            "test_case", "interFoam", self.experiment_variables
        )
        openfoam_writer.create_case(case, True)


if __name__ == "__main__":
    unittest.main()
