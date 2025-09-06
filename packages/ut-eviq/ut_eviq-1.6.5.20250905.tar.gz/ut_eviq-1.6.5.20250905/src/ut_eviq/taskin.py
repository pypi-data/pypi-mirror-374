"""
This module provides task input classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from ut_dic.dic import Dic
from ut_dfr.pddf import PdDf
from ut_path.pathnm import PathNm
from ut_xls.op.ioipathwb import IoiPathWb as OpIoiPathWb

from ut_eviq.utils import Evin
from ut_eviq.utils import Evex
from ut_eviq.utils import Evup

import pandas as pd
import openpyxl as op

from typing import Any, TypeAlias
TyPdDf: TypeAlias = pd.DataFrame
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]

TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnPdDf = None | TyPdDf
TnOpWb = None | TyOpWb


class TaskTmpIn:

    @classmethod
    def evupadm(
            cls, aod_evup_adm: TnAoD, kwargs: TyDic
    ) -> TnOpWb:
        """
        Administration processsing for evup xlsx workbooks
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _in_path_evup_tmp = PathNm.sh_path(_d_cfg['InPath']['evup_tmp'], kwargs)
        _sheet_adm = _d_cfg['_Utils']['sheet']['adm']
        _wb_evup_adm: TnOpWb = OpIoiPathWb.sh_wb_adm(
                _in_path_evup_tmp, aod_evup_adm, _sheet_adm)
        return _wb_evup_adm

    @classmethod
    def evupdel(
            cls, aod_evup_del: TnAoD, kwargs: TyDic
    ) -> TnOpWb:
        """
        Delete processsing for evup xlsx workbooks
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _in_path_evup_tmp = PathNm.sh_path(_d_cfg['InPath']['evup_tmp'], kwargs)
        _sheet_del = _d_cfg['_Utils']['sheet']['del']
        _wb_evup_del: TnOpWb = OpIoiPathWb.sh_wb_del(
                _in_path_evup_tmp, aod_evup_del, _sheet_del)
        return _wb_evup_del

    @classmethod
    def evupreg(
            cls, aod_evup_adm: TnAoD, aod_evup_del: TnAoD, kwargs: TyDic
    ) -> TnOpWb:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _pathnm = Dic.loc(_d_cfg, 'InPath', 'evup_tmp')
        _in_path_evup_tmp = PathNm.sh_path(_pathnm, kwargs)
        _sheet_adm = Dic.loc(_d_cfg, '_Utils', 'sheet', 'adm')
        _sheet_del = Dic.loc(_d_cfg, '_Utils', 'sheet', 'del')
        _wb_evup_reg: TnOpWb = OpIoiPathWb.sh_wb_reg(
           _in_path_evup_tmp, aod_evup_adm, aod_evup_del, _sheet_adm, _sheet_del)
        return _wb_evup_reg


class TaskIn:

    @staticmethod
    def evupadm(
            EvexIoc, kwargs: TyDic
    ) -> tuple[TnAoD, TyDoAoD]:
        """
        Administration processsing for evup
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _aod: TyAoD = Evin.read_wb_adm_to_aod(kwargs)
        _df = EvexIoc.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(_aod, _df, _d_cfg)
        return _tup_adm

    @staticmethod
    def evupdel(
            EvexIoc, kwargs: TyDic
    ) -> tuple[TnAoD, TyDoAoD]:
        """
        Delete processsing for evup
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)

        if Dic.loc(_d_cfg, '_Utils', 'sw_del', 'use_evex'):
            _pddf_evex: TnPdDf = EvexIoc.read_wb_exp_to_df(kwargs)
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                    _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, _d_cfg)
        else:
            _tup_del = Evup.sh_aod_evup_del(_aod_evin_del, _pddf_evin_adm, _d_cfg)

        return _tup_del

    @staticmethod
    def evupreg(
           EvexIoc, kwargs: TyDic
    ) -> tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD]:
        """
        Regular processsing for evup
        """
        _d_cfg: TyDic = Dic.loc(kwargs, 'd_cfg')
        _pddf_evin_adm: TnPdDf = Evin.read_wb_adm_to_df(kwargs)
        _aod_evin_adm: TnAoD = PdDf.to_aod(_pddf_evin_adm)
        _pddf_evex: TnPdDf = EvexIoc.read_wb_exp_to_df(kwargs)
        _tup_adm: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_adm(
                _aod_evin_adm, _pddf_evex, _d_cfg)

        _aod_evin_del: TnAoD = Evin.read_wb_del_to_aod(kwargs)

        if Dic.loc(_d_cfg, '_Utils', 'sw_del', 'use_evex'):
            _aod_evex: TnAoD = PdDf.to_aod(_pddf_evex)
            _tup_del: tuple[TnAoD, TyDoAoD] = Evup.sh_aod_evup_del_use_evex(
                _aod_evin_del, _pddf_evin_adm, _aod_evex, _pddf_evex, _d_cfg)
        else:
            _tup_del = Evup.sh_aod_evup_del(
                _aod_evin_del, _pddf_evin_adm, _d_cfg)

        return _tup_adm + _tup_del

    @staticmethod
    def evdomap(
            EvexIoc, kwargs: TyDic
    ) -> TyAoD:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _d_ecv_iq2umh_iq = Dic.loc(kwargs, 'd_cfg', '_Utils', 'd_ecv_iq2umh_iq')
        _aod = EvexIoc.read_wb_exp_to_aod(kwargs)
        _aod_evex_new: TyAoD = Evex.map(_aod, _d_ecv_iq2umh_iq)
        return _aod_evex_new
