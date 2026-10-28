#!/usr/bin/env python3
"""Meaningful local functional checks; no provider calls or production activation."""
import asyncio
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

class Gate(unittest.TestCase):
    def test_installed_graph_ingest_and_search_are_model_free(self):
        with tempfile.TemporaryDirectory() as d:
            env=dict(os.environ,KNOWLEDGE_HOME=d)
            base=[sys.executable,'-m','knowledge.cli']
            def run(args):
                r=subprocess.run(base+args,cwd=d,env=env,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);return r.stdout
            run(['ingest','--graph','fictional','--text','Fictional parser evidence links checks and validation.','--method','cooccurrence'])
            result=run(['search','parser','--graph','fictional','--json']);self.assertIn('parser',result.lower())

if __name__=='__main__':unittest.main(verbosity=2)
