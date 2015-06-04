# Copyright ClusterHQ Inc. See LICENSE file for details.

import os
from twisted.web import server, resource
from twisted.application import service, internet

from powerstripflocker.adapter import (HandshakeResource, CreateResource,
    RemoveResource, PathResource, MountResource, UnmountResource)

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

application = service.Application("Powerstrip Flocker Adapter")

DOCKER_PLUGINS_FOLDER = os.environ.get("DOCKER_PLUGINS_FOLDER",
    "/usr/share/docker/plugins") + "/flocker.sock"

adapterServer = internet.UNIXServer(DOCKER_PLUGINS_FOLDER, getAdapter())
adapterServer.setServiceParent(application)
