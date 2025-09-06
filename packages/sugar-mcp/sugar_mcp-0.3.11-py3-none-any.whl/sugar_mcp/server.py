import json
import os

from mcp.server.fastmcp import FastMCP
from netmind_sugar.chains import get_chain, OPChain, Token
from sugar_mcp.models import asdict

from typing import Literal, Optional
from functools import lru_cache


mcp = FastMCP("sugar-mcp")


@mcp.tool()
async def get_all_tokens(limit: int, offset: int, chain_id: str = "10"):
    """
    Retrieve all tokens supported by the protocol.

    Args:
        limit (int): Maximum number of tokens to return.
        offset (int): The starting point to retrieve tokens.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Token]: A list of Token objects.
    """
    with get_chain(chain_id) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: Token.from_tuple(
                    t, chain_id=chain.chain_id, chain_name=chain.name
                ),
                tokens,
            )
        )
        return json.dumps([asdict(t) for t in tokens])


@mcp.tool()
async def get_token_prices(token_address: str, chain_id: str = "10"):
    """
    Retrieve prices for a specific token in terms of the stable token.

    Args:
        token_address (str): The address of the token to retrieve prices for.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Price]: A list of Price objects with token-price mappings.
    """
    with get_chain(chain_id) as chain:
        append_stable = False
        append_native = False

        tokens = [chain.get_token(token_address)]
        if chain.settings.stable_token_addr.lower() != token_address.lower():
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() != token_address.lower():
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        if append_stable:
            # 如果在获取价格的时候加上了稳定币，在返回结果的时候再从列表里去掉，否则外部应用在传offset的时候会有问题
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]
        return json.dumps([asdict(p) for p in prices])


@mcp.tool()
async def get_prices(
    limit: int, offset: int, listed_only: bool = False, chain_id: str = "10"
):
    """
    Retrieve prices for a list of tokens in terms of the stable token.

    Args:
        limit (int): Maximum number of prices to return.
        offset (int): The starting point to retrieve prices.
        listed_only (bool): If True, only return prices for tokens that are marked as 'listed'.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[Price]: A list of Price objects with token-price mappings.
    """
    with get_chain(chain_id) as chain:
        tokens = chain.get_tokens_page(limit, offset)
        tokens = list(
            map(
                lambda t: Token.from_tuple(
                    t, chain_id=chain.chain_id, chain_name=chain.name
                ),
                tokens,
            )
        )

        append_stable = False
        append_native = False

        # 因为get price里需要用到稳定币的价格来计算usd的汇率，这里给tokens里加上一个稳定币
        token_address_list = [t.token_address.lower() for t in tokens]
        if chain.settings.stable_token_addr.lower() not in token_address_list:
            tokens.append(chain.get_token(chain.settings.stable_token_addr))
            append_stable = True

        if chain.settings.native_token_symbol.lower() not in token_address_list:
            tokens.append(
                Token.make_native_token(
                    chain.settings.native_token_symbol,
                    chain.settings.wrapped_native_token_addr,
                    chain.settings.native_token_decimals,
                    chain_id=chain.chain_id,
                    chain_name=chain.name,
                )
            )
            append_native = True

        prices = chain.get_prices(tokens)
        if append_stable:
            # 如果在获取价格的时候加上了稳定币，在返回结果的时候再从列表里去掉，否则外部应用在传offset的时候会有问题
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.stable_token_addr.lower()
            ]

        if append_native:
            prices = [
                p
                for p in prices
                if p.token.token_address.lower()
                != chain.settings.native_token_symbol.lower()
            ]

        return json.dumps([asdict(t) for t in prices])


@mcp.tool()
async def get_pools(limit: int, offset: int, chain_id: str = "10"):
    """
    Retrieve all raw liquidity pools.

    Args:
        limit (int): The maximum number of pools to retrieve.
        offset (int): The starting point for pagination.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPool] or List[LiquidityPoolForSwap]: A list of pool objects.
    """
    with get_chain(chain_id) as chain:
        pools = chain.get_pools_page(limit, offset)
        return json.dumps([asdict(p) for p in pools])


@mcp.tool()
async def get_pool_by_address(address: str, chain_id: str = "10"):
    """
    Retrieve a raw liquidity pool by its contract address.

    Args:
        address (str): The address of the liquidity pool contract.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        Optional[LiquidityPool]: The matching LiquidityPool object, or None if not found.
    """
    with get_chain(chain_id) as chain:
        try:
            pool = chain.get_pool_by_address(address)
        except Exception as e:
            return json.dumps({"error": str(e)})
        if pool is None:
            return json.dumps(None)
        return json.dumps(asdict(pool))


@mcp.tool()
async def get_pools_for_swaps(limit: int, offset: int, chain_id: str = "10"):
    """
    Retrieve all raw liquidity pools suitable for swaps.

    Args:
        limit (int): The maximum number of pools to retrieve.
        offset (int): The starting point for pagination.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolForSwap]: A list of simplified pool objects for swaps.
    """
    with get_chain(chain_id) as chain:
        pools = chain.get_pools_page(limit, offset, for_swaps=True)
        return json.dumps([asdict(p) for p in pools])


@mcp.tool()
async def get_latest_pool_epochs(
    offset: int, limit: int = 10, chain_id: str = "10"
):
    """
    Retrieve the latest epoch data for all pools.

    Args:
        limit (int): The maximum number of epochs to retrieve.
        offset (int): The starting point for pagination.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpoch]: A list of the most recent epochs across all pools.
    """
    with get_chain(chain_id) as chain:
        epochs = chain.get_latest_pool_epochs_page(limit, offset)
        return json.dumps([asdict(p) for p in epochs])


@mcp.tool()
async def get_pool_epochs(
    lp: str, offset: int = 0, limit: int = 10, chain_id: str = "10"
):
    """
    Retrieve historical epoch data for a given liquidity pool.

    Args:
        lp (str): Address of the liquidity pool.
        offset (int): Offset for pagination.
        limit (int): Number of epochs to retrieve.
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        List[LiquidityPoolEpoch]: A list of epoch entries for the specified pool.
    """
    with get_chain(chain_id) as chain:
        epochs = chain.get_pool_epochs_page(lp, offset, limit)
        return json.dumps([asdict(p) for p in epochs])


@mcp.tool()
async def get_quote(
    from_token: str,
    to_token: str,
    amount: int,
    chain_id: str = "10",
):
    """
    Retrieve the best quote for swapping a given amount from one token to another.

    Args:
        from_token (str): The token to swap from. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        to_token (str): The token to swap to. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        amount (int): The amount to swap (in int, not uint256).
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)
        filter_quotes (Callable[[Quote], bool], optional): Optional filter to apply on the quotes.

    Returns:
        Optional[Quote]: The best available quote, or None if no valid quote was found.
    """
    
    if chain_id == "10" and (from_token not in ["usdc", "velo", "eth", "o_usdt"] or to_token not in ["usdc", "velo", "eth", "o_usdt"]):
        raise ValueError("Only 'usdc', 'velo', 'eth', and 'o_usdt' are supported on OPChain.")

    if chain_id == "130" and (from_token not in ["o_usdt", "usdc"] or to_token not in ["o_usdt", "usdc"]):
        raise ValueError("Only 'o_usdt' and 'usdc' are supported on Unichain.")

    if chain_id == "1135" and (from_token not in ["o_usdt", "lsk", "eth", "usdt"] or to_token not in ["o_usdt", "lsk", "eth", "usdt"]):
        raise ValueError("Only 'o_usdt', 'lsk', 'eth', and 'usdt' are supported on List.")

    if chain_id == "8453" and (from_token not in ["usdc", "aero", "eth"] or to_token not in ["usdc", "aero", "eth"]):
        raise ValueError("Only 'usdc', 'aero', and 'eth' are supported on BaseChain.")

    with get_chain(chain_id) as chain:
        from_token = getattr(chain, from_token, None)
        to_token = getattr(chain, to_token, None)
        if from_token is None or to_token is None:
            raise ValueError("Invalid token specified.")

        quote = chain.get_quote(from_token, to_token, amount)
        return json.dumps(asdict(quote))


@mcp.tool()
async def swap(
    from_token: str,
    to_token: str,
    amount: int,
    slippage: Optional[float] = None,
    chain_id: str = "10",
):
    """
    Execute a token swap transaction.

    Args:
        from_token (str): The token being sold. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        to_token (str): The token being bought. For OPchain, this can be 'usdc', 'velo', 'eth', or 'o_usdt'. For BaseChain, this can be 'usdc', 'aero', or 'eth'. For Unichain, this can be 'o_usdt' or 'usdc'. For Lisk, this can be 'o_usdt', 'lsk', 'eth', or 'usdt'.
        amount (int): The amount of `from_token` to swap.
        slippage (float, optional): Maximum acceptable slippage (default uses config value).
        chain_id (str): The chain ID to use ('10' for OPChain, '8453' for BaseChain, '130' for Unichain, '1135' for List)

    Returns:
        TransactionReceipt: The transaction receipt from the swap execution.
    """

    if chain_id == "10" and (from_token not in ["usdc", "velo", "eth", "o_usdt"] or to_token not in ["usdc", "velo", "eth", "o_usdt"]):
        raise ValueError("Only 'usdc', 'velo', 'eth', and 'o_usdt' are supported on OPChain.")

    if chain_id == "130" and (from_token not in ["o_usdt", "usdc"] or to_token not in ["o_usdt", "usdc"]):
        raise ValueError("Only 'o_usdt' and 'usdc' are supported on Unichain.")

    if chain_id == "1135" and (from_token not in ["o_usdt", "lsk", "eth", "usdt"] or to_token not in ["o_usdt", "lsk", "eth", "usdt"]):
        raise ValueError("Only 'o_usdt', 'lsk', 'eth', and 'usdt' are supported on List.")

    if chain_id == "8453" and (from_token not in ["usdc", "aero", "eth"] or to_token not in ["usdc", "aero", "eth"]):
        raise ValueError("Only 'usdc', 'aero', and 'eth' are supported on BaseChain.")
    
    with get_chain(chain_id) as chain:
        from_token = getattr(chain, from_token, None)
        to_token = getattr(chain, to_token, None)
        if from_token is None or to_token is None:
            raise ValueError("Invalid token specified. Use 'usdc', 'velo', or 'eth'.")

        tx_hash = chain.swap(from_token, to_token, amount, slippage)
        return tx_hash


def main():
    if not os.environ.get("SUGAR_PK"):
        raise ValueError(
            "Environment variable SUGAR_PK is not set. Please set it to your private key."
        )
    print("Starting Sugar MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
