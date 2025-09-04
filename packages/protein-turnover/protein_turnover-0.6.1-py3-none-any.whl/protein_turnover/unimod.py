from __future__ import annotations

from collections import defaultdict
from math import fabs
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Literal
from typing import NamedTuple
from typing import TypedDict

import pandas as pd
from lxml import etree  # type: ignore


# umod = "http://www.unimod.org/xmlns/schema/unimod_2"
URL = "http://www.unimod.org/xml/unimod.xml"

ROWS = [
    "unimod_id",
    "name",
    "description",
    "mono_delta",
    "average_delta",
    "composition",
    "approved",
    "specificities",
]


class Composition(NamedTuple):
    symbol: str
    number: int


class DeltaD(TypedDict):
    mono_mass: float
    avge_mass: float
    composition: list[Composition]


class Unimod(NamedTuple):
    unimod_id: int
    name: str
    approved: bool
    description: str
    specificities: list[Specificity]
    mono_delta: float
    average_delta: float
    composition: list[Composition]


AZ = {chr(s) for s in range(ord("A"), ord("Z") + 1)}


class Specificity(NamedTuple):
    site: str  # Literal["Anywhere", "N-term", "C-term", *AZ]
    position: Literal[
        "Anywhere",
        "Any N-term",
        "Any C-term",
        "Protein N-term",
        "Protein C-term",
    ]
    classification: str
    isCommon: bool
    comment: str | None = None

    def matches(
        self,
        sequence: str,
        modPos: int,
        isProteinTerm: str | None = None,
    ) -> bool:
        def matchSite() -> bool:
            site = self.site
            if site == "Anywhere":
                return True
            if site == "Any N-term":
                return modPos == 1
            if site == "Any C-term":
                return modPos == len(sequence)
            return sequence[modPos - 1] == site

        position = self.position
        if position == "Anywhere":
            return matchSite()
        if position == "Any N-term":
            return modPos == 1 and matchSite()
        if position == "Any C-term":
            return modPos == len(sequence) and matchSite()
        if position == "Protein N-term":
            return isProteinTerm == "N" and matchSite()
        if position == "Protein C-term":
            return isProteinTerm == "C" and matchSite()

        return False


def fetch_unimod_from_web(filename: str = "unimod.xml") -> str:
    # pragma: no cover
    import requests

    resp = requests.get(URL, timeout=10)
    unimod_bytes = resp.content
    print("writing", filename)
    with open(filename, "wb") as fp:
        fp.write(unimod_bytes)
    return filename


class UnimodLookup:
    def __init__(
        self,
        unimods: list[Unimod] | dict[float, list[Unimod]],
        knownMods: Any = None,  # from pepxml file TODO
        massTolerance: float = 2e-5,
    ):
        self.knownMods = knownMods
        self.massTolerance = massTolerance
        if not isinstance(unimods, dict):
            unimodd = defaultdict(list)
            for u in unimods:
                unimodd[u.mono_delta].append(u)

            self.unimods: dict[float, list[Unimod]] = {k: v for k, v in unimodd.items()}
        else:
            self.unimods = unimods

    def create(self, knownMods: Any) -> UnimodLookup:
        return UnimodLookup(self.unimods, knownMods, self.massTolerance)

    def matchModification(
        self,
        sequence: str,
        position: int,
        monoDelta: float,
        isProteinTerm: Literal["N", "C"] | None = None,  # N,C or None
    ) -> list[tuple[Unimod, bool]]:
        """Returns a list or uniprot rows."""
        matchingMassMods = list(
            filter(lambda t: fabs(t - monoDelta) < self.massTolerance, self.unimods),
        )
        if not matchingMassMods:
            return []

        mod_delta_best = sorted(matchingMassMods, key=lambda d: fabs(d - monoDelta))[0]
        ret = []
        for mod in self.unimods[mod_delta_best]:
            matches = [
                s.isCommon
                for s in mod.specificities
                if s.matches(sequence, position, isProteinTerm)
            ]
            if matches:
                ret.append((mod, any(matches)))
        # most common first (this is different from Josh)
        return sorted(ret, key=lambda t: 0 if t[1] else 1)


def nodes(n: etree.Element) -> str:
    return etree.tostring(n).decode("utf-8")


def parse_unimod(root: etree.Element) -> Iterator[Unimod]:
    def specd(spec: etree.Element) -> Specificity:
        notes = " ".join(
            n.text for n in spec.xpath(".//umod:misc_notes", namespaces=root.nsmap)
        )
        d = dict(spec.attrib)

        site = d["site"]
        assert site in {"Anywhere", "N-term", "C-term"} or site in AZ, (
            site,
            nodes(spec),
        )

        pos = d["position"]
        assert pos in {
            "Anywhere",
            "Any N-term",
            "Any C-term",
            "Protein N-term",
            "Protein C-term",
        }, (
            pos,
            nodes(spec),
        )

        d["isCommon"] = d["hidden"] == "0"
        d["comment"] = notes

        for n in ["hidden", "spec_group"]:
            d.pop(n)
        return Specificity(**d)

    def deltad(delta: etree.Element) -> DeltaD:
        return DeltaD(
            mono_mass=float(delta.attrib["mono_mass"]),
            avge_mass=float(delta.attrib["avge_mass"]),
            composition=[
                Composition(
                    **{"symbol": n.attrib["symbol"], "number": int(n.attrib["number"])},
                )
                for n in delta.xpath(".//umod:element", namespaces=root.nsmap)
            ],
        )

    for umod in root.xpath(".//umod:mod", namespaces=root.nsmap):
        a = umod.attrib

        specs = [
            specd(spec)
            for spec in umod.xpath("./umod:specificity", namespaces=root.nsmap)
        ]

        deltas = [
            deltad(delta) for delta in umod.xpath("./umod:delta", namespaces=root.nsmap)
        ]
        assert len(deltas) == 1, nodes(umod)
        delta: DeltaD = deltas[0]

        rec = Unimod(
            unimod_id=int(a["record_id"]),
            name=a["title"],
            approved=bool(a["approved"]),
            description=a["full_name"],
            specificities=specs,  # json.dumps(specs)
            mono_delta=delta["mono_mass"],
            average_delta=delta["avge_mass"],
            composition=delta["composition"],
            # delta=delta,  # used for unimodlookup
        )
        yield rec


def unimodlookup_fromxml(xmlfile: str = "unimod.xml") -> UnimodLookup:
    with open(xmlfile, "rb") as fp:
        x = etree.parse(fp)
    root = x.getroot()
    data = list(parse_unimod(root))
    return UnimodLookup(data)


def make_modcol(
    unimodLookup: UnimodLookup,
    turnover: bool = True,
) -> Callable[[pd.Series], str]:
    # pragma: no cover
    # use with df['modcol'] = df.apply(make_modcol(unimodLookup), axis=1)
    delta, mass = ("monoDelta", "monoMass") if turnover else ("massdiff", "mass")

    def m(peptide: str, modifications: list[dict[str, Any]]) -> Iterator[str]:
        for mod in modifications:
            pos = mod["position"]
            ret = unimodLookup.matchModification(peptide, pos, mod[delta])
            if not ret:
                yield f"{mod[mass]:.3f}@{pos}"
            u, _ = ret[0]
            yield f"{u.name}[{pos}]"

    def modcol(row: pd.Series) -> str:
        return ", ".join(m(row["peptide"], row["modifications"]))

    return modcol


if __name__ == "__main__":
    fetch_unimod_from_web()
