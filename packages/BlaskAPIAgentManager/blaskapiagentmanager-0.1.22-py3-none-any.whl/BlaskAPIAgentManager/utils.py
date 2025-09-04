import os
from dotenv import load_dotenv

load_dotenv()


def get_nested_value(data, key_path):
    """
    Helper function to get a value from nested dictionary using dot notation.

    Args:
        data: Dictionary to search in
        key_path: String key path using dot notation (e.g., "ggr.mean")

    Returns:
        The value if found, None otherwise
    """
    if not isinstance(data, dict):
        return None

    if key_path in data:
        return data[key_path]

    if "." in key_path:
        parts = key_path.split(".")
        current_data = data

        for part in parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                return None

        return current_data
    else:
        return data.get(key_path)


def set_nested_value(data, key_path, value):
    """
    Helper function to set a value in nested dictionary using dot notation.

    Args:
        data: Dictionary to modify
        key_path: String key path using dot notation (e.g., "ggr.mean")
        value: Value to set
    """
    if not isinstance(data, dict):
        return

    data[key_path] = value


def has_nested_key(data, key_path):
    """
    Helper function to check if a nested key exists using dot notation.

    Args:
        data: Dictionary to search in
        key_path: String key path using dot notation (e.g., "ggr.mean")

    Returns:
        True if the key exists, False otherwise
    """
    return get_nested_value(data, key_path) is not None


def extract_country_ids(response: dict) -> dict:
    """
    Given a response dict of the form {"GET /v1/countries": {"data": [...]}},
    return a dictionary of {"country_name": id} pairs.
    """
    countries = {}
    data = response.get("GET /v1/countries", {}).get("data", [])
    for item in data:
        if "id" in item and "name" in item:
            countries[item["name"]] = item["id"]
    return countries


def filter_json_data(data, key, values):
    """
    Recursively filter JSON data to find all items where the specified key has any of the given values.
    Works at any depth in the data structure while preserving the hierarchy.
    Supports dot notation for nested key filtering (e.g., "ggr.mean").

    Args:
        data: JSON data (dict, list or primitive value)
        key: The key to search for at any depth (supports dot notation)
        values: A list of values to match against the key (items matching any value in the list will be included)

    Returns:
        Filtered data structure containing only matching items
    """
    if not isinstance(values, list):
        values = [values]

    if data is None:
        return None

    if isinstance(data, list):
        filtered_list = []
        for item in data:
            filtered_item = filter_json_data(item, key, values)
            if filtered_item is not None:
                filtered_list.append(filtered_item)
        return filtered_list if filtered_list else None

    if isinstance(data, dict):
        key_value = get_nested_value(data, key)
        # Type-insensitive comparison
        if key_value is not None and any(str(key_value) == str(v) for v in values):
            return data

        filtered_dict = {}
        has_matches = False

        for k, v in data.items():
            filtered_value = filter_json_data(v, key, values)
            if filtered_value is not None:
                filtered_dict[k] = filtered_value
                has_matches = True

        return filtered_dict if has_matches else None

    return None


def extract_json_data(data, keys):
    """
    Recursively extract specified keys from JSON data and return a new JSON structure
    containing only the requested keys. Handles nested keys using dot notation.

    Args:
        data: JSON data (dict, list or primitive value)
        keys: List of keys to extract (can use dot notation for nested keys, e.g., "parent.child")

    Returns:
        New JSON structure containing only the requested keys
    """
    if data is None:
        return None

    if isinstance(data, list):
        result = []
        for item in data:
            extracted = extract_json_data(item, keys)
            if extracted is not None:
                result.append(extracted)
        return result if result else None

    if isinstance(data, dict):
        result = {}

        for key_path in keys:
            parts = key_path.split(".")
            current_container = data
            temp_ptr = current_container
            path_valid = True

            for i, part_key in enumerate(parts):
                if i == len(parts) - 1:
                    if isinstance(temp_ptr, dict) and part_key in temp_ptr:
                        result[key_path] = temp_ptr[part_key]
                        path_valid = True
                    elif isinstance(temp_ptr, list):
                        extracted_list_values = []
                        all_items_in_list_processed = True
                        if not temp_ptr:
                            result[key_path] = []
                            path_valid = True
                            break

                        for item_in_list in temp_ptr:
                            if (
                                isinstance(item_in_list, dict)
                                and part_key in item_in_list
                            ):
                                extracted_list_values.append(item_in_list[part_key])
                            else:
                                all_items_in_list_processed = False
                                break
                        if all_items_in_list_processed:
                            result[key_path] = extracted_list_values
                            path_valid = True
                        else:
                            path_valid = False
                    else:
                        path_valid = False
                else:
                    if isinstance(temp_ptr, dict) and part_key in temp_ptr:
                        temp_ptr = temp_ptr[part_key]
                    else:
                        path_valid = False
                        break

                if not path_valid:
                    break

        for k, v in data.items():
            if isinstance(v, (dict, list)):
                is_prefix_of_extracted = False
                for extracted_key in result.keys():
                    if extracted_key.startswith(k + "."):
                        is_prefix_of_extracted = True
                        break

                if k not in result and not is_prefix_of_extracted:
                    extracted_recursive = extract_json_data(v, keys)
                    if extracted_recursive is not None and extracted_recursive != {}:
                        result[k] = extracted_recursive

        return result if result else None

    return None


def sort_slice_json_data(data, key, limit=0, order="ASC"):
    """
    Recursively sort JSON data by a specified key at any depth and optionally slice the results.
    Works at any depth in the data structure while preserving the hierarchy.
    Supports dot notation for nested key sorting (e.g., "ggr.mean").

    Args:
        data: JSON data (dict, list or primitive value)
        key: The key to sort by (supports dot notation for nested keys)
        limit: Maximum number of items to return after sorting (0 means no limit)
        order: Sort order, either 'ASC' (ascending) or 'DESC' (descending)

    Returns:
        Sorted (and optionally sliced) data structure
    """
    if data is None:
        return None

    if isinstance(data, list):
        sortable_items = []
        unsortable_items = []

        for item in data:
            processed_item = sort_slice_json_data(item, key, limit, order)

            if processed_item is not None:
                if isinstance(processed_item, dict) and has_nested_key(
                    processed_item, key
                ):
                    sortable_items.append(processed_item)
                else:
                    unsortable_items.append(processed_item)

        reverse_sort = order.upper() == "DESC"
        sorted_items = sorted(
            sortable_items, key=lambda x: get_nested_value(x, key), reverse=reverse_sort
        )

        if limit > 0 and sorted_items:
            sorted_items = sorted_items[:limit]

        result = sorted_items + unsortable_items
        return result if result else None

    if isinstance(data, dict):
        result_dict = {}
        for k, v in data.items():
            processed_value = sort_slice_json_data(v, key, limit, order)
            if processed_value is not None:
                result_dict[k] = processed_value

        return result_dict if result_dict else None

    return data


def calculate_statistics(data, keys, operations):
    """
    Recursively process JSON data to calculate statistics for specified keys using specified operations.
    Works at any depth in the data structure while preserving the hierarchy.
    Supports dot notation for nested key statistics (e.g., "ggr.mean").

    Args:
        data: JSON data (dict, list or primitive value)
        keys: List of keys to calculate statistics for (supports dot notation)
        operations: List of operations to perform ["sum", "min", "max", "avg", "delta"]

    Returns:
        Processed data structure with calculated statistics
    """
    if data is None:
        return None

    if isinstance(data, list):
        return [calculate_statistics(item, keys, operations) for item in data]

    if isinstance(data, dict):
        processed_dict = data.copy()

        for key_path_for_stat in keys:
            value_for_stat = get_nested_value(data, key_path_for_stat)

            # Handle both list values and single numeric values
            if isinstance(value_for_stat, list):
                numeric_values = [
                    x for x in value_for_stat if isinstance(x, (int, float))
                ]
            elif isinstance(value_for_stat, (int, float)):
                # If it's a single numeric value, treat it as a list with one element
                numeric_values = [value_for_stat]
            else:
                # Skip non-numeric values
                continue

            if not numeric_values:
                continue

            for op in operations:
                stat_result_key = f"{key_path_for_stat}.{op}"
                stat_value = None
                if op == "sum":
                    stat_value = sum(numeric_values)
                elif op == "avg":
                    if numeric_values:
                        stat_value = sum(numeric_values) / len(numeric_values)
                elif op == "min":
                    stat_value = min(numeric_values)
                elif op == "max":
                    stat_value = max(numeric_values)

                if stat_value is not None:
                    set_nested_value(processed_dict, stat_result_key, stat_value)

        for k, v_original in data.items():
            is_phase1_processed_list = False
            if (
                k in keys
                and isinstance(v_original, list)
                and all(
                    isinstance(x, (int, float)) for x in v_original if x is not None
                )
            ):
                is_phase1_processed_list = True

            if isinstance(v_original, dict):
                processed_dict[k] = calculate_statistics(v_original, keys, operations)
            elif isinstance(v_original, list) and not is_phase1_processed_list:
                processed_dict[k] = calculate_statistics(v_original, keys, operations)

        return processed_dict

    return data
