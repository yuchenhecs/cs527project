import os
import unittest
import docker 
from src import main as core

class CommandTests(unittest.TestCase):

    IsSetup = False
    inspect_c1 = None

    def setUp(self):
        if not self.IsSetup:
            print("Initializing testing environment")
            # run the real setup
            self.setupClass()
            # remember that it was setup already
            self.__class__.IsSetup = True


    def setupClass(self):
        core.process_yaml("blockade.yaml")
        client = docker.APIClient(
            **docker.utils.kwargs_from_env(assert_hostname=False)
        )
        self.__class__.inspect_c1 = client.inspect_container("c1")
        
        
    def test_image(self):
        self.assertEqual(self.__class__.inspect_c1["Config"]["Image"], "ubuntu:trusty")
    
    def test_cmd(self):
        self.assertEqual(" ".join(self.__class__.inspect_c1["Config"]["Cmd"]), "/bin/sleep 300000")

    def test_volume(self):
        self.assertEqual(self.__class__.inspect_c1["Mounts"][0]["Source"], "/Users/mac/Desktop/CS527/cs527project/volume")
        self.assertEqual(self.__class__.inspect_c1["Mounts"][0]["Destination"], "/opt/myapp")





if __name__ == '__main__':
    unittest.main()