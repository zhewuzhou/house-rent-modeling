from diagrams import Cluster, Diagram
from diagrams.elastic.elasticsearch import Elasticsearch, Kibana
from diagrams.k8s.compute import ReplicaSet
from diagrams.k8s.network import Service
from diagrams.onprem.database import PostgreSQL, Mongodb
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.logging import Fluentd
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx

with Diagram("RenNiXing Travel System Web Services", show=False):
    ingress = Nginx("ingress")

    metrics = Prometheus("metric")
    metrics << Grafana("monitoring")

    with Cluster("K8s cluster"):
        with Cluster("SVCs on k8s"):
            k8s_services = [
                Service("Flights Booking SVC"),
                Service("Hotel Booking SVC"),
                Service("Train Ticket Booking SVC"),
                Service("Settlement SVC"),
                Service("Stamp SVC")]

        with Cluster("Replicated pods on k8s"):
            replica_pods = [
                ReplicaSet("Flights Booking Pods"),
                ReplicaSet("Hotel Booking Pods"),
                ReplicaSet("Train Ticket Booking Pods"),
                ReplicaSet("Settlement Pods"),
                ReplicaSet("Stamp Pods")]

    for i in range(len(k8s_services)):
        k8s_services[i] >> replica_pods[i]
        replica_pods[i] << metrics

    with Cluster("Event Stream"):
        master = Redis("topics")
        master - Redis("replica") << metrics
        replica_pods >> master

    with Cluster("HA Cache"):
        master = Redis("Main Cache")
        master - Redis("Replica Cache") << metrics
        replica_pods >> master

    with Cluster("Database HA"):
        master = PostgreSQL("users")
        master - PostgreSQL("slave") << metrics
        replica_pods >> master

    with Cluster("Document Database HA"):
        master = Mongodb("users")
        master - Mongodb("slave") << metrics
        replica_pods >> master

    aggregator = Fluentd("logging")
    aggregator >> Elasticsearch("Inverted indexing") >> Kibana("data viz")

    ingress >> k8s_services
    replica_pods >> aggregator
