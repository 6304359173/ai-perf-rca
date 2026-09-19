import json
import os


# ---------------------------------------
# File locations
# ---------------------------------------



WORKSPACE = os.environ.get(
    "WORKSPACE",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

METRICS_FILE = os.path.join(
    WORKSPACE,
    "python-engine",
    "metrics.json"
)

PROMPT_FILE = os.path.join(
    WORKSPACE,
    "ai-engine",
    "rca_prompt.txt"
)

# ---------------------------------------
# Load performance metrics
# ---------------------------------------

def load_metrics():

    if not os.path.exists(METRICS_FILE):

        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_FILE}"
        )

    with open(
        METRICS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------
# Build AI RCA prompt
# ---------------------------------------

def build_prompt(metrics):

    test_summary = metrics["test_summary"]

    performance = metrics["performance_metrics"]

    sla = metrics["sla"]

    prompt = f"""
You are an AI assistant for a Senior Performance Engineer.

Analyze the following performance test evidence.

IMPORTANT RULES:

1. Compare actual results against the SLA.
2. Identify which SLAs passed or failed.
3. Do NOT declare a root cause without sufficient evidence.
4. Clearly separate facts from hypotheses.
5. If evidence is insufficient, state what additional
   telemetry is required.
6. Recommend specific investigation steps.
7. Recommend possible remediation only after identifying
   the likely problem area.
8. Recommend a controlled performance retest.

TEST SUMMARY
------------

Total Requests:
{test_summary["total_requests"]}

Successful Requests:
{test_summary["successful_requests"]}

Failed Requests:
{test_summary["failed_requests"]}

Test Duration:
{test_summary["test_duration_seconds"]} seconds


PERFORMANCE METRICS
-------------------

Average Response Time:
{performance["average_response_time_ms"]} ms

P90:
{performance["p90_ms"]} ms

P95:
{performance["p95_ms"]} ms

P99:
{performance["p99_ms"]} ms

TPS:
{performance["tps"]}

Error Rate:
{performance["error_rate_percent"]}%


SLA
---

Required P95:
{sla["required_p95_ms"]} ms

Required TPS:
{sla["required_tps"]}

Maximum Error Rate:
{sla["required_error_rate_percent"]}%


SLA STATUS
----------

P95:
{sla["p95_status"]}

TPS:
{sla["tps_status"]}

Error Rate:
{sla["error_rate_status"]}

Overall:
{sla["overall_status"]}


Please provide the analysis using this structure:

1. Executive Summary

2. SLA Assessment

3. Observed Facts

4. Possible RCA Hypotheses

5. Evidence Required to Confirm RCA

6. Recommended Investigation

7. Recommended Remediation

8. Performance Retest Strategy

9. Final Engineering Conclusion
"""

    return prompt


# ---------------------------------------
# Main
# ---------------------------------------

def main():

    print("====================================")
    print(" AI Performance RCA Engine")
    print("====================================")

    metrics = load_metrics()

    prompt = build_prompt(metrics)

    with open(
        PROMPT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(prompt.strip())

    print()
    print("Performance evidence loaded successfully.")

    print()
    print("AI RCA prompt generated.")

    print()
    print(f"Prompt saved to:")
    print(PROMPT_FILE)


if __name__ == "__main__":
    main()