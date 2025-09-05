import pytest

import babyyoda as by
from babyyoda.grogu.histo1d_v2 import GROGU_HISTO1D_V2
from babyyoda.grogu.histo2d_v2 import GROGU_HISTO2D_V2
from babyyoda.test import assert_ao, assert_histo1d, assert_histo2d, init_yoda

yoda, yoda_available, yoda2 = init_yoda()

pytest.importorskip("yoda")


def test_ao():
    gh1 = next(iter(by.read_grogu("tests/test_histo1d_v2.yoda").values()))
    yh1 = next(iter(by.read_yoda("tests/test_histo1d_v2.yoda").values()))

    assert_ao(gh1, yh1)

    gh2 = next(iter(by.read_grogu("tests/test_histo2d_v2.yoda").values()))
    yh2 = next(iter(by.read_yoda("tests/test_histo2d_v2.yoda").values()))

    assert_ao(gh2, yh2)


def test_histo1d_v2():
    gh1 = next(iter(by.read_grogu("tests/test_histo1d_v2.yoda").values()))
    yh1 = next(iter(by.read_yoda("tests/test_histo1d_v2.yoda").values()))

    assert len(gh1.bins()) == len(yh1.bins())
    assert all(x == y for x, y in zip(gh1.xEdges(), yh1.xEdges()))

    for gb, yb in zip(gh1.bins(), yh1.bins()):
        assert gb.xMin() == yb.xMin()
        assert gb.xMax() == yb.xMax()
        assert gb.sumW() == yb.sumW()
        assert gb.sumW2() == yb.sumW2()
        assert gb.sumWX() == yb.sumWX()
        assert gb.sumWX2() == yb.sumWX2()
        assert gb.numEntries() == yb.numEntries()
    # TODO test overflow and underflow


@pytest.mark.skipif(not yoda2, reason="yoda >= 2.0.0 is required")
def test_histo1d_v3():
    gh1 = next(iter(by.read_grogu("tests/test_histo1d_v3.yoda").values()))
    yh1 = next(iter(by.read_yoda("tests/test_histo1d_v3.yoda").values()))

    assert len(gh1.bins()) == len(yh1.bins())
    assert len(gh1.bins(True)) == len(yh1.bins(True))
    assert all(
        x == y for x, y in zip(gh1.xEdges(), yh1.xEdges())
    ), f"{gh1.xEdges()} != {yh1.xEdges()}"

    for gb, yb in zip(gh1.bins(), yh1.bins()):
        assert gb.sumW() == yb.sumW()
        assert gb.sumW2() == yb.sumW2()
        assert gb.sumWX() == yb.sumWX()
        assert gb.sumWX2() == yb.sumWX2()
        assert gb.numEntries() == yb.numEntries()

    for gb, yb in zip(gh1.bins(True), yh1.bins(True)):
        assert gb.sumW() == yb.sumW()
        assert gb.sumW2() == yb.sumW2()
        assert gb.sumWX() == yb.sumWX()
        assert gb.sumWX2() == yb.sumWX2()
        assert gb.numEntries() == yb.numEntries()


def test_histo2d_v2():
    gh2 = next(iter(by.read_grogu("tests/test_histo2d_v2.yoda").values()))
    yh2 = next(iter(by.read_yoda("tests/test_histo2d_v2.yoda").values()))

    assert len(gh2.bins()) == len(yh2.bins())
    assert all(x == y for x, y in zip(gh2.xEdges(), yh2.xEdges()))
    assert all(x == y for x, y in zip(gh2.yEdges(), yh2.yEdges()))

    for i, (gb, yb) in enumerate(zip(gh2.bins(), yh2.bins())):
        assert gb.xMin() == yb.xMin(), f"at index {i}, {gb.xMin()} != {yb.xMin()}"
        assert gb.xMax() == yb.xMax()
        assert gb.yMin() == yb.yMin()
        assert gb.yMax() == yb.yMax()

        assert gb.sumW() == yb.sumW(), f"at index {i}"
        assert gb.sumW2() == yb.sumW2()
        assert gb.numEntries() == yb.numEntries()

    # TODO test overflow and underflow


@pytest.mark.skipif(not yoda2, reason="yoda >= 2.0.0 is required")
def test_histo2d_v3():
    gh2 = next(iter(by.read_grogu("tests/test_histo2d_v3.yoda").values()))
    yh2 = next(iter(by.read_yoda("tests/test_histo2d_v3.yoda").values()))

    assert all(
        x == y for x, y in zip(gh2.xEdges(), yh2.xEdges())
    ), f"{gh2.xEdges()} != {yh2.xEdges()}"
    assert all(
        x == y for x, y in zip(gh2.yEdges(), yh2.yEdges())
    ), f"{gh2.yEdges()} != {yh2.yEdges()}"
    assert len(gh2.bins(True)) == len(yh2.bins(True))
    assert len(gh2.bins()) == len(yh2.bins())

    for i, (gb, yb) in enumerate(zip(gh2.bins(True), yh2.bins(True))):
        assert gb.sumW() == yb.sumW(), f"at index {i}"
        assert gb.sumW2() == yb.sumW2()
        assert gb.numEntries() == yb.numEntries()


def test_create_histo1d():
    from babyyoda import yoda

    h = yoda.Histo1D(10, 0, 10, title="test")

    g = GROGU_HISTO1D_V2(
        d_annotations={"Title": "test"},
        d_bins=[
            GROGU_HISTO1D_V2.Bin(d_xmin=hb.xMin(), d_xmax=hb.xMax()) for hb in h.bins()
        ],
        d_underflow=GROGU_HISTO1D_V2.Bin(),
        d_overflow=GROGU_HISTO1D_V2.Bin(),
        d_total=GROGU_HISTO2D_V2.Bin(),
    )

    for i in range(12):
        for _ in range(i):
            h.fill(i)
            g.fill(i)
    h.fill(-1)
    g.fill(-1)
    h.fill(10)
    g.fill(10)

    assert_histo1d(g, h)


def test_create_histo2d():
    import babyyoda.yoda as yd

    h = yd.Histo2D(10, 0, 10, 10, 0, 10)

    g = GROGU_HISTO2D_V2(
        d_bins=[
            GROGU_HISTO2D_V2.Bin(
                d_xmin=hb.xMin(), d_xmax=hb.xMax(), d_ymin=hb.yMin(), d_ymax=hb.yMax()
            )
            for hb in h.bins()
        ],
        d_total=GROGU_HISTO2D_V2.Bin(),
    )

    for i in range(12):
        for j in range(12):
            for _ in range(i * j):
                h.fill(i, j)
                g.fill(i, j)

    assert_histo2d(g, h, includeFlow=False)
