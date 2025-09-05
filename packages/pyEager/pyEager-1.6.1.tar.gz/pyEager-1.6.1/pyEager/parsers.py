from json import load
import pandas as pd
import numpy as np

## Helper statistics function provided by Konstantinos Siozios
def weighted_distribution_stats(df, val, weight):
    """small function to calculate the weighted mean, median, and std from a dataframe

    Args:
        df (pandas.DataFrame): The dataframe to calculate the statistics from
        val (string): The values to calculate the statistics for
        weight (string): The weights of the values

    Returns:
        pd.Dataframe(float64): A dataframe containing the weighted std, median, and mean of the values
    """
    df_sorted = df.sort_values(val)
    cumsum = df_sorted[weight].cumsum()
    cutoff = df_sorted[weight].sum() / 2.
    median = df_sorted[cumsum >= cutoff][val].iloc[0]
    mean = np.average(df_sorted[val], weights=df_sorted[weight])
    std = np.sqrt(np.average((df_sorted[val]-mean)**2, weights=df_sorted[weight]))
    results=pd.DataFrame({'std':[std],'median':[median],'mean':[mean]}, dtype='float64')
    return (results)


#### A set of functions to parse the JSON output of nf-core/eager modules into pandas DataFrames ####


def parse_sexdeterrmine_json(json_path, minimal=False):
    """Parses nf-core/eager sex determination results into a pandas DataFrame.

    Args:
        json_path (string): The path to the json file.
        minimal (bool, optional): Should a minimal Data frame be generated?. Defaults to False.

    Returns:
        pandas.DataFrame: A data frame containing the sample-level data from the json file.
          If minimal is True, then only the relative coverages on the X & Y are returned,
          with their respective errors.
    """

    with open(json_path) as f:
        data = pd.read_json(f, orient="index")
        data = data.drop(index="Metadata", columns=["tool_name", "version"])

        if minimal:
            data = data.drop(
                columns=[
                    "Snps Autosomal",
                    "XSnps",
                    "YSnps",
                    "NR Aut",
                    "NrX",
                    "NrY",
                ]
            )

    ## Reset the index
    data.reset_index(inplace=True, names=["id"])
    return data


def parse_damageprofiler_json(json_path):
    """Parses damageprofiler results into a dictionary of pandas DataFrames.

    Args:
        json_path (string): The path to the json file.

    Returns:
        dict: A dictionary containing each part of the json file as its own pandas data frame.
    """

    damageprofiler_json_attributes = [
        "metadata",
        "lendist_fw",
        "dmg_5p",
        "summary_stats",
        "dmg_3p",
        "lendist_rv",
    ]
    damage_profiler_results = {}

    with open(json_path) as f:
        data = load(f)
        for attr in damageprofiler_json_attributes:
            if attr.startswith("dmg_"):
                damage_profiler_results[attr] = pd.DataFrame(data=data[attr], columns=[attr])
            elif attr.startswith("lendist_"):
                damage_profiler_results[attr] = pd.DataFrame.from_dict(
                    data[attr], orient="index", columns=["count"]
                )
                damage_profiler_results[attr].index.name = "length"
                damage_profiler_results[attr].sort_index(axis=0, ascending=True, inplace=True)
            elif attr == "metadata":
                damage_profiler_results[attr] = pd.DataFrame.from_dict(
                    data[attr], orient="index", columns=["value"]
                )
            else:
                damage_profiler_results[attr] = pd.json_normalize(data[attr])

    ## Resetting the index cannot be done here, since the output is not a single data frame.
    ## Instead adding the 'id' column happens in compile_damage_table()
    return damage_profiler_results


def parse_nuclear_contamination_json(json_path):
    """Parses nf-core/eager nuclear_contamination results into a pandas DataFrame.

    Args:
        json_path (string): The path to the json file.

    Returns:
        pandas.DataFrame: A data frame containing the library-level nuclear contamination results from the json file.
    """

    with open(json_path) as f:
        data = load(f)
        contamination_table = pd.DataFrame.from_dict(data["data"], orient="index")

    ## Reset the index
    contamination_table.reset_index(inplace=True, names=["id"])
    return contamination_table


def parse_snp_coverage_json(json_path):
    """Parses eigenstratdatabasetools eigenstrat_snp_coverage results into pandas DataFrame.

    Args:
        json_path (string): The path to the json file.

    Returns:
        pandas.DataFrame: A data frame containing the sample-level SNP coverage results from the json file.
    """

    with open(json_path) as f:
        data = load(f)
        coverage_table = pd.DataFrame.from_dict(data["data"], orient="index")

    ## Reset the index
    coverage_table.reset_index(inplace=True, names=["id"])
    return coverage_table


def parse_endorspy_json(json_path):
    """Parses a single endorspy result JSON into pandas DataFrame.

    Args:
        json_path (string): The path to the json file.

    Returns:
        pandas.DataFrame: A data frame containing the endogenous DNA results from the json file.
    """

    with open(json_path) as f:
        data = load(f)
        endogenous_table = pd.DataFrame.from_dict(data["data"], orient="index")

        ## Reset the index
        endogenous_table.reset_index(inplace=True, names=["id"])
        return endogenous_table


def parse_eager_tsv(tsv_path):
    """Parse an nf-core/eager input TSV into a pandas DataFrame.

    Args:
        tsv_path (string): The path to the TSV file.

    Returns:
        pandas.DataFrame: A data frame containing the data of the TSV, with additional columns specifying what merging steps took place.
    """
    ## TODO Eventually, could add renaming of columns here to keep output consistent between eager 2.* and 3.*
    with open(tsv_path) as f:
        tsv_table = pd.read_table(f, sep="\t")

        ## Check what merging took place
    ## First: Post-dedup merging of libraries with shared UDG-treatment/Sample/Strandedness
    merged_after_dedup = (
        tsv_table.filter(["Sample_Name", "Library_ID", "Strandedness", "UDG_Treatment"])
        .groupby(["Sample_Name", "Strandedness", "UDG_Treatment"])
        .nunique()
    )
    merged_after_dedup["initial_merge"] = merged_after_dedup["Library_ID"].apply(lambda f: f > 1)
    merged_after_dedup.drop(columns=["Library_ID"], inplace=True)

    ## Next, merging of libraries across UDG-treatment that share Sample/Strandedness
    merged_after_trimming = (
        merged_after_dedup.reset_index()
        .filter(["Sample_Name", "Strandedness", "UDG_Treatment"])
        .groupby(["Sample_Name", "Strandedness"])
        .nunique()
    )
    merged_after_trimming["additional_merge"] = merged_after_trimming["UDG_Treatment"].apply(
        lambda f: f > 1
    )
    merged_after_trimming.drop(columns=["UDG_Treatment"], inplace=True)

    ## Finally, check if there are any samples have in multiple strandedness values
    multiple_strandedness_per_ind = (
        merged_after_trimming.reset_index()
        .filter(["Sample_Name", "Strandedness"])
        .groupby(["Sample_Name"])
        .nunique()
    )
    multiple_strandedness_per_ind["strandedness_clash"] = multiple_strandedness_per_ind[
        "Strandedness"
    ].apply(lambda f: f > 1)
    multiple_strandedness_per_ind.drop(columns=["Strandedness"], inplace=True)

    ## Create tsv table that includes decision tree results
    decision_tree = (
        pd.merge(
            tsv_table,
            merged_after_dedup,
            on=["Sample_Name", "Strandedness", "UDG_Treatment"],
            how="left",
        )
        .merge(merged_after_trimming, on=["Sample_Name", "Strandedness"], how="left")
        .merge(multiple_strandedness_per_ind, on=["Sample_Name"], how="left")
    )

    return decision_tree


## Takes the output of parse_eager_tsv() and adds the foreign keys at different levels
def infer_merged_bam_names(tsv_data, skip_deduplication=None, run_trim_bam=None):
    """Infer the names of eager output files based on the merging steps that took place.

    Args:
        tsv_data (pandas.DataFrame):  A dataframe with the TSV data, as returned from parse_eager_tsv.
        skip_deduplication (boolean): Was deduplication skipped during the nf-core/eager run?
        run_trim_bam (boolean):       Was BAM trimming activated during the nf-core/eager run?
    """
    ## Ensure tsv_dta is a pandas DataFrame
    if not isinstance(tsv_data, pd.DataFrame):
        raise ValueError("tsv_data must be a pandas DataFrame.")

    ## Ensure skip deduplication and run_trim_bam are booleans if they are not None
    if skip_deduplication:
        if not isinstance(skip_deduplication, bool):
            raise ValueError("skip_deduplication must be a boolean.")
    if run_trim_bam:
        if not isinstance(run_trim_bam, bool):
            raise ValueError("run_trim_bam must be a boolean.")

    ## TODO Implement inference of names when deduplication is skipped.
    ## Inner functions that applies conditional logic to infer the merged BAM names
    ## Get initial merge BAM name
    def initial_bam_name(row):
        ## Initial library merge happens prior to trimming, so trimming option can be ignored.
        if row["initial_merge"]:
            ## The _rmdup suffix is always added to the merged bam name in `library_merge` step, regardless of deduplication
            return f"{row['Sample_Name']}_udg{row['UDG_Treatment']}_libmerged_rmdup.bam"
        else:
            ## No library merging happened, so the BAM name is based on the individual library
            if skip_deduplication:
                return f"{row['Library_ID']}_{row['SeqType']}.mapped.bam"
            else:
                return f"{row['Library_ID']}_rmdup.bam"

    ## Get additional merge BAM name
    def additional_bam_name(row, run_trim_bam):
        ## No additional merge
        if not row["additional_merge"]:
            ## If trimming was not run, the initial BAM name is the same BAM name
            if not run_trim_bam or row['UDG_Treatment']=='full':
                return row["initial_bam_name"]
            elif row["initial_merge"]:
                ## If trimming was run, the trimmed bam is the "additional" bam. Libmerged if multiple libraries.
                ## The trimmed bam has the order of the udg and libmerged suffixes reversed for some reason.
                return f"{row['Sample_Name']}_libmerged_udg{row['UDG_Treatment']}.trimmed.bam"
            else:
                return f"{row['Library_ID']}_udg{row['UDG_Treatment']}.trimmed.bam"
        ## Additional merge
        elif row["additional_merge"]:
            return f"{row['Sample_Name']}_libmerged_add.bam"

    ## Get sex determination BAM name
    def sexdet_bam_name(row):
        return row["additional_bam_name"].replace(".bam", f"_{row['Strandedness']}strand.bam")

    ## Add columns with inferred BAM names
    tsv_data["initial_bam_name"] = tsv_data.apply(initial_bam_name, axis=1)
    tsv_data["additional_bam_name"] = tsv_data.apply(
        additional_bam_name, axis=1, run_trim_bam=run_trim_bam
    )
    tsv_data["sexdet_bam_name"] = tsv_data.apply(sexdet_bam_name, axis=1)

    return tsv_data


def parse_general_stats_table(general_stats_path):
    """Parse the general_stats_table.txt output of MultiQC into a pandas DataFrame.

    Args:
        general_stats_path (string): The path to the `general_stats_table.txt` TSV file.

    Returns:
        pandas.DataFrame: A data frame containing the data of the TSV.
    """
    with open(general_stats_path) as f:
        data = pd.read_table(f, sep="\t")

    return data


def parse_mapdamage_results(mapdamage_result_dir, results_basename, standardise_colnames=False):
    """Parse the mapDamage results into a pandas DataFrame.

    Args:
        mapdamage_result_dir (string): The path to the mapDamage results directory for a single BAM.

    Returns:
        dict: A dictionary containing the read length information and damage frequency information from mapDamage, each as its own pandas.DataFrame.
    """
    mapdamage_outputs = {
        ## "file_name" : "category_name"
        # "misincorporation.txt",
        # "dnacomp.txt",
        "3pGtoA_freq.txt": "dmg_3p",
        "lgdistribution.txt": "lendist",
        "5pCtoT_freq.txt": "dmg_5p",
    }
    mapdamage_results = {}
    for file in mapdamage_outputs:
        with open(f"{mapdamage_result_dir}/{file}") as f:
            if file.endswith("freq.txt"):
                file_results = pd.read_table(f, sep="\t").drop(columns="pos")
                ## Standardise column names to match the ones from damageprofiler parser
                if standardise_colnames:
                    file_results = file_results.rename(
                        columns={"3pG>A": "dmg_3p", "5pC>T": "dmg_5p"},
                    )
                mapdamage_results[mapdamage_outputs[file]] = file_results
            elif file == "lgdistribution.txt":
                ## Provide names explicitly because the column names sometimes include trailing spaces
                lendist = pd.read_table(
                    f,
                    sep="\t",
                    comment="#",
                    header=0,
                    names=["Std", "Length", "Occurences"],
                ).sort_values(by="Length")
                file_results_fw = (
                    lendist[lendist["Std"] == "+"].drop(columns="Std").set_index("Length")
                )
                file_results_rv = (
                    lendist[lendist["Std"] == "-"].drop(columns="Std").set_index("Length")
                )
                ## Standardise column names to match the ones from damageprofiler parser
                if standardise_colnames:
                    file_results_fw = file_results_fw.rename(
                        columns={"Occurences": "n"},
                        errors="raise",
                    ).rename_axis("length")
                    file_results_rv = file_results_rv.rename(
                        columns={"Occurences": "n"},
                        errors="raise",
                    ).rename_axis("length")
                mapdamage_results[mapdamage_outputs[file] + "_fw"] = file_results_fw
                mapdamage_results[mapdamage_outputs[file] + "_rv"] = file_results_rv
                
                ## Generate  summary stats to mimic damageprofiler output json.
                x = lendist.pivot(columns = "Std", index="Length").fillna(0)
                ## Create column with the total occurrences across both strands
                x['Total_Occurrences']=x.sum(axis=1, numeric_only=True)
                ## Filter down to only the two columns (also turn "Length" into column from an index)
                x=x.reset_index()[['Length', 'Total_Occurrences']]
                summary_stats = weighted_distribution_stats(
                    x, "Length", "Total_Occurrences"
                ).rename(columns={"mean":"mean_readlength"})
                mapdamage_results["summary_stats"] = summary_stats
    ## Collect version info from lgdistribution.txt
    with open(f"{mapdamage_result_dir}/lgdistribution.txt") as f:
        for line in f:
            ## get the mapDamage version from the first line of the lgdistribution.txt file
            mdg_version = line.strip().split()[-1]
            break
        metadata = {
            "tool_name": ["mapDamage"],
            "version": [mdg_version],
            "sample_name": [results_basename],
        }
        mapdamage_results["metadata"] = pd.DataFrame.from_dict(
            metadata, orient="index", columns=["value"]
        )
    return mapdamage_results
