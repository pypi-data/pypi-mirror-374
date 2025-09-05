"""By-frame 214 L1 only header keywords that are not instrument specific."""

from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.fits_access import MetadataKey


class L1FitsAccess(FitsAccessBase):
    """
    Class defining a fits access object for processed L1 data.

    Parameters
    ----------
    hdu
        The input fits hdu
    name
        An optional name to be associated with the hdu
    auto_squeeze
        A boolean indicating whether to 'squeeze' out dimensions of size 1
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = False,  # Because L1 data should always have the right form, right?
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self._set_metadata_key_value(MetadataKey.elevation)
        self._set_metadata_key_value(MetadataKey.azimuth)
        self._set_metadata_key_value(MetadataKey.table_angle)
        self._set_metadata_key_value(MetadataKey.gos_level3_status)
        self._set_metadata_key_value(MetadataKey.gos_level3_lamp_status)
        self._set_metadata_key_value(MetadataKey.gos_polarizer_status)
        self._set_metadata_key_value(MetadataKey.gos_retarder_status)
        self._set_metadata_key_value(MetadataKey.gos_level0_status)
        self._set_metadata_key_value(MetadataKey.time_obs)
        self._set_metadata_key_value(MetadataKey.ip_id)
        self._set_metadata_key_value(MetadataKey.instrument)
        self._set_metadata_key_value(MetadataKey.wavelength)
        self._set_metadata_key_value(MetadataKey.proposal_id)
        self._set_metadata_key_value(MetadataKey.experiment_id)
        self._set_metadata_key_value(MetadataKey.num_dsps_repeats)
        self._set_metadata_key_value(MetadataKey.current_dsps_repeat)
        self._set_metadata_key_value(MetadataKey.fpa_exposure_time_ms)
        self._set_metadata_key_value(MetadataKey.sensor_readout_exposure_time_ms)
        self._set_metadata_key_value(MetadataKey.num_raw_frames_per_fpa)

    @property
    def gos_polarizer_angle(self) -> float:
        """Convert the polarizer angle to a float if possible before returning."""
        try:
            return float(self.header[MetadataKey.gos_polarizer_angle])
        except ValueError:
            return -999  # The angle is only used if the polarizer is in the beam

    @property
    def gos_retarder_angle(self) -> float:
        """Convert the retarder angle to a float if possible before returning."""
        try:
            return float(self.header[MetadataKey.gos_retarder_angle])
        except ValueError:
            return -999  # The angle is only used if the retarder is in the beam
