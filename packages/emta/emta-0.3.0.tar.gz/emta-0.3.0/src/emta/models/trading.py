"""Data models for trading operations."""

from dataclasses import asdict, dataclass, field, fields
from decimal import Decimal
from enum import Enum
from typing import TypedDict, TypeVar


@dataclass
class AccountOverview:
    """账户资金总览数据类"""

    Djzj: float  # 冻结资金
    Dryk: float  # 当日盈亏
    Kqzj: float  # 可取资金
    Kyzj: float  # 可用资金
    Ljyk: float  # 累计盈亏
    Money_type: str  # 货币类型
    RMBZzc: float  # 人民币总资产
    Zjye: float  # 资金余额
    Zxsz: float  # 证券市值
    Zzc: float  # 总资产

    def __post_init__(self) -> None:
        # 确保所有数值字段都是浮点数
        for v in fields(self):
            if v.name not in ["Money_type"]:
                value = getattr(self, v.name)
                if isinstance(value, str):
                    setattr(self, v.name, float(value))

    def __str__(self) -> str:
        """格式化打印账户信息"""
        title = "账户资金总览"
        separator = "=" * 50

        # 创建格式化字符串
        lines = [
            separator,
            f"{title:^50}",
            separator,
            f"{'货币类型:':<20} {self.Money_type:>30}",
            f"{'总资产： ':<20} {self.Zzc:>30,.2f}",
            f"{'证券市值:':<20} {self.Zxsz:>30,.2f}",
            f"{'可用资金:':<20} {self.Kyzj:>30,.2f}",
            f"{'可取资金:':<20} {self.Kqzj:>30,.2f}",
            f"{'冻结资金:':<20} {self.Djzj:>30,.2f}",
            f"{'累计盈亏:':<20} {self.Ljyk:>30,.2f}",
            f"{'当日盈亏:':<20} {self.Dryk:>30,.2f}",
            f"{'资金余额:':<20} {self.Zjye:>30,.2f}",
            separator,
        ]

        return "\n".join(lines)


@dataclass
class Position:
    """持仓明细数据类"""

    Bz: str  # 币种
    Cbjg: Decimal  # 成本价格
    Cbjgex: Decimal  # 成本价格(精确)
    Ckcb: Decimal  # 持仓成本
    Ckcbj: Decimal  # 持仓成本价
    Ckyk: Decimal  # 持仓盈亏
    Cwbl: Decimal  # 仓位比例
    Djsl: int  # 冻结数量
    Dqcb: Decimal  # 当前成本
    Dryk: Decimal  # 当日盈亏
    Drykbl: Decimal  # 当日盈亏比例
    Gddm: str  # 股东代码
    Gfmcdj: int  # 股份卖出冻结
    Gfmrjd: int  # 股份买入解冻
    Gfssmmce: int  # 股份上市末码额
    Gfye: int  # 股份余额
    Jgbm: str  # 机构编码
    Khdm: str  # 客户代码
    Ksssl: int  # 可售数量
    Kysl: int  # 可用数量
    Ljyk: Decimal  # 累计盈亏
    Market: str  # 市场
    Mrssc: int  # 买入市场
    Sssl: int  # 申购数量
    Szjsbs: int  # 市值计算标识
    Ykbl: Decimal  # 盈亏比例
    Zjzh: str  # 资金账号
    Zqdm: str  # 证券代码
    Zqlx: str  # 证券类型
    Zqlxmc: str  # 证券类型名称
    Zqmc: str  # 证券名称
    Zqsl: int  # 证券数量
    Ztmc: int  # 状态码
    Ztmr: int  # 状态码
    Zxjg: Decimal  # 最新价格
    Zxsz: Decimal  # 最新市值
    zqzwqc: str  # 证券中文全称
    zxsznew: Decimal  # 最新市值(新)

    def __post_init__(self) -> None:
        # 转换数值类型
        decimal_fields = [
            "Cbjg",
            "Cbjgex",
            "Ckcb",
            "Ckcbj",
            "Ckyk",
            "Cwbl",
            "Dqcb",
            "Dryk",
            "Drykbl",
            "Ljyk",
            "Ykbl",
            "Zxjg",
            "Zxsz",
            "zxsznew",
        ]

        int_fields = [
            "Djsl",
            "Gfmcdj",
            "Gfmrjd",
            "Gfssmmce",
            "Gfye",
            "Ksssl",
            "Kysl",
            "Mrssc",
            "Sssl",
            "Szjsbs",
            "Zqsl",
            "Ztmc",
            "Ztmr",
        ]

        for field_name in decimal_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Decimal(value))

        for field_name in int_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, int(value))


@dataclass
class Portfolio:
    """持仓组合数据类，包含多个持仓"""

    positions: list[Position] = field(default_factory=list)

    def add_position(self, position: Position) -> None:
        """添加持仓"""
        self.positions.append(position)

    def __str__(self) -> str:
        """格式化打印持仓信息"""
        if not self.positions:
            return "暂无持仓"

        # 表头 - 使用固定宽度确保对齐
        headers = [
            "证券名称",
            "证券代码",
            "当前价",
            "持仓数量",
            "成本价",
            "当前市值",
            "累计盈亏",
            "盈亏比例",
        ]
        col_widths = [12, 10, 10, 12, 10, 12, 12, 12]  # 每列宽度

        # 构建表头
        header_line = "".join(
            f"{header:<{width}}"
            for header, width in zip(headers, col_widths, strict=False)
        )
        separator = "-" * sum(col_widths)

        # 构建表格行
        rows = [header_line, separator]
        total_market_value = Decimal("0")
        total_profit_loss = Decimal("0")

        for pos in self.positions:
            # 格式化数据
            name = pos.Zqmc if len(pos.Zqmc) <= 10 else pos.Zqmc[:7] + "..."
            code = pos.Zqdm
            price = f"{pos.Zxjg:.3f}"
            quantity = f"{pos.Zqsl:,}"
            cost = f"{pos.Cbjg:.3f}"
            market_value = f"{pos.Zxsz:,.2f}"
            profit_loss = f"{pos.Ljyk:,.2f}"
            profit_ratio = f"{pos.Ykbl:.2%}"

            # 构建行
            row_data = [
                name,
                code,
                price,
                quantity,
                cost,
                market_value,
                profit_loss,
                profit_ratio,
            ]
            row = "".join(
                f"{data:<{width}}"
                for data, width in zip(row_data, col_widths, strict=False)
            )
            rows.append(row)

            # 累加总市值和总盈亏
            total_market_value += pos.Zxsz
            total_profit_loss += pos.Ljyk

        # 添加总计行
        rows.append(separator)
        total_row_data = [
            "总计",
            "",
            "",
            "",
            "",
            f"{total_market_value:,.2f}",
            f"{total_profit_loss:,.2f}",
            "",
        ]
        total_row = "".join(
            f"{data:<{width}}"
            for data, width in zip(total_row_data, col_widths, strict=False)
        )
        rows.append(total_row)

        return "\n".join(rows)


class OrderType(Enum):
    """Order types for trading"""

    BUY = "B"
    SELL = "S"


class OrderStatus(Enum):
    """Order status types"""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order"""

    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    order_id: str | None = None
    status: OrderStatus = OrderStatus.PENDING


class AccountInfo(TypedDict):
    """Represents account information"""

    username: str
    account_overview: AccountOverview
    portfolio: Portfolio


class MarketData(TypedDict):
    """Represents market data for a symbol"""

    symbol: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    timestamp: str


T = TypeVar("T")


@dataclass
class OrderRecord:
    """交易记录数据类（仅包含关键字段）"""

    Zqdm: str  # 证券代码
    Zqmc: str  # 证券名称
    order_id: str  # 订单编号
    Mmsm: str  # 操作类型
    Wtsl: str  # 委托数量
    Wtjg: str  # 委托价格
    Wtzt: str  # 委托状态
    Cjsl: str  # 成交数量
    Cjje: str  # 成交金额

    def __str__(self) -> str:
        """格式化输出单条记录"""
        return (
            f"证券代码: {self.Zqdm} | 证券名称: {self.Zqmc} | 订单编号: {self.order_id}\n"
            f"操作类型: {self.Mmsm} | 委托数量: {self.Wtsl} | 委托价格: {self.Wtjg}\n"
            f"委托状态: {self.Wtzt} | 成交数量: {self.Cjsl} | 成交金额: {self.Cjje}\n"
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "OrderRecord":
        """从字典创建实例（仅提取关键字段）"""
        return cls(
            Zqdm=data.get("Zqdm", ""),
            Zqmc=data.get("Zqmc", ""),
            Mmsm=data.get("Mmsm", ""),
            Wtsl=data.get("Wtsl", ""),
            Wtjg=data.get("Wtjg", ""),
            Wtzt=data.get("Wtzt", ""),
            Cjsl=data.get("Cjsl", ""),
            Cjje=data.get("Cjje", ""),
            order_id=f"{data.get('Wtrq', '')}_{data.get('Wtbh', '')}",
        )

    def to_dict(self) -> dict[str, str]:
        """转换为字典"""
        return asdict(self)
