"""
This module provides task input output control classes for the management of Sustainability Risk Rating (SRR) processing.
"""

# import pandas as pd
import openpyxl as op

from ut_eviq.taskin import TaskIn
from ut_eviq.taskout import TaskOut
from ut_eviq.xls.utils import EvexIoc
import ut_eviq.cfg as Cfg

from typing import Any, TypeAlias
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb


class TaskIoc:
    """
    I/O Control Tasks class for EcoVadis IQ upload Excel workbooks
    """
    @staticmethod
    def set_kwargs(kwargs: TyDic) -> None:
        _d_cfg = kwargs.get('d_cfg', Cfg)
        _d_sw_adm = _d_cfg['Utils']['d_sw_adm']
        _d_sw_adm['vfy'] = kwargs.get('sw_adm_vfy', True)
        _d_sw_adm['vfy_duns'] = kwargs.get('sw_adm_vfy_duns', True)
        _d_sw_adm['vfy_duns_is_unique'] = kwargs.get('sw_adm_vfy_duns_is_unique', True)
        _d_sw_adm['vfy_cpydinm'] = kwargs.get('sw_adm_vfy_cpydinm', True)
        _d_sw_adm['vfy_regno'] = kwargs.get('sw_adm_vfy_regno', True)
        _d_sw_adm['vfy_coco'] = kwargs.get('sw_adm_vfy_coco', True)
        _d_sw_adm['vfy_objectid'] = kwargs.get('sw_adm_vfy_objectid', True)
        _d_sw_adm['vfy_objectid_is_unique'] = kwargs.get(
                'sw_adm_vfy_objectid_is_unique', True)
        _d_sw_adm['vfy_town'] = kwargs.get('sw_adm_vfy_town', False)
        _d_sw_adm['vfy_poco'] = kwargs.get('sw_adm_vfy_poco', True)
        _d_sw_adm['use_duns'] = kwargs.get('sw_adm_vfy_duns', True)

        _d_sw_del = _d_cfg['Utils']['d_sw_del']
        _d_sw_del['vfy'] = kwargs.get('sw_del_vfy', True)
        _d_sw_del['vfy_objectid'] = kwargs.get('sw_del_vfy_objectid', True)
        _d_sw_del['vfy_objectid_is_unique'] = kwargs.get(
                'sw_del_vfy_objectid_is_unique', True)
        _d_sw_del['vfy_iq_id'] = kwargs.get('sw_del_vfy_iq_id', True)
        _d_sw_del['vfy_iq_id_is_unique'] = kwargs.get(
                'sw_del_vfy_iq_id_is_unique', True)
        _d_sw_del['use_duns'] = kwargs.get('sw_del_use_duns', True)

    @classmethod
    def evupadm(cls, kwargs: TyDic) -> None:
        """
        Administration processsing for EcoVadis IQ upload Excel workbooks
        """
        cls.set_kwargs(kwargs)
        TaskOut.evupadm(TaskIn.evupadm(EvexIoc, kwargs), kwargs)

    @classmethod
    def evupdel(cls, kwargs: TyDic) -> None:
        """
        Delete processsing for EcoVadis IQ upload Excel workbooks
        """
        cls.set_kwargs(kwargs)
        TaskOut.evupdel(TaskIn.evupdel(EvexIoc, kwargs), kwargs)

    @classmethod
    def evupreg(cls, kwargs: TyDic) -> None:
        """
        Regular processsing for EcoVadis IQ upload Excel workbooks
        Regular Processing (create, update, delete) of partners using
          single Xlsx Workbook with a populated admin- or delete-sheet
          two xlsx Workbooks:
            the first one contains a populated admin-sheet
            the second one contains a populated delete-sheet
        """
        cls.set_kwargs(kwargs)
        _sw_single_wb: TyBool = kwargs.get('sw_single_wb', True)
        if _sw_single_wb:
            # write single workbook which contains admin and delete worksheets
            TaskOut.evupreg_reg_wb(TaskIn.evupreg(EvexIoc, kwargs), kwargs)
        else:
            # write separate workbooks for admin and delete worksheets
            TaskOut.evupreg_adm_del_wb(TaskIn.evupreg(EvexIoc, kwargs), kwargs)

    @classmethod
    def evdomap(cls, kwargs: TyDic) -> None:
        """
        EcoVadis Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        cls.set_kwargs(kwargs)
        TaskOut.evdomap(TaskIn.evdomap(EvexIoc, kwargs), kwargs)
