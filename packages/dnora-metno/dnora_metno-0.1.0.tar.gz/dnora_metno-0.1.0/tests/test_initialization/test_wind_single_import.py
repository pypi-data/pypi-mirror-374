import dnora_metno


def test_nora3():
    reader = dnora_metno.wind.NORA3()


def test_nora3_fp():
    reader = dnora_metno.wind.NORA3_fp()


def test_mywave3km():
    reader = dnora_metno.wind.MyWave3km()


def test_meps():
    reader = dnora_metno.wind.MEPS()


def test_climarest():
    reader = dnora_metno.wind.CLIMAREST()
