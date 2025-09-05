# TODO maybe promote all these to __eq__


def init_yoda():
    from packaging import version

    try:
        import yoda as yd

        from babyyoda import yoda

        yoda_available = True
        yoda_version = yd.__version__
        # version dependence possible here
    except ImportError:
        import babyyoda.grogu as yoda

        yoda_available = False
        yoda_version = "9999"

    yoda2 = version.parse(yoda_version) >= version.parse("2.0.0")
    return yoda, yoda_available, yoda2


def equal_ao(g, y):
    return (
        g.name() == y.name()
        and g.path() == y.path()
        and g.title() == y.title()
        and g.type() == y.type()
    )


def equal_bin1d(gb, yb):
    return gb.xMin() == yb.xMin() and gb.xMax() == yb.xMax() and equal_value1d(gb, yb)


def equal_value1d(gb, yb):
    return (
        gb.sumW() == yb.sumW()
        and gb.sumW2() == yb.sumW2()
        and gb.sumWX() == yb.sumWX()
        and gb.sumWX2() == yb.sumWX2()
        and gb.numEntries() == yb.numEntries()
    )


def equal_edges1d(ge, ye):
    return ge.xEdges() == ye.xEdges()


def equal_histo1d(gh1, yh1):
    return (
        equal_ao(gh1, yh1)
        and all(equal_bin1d(gb, yb) for gb, yb in zip(gh1.bins(), yh1.bins()))
        and equal_value1d(gh1.overflow(), yh1.overflow())
        and equal_value1d(gh1.underflow(), gh1.underflow())
        and equal_edges1d(gh1, yh1)
    )


def assert_ao(g, y):
    assert g.name() == y.name()
    assert g.path() == y.path()
    assert g.title() == y.title(), f"{g.title()} != {y.title()}"
    assert g.type() == y.type()


def assert_bin1d(gb, yb):
    assert gb.xMin() == yb.xMin()
    assert gb.xMax() == yb.xMax()
    assert_value1d(gb, yb)


def assert_value0d(gb, yb):
    assert gb.sumW() == yb.sumW(), f"{gb.sumW()} != {yb.sumW()}"
    assert gb.sumW2() == yb.sumW2()
    assert gb.numEntries() == yb.numEntries()


def assert_value1d(gb, yb):
    assert gb.sumW() == yb.sumW()
    assert gb.sumW2() == yb.sumW2()
    assert gb.sumWX() == yb.sumWX()
    assert gb.sumWX2() == yb.sumWX2()
    assert gb.numEntries() == yb.numEntries()


def assert_histo1d(gh1, yh1):
    assert_ao(gh1, yh1)

    assert len(gh1.bins()) == len(yh1.bins()), f"{len(gh1.bins())} != {len(yh1.bins())}"

    for ge, ye in zip(gh1.xEdges(), yh1.xEdges()):
        assert ge == ye, f"{gh1.xEdges()} != {yh1.xEdges()}"

    for gb, yb in zip(gh1.bins(), yh1.bins()):
        assert_value1d(gb, yb)

    if hasattr(gh1, "overflow") and hasattr(yh1, "overflow"):
        assert_value1d(gh1.overflow(), yh1.overflow())
        assert_value1d(gh1.underflow(), gh1.underflow())


def assert_bin2d(gb, yb):
    assert gb.xMin() == yb.xMin()
    assert gb.xMax() == yb.xMax()
    assert gb.yMin() == yb.yMin()
    assert gb.yMax() == yb.yMax()
    assert_value2d(gb, yb)


def assert_value2d(gb, yb):
    assert gb.numEntries() == yb.numEntries(), f"{gb.numEntries()} != {yb.numEntries()}"
    assert gb.sumW() == yb.sumW(), f"{gb.sumW()} != {yb.sumW()}"
    assert gb.sumW2() == yb.sumW2()
    assert gb.sumWX() == yb.sumWX(), f"{gb.sumWX()} != {yb.sumWX()}"
    assert gb.sumWX2() == yb.sumWX2()
    assert gb.sumWY() == yb.sumWY()
    assert gb.sumWY2() == yb.sumWY2()
    if hasattr(gb, "crossTerm") and hasattr(yb, "crossTerm"):
        assert gb.crossTerm(0, 1) == yb.crossTerm(0, 1)
    if hasattr(gb, "sumWXY") and hasattr(yb, "sumWXY"):
        assert gb.sumWXY() == yb.sumWXY()


def assert_histo2d(gh1, yh1, includeFlow=True):
    assert_ao(gh1, yh1)

    assert len(gh1.bins()) == len(yh1.bins())

    for ge, ye in zip(gh1.xEdges(), yh1.xEdges()):
        assert ge == ye, f"{gh1.xEdges()} != {yh1.xEdges()}"

    for ge, ye in zip(gh1.yEdges(), yh1.yEdges()):
        assert ge == ye, f"{gh1.yEdges()} != {yh1.yEdges()}"

    if includeFlow:
        for gb, yb in zip(gh1.bins(True), yh1.bins(True)):
            assert_value2d(gb, yb)

    for gb, yb in zip(gh1.bins(), yh1.bins()):
        print(f"gb: {gb.numEntries():=} {gb}")
        print(f"yb: {yb.numEntries():=} {yb}")
        assert_value2d(gb, yb)
