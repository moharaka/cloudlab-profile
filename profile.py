"""
This profile sets up an environment for a [vHive](https://github.com/ease-lab/vhive) cluster deployment of one or more nodes (this does not include the actual cluster bootstrapping). Note that this profile grows the root fs image to the maximum so it does not support disk snapshots.

The number of nodes set to run a specific operating system image (Ubuntu24), connected by a single link. It can be instantiated on any cluster, this particular Ubuntu image is available on all clusters.

Instructions:
Wait for the profile instance to start, then click on the node in the topology and choose the `shell` menu item. 
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()


node_type = "m400"
node_number = 1

# Params
pc.defineParameter("node_type", "Hardware specs of the nodes to use (tested on xl170 on Utah, rs440 on Mass, m400 on OneLab).",
    portal.ParameterType.NODETYPE, node_type, advanced=False, groupId=None)
pc.defineParameter("num_nodes", "Number of nodes to use.",
 portal.ParameterType.INTEGER, node_number, legalValues=[], advanced=False, groupId=None)
params = pc.bindParameters()
if params.num_nodes < 1:
    pc.reportError(portal.ParameterError("You must choose a minimum of 1 node "))
pc.verifyParameters()

##
nodes = []
interfaces = []
blockstores = []

link = pg.LAN("link-0")

for i in range(params.num_nodes):
    nodes.append(pg.RawPC("node-%03d" % i))
    nodes[i].hardware_type = params.node_type
    nodes[i].disk_image='urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD'
    
    # Grow the root fs to the maximum. Note that saving the image is not possible with that!
    nodes[i].addService(pg.Execute(shell="bash", command="curl -s https://raw.githubusercontent.com/vhive-serverless/vHive/9d8ea6753a5104ff4e061ea82d98197dcd6345ac/scripts/cloudlab/cloudlab-grow-rootfs.sh | sudo bash"))

    interfaces.append(nodes[i].addInterface("interface-%03d" % i))
    ip = "10.0.1." + str(i+1)
    interfaces[i].addAddress(pg.IPv4Address(ip, "255.255.255.0"))
    link.addInterface(interfaces[i])
    request.addResource(nodes[i])

request.addResource(link)


# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
