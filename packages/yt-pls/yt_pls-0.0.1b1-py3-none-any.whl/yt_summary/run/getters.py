"""Getters."""

from yt_summary.schemas.enums import SummarisationModesEnum
from yt_summary.summarisers.base_summariser import BaseSummariser
from yt_summary.summarisers.refined_summariser import RefinedSummariser
from yt_summary.summarisers.simple_summariser import SimpleSummariser

summarisers: dict[SummarisationModesEnum, type[BaseSummariser]] = {
    SummarisationModesEnum.COMPACT: SimpleSummariser,
    SummarisationModesEnum.REFINED: RefinedSummariser,
}
