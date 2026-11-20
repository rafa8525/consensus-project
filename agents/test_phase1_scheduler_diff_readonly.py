#!/usr/bin/env python3
"""No-network comparison fixture tests."""
import unittest
from phase1_scheduler_diff_readonly import compare
class Tests(unittest.TestCase):
    def setUp(self):
        self.before={'id':1524414,'command':'safe parent','interval':'daily','hour':10,'minute':0,'description':'private','enabled':True}
    def test_unchanged(self):
        r=compare(self.before,dict(self.before))
        self.assertEqual(r['status'],'MATCH')
        self.assertTrue(r['stable_fields_match'])
    def test_disabled_only(self):
        r=compare(self.before,{**self.before,'enabled':False})
        self.assertEqual(r['status'],'MATCH')
        self.assertFalse(r['current_enabled'])
    def test_volatile_field_name_only(self):
        r=compare(self.before,{**self.before,'next_run':'changed'})
        self.assertEqual(r['modified_field_names'],['next_run'])
        self.assertEqual(r['key_presence_changes'],['next_run'])
        self.assertEqual(r['status'],'METADATA_DIFF')
    def test_hidden_private_value(self):
        r=compare(self.before,{**self.before,'description':'secret-value'})
        self.assertNotIn('secret-value',str(r))
        self.assertIn('description',r['modified_field_names'])
    def test_wrong_schedule(self):
        r=compare(self.before,{**self.before,'id':125})
        self.assertFalse(r['stable_fields_match'])
if __name__=='__main__':unittest.main()
