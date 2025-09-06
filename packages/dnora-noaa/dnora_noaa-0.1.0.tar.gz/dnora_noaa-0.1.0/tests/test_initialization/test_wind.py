def test_pacioos():
    from dnora_noaa.wind import PacIOOS

    reader = PacIOOS()


def test_ncep():
    from dnora_noaa.wind import NCEP

    reader = NCEP()


def test_ncep1h():
    from dnora_noaa.wind import NCEP1h

    reader = NCEP1h()
