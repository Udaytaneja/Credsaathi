"""Text accuracy metrics: Character Error Rate (CER), Field Extraction Accuracy, and Confidence Calibration (ECE)."""
from typing import Any, Dict, List


def calculate_character_error_rate(reference: str, hypothesis: str) -> float:
    """Calculates Character Error Rate (CER) using Levenshtein distance."""
    if not reference:
        return 0.0 if not hypothesis else 1.0

    ref, hyp = reference.lower(), hypothesis.lower()
    r_len, h_len = len(ref), len(hyp)

    dp = [[0] * (h_len + 1) for _ in range(r_len + 1)]
    for i in range(r_len + 1):
        dp[i][0] = i
    for j in range(h_len + 1):
        dp[0][j] = j

    for i in range(1, r_len + 1):
        for j in range(1, h_len + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    edit_distance = dp[r_len][h_len]
    return round(edit_distance / max(r_len, 1), 4)


def calculate_field_extraction_accuracy(extracted: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
    """Calculates field extraction accuracy ratio between extracted dictionary and ground truth."""
    if not ground_truth:
        return 1.0 if not extracted else 0.0

    matches = 0
    for key, expected_val in ground_truth.items():
        actual_val = extracted.get(key)
        if str(actual_val).strip().lower() == str(expected_val).strip().lower():
            matches += 1

    return round(matches / len(ground_truth), 4)


def calculate_expected_calibration_error(confidences: List[float], accuracies: List[float], num_bins: int = 5) -> float:
    """Calculates Expected Calibration Error (ECE) across confidence bins."""
    if not confidences or not accuracies or len(confidences) != len(accuracies):
        return 0.0

    n = len(confidences)
    bin_size = 1.0 / num_bins
    ece = 0.0

    for b in range(num_bins):
        bin_lower = b * bin_size
        bin_upper = (b + 1) * bin_size

        indices = [i for i, c in enumerate(confidences) if bin_lower <= c < bin_upper or (b == num_bins - 1 and c == bin_upper)]
        if not indices:
            continue

        bin_conf_avg = sum(confidences[i] for i in indices) / len(indices)
        bin_acc_avg = sum(accuracies[i] for i in indices) / len(indices)

        ece += (len(indices) / n) * abs(bin_acc_avg - bin_conf_avg)

    return round(ece, 4)
