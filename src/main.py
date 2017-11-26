import collections
import docker
import yaml

def check_docker():
    client = docker.from_env()
    print(client.ping())


# def create_main_container():
#     client = docker.APIClient(
#         **docker.utils.kwargs_from_env(assert_hostname=False)
#     )
#     container = client.create_container(
#         "ubuntu:trusty", "/bin/sleep 300000", detach=True, ports=[10000], name="c1")
#     client.start(container=container.get('Id'))
#     print("c1 created")


# def create_children_container():
#     client = docker.APIClient(
#         **docker.utils.kwargs_from_env(assert_hostname=False)
#     )

#     host_config = client.create_host_config(
#         links=[("c1","c1")]
#     )

#     container = client.create_container(
#         "ubuntu:trusty", "sh -c \"ping $C1_PORT_10000_TCP_ADDR\"", detach=True, host_config=host_config, name="c2")
#     client.start(container=container.get('Id'))
#     print("c2 created")

def create_container(config):
    client = docker.APIClient(
        **docker.utils.kwargs_from_env(assert_hostname=False)
    )

    links_list=[]
    for link in config.get("links", []):
        links_list.append((link, link))
    
    host_config = client.create_host_config(
        links=links_list
    )

    container = client.create_container(
        config["image"], config["command"], detach=True, ports=config.get("ports", None), host_config=host_config, name=config["name"])
    client.start(container=container.get("Id"))
    print("Container "+config["name"]+" created!")
    

def parse_config(config):
    container_list = dependency_sorted(config.get("containers"))

    for container_name, container_config in container_list:
        container_config["name"] = container_name
        create_container(container_config)


def dependency_sorted(containers):
    container_links = dict((name, set(c.get("links", []))) for name, c in containers.items())                  
    sorted_names = _resolve(container_links)
    return [(name, containers[name]) for name in sorted_names]


def _resolve(d):
    all_keys = frozenset(d.keys())
    result = []
    resolved_keys = set()

    # TODO: take start delays into account as well

    while d:
        resolved_this_round = set()
        for name, links in list(d.items()):
            # containers with no links can be started in any order.
            # containers whose parent containers have already been resolved
            # can be added now too.
            if not links or links <= resolved_keys:
                result.append(name)
                resolved_this_round.add(name)
                del d[name]

            # guard against containers which link to unknown containers
            unknown = links - all_keys
            if len(unknown) == 1:
                raise Exception(
                    "container %s links to unknown container %s" %
                    (name, list(unknown)[0]))
            elif len(unknown) > 1:
                raise Exception(
                    "container %s links to unknown containers %s" %
                    (name, unknown))

        # if we made no progress this round, we have a circular dep
        if not resolved_this_round:
            raise Exception("containers have circular links!")

        resolved_keys.update(resolved_this_round)

    return result

def main(args=None):
    with open("blockade.yaml") as f:
        d = yaml.safe_load(f)
        #print(d)
        parse_config(d)

    # return 
    # check_docker()
    # create_main_container()
    # create_children_container()


if __name__ == '__main__':
    main()
