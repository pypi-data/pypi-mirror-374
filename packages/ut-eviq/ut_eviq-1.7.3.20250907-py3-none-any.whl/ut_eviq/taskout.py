"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
import openpyxl as op

from ut_path.pathnm import PathNm
from ut_xls.op.ioopathwb import IooPathWb as OpIooPathWb
from ut_xls.pe.ioopathwb import IooPathWb as PeIooPathWb

from ut_eviq.cfg import Cfg
from ut_eviq.taskin import TaskTmpIn

from typing import Any
TyOpWb = op.workbook.workbook.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb
TnPath = None | TyPath


class TaskOut:

    @classmethod
    def evupadm(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm

        _path = PathNm.sh_path(Cfg.OutPath.evup_adm, kwargs)
        OpIooPathWb.write(TaskTmpIn.evupadm(_aod_evup_adm, kwargs), _path)

        _out_path_evin_adm_vfy = PathNm.sh_path(Cfg.OutPath.evin_adm_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_adm_vfy, _out_path_evin_adm_vfy)

    @classmethod
    def evupdel(cls, tup_del: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _aod_evup_del, _doaod_evin_del_vfy = tup_del

        _wb: TnOpWb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        _path: TyPath = PathNm.sh_path(Cfg.OutPath.evup_del, kwargs)
        OpIooPathWb.write(_wb, _path)

        _path = PathNm.sh_path(Cfg.OutPath.evin_del_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod_evin_del_vfy, _path)

    @classmethod
    def evupreg_reg_wb(
            cls, tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del

        _wb: TnOpWb = TaskTmpIn.evupreg(_aod_evup_adm, _aod_evup_del, kwargs)
        _path = PathNm.sh_path(Cfg.OutPath.evup_reg, kwargs)
        OpIooPathWb.write(_wb, _path)

        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        _path = PathNm.sh_path(Cfg.OutPath.evin_reg_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod, _path)

    @classmethod
    def evupreg_adm_del_wb(
            cls,
            tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del

        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        _path: TnPath = PathNm.sh_path(Cfg.OutPath.evup_adm, kwargs)
        OpIooPathWb.write(_wb, _path)

        _wb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        _path = PathNm.sh_path(Cfg.OutPath.evup_del, kwargs)
        OpIooPathWb.write(_wb, _path)

        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        _path = PathNm.sh_path(Cfg.OutPath.evin_reg_vfy, kwargs)
        PeIooPathWb.write_wb_from_doaod(_doaod, _path)

    @classmethod
    def evdomap(cls, aod_evex: TyAoD, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        _path: TnPath = PathNm.sh_path(Cfg.OutPath.evex, kwargs)
        _sheet = Cfg.sheet_exp
        PeIooPathWb.write_wb_from_aod(aod_evex, _path, _sheet)
