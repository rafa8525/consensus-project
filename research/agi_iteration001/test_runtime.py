import json
import tempfile
import unittest
from pathlib import Path
from runtime import InvalidTask, load_registry, save_new, simulate

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.fixture = {'agents': [{'id':f'AGI-{i:02d}', 'name':f'Agent {i}', 'agi_division':'Research', 'status':'PROPOSED_UNVERIFIED','production_enabled':False} for i in range(1,56)]}
        self.registry_path=self.path/'registry.json'
        self.registry_path.write_text(json.dumps(self.fixture))
        self.registry=load_registry(self.registry_path)
    def test_count(self):
        self.assertEqual(len(self.registry),55)
    def test_task_proposal(self):
        out=simulate([{'agent_id':'AGI-01','operation':'design_experiment','objective':'Assess transfer'}],self.registry)
        self.assertEqual(out['task_count'],1)
        self.assertFalse(out['results'][0]['agent_executed'])
    def test_unknown_agent(self):
        with self.assertRaises(InvalidTask):
            simulate([{'agent_id':'AGI-99','operation':'design_experiment','objective':'x'}],self.registry)
    def test_no_arbitrary_commands(self):
        with self.assertRaises(InvalidTask):
            simulate([{'agent_id':'AGI-01','operation':'shell','objective':'run code'}],self.registry)
    def test_task_cap(self):
        with self.assertRaises(InvalidTask):
            simulate([{'agent_id':'AGI-01','operation':'design_experiment','objective':'x'}]*56,self.registry)
    def test_production_enabled_rejected(self):
        self.fixture['agents'][0]['production_enabled']=True
        self.registry_path.write_text(json.dumps(self.fixture))
        with self.assertRaises(InvalidTask):
            load_registry(self.registry_path)
    def test_no_overwrite(self):
        out=simulate([],self.registry)
        dest=self.path/'record.json'
        save_new(dest,out)
        with self.assertRaises(FileExistsError):
            save_new(dest,out)
    def test_reproducible(self):
        tasks=[{'agent_id':'AGI-02','operation':'evaluate_evidence','objective':'Test'}]
        self.assertEqual(simulate(tasks,self.registry),simulate(tasks,self.registry))

if __name__=='__main__':
    unittest.main()
