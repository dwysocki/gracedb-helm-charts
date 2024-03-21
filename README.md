# GraceDB Helm Charts

This repository contains the Helm charts to deploy GraceDB and the Hopskotch server on a Kubernetes cluster. Default values of both charts allow for a sandboxed deployment on Minikube. 

The package registry of this project can be used as Helm repository:

`helm repo add --username <username> --password <token> gracedb-helm https://git.ligo.org/api/v4/projects/15655/packages/helm/stable`

Where:
- `<username>` is your _albert.einstein_ username
- `<token>` is a _read_api_ scoped personal access token


After adding the Helm repository with the command above, the two charts can be installed in the _default_ namespace in this way:

`helm install hopskotch gracedb-helm/hopskotch`

`helm install gracedb gracedb-helm/gracedb`

## Hopskotch chart
This is a simple Helm chart that deploys the Hop server as outlined in: https://github.com/scimma/scimma-server-container/blob/master/doc/QuickDemo.md.

### Configuration

| Name | Description | Default value |
| --- |--- | ----- |
| `replicaCount`| Number of replicas in the Deployment | 1
| `storageClassName` | StorageClass for persistent volume | "standard"
| `storageCapacity` | Size of the persistent volume | 1Gi
| `security` | Enable authentication | true
| `image.repository` | Image name | "scimma/server"
| `image.tag` | Image tag | "latest"
| `image.pullPolicy` | Image pull policy | "IfNotPresent"
| `service.type` | Service type | "NodePort"
| `externalIP` | Only for LoadBalancer service type | - 
| `resources` | Resource limits and requests | {}

### Topic creation
Topics are automatically created via a Kubernetes Job, which starts after the server deployment is completed.

## GraceDB chart 

## CI pipeline
This repository's CI pipeline builds and uploads the Helm charts to the the package registry whenever a new tag is created.

