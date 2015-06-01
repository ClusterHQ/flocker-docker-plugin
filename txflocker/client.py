"""
A collection of utilities for using the flocker REST API.
"""

from treq.client import HTTPClient

from twisted.internet import reactor, ssl
from twisted.internet.ssl import optionsForClientTLS
from twisted.python.filepath import FilePath
from twisted.web.client import Agent

import yaml

def get_client(reactor=reactor, certificates_path=FilePath("/etc/flocker")):
    """
    Create a ``treq``-API object that implements the REST API TLS
    authentication.

    That is, validating the control service as well as presenting a
    certificate to the control service for authentication.

    :param reactor: The reactor to use.
    :param FilePath certificates_path: Directory where certificates and
        private key can be found.

    :return: ``treq`` compatible object.
    """
    config = certificates_path.child("agent.yml")
    node_key = certificates_path.child("node.key")
    cluster_crt = certificates_path.child("cluster.crt")
    if config.exists() and node_key.exists() and cluster_crt.exists():
        # we are installed on a flocker node with a certificate, try to reuse
        # it for auth against the control service
        cert_data = certificates_path.child("cluster.crt").getContent()
        auth_data = certificates_path.child("node.key").getContent()
        agent_config = yaml.load(config.open())
        client_certificate = ssl.PrivateCertificate.loadPEM(auth_data)
        authority = ssl.Certificate.loadPEM(cert_data)
        options = optionsForClientTLS(
                agent_config["control-service"]["hostname"],
                authority, client_certificate)
        return HTTPClient(Agent(reactor, contextFactory=options))
    else:
        return HTTPClient(Agent(reactor))
