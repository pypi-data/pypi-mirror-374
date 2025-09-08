speed = [86,87,88,86,87,85,86]

def mean(data: list):
    return sum(data) / len(data)

def median(data: list):
    if len(data) % 2 == 0:
        return (sorted(data)[len(data) // 2 - 1] + sorted(data)[len(data) // 2]) / 2
    else:
        return sorted(data)[len(data) // 2]

def mode(data: list):
    frequency = {}
    for item in data:
        if item in frequency:
            frequency[item] += 1
        else:
            frequency[item] = 1
    most_frequent = max(frequency, key=frequency.get)
    return most_frequent

def standard_deviation(data: list):
    mean_value = mean(data)
    variance = sum((x - mean_value) ** 2 for x in data) / len(data)
    return variance ** 0.5

x = mode(speed)

print(x)