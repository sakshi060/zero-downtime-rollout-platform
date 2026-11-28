import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request


def query_prometheus(base_url, promql):
    url = f"{base_url}/api/v1/query?" + urllib.parse.urlencode({"query": promql})
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.load(resp)
    results = data["data"]["result"]
    if not results:
        return None
    return float(results[0]["value"][1])


def error_rate(base_url, namespace, service):
    selector = f'namespace="{namespace}",service="{service}"'
    promql = (
        f'sum(rate(http_requests_total{{{selector},path!~"/health|/ready|/metrics",status=~"5.."}}[1m]))'
        f' / sum(rate(http_requests_total{{{selector},path!~"/health|/ready|/metrics"}}[1m]))'
    )
    value = query_prometheus(base_url, promql)
    if value is None or value != value:
        return 0.0
    return value


def rollback(namespace, deployment):
    print(f"ROLLBACK: kubectl rollout undo deployment/{deployment} -n {namespace}")
    subprocess.run(
        ["kubectl", "rollout", "undo", f"deployment/{deployment}", "-n", namespace],
        check=True,
    )


def main():
    p = argparse.ArgumentParser(description="Watch a release and roll back if the error-rate SLO is broken")
    p.add_argument("--prometheus", default="http://localhost:9090")
    p.add_argument("--namespace", default="app")
    p.add_argument("--deployment", default="orders-api")
    p.add_argument("--service", default="orders-api")
    p.add_argument("--slo", type=float, default=0.01, help="max allowed error rate, 0.01 = 1%%")
    p.add_argument("--watch", type=int, default=180, help="seconds to watch the release")
    p.add_argument("--interval", type=int, default=15, help="seconds between checks")
    args = p.parse_args()

    deadline = time.time() + args.watch
    print(f"Watching {args.deployment} for {args.watch}s, SLO error rate <= {args.slo:.2%}")
    while time.time() < deadline:
        rate = error_rate(args.prometheus, args.namespace, args.service)
        print(f"{time.strftime('%H:%M:%S')} error rate = {rate:.2%}")
        if rate > args.slo:
            print(f"SLO BREACHED ({rate:.2%} > {args.slo:.2%})")
            start = time.time()
            rollback(args.namespace, args.deployment)
            subprocess.run(
                ["kubectl", "rollout", "status", f"deployment/{args.deployment}", "-n", args.namespace],
                check=True,
            )
            print(f"Rolled back in {time.time() - start:.0f}s")
            sys.exit(1)
        time.sleep(args.interval)
    print("Release healthy: SLO held for the whole watch window")


if __name__ == "__main__":
    main()
