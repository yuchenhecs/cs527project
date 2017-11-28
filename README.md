# cs527project

An application that helps network testing by manipulating network condition in docker containers. Inspired by  https://github.com/worstcase/blockade

This program will read from a yaml file(blockade.yaml by default), and create containers accordingly.

## Prerequisites

* Python3
* docker

## Getting Started

make sure docker is started

```
$ dockerd
```

navigate to project folder, and install dependencies (right now there's only one)

```
$ pip install -r requirements.txt 
```

now run 

```
$ python3 src/main.py
```

or run with specific yaml file

```
$ python3 src/main.py --config other.yaml
```

## Testing

make sure docker is started, dependencies are installed, and navigate to project folder, and run


```
$ python3 test/test_command.py
```

## Caveat

You have to stop AND remove all docker containers before you run with the same yaml file again. Otherwise it will trigger name conflict exception.

To stop and remove all docker containers
```
$ docker stop $(docker ps -a -q)
$ docker rm $(docker ps -a -q)
```


## Example yaml file

```
containers:
  c1:
    image: ubuntu:trusty
    command: /bin/sleep 300000
    ports: [10000]
    expose: [12345]
    volumes: {"/Users/mac/Desktop/CS527/cs527project/volume": "/opt/myapp"}
    environment : {"deep" : "purple"}
    hostname: myhost
    dns: ["8.8.8.8"]
    cap_add: ["SYS_ADMIN"]

  c2:
    image: ubuntu:trusty
    command: sh -c "ping $C1_PORT_10000_TCP_ADDR"
    links: ["c1"]
    chaos: duplicate 50%

  c3:
    image: ubuntu:trusty
    command: sh -c "ping $C1_PORT_10000_TCP_ADDR"
    links: ["c1"]
    chaos: loss 50%

  c4:
    image: ubuntu:trusty
    command: sh -c "ping $C1_PORT_10000_TCP_ADDR"
    links: ["c1"]
    chaos: delay 1000ms
```


## YAML Commands

### image
image is required and specifies the Docker image name to use for the container. The image must exist in your Docker installation.
Example   ```image: my_docker_image:tag```
Same as    ``` docker run my_docker_image:tag```

### command
command is optional and specifies the command to run within the container. If not specified, a default command must be part of the image you are using. You may include environment variables in this command, but to do so you must typically wrap the command in a shell, like,  command: sh -c "/bin/myapp $MYENV".
Example   ```command: /bin/myapp```
Same as   ```docker run IMAGE /bin/myapp```

### volumes
volumes is optional and specifies the volumes to mount in the container, from the host. Volumes can be specified as either a map or a list. In map form, the key is the path on the host to expose and the value is the mountpoint within the container. In list form, the host path and container mountpoint are assumed to be the same. See the Docker volumes documentation for details about how this works.

Example1  ```volumes: {"/opt/myapp_host": "/opt/myapp"}```
Same as   ```docker run IMAGE --volume /opt/myapp_host:/opt/myapp```
Example2  ```volumes: ["/opt/myapp"]```
Same as   ```docker run IMAGE --volume /opt/myapp```

### expose
expose is optional and specifies ports to expose from the container. Ports must be exposed in order to use the Docker named links feature.
Example  ```expose: [80]```
Same as  ```docker run IMAGE  --expose 80```

### links
links is optional and specifies links from one container to another. A dependent container will be given environment variables with the parent container’s IP address and port information. See named links documentation for details.
Example  ```links: ["c1"]```
Same as  ```docker run  IMAGE  --link c1```

### ports
ports is optional and specifies ports published to the host machine. It is a dictionary from external port to internal container port.
Example  ```ports: [10000]```
Same as   ```docker run IMAGE -p 10000 ```

### environment
environment is optional and specifies environment variables for command. See more details in command section above.
Example  ```environment : {“deep” : “purple”}```
Same as   ```docker run IMAGE -e "deep=purple"```

### hostname
hostname is optional and gives the ability to redefine hostname of a container.
Example    ```hostname: “value”```
Same as    ```docker run --hostname value```

### dns
dns is optional and specifies a list of DNS-servers for container.
Example  ```dns: [“8.8.8.8”]```
Same as  ```docker run --dns 8.8.8.8```

### cap_add
cap_add is optional and specifies additional root capabilities
Example ```cap_add: “SYS_ADMIN”```
Same as ```docker run IMAGE --cap-add SYS_ADMIN```

### chao
chao is optional and specifies what network condition should be. It's the same as netem, so you can simply put netem parameters here. See more details in https://wiki.linuxfoundation.org/networking/netem
    
Example1 ```chao: loss 50%``` will drop 50% of the outgoing packets
Example2 ```chao: duplicate 50%``` will duplicate 50% of the outgoing packets
Example3 ```chao: delay 1000ms``` will delay all outgoing packets by 1000ms


