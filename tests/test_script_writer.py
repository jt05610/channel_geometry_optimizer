import unittest
import script_writer


class ScriptWriterTestCase(unittest.TestCase):
    template_path = "../templates/salome_script.py.template"

    variables = dict(
        path_name='r"test_path"',
        lattice_structure=(1, 2, 3),
        channel_spacing=5,
        channel_width=0.5,
        channel_height=0.56,
        save_name='r"test_save.unv"',
    )
    temp_dir_path = "../tmp"

    def test_get_template(self):
        template = script_writer.get_template(self.template_path)
        self.assertTrue(len(template) > 0)

    def test_parse_template_vars(self):
        template = script_writer.get_template(self.template_path)
        template_vars = tuple(script_writer.parse_template_vars(template))
        self.assertEqual(6, len(template_vars))

    def test_replace_template_vars(self):
        start_template = script_writer.get_template(self.template_path)
        template = script_writer.replace_template_vars(
            self.template_path, self.variables
        )
        self.assertEqual(len(start_template), len(template))
        self.assertNotEqual(start_template, template)

    def test_write_script(self):
        script_writer.write_script(
            self.template_path, self.variables, self.temp_dir_path
        )

    def test_delete_script_if_doesnt_exist(self):
        script_writer.delete_script(self.temp_dir_path)
        script_writer.delete_script(self.temp_dir_path)


if __name__ == "__main__":
    unittest.main()
