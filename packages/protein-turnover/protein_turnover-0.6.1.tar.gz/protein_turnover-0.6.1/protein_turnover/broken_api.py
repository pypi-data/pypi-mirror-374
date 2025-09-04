from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Any
from typing import Iterator

import pandas as pd
from more_itertools import ichunked
from pymzml.run import Reader
from typing_extensions import override

from .logger import log_iterator
from .pepxml_reader import chop_spectrum

# https://github.com/levitsky/pyteomics/blob/b9fabac991d2da524b4700af871e56f6a255f924/pyteomics/pepxml.py#L349
# taken from pyteomics.pepxml:DataFrame

# UNUSED: see pepxml_reader.py
if False:  #  pragma: no cover
    from pyteomics.pepxml import PepXML

    def fix_mods(mods: list[dict]) -> Iterator[dict]:
        for m in mods:
            if "variable" in m:
                yield dict(
                    mass=m["mass"],
                    position=m["position"],
                    massdiff=m["variable"],
                )

            elif "static" in m:
                yield dict(
                    mass=m["mass"],
                    position=m["position"],
                    massdiff=m["static"],
                )
            else:
                # both these are optional but one must exist?
                yield dict(mass=m["mass"], position=m["position"])

    def dict_to_series(item: dict[str, Any]) -> dict[str, Any]:
        info: dict[str, Any] = {}
        for k, v in item.items():
            if isinstance(v, (str, int, float)):
                info[k] = v
        if "search_hit" in item:
            sh = item["search_hit"][0]  # first element
            proteins = sh.pop("proteins")

            # list of dicts to dict of lists
            prot_dict: dict[str, list[Any]] = {}
            for p in proteins:
                for k in p:
                    prot_dict[k] = []
            for p in proteins:
                for k, v in prot_dict.items():
                    v.append(p.get(k))
            prot_dict["proteins"] = prot_dict.pop("protein")
            prot_dict["protein_descr"] = [
                p if p is not None else "" for p in prot_dict["protein_descr"]
            ]
            info.update(prot_dict)

            info.update(sh.pop("search_score"))
            mods = sh.pop("modifications", [])
            info["modifications"] = list(fix_mods(mods))

            for k, v in sh.items():
                if isinstance(v, (str, int, float)):
                    info[k] = v
            if "analysis_result" in sh:
                for ar in sh["analysis_result"]:
                    if ar["analysis"] == "peptideprophet":
                        result = ar["peptideprophet_result"]
                        try:
                            info.update(result["parameter"])
                        except KeyError:
                            pass
                        info["peptideprophet_probability"] = result["probability"]
                        info["peptideprophet_ntt_prob"] = result["all_ntt_prob"]
                    elif ar["analysis"] == "interprophet":
                        result = ar["interprophet_result"]
                        info.update(result["parameter"])
                        info["interprophet_probability"] = result["probability"]
                        info["interprophet_ntt_prob"] = result["all_ntt_prob"]

        info["run"] = chop_spectrum(info["spectrum"])
        # is_rejected: Potential use in future for user manual validation (0 or 1)
        if "is_rejected" in info:
            info.pop("is_rejected")
        if "xcorr" in info:
            info["searchEngineScore"] = info["xcorr"]  # COMET
        elif "ionscore" in info:
            info["searchEngineScore"] = info["ionscore"]  # MASCOT

        return info

    def pepxml_chunk(
        chunk: Iterator[dict[str, Any]],
        **kwargs: Any,
    ) -> pd.DataFrame | None:
        lst = [dict_to_series(r) for r in chunk]
        if not lst:
            return None
        return pd.DataFrame(lst, **kwargs)

    def PepXMLDataFrame(
        filename: Path,
        stop: int | None = None,
        start: int = 0,
        step: int = 1,
        level: int = 0,
        number_of_bg_processes: int = 0,
        **kwargs: Any,
    ) -> pd.DataFrame:
        from .config import PEPXML_CHUNKS

        pep = Path(filename)

        it = PepXML(str(filename), use_index=True)  # need to get total
        total = len(it)
        if stop is not None or start != 0 or step != 1:
            # find size
            if stop is None:
                stop = total
            else:
                stop = min(stop, total)
            r = range(start, stop, step)
            total = len(r)
            it = islice(it, r.start, r.stop, r.step)
        ret = []
        it = log_iterator(
            it,
            total=total,
            level=level,
            desc=f"{pep.name}",
            number_of_bg_processes=number_of_bg_processes,
        )
        for chunk in ichunked(it, PEPXML_CHUNKS):
            df = pepxml_chunk(chunk, **kwargs)
            if df is None:
                continue
            ret.append(df)

        if not ret:
            raise RuntimeError(f"{pep.name}: no runs!")

        return pd.concat(ret, axis=0, ignore_index=True)


# at least version 2.5.2
class PyMzMLReader(Reader):
    @override
    def term_is_a_member(self, tested_term, member_of_term):
        """shutup to the KeyError print statement"""
        try:
            self.OT[tested_term]
        except KeyError:  # pragma: no cover
            return False
        return super().term_is_a_member(tested_term, member_of_term)


def ProtXmlDataFrame(
    protxml: Path,
    level: int = 0,
    number_of_bg_processes: int = 0,
) -> pd.DataFrame:
    from pyteomics.protxml import ProtXML
    from .logger import log_iterator

    prot = ProtXML(str(protxml))
    total = len(prot)

    def gen_items(prot: ProtXML) -> Iterator[dict[str, Any]]:
        with prot as f:
            for item in f:
                info = {}
                # probability 1.0
                # group_number 1
                # protein [{}, {}]
                for k, v in item.items():
                    if isinstance(v, (str, int, float)):
                        info[k] = v
                if "protein" in item:
                    for prot in item["protein"]:
                        # protein_name contam_sp|P02769|ALBU_BOVIN
                        # n_indistinguishable_proteins 1
                        # probability 1.0
                        # percent_coverage 53.0
                        # unique_stripped_peptides ['AEFVEVTK', 'ATEEQLK', 'CCTESLVNR', 'CCTKPESER', 'DDPHACYSTVFDK', 'EACFAVEGPK', ]
                        # group_sibling_id a
                        # total_number_peptides 72
                        # total_number_distinct_peptides 72
                        # confidence 1.0
                        # protein_description Serum albumin OS=Bos taurus GN=ALB PE=1 SV=4
                        # pct_spectrum_ids 0.322
                        # prot_length 607
                        # peptide [{}, {}]

                        #
                        # peptide : {
                        # 'peptide_sequence': 'CCTESLVNR',
                        # 'charge': 2,
                        # 'initial_probability': 0.999,
                        # 'nsp_adjusted_probability': 0.9996,
                        # 'fpkm_adjusted_probability': 0.9996,
                        # 'weight': 1.0,
                        # 'group_weight': '1.00',
                        # 'n_enzymatic_termini': 2,
                        # 'n_sibling_peptides': 41.14,
                        # 'n_sibling_peptides_bin': 9,
                        # 'n_instances': 4,
                        # 'exp_tot_instances': 3.93,
                        # 'calc_neutral_pep_mass': 1137.4906,
                        # 'peptide_parent_protein': [{'protein_name': 'sp|P02768|ALBU_HUMAN'}],
                        # 'is_nondegenerate_evidence': False,
                        # 'is_contributing_evidence': True,
                        # 'modified_peptide': 'CCTESLVNR',
                        # 'mod_aminoacid_mass': [{position:1, mass:160.03}, ...]
                        # }
                        out = dict(info)
                        out.update(prot)
                        if "indistinguishable_protein" in out:
                            out["indistinguishable_protein"] = [
                                p["protein_name"]
                                for p in out["indistinguishable_protein"]
                            ]
                        else:
                            out["indistinguishable_protein"] = []
                        yield out

    it = log_iterator(
        gen_items(prot),
        total=total,
        level=level,
        desc=f"{protxml.name}",
        number_of_bg_processes=number_of_bg_processes,
    )

    return pd.DataFrame(it)
