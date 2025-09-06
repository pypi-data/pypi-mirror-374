"""Proposal Id parser."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.fits_access import MetadataKey
from dkist_processing_common.parsers.id_bud import ContributingIdsBud
from dkist_processing_common.parsers.id_bud import IdBud


class ProposalIdBud(IdBud):
    """Class to create a Bud for the proposal_id."""

    def __init__(self):
        super().__init__(constant_name=BudName.proposal_id, metadata_key=MetadataKey.proposal_id)


class ContributingProposalIdsBud(ContributingIdsBud):
    """Class to create a Bud for the proposal_ids."""

    def __init__(self):
        super().__init__(
            stem_name=BudName.contributing_proposal_ids, metadata_key=MetadataKey.proposal_id
        )
