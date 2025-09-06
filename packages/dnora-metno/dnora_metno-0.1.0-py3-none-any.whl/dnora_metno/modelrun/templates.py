# from ..run import model_executers
from dnora.modelrun.modelrun import ModelRun
from dnora.read.generic import ConstantData
from dnora.type_manager.dnora_types import DnoraDataType

import dnora_metno.spectra, dnora_metno.wind, dnora_metno.ice


class NORA3(ModelRun):
    _reader_dict = {
        DnoraDataType.SPECTRA: dnora_metno.spectra.NORA3(),
        DnoraDataType.WIND: dnora_metno.wind.NORA3(),
        DnoraDataType.ICE: dnora_metno.ice.NORA3(),
    }


class WAM4km(ModelRun):
    _reader_dict = {
        DnoraDataType.SPECTRA: dnora_metno.spectra.WAM4km(),
        DnoraDataType.WIND: dnora_metno.wind.MEPS(),
    }


class WW3_4km(ModelRun):
    _reader_dict = {
        DnoraDataType.SPECTRA: dnora_metno.spectra.WW3_4km(),
        DnoraDataType.WIND: dnora_metno.wind.MEPS(),
    }


class CLIMAREST(ModelRun):
    _reader_dict = {
        DnoraDataType.SPECTRA: dnora_metno.spectra.CLIMAREST(),
        DnoraDataType.WIND: dnora_metno.wind.CLIMAREST(),
        DnoraDataType.ICE: dnora_metno.ice.CLIMAREST(),
    }
