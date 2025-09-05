from pyEager import parsers
import pandas as pd


def collect_damageprofiler_results(damageprofiler_json_paths):
    """Collects damageprofiler results from multiple JSON files into a dictionary with the key for each dataset being the sample_name.

    Args:
        damageprofiler_json_paths (list): A list of paths to the damageprofiler JSON files.

    Returns:
        dict: A dictionary of data frames with the key for each dataset being the sample_name.
    """
    if not isinstance(damageprofiler_json_paths, list):
        raise ValueError("Input must be a list.")

    collected_damageprofiler_results = {}

    for json_path in damageprofiler_json_paths:
        data = parsers.parse_damageprofiler_json(json_path)
        collected_damageprofiler_results[data["metadata"].loc["sample_name", "value"]] = data
    return collected_damageprofiler_results


def collect_mapdamage_results(mapdamage_result_dir_paths, standardise_colnames=False):
    """Collects results from multiple mapDamage2 result directories a dictionary with the key for each dataset being the sample_name.

    Args:
        mapdamage_result_dir_paths (list): A list of paths to the mapDamage2 result directories.

    Returns:
        dict: A dictionary of data frames with the key for each dataset being the sample_name.
    """
    if not isinstance(mapdamage_result_dir_paths, list):
        raise ValueError("Input must be a list.")

    collected_mapdamage_results = {}

    for dirpath in mapdamage_result_dir_paths:
        sample_name = dirpath.split("/")[-1].replace("results_", "")
        data = parsers.parse_mapdamage_results(dirpath, sample_name, standardise_colnames)
        collected_mapdamage_results[data["metadata"].loc["sample_name", "value"]] = data
    return collected_mapdamage_results


def compile_endogenous_table(endorspy_json_paths):
    """Compile endorspy results from multiple JSON files into a single pandas DataFrame.

    Args:
        endorspy_json_paths (list): A list of paths to the damageprofiler JSON files.

    Returns:
        pandas.DataFrame: A data frame containing the endorspy results from all the json files.
    """
    if not isinstance(endorspy_json_paths, list):
        raise ValueError("Input must be a list.")

    collected_endorspy_results = pd.DataFrame()

    for json_path in endorspy_json_paths:
        data = parsers.parse_endorspy_json(json_path)
        collected_endorspy_results = pd.concat(
            [collected_endorspy_results, data], ignore_index=True
        )

    return collected_endorspy_results


def compile_damage_table(paths):
    """Compile damage results from damageprofiler or mapdamage2 into a single pandas DataFrame.

    Args:
        paths (list): A list of paths to the damageprofiler JSON files and/or the mapDamage2 result directories.

    Returns:
        pandas.DataFrame: A data frame containing the damageprofiler results (number of reads and damage in the first two bp of each side) for each sample from all the json files.
    """
    damageprofiler_json_paths = [path for path in paths if path.endswith(".json")]
    mapdamage_result_paths = [path for path in paths if not path.endswith(".json")]
    data = collect_damageprofiler_results(damageprofiler_json_paths)
    data.update(collect_mapdamage_results(mapdamage_result_paths, standardise_colnames=True))

    result = pd.DataFrame()

    for id in data.keys():
        new_row = {
            "id": id,
            "n_reads": (
                data[id]["lendist_fw"].sum().iloc[0] + data[id]["lendist_rv"].sum().iloc[0]
            ),  ## The number of reads analysed is the sum of fw and rv reads.
            "dmg_5p_1bp": data[id]["dmg_5p"].loc[0, "dmg_5p"],
            "dmg_5p_2bp": data[id]["dmg_5p"].loc[1, "dmg_5p"],
            "dmg_3p_1bp": data[id]["dmg_3p"].loc[0, "dmg_3p"],
            "dmg_3p_2bp": data[id]["dmg_3p"].loc[1, "dmg_3p"],
        }

        result = pd.concat([result, pd.DataFrame([new_row])], ignore_index=True)

    return result


def compile_snp_coverage_table(snp_coverage_json_paths):
    if not isinstance(snp_coverage_json_paths, list):
        raise ValueError("Input must be a list.")

    result = pd.DataFrame()

    for json_path in snp_coverage_json_paths:
        data = parsers.parse_snp_coverage_json(json_path)
        result = pd.concat([result, data], ignore_index=True)

    return result
