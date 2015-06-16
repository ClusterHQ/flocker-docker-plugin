"""
A collection of utilities for using the flocker REST API.
"""

from treq.client import HTTPClient

from twisted.internet import reactor, ssl, defer
from twisted.python.usage import UsageError
from twisted.python.filepath import FilePath
from twisted.web.client import Agent

import yaml
import treq
import copy

def process_metadata(metadata_str):
    if not metadata_str:
        return {}
    metadata = {}
    try:
        for pair in metadata_str.split(","):
            k, v = pair.split("=")
            metadata[k] = v
    except:
        raise UsageError("malformed metadata specification "
                "'%s', please use format 'a=b,c=d'" %
                (metadata_str,))
    return metadata

def parse_num(expression):
    if not expression:
        return None
    expression = expression.encode("ascii")
    unit = expression.translate(None, "1234567890.")
    num = expression.replace(unit, "")
    unit = unit.lower()
    if unit == 'tb' or unit == 't' or unit =='tib':
        return int(float(num)*1024*1024*1024*1024)
    elif unit == 'gb' or unit == 'g' or unit =='gib':
        return int(float(num)*1024*1024*1024)
    elif unit == 'mb' or unit == 'm' or unit =='mib':
        return int(float(num)*1024*1024)
    elif unit == 'kb' or unit == 'k' or unit =='kib':
        return int(float(num)*1024)
    else:
        return int(float(num))

def combined_state(client, base_url, deleted):
    d1 = client.get(base_url + "/configuration/datasets")
    d1.addCallback(treq.json_content)

    d2 = client.get(base_url + "/state/datasets")
    d2.addCallback(treq.json_content)

    d3 = client.get(base_url + "/state/nodes")
    d3.addCallback(treq.json_content)

    ds = [d1, d2, d3]

    d = defer.gatherResults(ds)
    def got_results(results):
        configuration_datasets, state_datasets, state_nodes = results

        # build up a table, based on which datasets are in the
        # configuration, adding data from the state as necessary
        configuration_map = dict((d["dataset_id"], d) for d in
                configuration_datasets)
        state_map = dict((d["dataset_id"], d) for d in state_datasets)
        nodes_map = dict((n["uuid"], n) for n in state_nodes)

        #print "got state:"
        #pprint.pprint(state_datasets)
        #print

        objects = []

        for (key, dataset) in configuration_map.iteritems():
            dataset = copy.copy(dataset)
            if dataset["deleted"]:
                # the user has asked to see deleted datasets
                if deleted:
                    if key in state_map:
                        status = "deleting"
                    else:
                        status = "deleted"
                # we are hiding deleted datasets
                else:
                    continue
            else:
                if key in state_map:
                    if ("primary" in state_map[key] and
                            state_map[key]["primary"] in nodes_map):
                        status = u"attached \u2705"
                    else:
                        status = u"detached"
                else:
                    # not deleted, not in state, probably waiting for it to
                    # show up.
                    status = u"pending \u231b"

            dataset["status"] = status

            meta = []
            if dataset["metadata"]:
                for k, v in dataset["metadata"].iteritems():
                    meta.append("%s=%s" % (k, v))

            dataset["meta"] = ",".join(meta)

            if dataset["primary"] in nodes_map:
                primary = nodes_map[dataset["primary"]]
                node = dict(uuid=primary["uuid"], host=primary["host"])
            else:
                node = None

            dataset["node"] = node

            dataset["short_dataset_id"] = dataset["dataset_id"][:8]

            if dataset.get("maximum_size"):
                size = "%.2fG" % (dataset["maximum_size"]
                        / (1024 * 1024 * 1024.),)
            else:
                # must be a backend with quotas instead of sizes
                size = "<no quota>"

            dataset["size"] = size
            objects.append(dataset)
        return objects
    d.addCallback(got_results)
    return d

def get_client(reactor=reactor, certificates_path=FilePath("/etc/flocker"),
        user_certificate_filename="plugin.crt", user_key_filename="plugin.key",
        cluster_certificate_filename="cluster.crt", target_hostname=None):
    """
    Create a ``treq``-API object that implements the REST API TLS
    authentication.

    That is, validating the control service as well as presenting a
    certificate to the control service for authentication.

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

        class ContextFactory(object):
            def getContext(self, hostname, port):
                context = client_certificate.options(authority).getContext()
                return context

        return HTTPClient(Agent(reactor, contextFactory=ContextFactory()))
    else:
        raise Exception("Not enough information to construct TLS context: "
                "user_crt: %s, cluster_crt: %s, user_key: %s, target_hostname: %s" % (
                    user_crt, cluster_crt, user_key, target_hostname))
