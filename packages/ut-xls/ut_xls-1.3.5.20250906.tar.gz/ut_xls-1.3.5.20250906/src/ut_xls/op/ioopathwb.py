from typing import Any, TypeAlias

# import openpyxl as op
from openpyxl import Workbook

from ut_xls.op.doaod import DoAoD

# TyOpWb: TypeAlias = op.workbook.workbook.Workbook
TyOpWb: TypeAlias = Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathnm = str
TySheet = int | str

TnPath = None | TyPath
TnOpWb = None | TyOpWb


class IooPathWb:

    @staticmethod
    def write(wb: TnOpWb, path: TnPath) -> None:
        if wb is None or not path:
            return
        wb.save(path)

    @classmethod
    def write_wb_from_doaod(cls, doaod: TyDoAoD, path: TnPath) -> None:
        if not doaod or not path:
            return
        # wb: TyOpWb = DoAoD.create_wb(doaod)
        cls.write(DoAoD.create_wb(doaod), path)
