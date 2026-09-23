import json
import os

from dotenv import load_dotenv
from openai import OpenAI


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


load_dotenv(ENV_FILE)

API_KEY = os.getenv("OPENAI_API_KEY")


def is_llm_configured():

    return (
        API_KEY is not None
        and API_KEY.strip() != ""
        and API_KEY != "YOUR_API_KEY_HERE"
    )


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


def build_rca_prompt(evidence):

    return f"""
You are a Senior Performance Engineer.

Analyze the following performance evidence obtained through MCP.

MCP PERFORMANCE EVIDENCE
========================

{json.dumps(evidence, indent=2)}

RCA INSTRUCTIONS
================

1. Identify passed and failed SLA requirements.
2. Explain the observed performance behavior.
3. Do NOT invent infrastructure, application, database,
   or APM metrics.
4. Do NOT declare a root cause without supporting evidence.
5. Identify possible causes as hypotheses only.
6. Identify additional telemetry required.
7. Recommend the next investigation steps.
8. Clearly separate:
   - Facts
   - Hypotheses
   - Required Evidence
   - Recommended Actions

Return the analysis in a structured format.
"""


def generate_ai_rca(prompt):

    client = OpenAI(
        api_key=API_KEY
    )

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":

    print("====================================")
    print(" AI Performance LLM Client")
    print("====================================")

    print()
    print(
        f"MCP Evidence: {MCP_EVIDENCE_FILE}"
    )
    print()

    evidence = load_mcp_evidence()

    print("MCP evidence loaded successfully.")
    print()

    prompt = build_rca_prompt(evidence)

    print("RCA prompt built successfully.")
    print()

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

        print("MCP-based RCA prompt saved.")
        print()
        print(f"Output: {prompt_file}")

    else:

        print("LLM Status : CONFIGURED")
        print()
        print("Sending MCP evidence to LLM...")

        result = generate_ai_rca(prompt)

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(result)

        print()
        print("AI RCA generated successfully.")
        print()
        print(f"Output: {OUTPUT_FILE}")