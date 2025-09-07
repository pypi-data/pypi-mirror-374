# Contract Return Values Guide

## Overview

The StandardWeb3 contract interaction functions have been enhanced to capture and return values from contract function calls. This guide explains how to access these return values in your applications.

## Changes Made

### 1. Enhanced Transaction Execution

The `_execute_transaction` method now returns a comprehensive dictionary instead of just the transaction receipt:

```python
{
    "tx_receipt": tx_receipt,      # Full transaction receipt
    "tx_hash": tx_hash_string,     # Transaction hash as hex string
    "return_values": decoded_logs, # Decoded event logs (if any)
    "gas_used": gas_amount,        # Gas consumed by transaction
    "status": 1_or_0              # Transaction status (1=success, 0=failed)
}
```

### 2. Updated Function Return Types

All trading functions now return `dict` instead of `str`:
- `market_buy()` → returns `dict`
- `market_sell()` → returns `dict`
- `limit_buy()` → returns `dict`
- `limit_sell()` → returns `dict`
- `cancel_orders()` → returns `dict`

### 3. New View Functions

Added view functions that return values directly without transactions:

```python
# Get order details
order = await client.contract.get_order(base, quote, is_bid, order_id)
# Returns: {"owner": address, "price": int, "deposit_amount": int}

# Get pair address
pair = await client.contract.get_pair(base, quote)
# Returns: pair_address (string)

# Get market price
price = await client.contract.get_market_price(base, quote)
# Returns: price (int)

# Get order book heads
heads = await client.contract.get_heads(base, quote)
# Returns: {"bid_head": int, "ask_head": int}

# Convert between tokens
converted = await client.contract.convert(base, quote, amount, is_bid)
# Returns: converted_amount (int)

# Get trading fee
fee = await client.contract.get_fee_of(base, quote, account, is_maker)
# Returns: fee_amount (int)
```

## Usage Examples

### Basic Transaction with Return Values

```python
# Execute a limit buy order
result = await client.contract.limit_buy(
    base=base_token,
    quote=quote_token,
    price=price,
    quote_amount=quote_amount,
    is_maker=True,
    n=1,
    recipient=client.address,
)

# Access transaction details
print(f"TX Hash: {result['tx_hash']}")
print(f"Gas used: {result['gas_used']}")
print(f"Status: {'Success' if result['status'] == 1 else 'Failed'}")

# Access decoded events
if result['return_values']:
    for event in result['return_values']:
        print(f"Event: {event['event']}")
        print(f"Args: {event['args']}")
```

### View Function Calls

```python
# Get current market price
price = await client.contract.get_market_price(base_token, quote_token)
print(f"Current price: {price}")

# Get order details
order = await client.contract.get_order(base_token, quote_token, True, order_id)
print(f"Order owner: {order['owner']}")
print(f"Order price: {order['price']}")
```

## Important Notes

### Event Decoding Limitations

The current implementation attempts to decode common events (`OrderPlaced`, `OrderMatched`, `OrderCanceled`). However:

1. **Solidity return values are not automatically emitted as events**
2. **The actual return values (like `OrderResult` struct) may not appear in events**
3. **Custom events need to be specifically handled**

### Recommended Approach for Return Values

For functions that return structured data (like `OrderResult`), consider:

1. **Use view functions when possible** - They return values directly
2. **Look for specific events** - Many contracts emit events with return data
3. **Call view functions after transactions** - To get updated state

### Migration Guide

If you're updating existing code:

**Old way:**
```python
tx_receipt = await client.limit_buy(...)
tx_hash = tx_receipt['transactionHash'].hex()
```

**New way:**
```python
result = await client.limit_buy(...)
tx_hash = result['tx_hash']
tx_receipt = result['tx_receipt']  # Full receipt still available
```

## Example Files

- `examples/return_values_example.py` - Comprehensive example showing all features
- `examples/simple_trading.py` - Updated to work with new return format

## Advanced Usage

### Custom Event Decoding

To decode custom events, modify the `_decode_function_return_values` method in the contract class:

```python
def _decode_function_return_values(self, contract, function_name: str, tx_receipt):
    decoded_logs = []
    for log in tx_receipt.logs:
        try:
            # Add your custom event decoding here
            decoded_log = contract.events.YourCustomEvent().process_log(log)
            decoded_logs.append(decoded_log)
        except:
            continue
    return decoded_logs if decoded_logs else None
```

### Direct ABI Function Calls

For maximum flexibility, you can also call contract functions directly:

```python
contract = client.contract.get_contract(
    client.contract.matching_engine,
    client.contract.matching_engine_abi
)

# Call any function from the ABI
result = await asyncio.to_thread(
    contract.functions.yourFunction(args).call
)
```
