import collections
import os
import re
import docker
import yaml
import argparse

def check_docker():
    # check if docker cli is running
    client = docker.from_env()
    print(client.ping())

def create_container(config):
    client = docker.APIClient(
        **docker.utils.kwargs_from_env(assert_hostname=False)
    )

    volumes = list(config.get("volumes", {}).values()) or None

    host_config = client.create_host_config(
        binds=config.get("volumes"),
        dns=config.get("dns"),
        port_bindings=config.get("ports"),
        ulimits=[{'name': 'core', 'soft': 3145728, 'hard': 4194304}],
        links=config.get("links"),
        cap_add=config.get("cap_add"))

    container = client.create_container(
        config["image"], 
        command=config.get("command"), 
        detach=True, 
        ports=config.get("expose"), 
        volumes=volumes,
        hostname=config.get("hostname"),
        environment=config.get("environment"),
        host_config=host_config, 
        name=config.get("name"))
    
    container_id = container.get("Id")
    client.start(container=container_id)

    if config.get("chaos"):
        device = get_container_device(client, container_id)
        cmd = ["tc", "qdisc", "replace", "dev", device, "root", "netem"] + config.get("chaos").split()
        output = run(client, container_id, cmd)
        print(output)
            
    print("Container "+config["name"]+" created!")


def run( client, container_id, command):
    def _exec():
        exec_handle = client.exec_create(container_id, command)
        output = client.exec_start(exec_handle).decode('utf-8')
        return output

    return _exec()

def get_container_device( docker_client, container_id):
    container_idx = get_container_device_index(docker_client, container_id)

    host_idx = container_idx 
    cmd = 'ip link'
    host_res = run(docker_client, container_id, cmd)
    host_rgx = '^%d: ([^:@]+)[:@]' % host_idx
    host_match = re.search(host_rgx, host_res, re.M)
    if host_match:
        return host_match.group(1)

def get_container_device_index(docker_client, container_id):
    cmd_args = ['cat', '/sys/class/net/eth0/ifindex']
    res = run(docker_client,container_id,cmd_args)
    return int(res)
    
def parse_config(config):    
    for container_name, container_config in config["containers"].items():
        container_config["name"] = container_name
        container_config["links"] = _dictify(container_config.get("links"), 'links')
        container_config["volumes"] = _dictify(container_config.get("volumes"), 'volumes', lambda x: os.path.abspath(x))
        container_config["ports"] = _dictify(container_config.get("ports"), 'ports')
        container_config["cap_add"] = container_config.get("cap_add", [])
        container_config["cap_add"].append("NET_ADMIN")

        container_config["expose"] = list(set(
            int(port) for port in
            container_config.get("expose", []) + list(container_config.get("ports",{}).values())
        ))

        container_config["environment"] = _dictify(container_config.get("environment"),'environment')
        
    container_list = dependency_sorted(config["containers"])

    for container_config in container_list:
        create_container(container_config)

    
    # client = docker.APIClient(
    #     **docker.utils.kwargs_from_env(assert_hostname=False)
    # )
    # test = client.inspect_container("c1")
    # print(test)


def dependency_sorted(containers):
    container_links = dict((name, set(c.get("links")))   for name, c in containers.items())                  
    sorted_names = _resolve(container_links)
    return [ containers[name] for name in sorted_names]


def _resolve(d):
    all_keys = frozenset(d.keys())
    result = []
    resolved_keys = set()

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


def _dictify(data, name='input', key_mod=lambda x: x, value_mod=lambda x: x):
    if data:
        if isinstance(data, collections.Sequence):
            return dict((key_mod(str(v)), value_mod(str(v))) for v in data)
        elif isinstance(data, collections.Mapping):
            return dict((key_mod(str(k)), value_mod(str(v or k))) for k, v in list(data.items()))
        else:
            raise Exception("invalid %s: need list or map" % (name,))
    else:
        return {}

def process_yaml(config_file):
    with open(config_file) as f:
        d = yaml.safe_load(f)
        parse_config(d)

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", metavar="blockade.yaml",
                        help="Config YAML.")
    
    args = parser.parse_args()
    config_file = args.config or "blockade.yaml"

    process_yaml(config_file)
    


if __name__ == '__main__':
    main()
