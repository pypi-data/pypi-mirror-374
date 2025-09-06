import dnora_metno


def test_nora3():
    model = dnora_metno.modelrun.NORA3()


def test_wam4km():
    model = dnora_metno.modelrun.WAM4km()


def test_ww3_4km():
    model = dnora_metno.modelrun.WW3_4km()


def test_climarest():
    model = dnora_metno.modelrun.CLIMAREST()
