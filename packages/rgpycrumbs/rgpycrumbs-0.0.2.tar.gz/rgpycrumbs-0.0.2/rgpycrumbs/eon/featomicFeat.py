#!/usr/bin/env python3

import warnings

warnings.filterwarnings("ignore", message=".*OVITO.*PyPI")
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*Please use atoms.calc.*"
)

# 2. IMPORTS (grouped by type)
# Standard Library
import logging
import sys
from enum import StrEnum
from typing import Dict, List, Optional

# Third-Party
import ase.io as aseio
import chemfiles
from featomic import SphericalExpansion

import click
import numpy as np
from ovito.io.ase import ase_to_ovito
from ovito.modifiers import (
    PolyhedralTemplateMatchingModifier,
    SelectTypeModifier,
    CentroSymmetryModifier,
    DeleteSelectedModifier,
    ExpressionSelectionModifier,
    InvertSelectionModifier,
)
from ovito.pipeline import Pipeline, StaticSource
from rich.logging import RichHandler

import numpy as np
import requests
from ase.io import read
from featomic import SoapPowerSpectrum
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from sklearn.decomposition import PCA
from skmatter.metrics import local_prediction_rigidity as lpr

# 3. CONSTANTS and ENUMERATIONS
# Set up logging to stderr using Rich.
logging.basicConfig(
    level="WARNING",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
)
log = logging.getLogger(__name__)


def find_mismatch_indices(filename: str) -> np.ndarray:
    """
    Analyzes a structure file with PTM and returns indices of atoms that
    do NOT match the target crystal structure.
    """
    try:
        log.info(f"Reading structure from '{filename}'...")
        atoms = aseio.read(filename)
        # XXX(rg): con readers in ase somehow lose this information, seems like an ase bug
        atoms.set_pbc([True] * 3)
        # with chemfiles.Trajectory(filename) as trajectory:
        #     structures = [s for s in trajectory]
    except FileNotFoundError:
        log.critical(f"Error: The file '{filename}' was not found.")
        sys.exit(1)
    except Exception as e:
        log.critical(f"Failed to read or parse file '{filename}'. Error: {e}")
        sys.exit(1)
    interstitial = np.zeros(3)

    # Hypers dictionary
    hypers = {
        "cutoff": {"radius": 2.85, "smoothing": {"type": "ShiftedCosine", "width": 0.1}},
        "density": {"type": "Gaussian", "width": 0.5},
        "basis": {
            "type": "TensorProduct",
            "max_angular": 12,
            "radial": {"type": "Gto", "max_radial": 9},
            "spline_accuracy": 1e-08,
        },
    }
    # Define featomic calculator
    calculator = SoapPowerSpectrum(**hypers)
    interstitial = [2356, 2477, 2492, 2604, 2608, 2610, 2985, 3369, 3372, 3375, 3377, 3385, 3387, 3504, 3510, 3987]
    non_fcc = [799, 827, 828, 829, 831, 836, 837, 840, 926, 955, 956, 965, 2356, 2477, 2492, 2604, 2608, 2610, 2985, 3369, 3372, 3375, 3377, 3385, 3387, 3504, 3510, 3987]
    vacancy = np.setdiff1d(non_fcc, interstitial)

    # calculator = SphericalExpansion(cutoff=cutoff, density=density, basis=basis)
    # spex = featomic.torch.SphericalExpansion(
    #         **{
    #             "cutoff": {
    #                 "radius": 1.3,
    #                 "smoothing": {"type": "ShiftedCosine", "width": 0.5},
    #             },
    #             "density": {"type": "Gaussian", "width": 0.3},
    #             "basis": {
    #                 "type": "TensorProduct",
    #                 "max_angular": 6,
    #                 "radial": {"type": "Gto", "max_radial": 3},
    #             },
    #         }
    #     )
    # selected_keys = mts.Labels(
    #         # These represent the degree of the spherical harmonics
    #         "o3_lambda",
    #         torch.tensor([4, 6]).reshape(-1, 1),
    #     )
    # descriptor_0 = calculator.compute(structure_0, selected_keys = selected_keys)
    # desc = spex.compute(structure_0, selected_keys = selected_keys)
    breakpoint()
    pviz = Pipeline(source=StaticSource(data=ase_to_ovito(atoms[interstitial])))
    pviz.add_to_scene()
    from ovito.vis import Viewport

    vp = Viewport()
    vp.type = Viewport.Type.Ortho
    vp.zoom_all()
    vp.render_image(
        size=(800, 600), filename="interstitial.png", background=(0, 0, 0), frame=0
    )
    return interstitial


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument(
    "filename",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
def main(filename: str):
    """
    Analyzes FILENAME to find all atoms that are NOT the specified
    crystal structure type and prints their 0-based indices as a
    comma-separated list, suitable for use in other programs.
    """

    indices = find_mismatch_indices(filename)

    # Final, clean output is printed to stdout.
    # All logs, errors, and status messages go to stderr.
    print(", ".join(map(str, indices)))


# 5. SCRIPT ENTRY POINT
if __name__ == "__main__":
    main()
