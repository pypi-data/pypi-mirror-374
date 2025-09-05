import contextlib
import sys
from typing import Any, Optional, Union

import mplhep as hep
import numpy as np
import smplr
from uhi.typing.plottable import (
    PlottableHistogram,
)

import babyyoda
from babyyoda.analysisobject import UHIAnalysisObject
from babyyoda.axis import UHIAxis
from babyyoda.util import loc, overflow, project, rebin, rebinBy_to_rebinTo, underflow


def set_bin1d(target: Any, source: Any) -> None:
    # TODO allow modify those?
    # self.d_xmin = bin.xMin()
    # self.d_xmax = bin.xMax()
    if hasattr(target, "set"):
        if (
            hasattr(source, "sumW")
            and hasattr(source, "sumWX")
            and hasattr(source, "sumW2")
            and hasattr(source, "sumWX2")
            and hasattr(source, "numEntries")
        ):
            target.set(
                source.numEntries(),
                [source.sumW(), source.sumWX()],
                [source.sumW2(), source.sumWX2()],
            )
        # else if tuple with 3 elements
        elif len(source) == 3:
            target.set(source[0], source[1], source[2])
        else:
            err = "Invalid argument type"
            raise NotImplementedError(err)
    else:
        err = "YODA1 backend can not set bin values"
        raise NotImplementedError(err)


def Histo1D(*args: Any, **kwargs: Any) -> "UHIHisto1D":
    """
    Automatically select the correct version of the Histo1D class
    """
    try:
        from babyyoda import yoda

        return yoda.Histo1D(*args, **kwargs)
    except ImportError:
        from babyyoda import grogu

        return grogu.Histo1D(*args, **kwargs)


# TODO make this implementation independent (no V2 or V3...)
class UHIHisto1D(
    UHIAnalysisObject,
    PlottableHistogram,
):
    ######
    # Minimum required functions
    ######

    def bins(self, includeOverflows: bool = False) -> list[Any]:
        raise NotImplementedError

    def bin(self, i: int) -> Any:
        return self.bins()[i]

    def xEdges(self) -> list[float]:
        raise NotImplementedError

    def annotationsDict(self) -> dict[str, Optional[str]]:
        raise NotImplementedError

    def clone(self) -> "UHIHisto1D":
        raise NotImplementedError

    def get_projector(self) -> Any:
        raise NotImplementedError

    def rebinXTo(self, bins: list[float]) -> None:
        raise NotImplementedError

    ######
    # BACKENDS
    ######

    def to_uncertainties(self, divide_by_volume: bool = True) -> Any:
        from uncertainties import unumpy

        # compute bin mid from edges
        xe = self.xEdges()
        mid = (np.array(xe[:-1]) + np.array(xe[1:])) / 2
        width = np.diff(xe)

        if divide_by_volume:
            return unumpy.uarray(mid, width / 2), unumpy.uarray(
                self.sumWs() / width, self.errWs() / width
            )

        return unumpy.uarray(mid, width / 2), unumpy.uarray(self.sumWs(), self.errWs())

    def to_boost_histogram(self) -> Any:
        import boost_histogram as bh

        h = bh.Histogram(
            # TODO also carry over overflow and underflow?
            bh.axis.Variable(
                self.xEdges(), underflow=False, overflow=False
            ),  # Regular float axis
            storage=bh.storage.Weight(),  # Weighted storage
        )
        h[:] = [(b.sumW(), b.sumW2()) for b in self.bins()]
        # for i in range(len(self.xEdges()) - 1):
        #    # we do not carry over numEntries nor sumWX...
        #    b = self.bin(i)
        #    h[i] = (b.sumW(), b.sumW2())
        return h

    def to_hist(self) -> Any:
        import hist

        h = hist.Hist(
            # TODO also carry over overflow and underflow?
            hist.axis.Variable(
                self.xEdges(), underflow=False, overflow=False
            ),  # Regular float axis
            storage=hist.storage.Weight(),  # Weighted storage
        )
        h[:] = [(b.sumW(), b.sumW2()) for b in self.bins()]
        # for i in range(len(self.xEdges()) - 1):
        #    # we do not carry over numEntries nor sumWX...
        #    b = self.bin(i)
        #    h[i] = (b.sumW(), b.sumW2())
        return h

    def to_grogu_v2(self) -> Any:
        from babyyoda.grogu.histo1d_v2 import GROGU_HISTO1D_V2

        tot = GROGU_HISTO1D_V2.Bin()
        for b in self.bins():
            tot.d_sumw += b.sumW()
            tot.d_sumw2 += b.sumW2()
            tot.d_sumwx += b.sumWX()
            tot.d_sumwx2 += b.sumWX2()
            tot.d_numentries += b.numEntries()

        return GROGU_HISTO1D_V2(
            d_key=self.key(),
            d_annotations=self.annotationsDict(),
            d_total=tot,
            d_bins=[
                GROGU_HISTO1D_V2.Bin(
                    d_xmin=self.xEdges()[i],
                    d_xmax=self.xEdges()[i + 1],
                    d_sumw=b.sumW(),
                    d_sumw2=b.sumW2(),
                    d_sumwx=b.sumWX(),
                    d_sumwx2=b.sumWX2(),
                    d_numentries=b.numEntries(),
                )
                for i, b in enumerate(self.bins())
            ],
            d_overflow=GROGU_HISTO1D_V2.Bin(
                d_xmin=None,
                d_xmax=None,
                d_sumw=self.overflow().sumW(),
                d_sumw2=self.overflow().sumW2(),
                d_sumwx=self.overflow().sumWX(),
                d_sumwx2=self.overflow().sumWX2(),
                d_numentries=self.overflow().numEntries(),
            ),
            d_underflow=GROGU_HISTO1D_V2.Bin(
                d_xmin=None,
                d_xmax=None,
                d_sumw=self.underflow().sumW(),
                d_sumw2=self.underflow().sumW2(),
                d_sumwx=self.underflow().sumWX(),
                d_sumwx2=self.underflow().sumWX2(),
                d_numentries=self.underflow().numEntries(),
            ),
        )

    def to_grogu_v3(self) -> Any:
        from babyyoda.grogu.histo1d_v3 import GROGU_HISTO1D_V3

        return GROGU_HISTO1D_V3(
            d_key=self.key(),
            d_annotations=self.annotationsDict(),
            d_edges=self.xEdges(),
            d_bins=[
                GROGU_HISTO1D_V3.Bin(
                    d_sumw=self.underflow().sumW(),
                    d_sumw2=self.underflow().sumW2(),
                    d_sumwx=self.underflow().sumWX(),
                    d_sumwx2=self.underflow().sumWX2(),
                    d_numentries=self.underflow().numEntries(),
                )
            ]
            + [
                GROGU_HISTO1D_V3.Bin(
                    d_sumw=b.sumW(),
                    d_sumw2=b.sumW2(),
                    d_sumwx=b.sumWX(),
                    d_sumwx2=b.sumWX2(),
                    d_numentries=b.numEntries(),
                )
                for b in self.bins()
            ]
            + [
                GROGU_HISTO1D_V3.Bin(
                    d_sumw=self.overflow().sumW(),
                    d_sumw2=self.overflow().sumW2(),
                    d_sumwx=self.overflow().sumWX(),
                    d_sumwx2=self.overflow().sumWX2(),
                    d_numentries=self.overflow().numEntries(),
                )
            ],
        )

    def to_yoda_v3(self) -> Any:
        err = "Not implemented yet"
        raise NotImplementedError(err)

    def to_string(self) -> str:
        # Now we need to map YODA to grogu and then call to_string
        # TODO do we want to hardcode v3 here?
        return str(self.to_grogu_v3().to_string())

    ########################################################
    # YODA compatibility code (dropped legacy code?)
    ########################################################

    def overflow(self) -> Any:
        return self.bins(includeOverflows=True)[-1]

    def underflow(self) -> Any:
        return self.bins(includeOverflows=True)[0]

    def errWs(self) -> Any:
        return np.sqrt(np.array([b.sumW2() for b in self.bins()]))

    def xMins(self) -> list[float]:
        return self.xEdges()[:-1]
        # return np.array([b.xMin() for b in self.bins()])

    def xMaxs(self) -> list[float]:
        return self.xEdges()[1:]
        # return np.array([b.xMax() for b in self.bins()])

    def sumWs(self) -> list[float]:
        return [b.sumW() for b in self.bins()]

    def sumW2s(self) -> list[float]:
        return [b.sumW2() for b in self.bins()]

    def xMean(self, includeOverflows: bool = True) -> float:
        return sum(
            float(b.sumWX()) for b in self.bins(includeOverflows=includeOverflows)
        ) / sum(float(b.sumW()) for b in self.bins(includeOverflows=includeOverflows))

    def integral(self, includeOverflows: bool = True) -> float:
        return sum(
            float(b.sumW()) for b in self.bins(includeOverflows=includeOverflows)
        )

    def rebinXBy(self, factor: int, begin: int = 1, end: int = sys.maxsize) -> None:
        new_edges = rebinBy_to_rebinTo(self.xEdges(), factor, begin, end)
        self.rebinXTo(new_edges)

    def rebinBy(self, *args: Any, **kwargs: Any) -> None:
        self.rebinXBy(*args, **kwargs)

    def rebinTo(self, *args: Any, **kwargs: Any) -> None:
        self.rebinXTo(*args, **kwargs)

    def dVols(self) -> list[float]:
        ret = []
        for ix in range(len(self.xMins())):
            ret.append(self.xMaxs()[ix] - self.xMins()[ix])
        return ret

    ########################################################
    # Generic UHI code
    ########################################################

    @property
    def axes(self) -> list[UHIAxis]:
        return [UHIAxis(list(zip(self.xMins(), self.xMaxs())))]

    @property
    def kind(self) -> str:
        # TODO reevaluate this
        return "COUNT"

    def counts(self) -> np.typing.NDArray[Any]:
        return np.array([b.numEntries() for b in self.bins()])

    def values(self) -> np.typing.NDArray[Any]:
        return np.array([b.sumW() for b in self.bins()])

    def variances(self) -> np.typing.NDArray[Any]:
        return np.array([(b.sumW2()) for b in self.bins()])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UHIHisto1D):
            return False
        return (
            np.array_equal(self.counts(), other.counts())
            and self.axes == other.axes
            and np.array_equal(self.variances(), other.variances())
        )

    def __getitem__(
        self,
        slices: Union[  # type: ignore[valid-type]
            int,
            loc,
            slice,
            type[Ellipsis],
            type[babyyoda.util.underflow],
            type[babyyoda.util.overflow],
        ],
    ) -> Any:
        if slices is Ellipsis:
            return self.clone()
        index = self.__get_index(slices)
        # integer index
        if isinstance(index, int):  # loc and int
            if index >= len(self.bins()):
                err = "Index out of bounds"
                raise IndexError(err)
            return self.bin(index)
        if index is underflow:
            return self.underflow()
        if index is overflow:
            return self.overflow()

        if isinstance(slices, slice):
            # TODO handle ellipsis
            item = slices
            # print(f"slice {item}")
            start, stop, step = (
                self.__get_index(item.start),
                self.__get_index(item.stop),
                item.step,
            )
            if not (start is None or isinstance(start, int)) or not (
                stop is None or isinstance(stop, int)
            ):
                err = "Invalid argument type"
                raise TypeError(err)

            sc = self.clone()
            if isinstance(step, rebin):
                # if stop - start is not divisible by step.factor we drop the last bins
                # Compute closest stop = n * step.factor + start
                if start is None:
                    start = 0
                if stop is None:
                    stop = len(self.bins())
                closest_stop = (stop - start) // step.factor * step.factor + start
                sc = sc[start:closest_stop]
                sc.rebinBy(step.factor, 1, sys.maxsize)
            elif step is project:
                # Get the subset and then project
                sc = self[item.start : item.stop].project(
                    includeUnderflow=item.start is None,
                    includeOverflow=item.stop is None,
                )
            else:
                if stop is not None:
                    stop += 1
                sc.rebinTo(self.xEdges()[start:stop])
            return sc

        err = "Invalid argument type"
        raise TypeError(err)

    def __get_index(
        self,
        slices: Union[
            int, loc, slice, type[babyyoda.util.underflow], type[babyyoda.util.overflow]
        ],
    ) -> Optional[
        Union[int, type[babyyoda.util.underflow], type[babyyoda.util.overflow]]
    ]:
        index: Optional[
            Union[type[Union[babyyoda.util.underflow, babyyoda.util.overflow]], int]
        ] = None
        if isinstance(slices, int):
            index = slices
            while index < 0:
                index = len(self.bins()) + index
        if isinstance(slices, loc):
            # TODO cyclic maybe
            idx = None
            for i, _b in enumerate(self.bins()):
                if (
                    slices.value >= self.xEdges()[i]
                    and slices.value < self.xEdges()[i + 1]
                ):
                    idx = i
            if idx is not None:
                index = idx + slices.offset
            elif slices.value < self.xEdges()[0]:
                index = underflow
            elif slices.value > self.xEdges()[-1]:
                index = overflow
        if slices is underflow:
            index = underflow
        if slices is overflow:
            index = overflow
        return index

    def __set_by_index(
        self,
        index: Union[type[babyyoda.util.underflow], type[babyyoda.util.overflow], int],
        value: Any,
    ) -> None:
        if index is underflow:
            set_bin1d(self.underflow(), value)
            return
        if index is overflow:
            set_bin1d(self.overflow(), value)
            return
        if isinstance(index, int):
            set_bin1d(self.bin(index), value)
            return
        err = "Invalid argument type"
        raise TypeError(err)

    def __setitem__(self, slices: Any, value: Any) -> None:
        # integer index
        index = self.__get_index(slices)
        if index is not None:
            self.__set_by_index(index, value)

        if isinstance(slices, slice):
            # TODO handle ellipsis
            item = slices
            # print(f"slice {item}")
            start, stop, step = (
                self.__get_index(item.start),
                self.__get_index(item.stop),
                item.step,
            )
            if not (start is None or isinstance(start, int)) or not (
                stop is None or isinstance(stop, int)
            ):
                err = "Invalid argument type"
                raise TypeError(err)
            a = []
            c = []
            if start is None:
                start = 0
                a += [underflow]
            if stop is None:
                stop = len(self.bins())
                c += [overflow]
            if step is None:
                step = 1
            b = list(range(start, stop, step))
            d = a + b + c

            # if value is not an array set everything to the same value
            if not isinstance(value, (list, np.ndarray)):
                for i in d:
                    self.__set_by_index(i, value)
            else:
                # automagic inclusion of under and overflow depending on the value size...
                if len(value) == len(d) - 1 and (
                    item.start is not None or item.stop is not None
                ):
                    if item.start is None:
                        d = d[1:]
                    elif item.stop is None:
                        d = d[:-1]
                elif (
                    len(value) == len(d) - 2
                    and item.start is None
                    and item.stop is None
                ):
                    d = d[1:-1]
                if len(value) != len(d):
                    err = "Value length does not match slice length"
                    raise ValueError(err)
                for i, v in zip(d, value):
                    self.__set_by_index(i, v)

    def project(
        self, includeUnderflow: bool = False, includeOverflow: bool = False
    ) -> Any:
        # sc = self.clone().rebinTo(self.xEdges()[0], self.xEdges()[-1])
        p = self.get_projector()()
        thebins = self.bins(includeOverflows=True)[
            0 if includeUnderflow else 1 : None if includeOverflow else -1
        ]
        p.set(
            sum([b.numEntries() for b in thebins]),
            sum([b.sumW() for b in thebins]),
            sum([b.sumW2() for b in thebins]),
        )
        p.setAnnotationsDict(self.annotationsDict())
        return p

    def plot(
        self,
        *args: Any,
        binwnorm: float = 1.0,
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        hep.histplot(
            self,
            *args,
            yerr=self.variances() ** 0.5,
            w2method="sqrt",
            binwnorm=binwnorm,
            **kwargs,
        )
        title = title if title is not None else self.path()
        smplr.style_plot1d(title=title, **kwargs)

    def _ipython_display_(self) -> "UHIHisto1D":
        with contextlib.suppress(ImportError):
            self.plot()
        return self
