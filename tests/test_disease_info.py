import importlib.util
import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "backend", "model.py")

spec = importlib.util.spec_from_file_location("leafguard_model", MODEL_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DiseaseInfoTests(unittest.TestCase):
    def test_brown_spot_has_solution(self):
        info = module.get_disease_details("brown_spot")
        self.assertIn("brown spot", info["label"].lower())
        self.assertIn("solution", info)
        self.assertTrue(info["solution"])

    def test_healthy_has_no_disease_message(self):
        info = module.get_disease_details("healthy")
        self.assertIn("healthy", info["label"].lower())
        self.assertIn("no disease", info["description"].lower())


if __name__ == "__main__":
    unittest.main()
