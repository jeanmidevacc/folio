"""bulletin.blocks — core block types re-exported from one place.

Custom-visualisation blocks (DataProfile, DataDive) live in ``bulletin.lab``.
"""
from bulletin.blocks.asset import DataTable, Plot, Table
from bulletin.blocks.base import Block, BlockId, BlockOrPrimitive, ContainerBlock, wrap_block
from bulletin.blocks.layout import Bulletin, Group, Page, Select, SelectType, Toggle, VAlign
from bulletin.blocks.text import HTML, Alert, AlertLevel, BigNumber, Code, Formula, Text

__all__: list[str] = [
    # base
    "Block",
    "BlockId",
    "BlockOrPrimitive",
    "ContainerBlock",
    "wrap_block",
    # text
    "Alert",
    "AlertLevel",
    "BigNumber",
    "Code",
    "Formula",
    "HTML",
    "Text",
    # layout
    "Bulletin",
    "Group",
    "Page",
    "Select",
    "SelectType",
    "Toggle",
    "VAlign",
    # asset
    "DataTable",
    "Plot",
    "Table",
]
