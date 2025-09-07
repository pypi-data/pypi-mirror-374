"""
This module provides utilities classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias, TextIO, BinaryIO

import pandas as pd
from pathlib import Path

from ut_dic.dic import Dic
from ut_path.pathnm import PathNm
from ut_xls.pd.ioipathwb import IoiPathWb

TyPdDf: TypeAlias = pd.DataFrame
TyXls: TypeAlias = pd.ExcelFile

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPdFileSrc = str | bytes | TyXls | Path | TextIO | BinaryIO
TySheet = int | str

TnDic = None | TyDic
TnAoD = None | TyAoD
TnPdDf = None | TyPdDf
TnSheet = None | TySheet


class EvexIoc:
    """
    EcoVadis Export class
    """
    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def read_wb_exp_to_df(cls, kwargs: TyDic) -> TnPdDf:
        _d_cfg = Dic.loc(kwargs, 'd_cfg')
        _io: TyPdFileSrc = PathNm.sh_path(Dic.loc(_d_cfg, 'InPath', 'evex'), kwargs)
        _sheet: TnSheet = Dic.loc(_d_cfg, 'sheet_exp')
        _pddf: TnPdDf = IoiPathWb.read_wb_to_df(_io, _sheet, **cls.kwargs_wb)
        return _pddf

    @classmethod
    def read_wb_exp_to_aod(cls, kwargs: TyDic) -> TnAoD:
        _io: TyPdFileSrc = PathNm.sh_path(
                Dic.loc(kwargs, 'd_cfg', 'InPath', 'evex'), kwargs)
        _sheet: TnSheet = Dic.loc(kwargs, 'd_cfg', 'sheet_exp')
        _aod: TnAoD = IoiPathWb.read_wb_to_aod(_io, _sheet, **cls.kwargs_wb)
        return _aod
