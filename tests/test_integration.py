@unittest.skipIf(*INT_SKIP)
    def test_containers2(self):
        config_path = example_config_path("sleep2/blockade.yaml")

        try:
            self.call_blockade("-c", config_path, "up")

            self.call_blockade("-c", config_path, "status")
            stdout, _ = self.call_blockade("-c", config_path, "status",
                                           "--json")
            parsed = json.loads(stdout)
            self.assertEqual(len(parsed), 3) # check if 3 containers are created

            self.call_blockade("-c", config_path, "flaky", "c1")
            self.call_blockade("-c", config_path, "slow", "c2", "c3")
            self.call_blockade("-c", config_path, "duplicate", "c2", "c3")
            self.call_blockade("-c", config_path, "fast", "c3")

            self.call_blockade("-c", config_path, "fast", "--all")

            with self.assertRaises(FakeExit):  # check if it throws exception when interacting with non-existing container
                self.call_blockade("-c", config_path, "slow", "nonexisting")

        finally:
            try:
                self.call_blockade("-c", config_path, "destroy")
            except Exception:
                print("Failed to destroy Blockade!")
                traceback.print_exc(file=sys.stdout)