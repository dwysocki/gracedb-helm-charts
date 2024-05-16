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
### Configuration

| Name | Description | Type | Default value |
| --- |--- | --- | ----- | 
| `cert_manager.enabled`| Enable automatic creation of TLS certificates using cert-manager.io operator | boolean | true
|`cert_manager.install`| Install the cert-manager.io operator | boolean | true
| `cert_manager.issuer.name` | Name of the issuer resource to use for the TLS certificate (if no issuer is given a self-signed certificate is created) | string | -
| `cert_manager.issuer.type` | Either Issuer or ClusterIssuer | string | -
|`distributed.enabled` | Deploy a distributed version of GraceDB and PostgreSQL | boolean | false
|`sandboxed.enabled` | Deploy a sandboxed version with username/password authentication (no Shibboleth) | boolean | true
|`alerts.igwn`| Enables the IGWN-alert overseer | boolean | true
|`storageClassName` | Name of the k8s storage class to be used in PVCs | string | "standard"
|`storageClassNameRWX`| Name of the k8s storage class to be used in ReadWriteMany PVCs (only used in distributed deployments) | string | -
|`database.name`| Name of the (postgreSQL) database to be used by GraceDB | string | "gracedb"
|`database.user`| Name of the database user for GraceDB | string | "gracedb"
|`database.storageCapacity`| Storage capacity to be allocated for postgreSQL's PVC | string | "10Gi"
|`database.readReplicas`| Number of read replicas for the database (only relevant for distributed deployments) | integer | -
|`publicName`| The public FQDN of the GraceDB webserver (will also be used by the GraceDB API client when making requests) | string | "gracedb.default.svc.cluster.local"
|`sentryEnvironment`| Name of the Sentry environment | string | "generic-test"
|`supportContact`| Email of the support contact that will appear in the main page | string | "albert.einstein@ligo.org"
|`gracedb.image`| The GraceDB container image to be used | string | "containers.ligo.org/computing/gracedb/server:gracedb-2.27.0"
|`gracedb.storage.capacity`| The storage capacity to be allocated for the GraceDB data PVC | string | "10Gi"
|`gracedb.resources.cpu`| The number of CPUs to allocate for the GraceDB pod | number | 4 
|`gracedb.resources.memory`| The amount of memory to allocate for the GraceDB pod | string | "5Gi"
|`gracedb.djangoSuperuserName`| The name of the Django superuser (will be created if not already present) | string | "admin"
|`gracedb.djangoSuperuserEmail`| The email of the Django superuser | string | "albert.einstein@ligo.org"
|`gracedb.igwnAlertAuth`| Enable authenticated connections to the Hopskotch server | boolean | false
|`gracedb.igwnAlertServer`| DNS name of the Hopskotch server | string | "hopskotch"
|`gracedb.igwnAlertGroup`| Prefix for Kafka topics | string | "default"
|`gracedb.replicaCount`| The number of replicas for the GraceDB server (only relevant for distributed deployments) | integer | -
|`gracedb.pvcName`| Name of an external PVC of type RWX to be used as file storage | string | -
|`secrets.enabled`| If true k8s secrets will be created and populated using the defined chart values (do not use in production) | boolean | true
|`secrets.djangoSecretKey`| The Django secret key used by GraceDB webserver | string | "verylongstring"
|`secrets.djangoSuperuserPassword`| The password for the automatically created Django superuser | string | "mypassword"
|`secrets.dbPassword`| The password for GraceDB's postgreSQL database | string | "dbpassword"
|`secrets.igwnAlertUsername`| Username for the IGWN-alert broker (only used if gracedb.igwnAlertAuth is true) | string | -
|`secrets.igwnAlertPassword`| Password for the IGWN-alert broker (only used if gracedb.igwnAlertAuth is true) | string | - 
|`secrets.shibbolethCert`| The x509 certificate to be used for Shibboleth | string | -
|`secrets.shibbolethPKey`| The x509 private key to be used for Shibboleth | string | -
|`postgres.image`| The PostgreSQL container image to be used (for non replicated deployments) | string | "postgres:16.2"
|`postgres.resources.cpu`| The number of CPUs to allocate for the PostgreSQL pod | number | 0.5
|`postgres.resources.memory` | The amount of memory to allocate for the PostgreSQL pod | string | "1Gi"

### Subcharts
This chart depends on the following external charts:

#### Memcached
Chart: https://artifacthub.io/packages/helm/bitnami/memcached.

The applied configuration for this chart is the following:
```
memcached:
  replicaCount: 1
  resources:
    requests:
      cpu: 0.1
      memory: 100Mi
    limits:
      cpu: 0.1
      memory: 100Mi
```

#### Traefik (optional)
Chart: https://artifacthub.io/packages/helm/traefik/traefik

The applied configuration for this chart is the following:
```
traefik:
  install: true
  service:
    spec:
      clusterIP: 10.100.100.10
```

#### cert-manager (optional)
Chart: https://artifacthub.io/packages/helm/cert-manager/cert-manager.
The applied configuration for this chart is the following:
```
cert-manager:
  installCRDs: true
```

#### PostgreSQL (optional)
Chart: https://artifacthub.io/packages/helm/bitnami/postgresql

This chart is only used in the distributed deployment. We suggest to use the following configuration options and reference an existing Secret for credentials:
```
postgresql:
  architecture: replication
  auth:
    username: *database_user
    database: *database_name
    existingSecret: ""
    secretKeys:
      adminPasswordKey: ""
      userPasswordKey: ""
      replicationPasswordKey: ""
  primary:
    persistence:
      size: *database_storage_capacity
      storageClass: *storage_class
    resources:
      requests:
        cpu: 1
        memory: 1Gi
      limits:
        cpu: 1
        memory: 1Gi
  readReplicas:
    replicaCount: *database_read_replicas
    persistence:
      size: *database_storage_capacity
      storageClass: *storage_class
    resources:
      requests:
        cpu: 1
        memory: 1Gi
      limits:
        cpu: 1
        memory: 1Gi
```

## CI pipeline
This repository's CI pipeline builds and uploads the Helm charts to the the package registry whenever a new tag is created.

