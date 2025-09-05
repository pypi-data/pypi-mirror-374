import pytest
from histoprint import print_hist

import babyyoda
import babyyoda.read
from babyyoda import grogu
from babyyoda.test import init_yoda

yoda, yoda_available, yoda2 = init_yoda()


@pytest.mark.parametrize(
    "mod",
    [
        babyyoda.read,
        grogu.read,
        yoda.read,
    ],
)
def test_histoprint_histo1d_v2(mod):
    hists = mod("tests/test_histo1d_v2.yoda")
    for _, v in hists.items():
        assert isinstance(v, babyyoda.histo1d.UHIHisto1D)
        print_hist(v, summary=True, title=v.title())


@pytest.mark.parametrize(
    "mod",
    [
        babyyoda.read,
        grogu.read,
        yoda.read,
    ],
)
@pytest.mark.skipif(not yoda2, reason="yoda >= 2.0.0 is required")
def test_histoprint_histo1d_v3(mod):
    hists = mod("tests/test_histo1d_v3.yoda")
    for _, v in hists.items():
        assert isinstance(v, babyyoda.histo1d.UHIHisto1D)
        print_hist(v, summary=True, title=v.title())
