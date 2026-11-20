import unittest
from train import train

class TrainingTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(train(), train())
    def test_xor(self):
        result = train()
        self.assertEqual(result["model_metrics"]["correct"], 4)
        self.assertLess(result["baseline_metrics"]["correct"], 4)
    def test_architecture(self):
        self.assertEqual(train()["parameters"], 17)

if __name__ == "__main__":
    unittest.main()
