# Copyright ClusterHQ Inc. See LICENSE file for details.

import os
from twisted.web import server, resource
from twisted.application import service, internet

from flockerdockerplugin.adapter import (HandshakeResource, CreateResource,
    RemoveResource, PathResource, MountResource, UnmountResource)

"""
Docker 1.8 moved the plugins folder from 
/usr/share/docker/plugins to
/run/docker/plugins
We will listen on both paths for backwards compat reasons
"""
socketPaths = [
    "/usr/share/docker/plugins/flocker.sock",
    "/run/docker/plugins/flocker.sock"
]

"""
Create the handler that will deal with incoming requests
"""
def getAdapter():
    root = resource.Resource()
    root.putChild("Plugin.Activate", HandshakeResource())
    root.putChild("VolumeDriver.Create", CreateResource())
    root.putChild("VolumeDriver.Remove", RemoveResource())
    root.putChild("VolumeDriver.Path", PathResource())
    root.putChild("VolumeDriver.Mount", MountResource())
    root.putChild("VolumeDriver.Unmount", UnmountResource())

    site = server.Site(root)
    return site

"""
Ensure the directory for the socket exists and remove the existing
socket file if it is found
"""
def prepareSocketPath(path):
    dirName = os.path.dirname(socketPath)
    if not os.path.exists(dirName):
        os.makedirs(dirName)

"""
Create a UNIX socket on the given path and mount the 
given adapter on the socket
make the service parent of the server the given application
"""
def mountAdapter(path, adapter, app):
    adapterServer = internet.UNIXServer(path, adapter)
    adapterServer.setServiceParent(app)

"""
The base application and adapter that will be mounted on each SocketPath
"""
application = service.Application("Flocker Docker Plugin")
adapter = getAdapter()

"""
Loop over each socketPath and mount the adapter
on the socket for that path
"""
for socketPath in socketPaths:
    prepareSocketPath(socketPath)
    mountAdapter(socketPath, adapter, application)