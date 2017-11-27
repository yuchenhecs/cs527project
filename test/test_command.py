import os
import unittest
import docker 
from src import main as core

class CommandTests(unittest.TestCase):
    def setUp(self):
        core.process_yaml("blockade.yaml")
        
    def test_create(self):
        client = docker.APIClient(
            **docker.utils.kwargs_from_env(assert_hostname=False)
        )
        inspect = client.inspect_container("c1")
        self.assertEqual(inspect["Config"]["Image"], "ubuntu:trusty")


if __name__ == '__main__':
    unittest.main()