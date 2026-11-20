import json,tempfile,unittest
from pathlib import Path
from local_inference import LABELS,TEST,evaluate,fit,load_checkpoint,predict,save_checkpoint

class ModelTests(unittest.TestCase):
    def setUp(self): self.model=fit()
    def test_heldout(self): self.assertEqual(evaluate(self.model)['correct'],len(TEST))
    def test_labels(self): self.assertEqual(set(self.model['labels']),set(LABELS))
    def test_deterministic(self): self.assertEqual(fit(),fit())
    def test_probabilities(self):
        probs=predict(self.model,'review scientific claim')['probabilities']
        self.assertAlmostEqual(sum(probs.values()),1,places=5)
    def test_input_validation(self):
        with self.assertRaises(ValueError): predict(self.model,'')
        with self.assertRaises(ValueError): predict(self.model,'x'*501)
    def test_checkpoint_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'model.json'
            saved=save_checkpoint(p,self.model)
            self.assertEqual(load_checkpoint(p),saved)
    def test_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'model.json'
            save_checkpoint(p,self.model)
            data=json.loads(p.read_text())
            data['model']['training_count']=999
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError): load_checkpoint(p)
    def test_tiny_dataset_provenance(self):
        self.assertEqual(self.model['training_count'],18)
        self.assertEqual(len(TEST),6)
if __name__=='__main__': unittest.main()
