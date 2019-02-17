import docker #retrieves docker-py fucntionality
from flask import Flask, request, Response
import flask
import json #for dumping JSON format
import requests
import subprocess #to execute terminal command
app = Flask(__name__)

"""successful server creation"""


client = docker.from_env() #connect to docker environment
#data = request.get_json() # cannnot be used outside of request
@app.route("/", methods=['GET'])
def test():
    return 'server has been created'


"""Show docker info in json format"""


@app.route("/info", methods=['GET'])
def info():
    try:

        docker_info = client.info()
        """load ouput in json format"""
        docker_info_string = (json.dumps(docker_info, indent=4))
        return (docker_info_string)
    except requests.exceptions.HTTPError:
        pass


"""Show image list"""


@app.route("/Ilist", methods=['GET'])
def show_image_list():
    try:
        li = client.images.list()
        """iterate through the imagelist and print it in server side"""
        iterator = li.__iter__()
        for i in iterator:
            return str(i)
        return str(li)
    except requests.exceptions.HTTPError:
        pass


"""Show container list"""


@app.route("/Clist", methods=['GET'])
def show_container_list():
    try:
        container_list = client.containers.list()
        return ('\n'+'online containers \n'+str(container_list))
    except requests.exceptions.HTTPError:
        pass


"""Pull the image"""


@app.route("/pull", methods=['POST'])
def pull_image_from_hub():
    try:
        data = request.get_json() 
        imagename = data['imagename'] # 'imagename' in JSON format
        pulledimage = client.images.pull(imagename)
        return ("pulled image:" +str(pulledimage))
    except requests.exceptions.HTTPError:
        pass


"""Create Container"""


@app.route("/create", methods=['POST'])
def create_container_from_image():
    try:
        data = request.get_json() 
        imagename = data['imagename']
        containername = data['containername']
        container = client.containers.create(imagename, detach=True, name=containername)
        return (str(container))
        return ('Created Container Name:'+container.name)
    except requests.exceptions.HTTPError:
        pass


"""Start the container"""

@app.route("/start", methods=['POST'])
def start_container_from_id():
    try:

        """Container is possible to run either with imagename or the containername. But it is not 
         possible to use both value to run a container """
        data = request.get_json() 
        containerid = str(data['containerid'])
        container = client.containers.get(containerid)
        container.start()
        return ('started container id' + str(container))
    except requests.exceptions.HTTPError:
        pass

@app.route("/run", methods=['POST'])
def start_container_from_image():
    try:

        """Container is possible to run either with imagename or the containername. But it is not 
         possible to use both value to run a container """
        data = request.get_json() 
        imagename = data['imagename']
        containername = str(data['containername'])
        client.containers.run(imagename, detach=True, name=containername)
        containerstate = client.containers.get(containername)
        return ('started container'+ str(containerstate))
    except requests.exceptions.HTTPError:
        pass


"""Inspect running container"""


@app.route("/inspectCon", methods=['POST'])
def inspect_running_container():
    try:
        data = request.get_json() 
        containerID = data['containerID']
        inspect = client.api.inspect_container(containerID)
        """Return in json format"""
        inspect_info = (json.dumps(inspect, indent=4))
        return (inspect_info)
    except requests.exceptions.HTTPError:
        pass


"""Stop all container"""


@app.route("/stop", methods=['GET'])
def stop():
    try:
        container_list = client.containers.list()
        for container in container_list:
            container.stop()
        return "All container stopped"
    except requests.exceptions.HTTPError:
        pass


"""Remove all container"""


@app.route("/remove", methods=['DELETE'])
def remove_existing_container():
    try:
        delete = client.containers.prune()
        return str(delete)
    except requests.exceptions.HTTPError:
        pass


"""Create Bridge Network"""


@app.route("/networkcreate", methods=['POST'])
def network_create():
    try:
        data = request.get_json() 
        networkname = data['networkname']
        subnet = data['subnet']
        iprange = data['iprange']
        gateway = data['gateway']
        bridgename = str(data['bridgename'])
        ipam_pool = docker.types.IPAMPool(subnet, iprange, gateway)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        networkcreate = client.networks.create(networkname, driver = "bridge", ipam = ipam_config, options={
            "com.docker.network.bridge.name": bridgename
        })
        return str(networkcreate) + 'created successfully'
    except requests.exceptions.HTTPError:
        pass


@app.route("/containerexec", methods=['POST'])
def container_exec():
    try:
        imagename = data['imagename']
        containername = str(data['containername'])
        command = str(data['command'])
        container=client.containers.run(imagename, detach=True, name=containername, command=command)
        log = str(container.logs())
        runningcontainer = client.containers.get(containername)
        return "Container is: " + str(runningcontainer) + "and log is " + str(log)
    except requests.exceptions.HTTPError:
        pass

@app.route("/meshnet", methods=['POST'])
def station_dump():

    try:
        data = request.get_json() 
        interface = str(data['wifi'])
        i=subprocess.call(["iw", "dev",interface, "station", "dump"])
        return ('hello'+str(i))

    except requests.exceptions.HTTPError:
            pass


if __name__ == "__main__":
    app.run(debug=True)
