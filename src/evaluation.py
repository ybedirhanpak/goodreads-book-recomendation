from typing import List


def evaluate_precision(original_list: List, calculated_list: List):
    average_precision = 0
    relevant_count = 0
    precision = 0
    precision_sum = 0
    for index, book_url in enumerate(calculated_list):
        if book_url in original_list:
            relevant_count += 1
        precision = relevant_count / (index + 1)
        if book_url in original_list:
            precision_sum += precision

    if relevant_count > 0:
        average_precision = precision_sum / relevant_count

    return (precision, average_precision)
