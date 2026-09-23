import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

EVIDENCE_FILE = os.path.join(
    BASE_DIR,
    "ai-engine",
    "mcp_rca_evidence.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "ai-engine",
    "ai_rca_report.md"
)


def load_evidence():

    with open(
        EVIDENCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def generate_rca(evidence):

    data = evidence["evidence"]

    summary = data["test_summary"]
    metrics = data["performance_metrics"]
    sla = data["sla"]

    report = f"""# AI Performance RCA Report

## 1. Executive Summary

The performance test executed {summary["total_requests"]} requests.

Successful requests: {summary["successful_requests"]}

Failed requests: {summary["failed_requests"]}

Overall SLA status: **{sla["overall_status"]}**

The P95 response-time SLA passed, while the throughput SLA failed.

---

## 2. Performance Metrics

| Metric | Result |
|---|---:|
| Total Requests | {summary["total_requests"]} |
| Test Duration | {summary["test_duration_seconds"]} sec |
| Average Response Time | {metrics["average_response_time_ms"]} ms |
| P90 | {metrics["p90_ms"]} ms |
| P95 | {metrics["p95_ms"]} ms |
| P99 | {metrics["p99_ms"]} ms |
| Maximum Response Time | {metrics["max_response_time_ms"]} ms |
| TPS | {metrics["tps"]} |
| Error Rate | {metrics["error_rate_percent"]}% |

---

## 3. SLA Analysis

### P95 Response Time

Required: **{sla["required_p95_ms"]} ms**

Actual: **{metrics["p95_ms"]} ms**

Status: **{sla["p95_status"]}**

The observed P95 response time is significantly below the configured SLA threshold.

### Throughput

Required: **{sla["required_tps"]} TPS**

Actual: **{metrics["tps"]} TPS**

Status: **{sla["tps_status"]}**

The required throughput was not achieved.

### Error Rate

Required maximum: **{sla["required_error_rate_percent"]}%**

Actual: **{metrics["error_rate_percent"]}%**

Status: **{sla["error_rate_status"]}**

No application errors were observed in this test.

---

## 4. Facts

- P95 response time passed.
- Error rate passed.
- Throughput failed.
- All {summary["total_requests"]} requests were successful.
- The observed throughput was {metrics["tps"]} TPS.
- The required throughput was {sla["required_tps"]} TPS.

---

## 5. RCA Hypotheses

The current evidence is **not sufficient to declare a confirmed root cause**.

Possible areas requiring investigation include:

1. Load-generator capacity.
2. Application CPU or thread saturation.
3. Application connection-pool limitations.
4. Database connection or query limitations.
5. Network latency or throughput limitations.
6. Application-level concurrency or throttling.

These are hypotheses only and require additional telemetry.

---

## 6. Required Evidence

To determine the actual bottleneck, collect:

### Application

- CPU utilization
- Memory utilization
- JVM/Node.js process metrics
- Thread or event-loop utilization
- Connection-pool usage

### Database

- CPU utilization
- Active connections
- Query response time
- Slow queries
- Lock/wait statistics

### Infrastructure

- CPU
- Memory
- Network throughput
- Disk I/O
- Container/Kubernetes resource utilization

### APM

- Transaction response time
- Backend call duration
- Database call duration
- External service latency
- Distributed traces

---

## 7. Recommended Next Actions

1. Increase the workload gradually toward the required 100 TPS.
2. Monitor the load generator during the test.
3. Capture application and infrastructure metrics.
4. Capture APM transaction traces.
5. Capture database performance metrics.
6. Correlate response time, throughput and resource utilization.
7. Identify the component that limits throughput.
8. Apply remediation.
9. Re-run the performance test.
10. Validate the SLA again.

---

## 8. Engineering Conclusion

The test **passed response-time and error-rate requirements but failed the throughput requirement**.

The current evidence does not prove a specific bottleneck.

Additional telemetry and correlation are required before declaring the root cause.

The next performance-engineering step is therefore:

**Measure → Correlate → Identify Bottleneck → Remediate → Retest → Validate**
"""

    return report


if __name__ == "__main__":

    print("====================================")
    print(" Mock AI Performance RCA")
    print("====================================")

    evidence = load_evidence()

    print()
    print("MCP evidence loaded.")
    print()

    report = generate_rca(evidence)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    print("Mock AI RCA generated successfully.")
    print()
    print(f"Output: {OUTPUT_FILE}")