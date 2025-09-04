"""
A package for setting frequenstist limits from unbinned data
"""

from freqfit.dataset import Dataset, ToyDataset, CombinedDataset
from freqfit.experiment import Experiment
from freqfit.limit import SetLimit
from freqfit.workspace import Workspace

__all__ = [
    "Dataset",
    "ToyDataset",
    "CombinedDataset",
    "Experiment",
    "SetLimit",
    "Superset",
    "Workspace",
    "PlotLimit",
    "__version__",
]
