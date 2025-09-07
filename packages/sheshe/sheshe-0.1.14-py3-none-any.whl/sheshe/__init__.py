from .sheshe import ModalBoundaryClustering, ClusterRegion
from .subspace_scout import SubspaceScout
from .modal_scout_ensemble import ModalScoutEnsemble
from .region_interpretability import RegionInterpreter
from .meta_optimization import random_search
from .shushu import ShuShu
from .cheche import CheChe
from .chuchu import ChuchuClassifier, ChuchuRegressor, ChuchuConfig

# ``OpenAIRegionInterpreter`` relies on the optional ``openai`` dependency.  In
# environments where that dependency (or the module itself) is missing we still
# want the base package to be importable.  Import lazily and fall back to a
# ``None`` placeholder so that ``from sheshe import OpenAIRegionInterpreter``
# works even when the optional components are unavailable.
try:  # pragma: no cover - exercised via import side effect
    from .openai_text import OpenAIRegionInterpreter  # type: ignore
except Exception:  # pragma: no cover - optional dependency not installed
    OpenAIRegionInterpreter = None  # type: ignore

__all__ = [
    "ModalBoundaryClustering",
    "ClusterRegion",
    "SubspaceScout",
    "ModalScoutEnsemble",
    "RegionInterpreter",
    "random_search",
    "OpenAIRegionInterpreter",
    "ShuShu",
    "CheChe",
    "ChuchuClassifier",
    "ChuchuRegressor",
    "ChuchuConfig",
]

__version__ = "0.1.3"
