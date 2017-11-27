import os
import unittest
import docker 
from src import main as core

class CommandTests(unittest.TestCase):

    IsSetup = False
    inspect_c1 = None
    inspect_c2 = None

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
        self.__class__.inspect_c2 = client.inspect_container("c2")
        
    def test_image(self):
        self.assertEqual(self.__class__.inspect_c1["Config"]["Image"], "ubuntu:trusty")
    
    def test_cmd(self):
        self.assertEqual(" ".join(self.__class__.inspect_c1["Config"]["Cmd"]), "/bin/sleep 300000")

    def test_volume(self):
        self.assertEqual(self.__class__.inspect_c1["Mounts"][0]["Source"], "/Users/mac/Desktop/CS527/cs527project/volume")
        self.assertEqual(self.__class__.inspect_c1["Mounts"][0]["Destination"], "/opt/myapp")

    def test_expose(self):
        self.assertEqual(self.__class__.inspect_c1["NetworkSettings"]["Ports"]["12345/tcp"], None)

    def test_link(self):
        self.assertEqual(self.__class__.inspect_c2["HostConfig"]["Links"][0], "/c1:/c2/c1")

    def test_port(self):
        self.assertEqual(self.__class__.inspect_c1["NetworkSettings"]["Ports"]["10000/tcp"][0]["HostIp"], "0.0.0.0")
        self.assertEqual(self.__class__.inspect_c1["NetworkSettings"]["Ports"]["10000/tcp"][0]["HostPort"], "10000")

    def test_env(self):
        self.assertEqual(self.__class__.inspect_c1["Config"]["Env"][0], "deep=purple")
    
    def test_hostname(self):
        self.assertEqual(self.__class__.inspect_c1["Config"]["Hostname"], "myhost")
    
    def test_dns(self):
        self.assertEqual(self.__class__.inspect_c1["HostConfig"]["Dns"][0], "8.8.8.8")

    def test_capadd(self):
        self.assertEqual(self.__class__.inspect_c1["HostConfig"]["CapAdd"][0], "SYS_ADMIN")

    def test_name(self):
        self.assertEqual(self.__class__.inspect_c1["Name"], "/c1")




if __name__ == '__main__':
    unittest.main()