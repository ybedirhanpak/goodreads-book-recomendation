from typing import List


def evaluate_precision(original_list: List, calculated_list: List):
    precision = len(
        [book_url for book_url in calculated_list if book_url in original_list]) / len(original_list)

    average_precision = 0
    relevant_count = 0
    precision_list = []
    precision_sum = 0
    for index, book_url in enumerate(calculated_list):
        if book_url in original_list:
            relevant_count += 1
        precision = relevant_count / (index + 1)
        if book_url in original_list:
            precision_sum += precision
        precision_list.append(precision)

    if relevant_count > 0:
        average_precision = precision_sum / relevant_count

    return (precision, average_precision)
