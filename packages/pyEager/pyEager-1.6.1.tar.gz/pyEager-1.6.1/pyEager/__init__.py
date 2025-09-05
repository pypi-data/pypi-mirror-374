__version__ = "1.6.1"
from pyEager.parsers import (
    parse_sexdeterrmine_json,
    parse_damageprofiler_json,
    parse_mapdamage_results,
    parse_nuclear_contamination_json,
    parse_snp_coverage_json,
    parse_endorspy_json,
    parse_eager_tsv,
    infer_merged_bam_names,
    parse_general_stats_table,
)
from pyEager.wrappers import (
    collect_damageprofiler_results,
    collect_mapdamage_results,
    compile_endogenous_table,
    compile_damage_table,
    compile_snp_coverage_table,
)
