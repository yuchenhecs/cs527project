import docker

def check_docker():
    client = docker.from_env()
    print(client.ping())
   
def create_main_container():
    client = docker.APIClient(
        **docker.utils.kwargs_from_env(assert_hostname=False)
    )
    container = client.create_container("ubuntu:trusty", "/bin/sleep 300000", detach=True, ports=[10000], name="c1")
    client.start(container=container.get('Id'))
    print("c1 created")


def create_children_container():
    client = docker.APIClient(
        **docker.utils.kwargs_from_env(assert_hostname=False)
    )

    host_config = client.create_host_config(
        links=[( "c1", "c1")]
    )

    container = client.create_container("ubuntu:trusty", "sh -c \"ping $C1_PORT_10000_TCP_ADDR\"", detach=True, host_config=host_config, name="c2")
    client.start(container=container.get('Id'))
    print("c2 created")

def main(args=None):
    check_docker()
    create_main_container()
    create_children_container()


if __name__ == '__main__':
    main()