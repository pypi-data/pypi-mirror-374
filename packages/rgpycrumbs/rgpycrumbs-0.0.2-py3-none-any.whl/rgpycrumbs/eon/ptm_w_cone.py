#!/usr/bin/env python3

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "ase",
#   "click",
#   "numpy",
#   "ovito",
#   "rich",
# ]
# ///
"""
Identifies atoms for saddle point search displacement.
Biases the search by selecting atoms in a bounding box that connects
the two largest defect clusters identified by PTM.
"""

# 1. WARNING SUPPRESSION
import warnings

warnings.filterwarnings("ignore", message=".*OVITO.*PyPI")
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*Please use atoms.calc.*"
)

# 2. IMPORTS
import logging
import sys
from enum import StrEnum

import ase.io as aseio
import click
import numpy as np
from ovito.io.ase import ase_to_ovito
from ovito.modifiers import (
    ClusterAnalysisModifier,
    PolyhedralTemplateMatchingModifier,
    SelectTypeModifier,
)
from ovito.pipeline import Pipeline, StaticSource
from rich.logging import RichHandler

# 3. CONSTANTS and ENUMERATIONS
logging.basicConfig(
    level="WARNING",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
log = logging.getLogger(__name__)


class CrystalStructure(StrEnum):
    FCC = "FCC"


STRUCTURE_TYPE_MAP = {
    CrystalStructure.FCC: PolyhedralTemplateMatchingModifier.Type.FCC,
}
STRUCTURE_PROPERTY_NAME = "Structure Type"


# 4. HELPER FUNCTIONS
def get_defect_indices(data_collection) -> np.ndarray:
    """Finds indices of non-FCC atoms using PTM."""
    pipeline = Pipeline(source=StaticSource(data=data_collection))
    ptm = PolyhedralTemplateMatchingModifier()
    pipeline.modifiers.append(ptm)
    select_mod = SelectTypeModifier(
        operate_on="particles",
        property=STRUCTURE_PROPERTY_NAME,
        types={STRUCTURE_TYPE_MAP[CrystalStructure.FCC]},
    )
    pipeline.modifiers.append(select_mod)
    data = pipeline.compute()
    mismatch_indices = np.where(data.particles.selection.array == 0)[0]
    log.info(f"Found {len(mismatch_indices)} non-FCC atoms via PTM.")
    return mismatch_indices


def get_bounding_box_indices(
    data_collection,
    defect_indices: np.ndarray,
    box_expansion: float,
) -> np.ndarray:
    """
    Clusters PTM defects and finds atoms in a bounding box between the two largest.
    """
    if defect_indices.size < 2:
        log.warning("Not enough defect atoms to form two clusters. Skipping bias.")
        return np.array([], dtype=int)

    # Create a new data collection containing only the defect atoms for clustering
    defect_pipeline = Pipeline(source=StaticSource(data=data_collection))
    defect_pipeline.modifiers.append(
        SelectTypeModifier(
            operate_on="particles",
            types=set(defect_indices),
        )
    )
    # Cluster the defect atoms to separate the SIA from the vacancy region
    cluster_mod = ClusterAnalysisModifier(
        cutoff=3.0,  # Angstrom, adjust if necessary
        sort_by_size=True,
        only_selected=True,
    )
    defect_pipeline.modifiers.append(cluster_mod)
    data = defect_pipeline.compute()

    if data.tables["clusters"].number_of_clusters < 2:
        log.warning("Could not identify two separate defect clusters. Skipping bias.")
        return np.array([], dtype=int)

    # Get the particle indices for the two largest clusters
    cluster_table = data.tables["clusters"]
    cluster_1_indices = cluster_table.cluster_by_id(1)["Particle Indices"]
    cluster_2_indices = cluster_table.cluster_by_id(2)["Particle Indices"]

    all_pos = data_collection.particles.positions.array
    center_1 = np.mean(all_pos[cluster_1_indices], axis=0)
    center_2 = np.mean(all_pos[cluster_2_indices], axis=0)

    log.info(f"Center of defect cluster 1: {np.round(center_1, 2)}")
    log.info(f"Center of defect cluster 2: {np.round(center_2, 2)}")

    # Define the bounding box including an expansion factor
    min_coords = np.minimum(center_1, center_2) - box_expansion
    max_coords = np.maximum(center_1, center_2) + box_expansion

    # Select all atoms within this bounding box
    is_in_box = np.all((all_pos >= min_coords) & (all_pos <= max_coords), axis=1)
    bias_indices = np.where(is_in_box)[0]

    log.info(f"Found {len(bias_indices)} atoms within the bias bounding box.")
    return bias_indices


# 5. MAIN SCRIPT LOGIC
@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument(
    "filename", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Enable verbose output."
)
@click.option(
    "--bias/--no-bias",
    "bias_mode",
    default=True,
    show_default=True,
    help="Enable biasing between defect clusters.",
)
@click.option(
    "--box-expansion",
    type=float,
    default=1.0,
    show_default=True,
    help="Expansion distance (in Angstrom) for the bias bounding box.",
)
def main(
    filename: str,
    verbose: bool,
    bias_mode: bool,
    box_expansion: float,
):
    """
    Analyzes FILENAME to find atoms for displacement and prints their
    0-based indices as a comma-separated list.
    """
    if verbose:
        log.setLevel(logging.INFO)

    try:
        atoms = aseio.read(filename)
        atoms.set_pbc([True] * 3)
        ovito_data = ase_to_ovito(atoms)
    except Exception as e:
        log.critical(f"Failed to read or process file '{filename}'. Error: {e}")
        sys.exit(1)

    defect_indices = get_defect_indices(ovito_data)

    if defect_indices.size == 0:
        log.info("No defect atoms found. Emitting empty list to stop EON.")
        print("")
        return

    final_indices = defect_indices

    if bias_mode:
        bias_indices = get_bounding_box_indices(
            ovito_data, defect_indices, box_expansion
        )
        # Combine the original PTM defects with the new biasing atoms
        final_indices = np.union1d(defect_indices, bias_indices)

    log.info(f"Total unique atoms in displacement list: {len(final_indices)}")
    print(",".join(map(str, final_indices)))


# 6. SCRIPT ENTRY POINT
if __name__ == "__main__":
    main()
