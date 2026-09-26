import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AI_ENGINE_DIR = os.path.join(
    BASE_DIR,
    "ai-engine"
)

MCP_EVIDENCE_FILE = os.path.join(
    AI_ENGINE_DIR,
    "mcp_rca_evidence.json"
)

OUTPUT_FILE = os.path.join(
    AI_ENGINE_DIR,
    "ai_rca_response.txt"
)

ENV_FILE = os.path.join(
    AI_ENGINE_DIR,
    ".env"
)


# ============================================================
# Environment
# ============================================================

load_dotenv(ENV_FILE)

API_KEY = os.getenv("OPENAI_API_KEY")


def is_llm_configured():

    return (
        API_KEY is not None
        and API_KEY.strip() != ""
        and API_KEY != "YOUR_API_KEY_HERE"
    )


# ============================================================
# Load MCP Evidence
# ============================================================

def load_mcp_evidence():

    if not os.path.exists(MCP_EVIDENCE_FILE):

        raise FileNotFoundError(
            f"MCP evidence not found: {MCP_EVIDENCE_FILE}"
        )

    with open(
        MCP_EVIDENCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# Build AI RCA Prompt
# ============================================================

def build_rca_prompt(evidence):

    return f"""
You are a Senior Performance Engineer
performing evidence-based performance analysis.

The following evidence was collected through an MCP
(Model Context Protocol) server.

Your responsibility is to correlate application performance,
SLA results, transaction behavior, failures, and Kubernetes
infrastructure metrics.

Do NOT invent metrics.

Do NOT assume a bottleneck without supporting evidence.

============================================================
MCP PERFORMANCE EVIDENCE
============================================================

{json.dumps(evidence, indent=2)}


============================================================
PERFORMANCE RCA ANALYSIS
============================================================

Analyze the evidence using the following sequence:

Requirement
    ->
Baseline
    ->
Workload
    ->
Performance Metrics
    ->
Transaction Analysis
    ->
Infrastructure Correlation
    ->
Bottleneck Analysis
    ->
Root Cause Hypotheses
    ->
Additional Evidence
    ->
Remediation
    ->
Retest
    ->
Validation


============================================================
1. SLA ANALYSIS
============================================================

Identify:

- Required P95
- Actual P95
- Required TPS
- Actual TPS
- Allowed error rate
- Actual error rate

Clearly identify:

- SLA PASS
- SLA FAIL


============================================================
2. PERFORMANCE ANALYSIS
============================================================

Analyze:

- Average response time
- P90
- P95
- P99
- Maximum response time
- TPS
- Error rate


============================================================
3. TRANSACTION ANALYSIS
============================================================

For each transaction:

- Total requests
- Successful requests
- Failed requests
- Average response time
- P95
- P99
- Maximum response time
- TPS
- Error rate

Identify transactions that require further investigation.

Do not call a transaction a bottleneck solely because
it has the highest response time.


============================================================
4. FAILURE ANALYSIS
============================================================

Analyze:

- Failed transactions
- HTTP response codes
- Error rate
- Any sampler-specific failures

If there are no failures, explicitly state that.


============================================================
5. KUBERNETES INFRASTRUCTURE ANALYSIS
============================================================

Analyze the Kubernetes evidence separately.

Consider:

- Node CPU utilization
- Node memory utilization
- Application pod CPU
- Application pod memory
- Number of application pods
- Whether resource saturation is visible

Important:

Low CPU or memory utilization does NOT automatically prove
that infrastructure is healthy.

High CPU or memory utilization does NOT automatically prove
that infrastructure is the root cause.

Correlate infrastructure metrics with performance symptoms.


============================================================
6. BOTTLENECK ANALYSIS
============================================================

Determine whether the available evidence confirms a bottleneck.

Possible areas include:

- Application
- Kubernetes infrastructure
- Database
- Network
- External dependency
- Load generator
- Test configuration
- Workload model

Do not declare a confirmed bottleneck unless the evidence
supports it.

If evidence is insufficient, explicitly state:

"NO CONFIRMED BOTTLENECK FROM AVAILABLE EVIDENCE."


============================================================
7. ROOT CAUSE ANALYSIS
============================================================

Separate the findings into:

FACTS

HYPOTHESES

REQUIRED EVIDENCE

RECOMMENDED INVESTIGATION


For every hypothesis, explain why it is being considered
and what telemetry would confirm or reject it.


============================================================
8. ADDITIONAL TELEMETRY
============================================================

Identify additional evidence that would be useful, such as:

- Application CPU
- Application memory
- JVM heap
- Garbage collection
- Thread pools
- Database CPU
- Database wait time
- Database connection pool
- Network latency
- External service latency
- Kubernetes pod restarts
- Kubernetes resource throttling
- Application logs
- Distributed traces
- Dynatrace PurePath
- AppDynamics transaction snapshots


============================================================
9. REMEDIATION
============================================================

Recommend actions only when supported by the evidence.

Do not recommend scaling, code changes, database tuning,
or infrastructure changes without explaining the evidence
that would justify the action.


============================================================
10. RETEST STRATEGY
============================================================

Define:

- Workload to rerun
- Duration
- Success criteria
- Metrics to compare
- Infrastructure metrics to monitor
- Application/APM metrics to monitor


============================================================
11. FINAL ENGINEERING CONCLUSION
============================================================

Provide a concise conclusion containing:

- SLA status
- Performance behavior
- Infrastructure observation
- Confirmed bottleneck status
- Root cause status
- Next investigation step


============================================================
IMPORTANT ENGINEERING RULES
============================================================

1. Correlate multiple evidence sources.

2. Do not rely on a single metric.

3. Do not confuse an observation with a root cause.

4. Do not invent missing metrics.

5. Clearly distinguish facts from hypotheses.

6. If the evidence is insufficient, say so.

7. Validate remediation through controlled retesting.

Return the analysis in a structured format suitable for a
Senior Performance Engineer review.
"""


# ============================================================
# Generate AI RCA
# ============================================================

def generate_ai_rca(prompt):

    client = OpenAI(
        api_key=API_KEY
    )

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return response.output_text


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("====================================")
    print(" AI Performance LLM Client")
    print("====================================")
    print()

    print(
        f"MCP Evidence: {MCP_EVIDENCE_FILE}"
    )
    print()

    # --------------------------------------------------------
    # Load MCP evidence
    # --------------------------------------------------------

    evidence = load_mcp_evidence()

    print("MCP evidence loaded successfully.")
    print()

    # --------------------------------------------------------
    # Check Kubernetes evidence
    # --------------------------------------------------------

    kubernetes_metrics = (
        evidence
        .get("evidence", {})
        .get("kubernetes_metrics")
    )

    if kubernetes_metrics:

        print(
            "Kubernetes evidence detected in MCP data."
        )

    else:

        print(
            "WARNING: Kubernetes evidence not found."
        )

    print()

    # --------------------------------------------------------
    # Build RCA prompt
    # --------------------------------------------------------

    prompt = build_rca_prompt(evidence)

    print("RCA prompt built successfully.")
    print()

    # --------------------------------------------------------
    # Check LLM configuration
    # --------------------------------------------------------

    if not is_llm_configured():

        print("LLM Status : NOT CONFIGURED")
        print()
        print("OPENAI_API_KEY is not configured.")
        print("Skipping external LLM call.")
        print()

        prompt_file = os.path.join(
            AI_ENGINE_DIR,
            "ai_rca_prompt_from_mcp.txt"
        )

        with open(
            prompt_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(prompt)

        print(
            "MCP-based RCA prompt saved."
        )
        print()

        print(
            f"Output: {prompt_file}"
        )

    else:

        print("LLM Status : CONFIGURED")
        print()
        print(
            "Sending MCP evidence to LLM..."
        )

        result = generate_ai_rca(prompt)

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(result)

        print()
        print(
            "AI RCA generated successfully."
        )
        print()

        print(
            f"Output: {OUTPUT_FILE}"
        )