from collections import Counter
import math

def data_analyzer(numbers):
    if not numbers:
        return "No data provided."
    
    numbers = sorted(numbers)
    n = len(numbers)
    total = sum(numbers)
    mean = total / n
    median = numbers[n // 2] if n % 2 != 0 else (numbers[n // 2 - 1] + numbers[n // 2]) / 2
    counts = Counter(numbers)
    mode = counts.most_common(1)[0][0]
    minimum = min(numbers)
    maximum = max(numbers)
    data_range = maximum - minimum

    # Variance and standard deviation
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = math.sqrt(variance)

    # Percentiles
    def percentile(p):
        k = (n - 1) * (p / 100)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return numbers[int(k)]
        d0 = numbers[f] * (c - k)
        d1 = numbers[c] * (k - f)
        return d0 + d1

    p25 = percentile(25)
    p50 = median
    p75 = percentile(75)

    # Horizontal histogram (scaled)
    max_count = max(counts.values())
    scale_factor = 40 / max_count  # max width 40 chars
    histogram_lines = []
    for num in sorted(counts):
        bar = '█' * int(counts[num] * scale_factor)
        histogram_lines.append(f"{num:>3} | {bar} ({counts[num]})")
    histogram = "\n".join(histogram_lines)

    # Build analysis string
    analysis_str = f"numbers: {numbers}\n\n"  # show numbers first
    analysis_str += f"count: {n}\n"
    analysis_str += f"sum: {total}\n"
    analysis_str += f"min: {minimum}\n"
    analysis_str += f"max: {maximum}\n"
    analysis_str += f"range: {data_range}\n"
    analysis_str += f"mean: {mean}\n"
    analysis_str += f"median: {median}\n"
    analysis_str += f"mode: {mode}\n"
    analysis_str += f"variance: {variance}\n"
    analysis_str += f"std_dev: {std_dev}\n"
    analysis_str += f"25th percentile: {p25}\n"
    analysis_str += f"50th percentile: {p50}\n"
    analysis_str += f"75th percentile: {p75}\n"
    analysis_str += f"histogram:\n{histogram}"

    return analysis_str

if __name__ == "__main__":
    data = [5, 3, 8, 3, 9, 5, 1, 3]
    print(data_analyzer(data))
