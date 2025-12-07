from kubernetes import client, config, watch
import time

# Configura acesso ao cluster
config.load_kube_config()  # ou config.load_incluster_config() se rodar dentro do cluster
v1 = client.CoreV1Api()
scheduler_name = "my-heuristic-scheduler"

def find_best_node(pod):
    nodes = v1.list_node().items
    best_node = None
    max_cpu = -1

    for node in nodes:
        node_name = node.metadata.name
        status = node.status
        allocatable = status.allocatable

        cpu_str = allocatable.get("cpu")
        if cpu_str:
            cpu = int(cpu_str.replace("m", "")) if "m" in cpu_str else int(cpu_str) * 1000
            if cpu > max_cpu:
                max_cpu = cpu
                best_node = node_name

    return best_node

def bind_pod(pod, node_name):
    target = client.V1ObjectReference(kind="Node", api_version="v1", name=node_name)
    meta = client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace)
    body = client.V1Binding(target=target, metadata=meta)

    v1.create_namespaced_binding(namespace=pod.metadata.namespace, body=body)

def run_scheduler():
    print("Iniciando scheduler heurístico...")
    w = watch.Watch()
    for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=0):
        pod = event['object']
        if pod.status.phase == "Pending" and pod.spec.scheduler_name == scheduler_name:
            node = find_best_node(pod)
            if node:
                print(f"Atribuindo pod {pod.metadata.name} ao nó {node}")
                try:
                    bind_pod(pod, node)
                except Exception as e:
                    print(f"Erro ao fazer bind: {e}")

if __name__ == "__main__":
    while True:
        try:
            run_scheduler()
        except Exception as e:
            print(f"Erro: {e}")
        time.sleep(1)
