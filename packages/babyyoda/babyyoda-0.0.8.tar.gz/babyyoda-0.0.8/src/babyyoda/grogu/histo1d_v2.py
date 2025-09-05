import re
from dataclasses import dataclass, field
from typing import Any, Optional

from babyyoda.grogu.analysis_object import GROGU_ANALYSIS_OBJECT
from babyyoda.grogu.counter_v2 import Counter_v2
from babyyoda.histo1d import UHIHisto1D


def Histo1D_v2(
    *args: Any, title: Optional[str] = None, **kwargs: Any
) -> "GROGU_HISTO1D_V2":
    edges = []
    if isinstance(args[0], list):
        edges = args[0]
    elif (
        isinstance(args[0], int)
        and isinstance(args[1], (float, int))
        and isinstance(args[2], (float, int))
    ):
        nbins = args[0]
        start = float(args[1])
        end = float(args[2])
        edges = [start + i * (end - start) / nbins for i in range(nbins + 1)]
    else:
        err = "Invalid arguments"
        raise ValueError(err)
    return GROGU_HISTO1D_V2(
        d_bins=[
            GROGU_HISTO1D_V2.Bin(
                d_xmin=edges[i],
                d_xmax=edges[i + 1],
            )
            for i in range(len(edges) - 1)
        ],
        d_overflow=GROGU_HISTO1D_V2.Bin(),
        d_underflow=GROGU_HISTO1D_V2.Bin(),
        d_total=GROGU_HISTO1D_V2.Bin(),
        d_annotations={"Title": title} if title else {},
        **kwargs,
    )


@dataclass
class GROGU_HISTO1D_V2(GROGU_ANALYSIS_OBJECT, UHIHisto1D):
    @dataclass
    class Bin:
        d_xmin: Optional[float] = None
        d_xmax: Optional[float] = None
        d_sumw: float = 0.0
        d_sumw2: float = 0.0
        d_sumwx: float = 0.0
        d_sumwx2: float = 0.0
        d_numentries: float = 0.0

        def __post_init__(self) -> None:
            assert (
                self.d_xmin is None or self.d_xmax is None or self.d_xmin < self.d_xmax
            )

        ########################################################
        # YODA compatibility code
        ########################################################

        def clone(self) -> "GROGU_HISTO1D_V2.Bin":
            return GROGU_HISTO1D_V2.Bin(
                d_xmin=self.d_xmin,
                d_xmax=self.d_xmax,
                d_sumw=self.d_sumw,
                d_sumw2=self.d_sumw2,
                d_sumwx=self.d_sumwx,
                d_sumwx2=self.d_sumwx2,
                d_numentries=self.d_numentries,
            )

        def fill(self, x: float, weight: float = 1.0, fraction: float = 1.0) -> None:
            # if (self.d_xmin is None or x > self.d_xmin) and (self.d_xmax is None or x < self.d_xmax):
            sf = fraction * weight
            self.d_sumw += sf
            self.d_sumw2 += sf * weight
            self.d_sumwx += sf * x
            self.d_sumwx2 += sf * x**2
            self.d_numentries += fraction

        def set_bin(self, bin: Any) -> None:
            # TODO allow modify those?
            # self.d_xmin = bin.xMin()
            # self.d_xmax = bin.xMax()
            self.d_sumw = bin.sumW()
            self.d_sumw2 = bin.sumW2()
            self.d_sumwx = bin.sumWX()
            self.d_sumwx2 = bin.sumWX2()
            self.d_numentries = bin.numEntries()

        def contains(self, x: float) -> bool:
            if self.d_xmin is None or self.d_xmax is None:
                return False
            return x >= self.d_xmin and x < self.d_xmax

        def set(self, numEntries: float, sumW: list[float], sumW2: list[float]) -> None:
            assert len(sumW) == 2
            assert len(sumW2) == 2
            self.d_sumw = sumW[0]
            self.d_sumw2 = sumW2[0]
            self.d_sumwx = sumW[1]
            self.d_sumwx2 = sumW2[1]
            self.d_numentries = numEntries

        def xMin(self) -> Optional[float]:
            return self.d_xmin

        def xMax(self) -> Optional[float]:
            return self.d_xmax

        def xMid(self) -> Optional[float]:
            if self.d_xmin is None or self.d_xmax is None:
                return None
            return (self.d_xmin + self.d_xmax) / 2

        def sumW(self) -> float:
            return self.d_sumw

        def sumW2(self) -> float:
            return self.d_sumw2

        def sumWX(self) -> float:
            return self.d_sumwx

        def sumWX2(self) -> float:
            return self.d_sumwx2

        def variance(self) -> float:
            if self.d_sumw**2 - self.d_sumw2 == 0:
                return 0
            return abs(
                (self.d_sumw2 * self.d_sumw - self.d_sumw**2)
                / (self.d_sumw**2 - self.d_sumw2)
            )
            # return self.d_sumw2/self.d_numentries - (self.d_sumw/self.d_numentries)**2

        def errW(self) -> Any:
            return self.d_sumw2**0.5

        def stdDev(self) -> Any:
            return self.variance() ** 0.5

        def effNumEntries(self) -> Any:
            return self.sumW() ** 2 / self.sumW2()

        def stdErr(self) -> Any:
            return self.stdDev() / self.effNumEntries() ** 0.5

        def dVol(self) -> Optional[float]:
            if self.d_xmin is None or self.d_xmax is None:
                return None
            return self.d_xmax - self.d_xmin

        def xVariance(self) -> float:
            # return self.d_sumwx2/self.d_sumw - (self.d_sumwx/self.d_sumw)**2
            if self.d_sumw**2 - self.d_sumw2 == 0:
                return 0
            return abs(
                (self.d_sumwx2 * self.d_sumw - self.d_sumwx**2)
                / (self.d_sumw**2 - self.d_sumw2)
            )

        def numEntries(self) -> float:
            return self.d_numentries

        # def __eq__(self, other):
        #    return (
        #        isinstance(other, GROGU_HISTO1D_V2.Bin)
        #        and self.d_xmin == other.d_xmin
        #        and self.d_xmax == other.d_xmax
        #        and self.d_sumw == other.d_sumw
        #        and self.d_sumw2 == other.d_sumw2
        #        and self.d_sumwx == other.d_sumwx
        #        and self.d_sumwx2 == other.d_sumwx2
        #        and self.d_numentries == other.d_numentries
        #    )

        def __add__(self, other: Any) -> "GROGU_HISTO1D_V2.Bin":
            assert isinstance(other, GROGU_HISTO1D_V2.Bin)
            return GROGU_HISTO1D_V2.Bin(
                self.d_xmin,
                self.d_xmax,
                self.d_sumw + other.d_sumw,
                self.d_sumw2 + other.d_sumw2,
                self.d_sumwx + other.d_sumwx,
                self.d_sumwx2 + other.d_sumwx2,
                self.d_numentries + other.d_numentries,
            )

        @classmethod
        def from_string(cls, line: str) -> "GROGU_HISTO1D_V2.Bin":
            values = re.split(r"\s+", line.strip())
            assert len(values) == 7
            if (
                values[0] == "Underflow"
                or values[0] == "Overflow"
                or values[0] == "Total"
            ):
                return cls(
                    None,
                    None,
                    float(values[2]),
                    float(values[3]),
                    float(values[4]),
                    float(values[5]),
                    float(values[6]),
                )
            return cls(
                float(values[0]),
                float(values[1]),
                float(values[2]),
                float(values[3]),
                float(values[4]),
                float(values[5]),
                float(values[6]),
            )

        def to_string(bin, label: Optional[str] = None) -> str:
            """Convert a Histo1DBin object to a formatted string."""
            if label is None:
                return f"{bin.d_xmin:<12.6e}\t{bin.d_xmax:<12.6e}\t{bin.d_sumw:<12.6e}\t{bin.d_sumw2:<12.6e}\t{bin.d_sumwx:<12.6e}\t{bin.d_sumwx2:<12.6e}\t{bin.d_numentries:<12.6e}"
            return f"{label:8}\t{label:8}\t{bin.d_sumw:<12.6e}\t{bin.d_sumw2:<12.6e}\t{bin.d_sumwx:<12.6e}\t{bin.d_sumwx2:<12.6e}\t{bin.d_numentries:<12.6e}"

    d_bins: list[Bin] = field(default_factory=list)
    d_overflow: Bin = field(default_factory=Bin)
    d_underflow: Bin = field(default_factory=Bin)
    d_total: Bin = field(default_factory=Bin)

    def __post_init__(self) -> None:
        GROGU_ANALYSIS_OBJECT.__post_init__(self)
        self.setAnnotation("Type", "Histo1D")

    ############################################
    # YODA compatibility code
    ############################################

    def clone(self) -> "GROGU_HISTO1D_V2":
        return GROGU_HISTO1D_V2(
            d_key=self.d_key,
            d_annotations=self.annotationsDict(),
            d_bins=[b.clone() for b in self.d_bins],
            d_underflow=self.d_underflow,
            d_overflow=self.d_overflow,
            d_total=self.d_total,
        )

    def underflow(self) -> Bin:
        return self.d_underflow

    def overflow(self) -> Bin:
        return self.d_overflow

    def fill(self, x: float, weight: float = 1.0, fraction: float = 1.0) -> None:
        self.d_total.fill(x, weight, fraction)
        for b in self.d_bins:
            if b.contains(x):
                b.fill(x, weight, fraction)
        xmax = self.xMax()
        xmin = self.xMin()
        if x >= xmax and self.d_overflow is not None:
            self.d_overflow.fill(x, weight, fraction)
        if x < xmin and self.d_underflow is not None:
            self.d_underflow.fill(x, weight, fraction)

    def xMax(self) -> float:
        return max(b.d_xmax for b in self.d_bins if b.d_xmax is not None)

    def xMin(self) -> float:
        return min(b.d_xmin for b in self.d_bins if b.d_xmin is not None)

    def bins(self, includeOverflows: bool = False) -> list[Bin]:
        if includeOverflows:
            return [self.d_underflow, *self.d_bins, self.d_overflow]
        # TODO sorted needed here?
        return sorted(self.d_bins, key=lambda b: b.d_xmin or -float("inf"))

    def binAt(self, x: float) -> Optional[Bin]:
        for b in self.bins():
            if b.contains(x):
                return b
        return None

    def binDim(self) -> int:
        return 1

    def xEdges(self) -> list[float]:
        return list(
            {b.d_xmin for b in self.d_bins if b.d_xmin is not None} | {self.xMax()}
        )

    def rebinXTo(self, edges: list[float]) -> None:
        own_edges = self.xEdges()
        for e in edges:
            assert e in own_edges, f"Edge {e} not found in own edges {own_edges}"

        new_bins = []
        for i in range(len(edges) - 1):
            new_bins.append(GROGU_HISTO1D_V2.Bin(d_xmin=edges[i], d_xmax=edges[i + 1]))
        for b in self.bins():
            bm = b.xMid()
            if bm is None:
                err = "Bin has no xMid"
                raise ValueError(err)
            if bm < min(edges):
                self.d_underflow += b
            elif bm > max(edges):
                self.d_overflow += b
            else:
                for i in range(len(edges) - 1):
                    if edges[i] <= bm <= edges[i + 1]:
                        new_bins[i] += b
        self.d_bins = new_bins

        assert len(self.d_bins) == len(self.xEdges()) - 1
        # return self

    def get_projector(self) -> Any:
        return Counter_v2

    def to_string(histo) -> str:
        """Convert a YODA_HISTO1D_V2 object to a formatted string."""
        header = (
            f"BEGIN YODA_HISTO1D_V2 {histo.d_key}\n"
            f"{GROGU_ANALYSIS_OBJECT.to_string(histo)}"
            "---\n"
        )

        # Add the sumw and other info (we assume it's present in the metadata but you could also compute)
        stats = f"# Mean: {histo.xMean():.6e}\n" f"# Area: {histo.integral():.6e}\n"

        underflow = histo.d_underflow.to_string("Underflow")
        overflow = histo.d_overflow.to_string("Overflow")
        total = histo.d_total.to_string("Total")

        xlegend = "# ID\t ID\t sumw\t sumw2\t sumwx\t sumwx2\t numEntries\n"
        legend = "# xlow\t xhigh\t sumw\t sumw2\t sumwx\t sumwx2\t numEntries\n"
        # Add the bin data
        bin_data = "\n".join(b.to_string() for b in histo.bins())

        footer = "END YODA_HISTO1D_V2"

        return f"{header}{stats}{xlegend}{total}\n{underflow}\n{overflow}\n{legend}{bin_data}\n{footer}"

    @classmethod
    def from_string(cls, file_content: str) -> "GROGU_HISTO1D_V2":
        lines = file_content.strip().splitlines()
        key = ""
        if find := re.search(r"BEGIN YODA_HISTO1D_V2 (\S+)", lines[0]):
            key = find.group(1)

        annotations = GROGU_ANALYSIS_OBJECT.from_string(
            file_content=file_content
        ).d_annotations

        # Extract bins and overflow/underflow
        bins = []
        underflow = overflow = total = None
        data_section_started = False

        for line in lines:
            if line.startswith("BEGIN YODA_HISTO1D_V2"):
                continue
            if line.startswith("END YODA_HISTO1D_V2"):
                break
            if line.startswith("#") or line.isspace():
                continue
            if line.startswith("---"):
                data_section_started = True
                continue
            if not data_section_started:
                continue

            values = re.split(r"\s+", line.strip())
            if values[0] == "Underflow":
                underflow = cls.Bin.from_string(line)
            elif values[0] == "Overflow":
                overflow = cls.Bin.from_string(line)
            elif values[0] == "Total":
                total = cls.Bin.from_string(line)
            else:
                # Regular bin
                bins.append(cls.Bin.from_string(line))

        # Create and return the YODA_HISTO1D_V2 object
        if underflow is None or overflow is None or total is None:
            err = "Underflow, overflow or total bin not found"
            raise ValueError(err)
        return cls(
            d_key=key,
            d_annotations=annotations,
            d_bins=bins,
            d_underflow=underflow,
            d_total=total,
            d_overflow=overflow,
        )
