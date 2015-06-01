"""
A collection of utilities for using the flocker REST API.
"""

from treq.client import HTTPClient

from twisted.internet import reactor, ssl
from twisted.internet.ssl import optionsForClientTLS
from twisted.python.filepath import FilePath
from twisted.web.client import Agent

import yaml

def get_client(reactor=reactor, certificates_path=FilePath("/etc/flocker"),
        user_certificate_filename="plugin.crt", user_key_filename="plugin.key",
        cluster_certificate_filename="cluster.crt", target_hostname=None):
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
    if target_hostname is None:
        config = certificates_path.child("agent.yml")
        if config.exists():
            agent_config = yaml.load(config.open())
            target_hostname = agent_config["control-service"]["hostname"]
    user_crt = certificates_path.child(user_certificate_filename)
    user_key = certificates_path.child(user_key_filename)
    cluster_crt = certificates_path.child(cluster_certificate_filename)
    if (user_crt.exists() and user_key.exists() and cluster_crt.exists()
            and target_hostname is not None):
        # we are installed on a flocker node with a certificate, try to reuse
        # it for auth against the control service
        cert_data = cluster_crt.getContent()
        auth_data = user_crt.getContent() + user_key.getContent()

        authority = ssl.Certificate.loadPEM(cert_data)
        client_certificate = ssl.PrivateCertificate.loadPEM(auth_data)

        options = optionsForClientTLS(
                unicode(target_hostname),
                authority, client_certificate)
        return HTTPClient(Agent(reactor, contextFactory=options))
    else:
        raise Exception("Not enough information to construct TLS context: "
                "user_crt: %s, cluster_crt: %s, user_key: %s, target_hostname: %s" % (
                    user_crt, cluster_crt, user_key, target_hostname))
