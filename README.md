## powerstrip-flocker: portable volumes using just the docker cli
*or: how I learned to love running stateful docker containers and stop worrying where the data is*

![flying books to illustrate portable volumes](resources/flying_books.jpg)

(Portable "volumes", hee hee.)

## What's the problem?

When you want to run Docker in production, you want to run it across multiple machines and you probably want to use some orchestration tools.
However, when you attach a volume to a Docker container, the machine it's running on becomes [a pet when it should be cattle](http://www.theregister.co.uk/2013/03/18/servers_pets_or_cattle_cern/).

## The solution

You should be able to run a stateful container with a given volume on any host in your cluster, and the platform should handle moving data around as necessary.

## What is the flocker plugin for docker (`flocker-docker`)?

`flocker-docker` allows you to use the regular `docker` CLI commands to create or move flocker volumes, automatically moving volumes around between hosts in the cluster as-needed.

## How does it work?

`flocker-docker` connects [Docker](https://docker.com/) to the [Flocker Volumes API](http://doc-dev.clusterhq.com/advanced/api.html) via Docker volumes plugins.

## Killer demo

Write some data into a volume on one host, read it from another:

```
$ ssh node1 docker run -v demo:/data --volume-driver=flocker busybox sh -c "echo fish > /data/file"
$ ssh node2 docker run -v demo:/data --volume-driver=flocker busybox sh -c "cat /data/file"
fish
```

Note that the volume above has become "global" to both hosts.

## What this means

Finally you can run stateful containers in docker and stop worrying about where the data is.

In other words, `flocker-docker` exposes a *global namespace* of volumes which flocker will move into place just-in-time before letting docker start your containers.

## Orchestration

We are working on adding support for Docker volumes plugins to common orchestration frameworks so that this can work in concert with them.

## Composition

We are also working on assing support to composition tools.

## Is it ready yet?

This depends on an "experimental" release of the docker binary, coming soon.

If you have issues, please [get in touch](https://github.com/ClusterHQ/flocker-docker/issues/new).

## OK, how do I try it?

Install instructions coming soon!
