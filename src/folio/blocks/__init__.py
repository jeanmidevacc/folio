"""folio.blocks — all block types re-exported from one place."""
from folio.blocks.asset import DataTable, Plot, Table
from folio.blocks.base import BaseBlock, BlockId, BlockOrPrimitive, ContainerBlock, wrap_block
from folio.blocks.data import DataDive, DataProfile
from folio.blocks.layout import Blocks, Group, Page, Select, SelectType, Toggle, VAlign
from folio.blocks.text import Alert, AlertLevel, BigNumber, Code, Formula, HTML, Text

__all__: list[str] = [
    # base
    "BaseBlock",
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
    "Blocks",
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
    # data
    "DataDive",
    "DataProfile",
]
