import unittest
import config


class MyTestCase(unittest.TestCase):
    def test_path_name(self):
        print(config.PATH_NAME)


if __name__ == "__main__":
    unittest.main()
