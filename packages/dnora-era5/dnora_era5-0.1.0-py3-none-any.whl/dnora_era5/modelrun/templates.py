from dnora.modelrun.modelrun import ModelRun
from dnora.type_manager.dnora_types import DnoraDataType
import dnora_era5.spectra, dnora_era5.wind, dnora_era5.waterlevel


class ERA5(ModelRun):
    _reader_dict = {
        DnoraDataType.SPECTRA: dnora_era5.spectra.ERA5(),
        DnoraDataType.WIND: dnora_era5.wind.ERA5(),
        DnoraDataType.WATERLEVEL: dnora_era5.waterlevel.GTSM(),
    }
