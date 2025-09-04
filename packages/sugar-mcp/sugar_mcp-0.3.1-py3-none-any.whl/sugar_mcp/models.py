from typing import Optional

from netmind_sugar.token import Token as S_Token
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Token(S_Token):
    wrapped_token_address: Optional[str] = None


@dataclass(frozen=True)
class LiquidityPool:
    address: str
    token0: Token
    token1: Token
    total_supply: int
    reserves: dict
