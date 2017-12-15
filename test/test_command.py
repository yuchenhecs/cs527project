import os
import unittest
import docker 
# from src import main as core

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        
        self.__class__.client = docker.APIClient(
            **docker.utils.kwargs_from_env(assert_hostname=False)
        )
        self.__class__.inspect_c1 = self.client.inspect_container("c1")
        self.__class__.inspect_c2 = self.client.inspect_container("c2")
        self.__class__.inspect_c3 = self.client.inspect_container("c3")
        self.__class__.inspect_c4 = self.client.inspect_container("c4")

    @classmethod
    def tearDownClass(cls):
        # clean up the test containers
        print("Cleaning up the test containers. This may take a few minutes")
        # print(cls.inspect_c1)
        container_id_c1 = cls.inspect_c1["Id"]
        container_id_c2 = cls.inspect_c2["Id"]
        container_id_c3 = cls.inspect_c3["Id"]
        container_id_c4 = cls.inspect_c4["Id"]


        cls.client.stop(container_id_c1)
        cls.client.stop(container_id_c2)
        cls.client.stop(container_id_c3)
        cls.client.stop(container_id_c4)


        cls.client.remove_container(container_id_c1)
        cls.client.remove_container(container_id_c2)
        cls.client.remove_container(container_id_c3)
        cls.client.remove_container(container_id_c4)
        
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

    def test_chao_duplicate(self):
        container_id = self.__class__.inspect_c2["Id"]
        self.assertEqual(core.get_tc_qdisc_status(self.__class__.client, container_id, "duplicate 70%"), True)

    def test_chao_duplicate_with_ping(self):
        host_ip = self.__class__.inspect_c1["NetworkSettings"]["IPAddress"]
        container_id = self.__class__.inspect_c2["Id"]
        self.assertEqual(core.get_ping_response_duplicate(self.__class__.client, container_id, host_ip), True)

    def test_chao_loss(self):
        container_id = self.__class__.inspect_c3["Id"]
        self.assertEqual(core.get_tc_qdisc_status(self.__class__.client, container_id, "loss 70%"), True)

    def test_chao_loss_with_ping(self):
        host_ip = self.__class__.inspect_c1["NetworkSettings"]["IPAddress"]
        container_id = self.__class__.inspect_c3["Id"]
        self.assertEqual(core.get_ping_response_loss(self.__class__.client, container_id, host_ip), True)

    def test_chao_delay(self):
        container_id = self.__class__.inspect_c4["Id"]
        self.assertEqual(core.get_tc_qdisc_status(self.__class__.client, container_id, "delay 1.0s"), True)
    
    def test_chao_delay_with_ping(self):
        host_ip = self.__class__.inspect_c1["NetworkSettings"]["IPAddress"]
        container_id = self.__class__.inspect_c4["Id"]
        self.assertEqual(core.get_ping_response_delay(self.__class__.client, container_id, host_ip), True)

    

    



if __name__ == '__main__':
    unittest.main()