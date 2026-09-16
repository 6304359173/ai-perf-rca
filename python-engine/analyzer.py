import csv
import json
import os
import statistics


# ---------------------------------------
# File locations
# ---------------------------------------

JTL_FILE = r"E:\ai-perf-framework\scripts\results.jtl"
OUTPUT_FILE = r"E:\ai-perf-framework\python-engine\metrics.json"


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

    for row in rows:

        elapsed = float(row["elapsed"])

        response_times.append(elapsed)

        timestamp = int(row["timeStamp"])
        timestamps.append(timestamp)

        success = row["success"].lower() == "true"

        if success:
            successful += 1
        else:
            failed += 1


    # -----------------------------------
    # Basic metrics
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

    # For very small tests, make sure
    # duration is never zero.

    if duration_seconds <= 0:

        duration_seconds = 1


    # -----------------------------------
    # TPS
    # -----------------------------------

    tps = total / duration_seconds


    # -----------------------------------
    # Error rate
    # -----------------------------------

    error_rate = (
        failed / total
    ) * 100


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

        "test_summary": {

            "total_requests": total,

            "successful_requests": successful,

            "failed_requests": failed,

            "test_duration_seconds":
                round(duration_seconds, 2)
        },

        "performance_metrics": {

            "average_response_time_ms":
                round(average, 2),

            "min_response_time_ms":
                round(minimum, 2),

            "max_response_time_ms":
                round(maximum, 2),

            "p90_ms":
                round(p90, 2),

            "p95_ms":
                round(p95, 2),

            "p99_ms":
                round(p99, 2),

            "tps":
                round(tps, 2),

            "error_rate_percent":
                round(error_rate, 2)
        },

        "sla": {

            "required_p95_ms":
                SLA["p95_ms"],

            "required_tps":
                SLA["tps"],

            "required_error_rate_percent":
                SLA["error_rate_percent"],

            "p95_status":
                "PASS" if p95_pass else "FAIL",

            "tps_status":
                "PASS" if tps_pass else "FAIL",

            "error_rate_status":
                "PASS" if error_pass else "FAIL",

            "overall_status":
                "PASS" if overall_pass else "FAIL"
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

    print(f"Reading JTL: {JTL_FILE}")

    rows = read_jtl()

    print(f"Records found: {len(rows)}")

    metrics = analyze(rows)

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

    print()
    print(
        f"SLA Status          : "
        f"{metrics['sla']['overall_status']}"
    )

    print()
    print(f"Metrics saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()