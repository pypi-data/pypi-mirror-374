def test_nora3():
    from dnora_metno.wind import NORA3

    reader = NORA3()


def test_nora3_fp():
    from dnora_metno.wind import NORA3_fp

    reader = NORA3_fp()


def test_mywave3km():
    from dnora_metno.wind import MyWave3km

    reader = MyWave3km()


def test_meps():
    from dnora_metno.wind import MEPS

    reader = MEPS()


def test_climarest():
    from dnora_metno.wind import CLIMAREST

    reader = CLIMAREST()
