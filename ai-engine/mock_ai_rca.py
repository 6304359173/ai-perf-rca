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


def status_text(status):

    if status == "PASS":
        return "PASS"

    if status == "FAIL":
        return "FAIL"

    return status


def generate_rca(evidence):

    data = evidence["evidence"]

    summary = data["test_summary"]
    metrics = data["performance_metrics"]
    sla = data["sla"]

    p95_status = status_text(sla["p95_status"])
    tps_status = status_text(sla["tps_status"])
    error_status = status_text(sla["error_rate_status"])
    overall_status = status_text(sla["overall_status"])

    total_requests = summary["total_requests"]
    successful_requests = summary["successful_requests"]
    failed_requests = summary["failed_requests"]

    p95_ms = metrics["p95_ms"]
    tps = metrics["tps"]
    error_rate = metrics["error_rate_percent"]

    # Build dynamic SLA summary

    sla_results = []

    if p95_status == "PASS":
        sla_results.append(
            f"P95 response time passed ({p95_ms} ms)."
        )
    else:
        sla_results.append(
            f"P95 response time failed ({p95_ms} ms)."
        )

    if tps_status == "PASS":
        sla_results.append(
            f"Throughput passed ({tps} TPS)."
        )
    else:
        sla_results.append(
            f"Throughput failed ({tps} TPS)."
        )

    if error_status == "PASS":
        sla_results.append(
            f"Error rate passed ({error_rate}%)."
        )
    else:
        sla_results.append(
            f"Error rate failed ({error_rate}%)."
        )

    sla_summary = " ".join(sla_results)

    # Dynamic RCA focus

    investigation_areas = []

    if error_status == "FAIL":
        investigation_areas.extend([
            "HTTP response codes and failed transactions.",
            "Application logs corresponding to failed requests.",
            "Application CPU, memory and event-loop/thread utilization.",
            "Application connection pools and concurrency limits.",
            "Database errors, connection limits and slow queries.",
            "APM traces for failed transactions."
        ])

    if p95_status == "FAIL":
        investigation_areas.extend([
            "Application response-time distribution.",
            "Backend service latency.",
            "Database query latency.",
            "External dependency latency."
        ])

    if tps_status == "FAIL":
        investigation_areas.extend([
            "Load-generator capacity.",
            "Application throughput limitations.",
            "Connection-pool saturation.",
            "Infrastructure resource limits."
        ])

    if not investigation_areas:
        investigation_areas.append(
            "Continue monitoring application, infrastructure and APM telemetry."
        )

    investigation_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(investigation_areas, 1)
    )

    # Dynamic engineering conclusion

    if overall_status == "PASS":

        conclusion = (
            "All configured performance SLAs passed. "
            "No SLA violation was identified in this test."
        )

    else:

        conclusion = (
            "The performance test failed one or more configured SLAs. "
            "The available evidence identifies the failed SLA criteria, "
            "but it does not by itself prove the underlying root cause. "
            "Additional telemetry and correlation are required."
        )

    report = f"""# AI Performance RCA Report

## 1. Executive Summary

The performance test executed **{total_requests} requests**.

Successful requests: **{successful_requests}**

Failed requests: **{failed_requests}**

Overall SLA status: **{overall_status}**

{sla_summary}

---

## 2. Performance Metrics

| Metric | Result |
|---|---:|
| Total Requests | {total_requests} |
| Successful Requests | {successful_requests} |
| Failed Requests | {failed_requests} |
| Test Duration | {summary["test_duration_seconds"]} sec |
| Average Response Time | {metrics["average_response_time_ms"]} ms |
| P90 | {metrics["p90_ms"]} ms |
| P95 | {metrics["p95_ms"]} ms |
| P99 | {metrics["p99_ms"]} ms |
| Maximum Response Time | {metrics["max_response_time_ms"]} ms |
| TPS | {tps} |
| Error Rate | {error_rate}% |

---

## 3. SLA Analysis

### P95 Response Time

Required: **{sla["required_p95_ms"]} ms**

Actual: **{p95_ms} ms**

Status: **{p95_status}**

---

### Throughput

Required: **{sla["required_tps"]} TPS**

Actual: **{tps} TPS**

Status: **{tps_status}**

---

### Error Rate

Required maximum: **{sla["required_error_rate_percent"]}%**

Actual: **{error_rate}%**

Status: **{error_status}**

---

## 4. Performance Facts

- Total requests: **{total_requests}**
- Successful requests: **{successful_requests}**
- Failed requests: **{failed_requests}**
- P95 response time: **{p95_ms} ms**
- Throughput: **{tps} TPS**
- Error rate: **{error_rate}%**
- Overall SLA status: **{overall_status}**

These are observed test results and should be treated as performance facts.

---

## 5. RCA Assessment

The current evidence is **not sufficient to declare a confirmed root cause**.

The following areas require investigation:

{investigation_text}

These are investigation areas and hypotheses only. 
They should be validated using application, infrastructure, database and APM telemetry.

---

## 6. Required Evidence

### Application

- CPU utilization
- Memory utilization
- JVM/Node.js process metrics
- Thread or event-loop utilization
- Connection-pool usage
- Application logs
- HTTP response codes

### Database

- CPU utilization
- Active connections
- Query response time
- Slow queries
- Lock/wait statistics
- Database errors

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
- Failed transaction traces

---

## 7. Recommended Next Actions

1. Identify the failed transactions from the JMeter JTL.
2. Group failures by sampler and response code.
3. Correlate failed requests with application logs.
4. Capture application and infrastructure metrics.
5. Capture APM transaction traces.
6. Capture database performance metrics.
7. Correlate errors with resource utilization and backend dependencies.
8. Identify the confirmed bottleneck or failure cause.
9. Apply remediation.
10. Re-run the performance test.
11. Validate the SLA again.

---

## 8. Engineering Conclusion

{conclusion}

The next performance-engineering step is:

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