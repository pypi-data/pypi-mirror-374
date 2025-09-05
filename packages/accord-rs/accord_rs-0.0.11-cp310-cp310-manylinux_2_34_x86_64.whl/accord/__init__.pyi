from .data import Seq, AlnQualityReqs, Consensus
from .data.stats import AlnData, AlnStats


class Calculator:
    aln_quality_reqs: AlnQualityReqs

    def __init__(self, reqs: AlnQualityReqs): ...

    def calculate(self, ref_path: str, aln_path: str) -> list[Consensus]: ...
