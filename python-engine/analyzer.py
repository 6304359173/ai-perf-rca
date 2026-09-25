import csv
import json
import os
import statistics


# ---------------------------------------
# File locations
# ---------------------------------------

WORKSPACE = os.environ.get(
    "WORKSPACE",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

JTL_FILE = os.path.join(WORKSPACE, "scripts", "results.jtl")
OUTPUT_FILE = os.path.join(WORKSPACE, "python-engine", "metrics.json")


# ---------------------------------------
# SLA Configuration
# ---------------------------------------

SLA = {
    "p95_ms": 2000,
    "tps": 100,
    "error_rate_percent": 1
}


# ---------------------------------------
# Percentile calculation
# ---------------------------------------

def percentile(values, percentile):

    if not values:
        return 0

    values = sorted(values)

    index = (len(values) - 1) * percentile / 100

    lower = int(index)
    upper = lower + 1

    if upper >= len(values):
        return values[lower]

    weight = index - lower

    return values[lower] + (
        values[upper] - values[lower]
    ) * weight


# ---------------------------------------
# Read JMeter JTL
# ---------------------------------------

def read_jtl():

    if not os.path.exists(JTL_FILE):

        raise FileNotFoundError(
            f"JTL file not found: {JTL_FILE}"
        )

    rows = []

    with open(
        JTL_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


# ---------------------------------------
# Analyze performance results
# ---------------------------------------

def analyze(rows):

    if not rows:

        raise ValueError(
            "JTL file contains no results."
        )

    response_times = []

    successful = 0
    failed = 0

    timestamps = []

    # -----------------------------------
    # Transaction statistics
    # -----------------------------------

    transaction_stats = {}

    # -----------------------------------
    # Failure analysis
    # -----------------------------------

    response_code_stats = {}

    for row in rows:

        elapsed = float(row["elapsed"])

        response_times.append(elapsed)

        timestamp = int(row["timeStamp"])
        timestamps.append(timestamp)

        success = row["success"].lower() == "true"

        transaction = (
            row.get("label")
            or row.get("sampler")
            or "Unknown"
        )

        response_code = (
            row.get("responseCode")
            or "UNKNOWN"
        )

        # --------------------------------
        # Overall success/failure
        # --------------------------------

        if success:
            successful += 1
        else:
            failed += 1

        # --------------------------------
        # Transaction statistics
        # --------------------------------

        if transaction not in transaction_stats:

            transaction_stats[transaction] = {
                "response_times": [],
                "timestamps": [],
                "total": 0,
                "successful": 0,
                "failed": 0
            }

        transaction_stats[transaction]["response_times"].append(
            elapsed
        )

        transaction_stats[transaction]["timestamps"].append(
            timestamp
        )

        transaction_stats[transaction]["total"] += 1

        if success:
            transaction_stats[transaction]["successful"] += 1
        else:
            transaction_stats[transaction]["failed"] += 1

        # --------------------------------
        # Response-code statistics
        # --------------------------------

        if response_code not in response_code_stats:

            response_code_stats[response_code] = {
                "total": 0,
                "successful": 0,
                "failed": 0
            }

        response_code_stats[response_code]["total"] += 1

        if success:
            response_code_stats[response_code]["successful"] += 1
        else:
            response_code_stats[response_code]["failed"] += 1

    # -----------------------------------
    # Basic overall metrics
    # -----------------------------------

    total = len(rows)

    average = statistics.mean(response_times)

    minimum = min(response_times)

    maximum = max(response_times)

    p90 = percentile(response_times, 90)

    p95 = percentile(response_times, 95)

    p99 = percentile(response_times, 99)

    # -----------------------------------
    # Test duration
    # -----------------------------------

    start_time = min(timestamps)

    end_time = max(timestamps)

    duration_seconds = (
        (end_time - start_time) / 1000
    )

    if duration_seconds <= 0:
        duration_seconds = 1

    # -----------------------------------
    # Overall TPS
    # -----------------------------------

    tps = total / duration_seconds

    # -----------------------------------
    # Overall error rate
    # -----------------------------------

    error_rate = (
        failed / total
    ) * 100

    # -----------------------------------
    # Build transaction summary
    # -----------------------------------

    transaction_summary = {}

    for transaction, stats in transaction_stats.items():

        times = stats["response_times"]

        transaction_start = min(
            stats["timestamps"]
        )

        transaction_end = max(
            stats["timestamps"]
        )

        transaction_duration = (
            transaction_end - transaction_start
        ) / 1000

        if transaction_duration <= 0:
            transaction_duration = 1

        transaction_tps = (
            stats["total"]
            / transaction_duration
        )

        transaction_error_rate = (
            stats["failed"]
            / stats["total"]
        ) * 100

        transaction_summary[transaction] = {

            "total": stats["total"],

            "successful": stats["successful"],

            "failed": stats["failed"],

            "error_rate_percent":
                round(
                    transaction_error_rate,
                    2
                ),

            "average_response_time_ms":
                round(
                    statistics.mean(times),
                    2
                ),

            "min_response_time_ms":
                round(
                    min(times),
                    2
                ),

            "max_response_time_ms":
                round(
                    max(times),
                    2
                ),

            "p90_ms":
                round(
                    percentile(times, 90),
                    2
                ),

            "p95_ms":
                round(
                    percentile(times, 95),
                    2
                ),

            "p99_ms":
                round(
                    percentile(times, 99),
                    2
                ),

            "tps":
                round(
                    transaction_tps,
                    2
                )
        }

    # -----------------------------------
    # Calculate response-code error rates
    # -----------------------------------

    for code, stats in response_code_stats.items():

        stats["error_rate_percent"] = round(
            (
                stats["failed"]
                / stats["total"]
            ) * 100,
            2
        )

    # -----------------------------------
    # SLA validation
    # -----------------------------------

    p95_pass = (
        p95 < SLA["p95_ms"]
    )

    tps_pass = (
        tps >= SLA["tps"]
    )

    error_pass = (
        error_rate < SLA["error_rate_percent"]
    )

    overall_pass = (
        p95_pass
        and tps_pass
        and error_pass
    )

    # -----------------------------------
    # Final result
    # -----------------------------------

    metrics = {

        # --------------------------------
        # Overall test summary
        # --------------------------------

        "test_summary": {

            "total_requests": total,

            "successful_requests": successful,

            "failed_requests": failed,

            "test_duration_seconds":
                round(
                    duration_seconds,
                    2
                )
        },

        # --------------------------------
        # Overall performance metrics
        # --------------------------------

        "performance_metrics": {

            "average_response_time_ms":
                round(
                    average,
                    2
                ),

            "min_response_time_ms":
                round(
                    minimum,
                    2
                ),

            "max_response_time_ms":
                round(
                    maximum,
                    2
                ),

            "p90_ms":
                round(
                    p90,
                    2
                ),

            "p95_ms":
                round(
                    p95,
                    2
                ),

            "p99_ms":
                round(
                    p99,
                    2
                ),

            "tps":
                round(
                    tps,
                    2
                ),

            "error_rate_percent":
                round(
                    error_rate,
                    2
                )
        },

        # --------------------------------
        # NEW: Transaction Summary
        # --------------------------------

        "transaction_summary":
            transaction_summary,

        # --------------------------------
        # Failure Analysis
        # --------------------------------

        "failure_analysis": {

            "by_sampler":
                transaction_summary,

            "by_response_code":
                response_code_stats
        },

        # --------------------------------
        # SLA
        # --------------------------------

        "sla": {

            "required_p95_ms":
                SLA["p95_ms"],

            "required_tps":
                SLA["tps"],

            "required_error_rate_percent":
                SLA["error_rate_percent"],

            "p95_status":
                "PASS"
                if p95_pass
                else "FAIL",

            "tps_status":
                "PASS"
                if tps_pass
                else "FAIL",

            "error_rate_status":
                "PASS"
                if error_pass
                else "FAIL",

            "overall_status":
                "PASS"
                if overall_pass
                else "FAIL"
        }
    }

    return metrics


# ---------------------------------------
# Main
# ---------------------------------------

def main():

    print("====================================")
    print(" AI Performance JTL Analyzer")
    print("====================================")

    print(
        f"Reading JTL: {JTL_FILE}"
    )

    rows = read_jtl()

    print(
        f"Records found: {len(rows)}"
    )

    metrics = analyze(rows)

    # -----------------------------------
    # Save JSON
    # -----------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4
        )

    # -----------------------------------
    # Overall Performance
    # -----------------------------------

    print()
    print("Performance Analysis")
    print("------------------------------------")

    print(
        f"Total Requests      : "
        f"{metrics['test_summary']['total_requests']}"
    )

    print(
        f"Successful Requests : "
        f"{metrics['test_summary']['successful_requests']}"
    )

    print(
        f"Failed Requests     : "
        f"{metrics['test_summary']['failed_requests']}"
    )

    print(
        f"Average Response    : "
        f"{metrics['performance_metrics']['average_response_time_ms']} ms"
    )

    print(
        f"P95                 : "
        f"{metrics['performance_metrics']['p95_ms']} ms"
    )

    print(
        f"P99                 : "
        f"{metrics['performance_metrics']['p99_ms']} ms"
    )

    print(
        f"TPS                 : "
        f"{metrics['performance_metrics']['tps']}"
    )

    print(
        f"Error Rate          : "
        f"{metrics['performance_metrics']['error_rate_percent']}%"
    )

    # -----------------------------------
    # Transaction Summary
    # -----------------------------------

    print()
    print("Transaction Summary")
    print("------------------------------------")

    print(
        f"{'Transaction':<22}"
        f"{'Total':>8}"
        f"{'Success':>10}"
        f"{'Failed':>9}"
        f"{'Error %':>10}"
    )

    print("-" * 59)

    for transaction, stats in (
        metrics["transaction_summary"].items()
    ):

        print(
            f"{transaction:<22}"
            f"{stats['total']:>8}"
            f"{stats['successful']:>10}"
            f"{stats['failed']:>9}"
            f"{stats['error_rate_percent']:>10.2f}"
        )

    print("-" * 59)

    print(
        f"{'TOTAL':<22}"
        f"{metrics['test_summary']['total_requests']:>8}"
        f"{metrics['test_summary']['successful_requests']:>10}"
        f"{metrics['test_summary']['failed_requests']:>9}"
        f"{metrics['performance_metrics']['error_rate_percent']:>10.2f}"
    )

    # -----------------------------------
    # SLA
    # -----------------------------------

    print()
    print(
        f"SLA Status          : "
        f"{metrics['sla']['overall_status']}"
    )

    print()
    print(
        f"Metrics saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()