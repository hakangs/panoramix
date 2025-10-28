# EIP Reference: Shanghai and Cancún Support

This document provides detailed information about the EIPs implemented in this Panoramix fork for Shanghai and Cancún hard fork support.

## Table of Contents

1. [Shanghai (March 2023)](#shanghai-march-2023)
2. [Cancún (March 2024)](#cancún-march-2024)
3. [Testing](#testing)
4. [Examples](#examples)
5. [References](#references)

## Shanghai (March 2023)

### EIP-3855: PUSH0 Instruction

**Status**: ✅ Implemented

**Opcode**: `0x5f`

**Description**: Introduces a new instruction that pushes the constant value 0 onto the stack.

**Motivation**: 
- Most common value pushed to stack is 0
- `PUSH1 0` uses 2 bytes and costs 3 gas
- `PUSH0` uses 1 byte and costs 2 gas
- Results in ~200 bytes saved per average contract

**Implementation**:
```python
# In opcode_dict.py
0x5f: "push0"

# In vm.py
elif op == "push0":
    # EIP-3855 (Shanghai): PUSH0 - pushes 0 to the stack
    stack.append(0)
```

**Example Bytecode**:
```
5f5f01  # PUSH0 PUSH0 ADD → pushes 0+0=0 to stack
```

**Solidity Support**: Solidity 0.8.20+ with optimization enabled

## Cancún (March 2024)

### EIP-1153: Transient Storage Opcodes

**Status**: ✅ Implemented

**Opcodes**: `TLOAD (0x5c)`, `TSTORE (0x5d)`

**Description**: Introduces transient storage that behaves identically to storage but is discarded after every transaction.

**Motivation**:
- Cheaper than SSTORE/SLOAD (100 gas vs 20,000 gas for cold SSTORE)
- Perfect for reentrancy locks
- Temporary variables within transaction scope
- No need for cleanup operations

**Implementation**:
```python
# In vm.py
elif op == "tload":
    # EIP-1153 (Cancún): TLOAD - Load from transient storage
    tsloc = stack.pop()
    stack.append(("tstorage", 256, 0, tsloc))

elif op == "tstore":
    # EIP-1153 (Cancún): TSTORE - Store to transient storage
    tsloc = stack.pop()
    val = stack.pop()
    trace(("tstore", 256, 0, tsloc, val))
```

**Use Cases**:
1. **Reentrancy Guards**:
   ```solidity
   modifier nonReentrant() {
       require(tload(0) == 0);
       tstore(0, 1);
       _;
       tstore(0, 0);
   }
   ```

2. **Temporary Calculations**:
   ```solidity
   function complexCalculation() internal {
       tstore(0, intermediateResult1);
       tstore(1, intermediateResult2);
       // Use values...
       // No cleanup needed!
   }
   ```

**Example Bytecode**:
```
604260005d60005c  # PUSH1 42, PUSH1 0, TSTORE, PUSH1 0, TLOAD
```

### EIP-5656: MCOPY - Memory Copying Instruction

**Status**: ✅ Implemented

**Opcode**: `0x5e`

**Description**: Introduces an efficient EVM instruction for copying memory areas.

**Motivation**:
- Copying memory currently requires loops or CODECOPY tricks
- MCOPY is more efficient and cheaper
- Handles overlapping memory regions correctly
- Common operation deserves dedicated instruction

**Gas Cost**: 
- 3 + 3 * words + memory expansion cost
- Significantly cheaper than loop-based copying

**Implementation**:
```python
elif op == "mcopy":
    # EIP-5656 (Cancún): MCOPY - Efficient memory copying
    dest = stack.pop()
    src = stack.pop()
    length = stack.pop()
    
    if length != 0:
        src_data = ("mem", ("range", src, length))
        trace(("setmem", ("range", dest, length), src_data))
```

**Comparison with Alternatives**:
```
# Old way (using CODECOPY)
CODESIZE                    # Get code size
DUP1                        # Duplicate
PUSH1 32                    # Source in code
PUSH1 64                    # Destination in memory  
CODECOPY                    # Copy

# New way (using MCOPY)
PUSH1 32                    # Length
PUSH1 0                     # Source
PUSH1 64                    # Destination
MCOPY                       # Copy
```

**Example Bytecode**:
```
602060006040 5e  # PUSH1 32, PUSH1 0, PUSH1 64, MCOPY
```

### EIP-4844: Shard Blob Transactions (Proto-Danksharding)

**Status**: ✅ Implemented

**Opcode**: `BLOBHASH (0x49)`

**Description**: Introduces blob-carrying transactions with a new BLOBHASH opcode to access blob versioned hashes.

**Motivation**:
- Scaling solution for L2 rollups
- Cheaper data availability (blob data not in execution layer)
- Target: ~1 MB per block of blob data
- 10-100x cheaper than CALLDATA

**Implementation**:
```python
elif op == "blobhash":
    # EIP-4844 (Cancún): BLOBHASH - Returns versioned hash of blob
    index = stack.pop()
    stack.append(("blobhash", index))
```

**Use Cases**:
- L2 rollups posting batch data
- Data availability for zk-proofs
- Temporary bulk storage (blob data expires after ~18 days)

**Example Bytecode**:
```
60004900  # PUSH1 0, BLOBHASH, STOP → Get hash of first blob
```

### EIP-7516: BLOBBASEFEE Opcode

**Status**: ✅ Implemented

**Opcode**: `0x4a`

**Description**: Returns the current blob base fee, similar to how BASEFEE (0x48) returns the block base fee.

**Motivation**:
- Contracts need to know blob costs for economic calculations
- Dynamic pricing mechanism for blobs
- Follows similar pattern to EIP-1559 (BASEFEE)

**Implementation**:
```python
# Added to environmental information opcodes
elif op in [
    # ... other opcodes ...
    "blobbasefee",  # EIP-7516 (Cancún)
]:
    stack.append(op)
```

**Use Cases**:
```solidity
// Check if blob posting is economical
function shouldPostBlob() public view returns (bool) {
    return blobbasefee() < maxAcceptableFee;
}
```

**Example Bytecode**:
```
4a  # BLOBBASEFEE → Returns current blob base fee
```

## Testing

### Running Tests

```bash
# Run all new opcode tests
python tests/test_new_opcodes.py

# Test sample contract parsing
python tests/test_sample_contract.py
```

### Test Coverage

Our test suite covers:

1. ✅ Opcode dictionary completeness
2. ✅ Stack diff calculations
3. ✅ PUSH0 parsing and execution
4. ✅ TLOAD/TSTORE operations
5. ✅ MCOPY memory operations
6. ✅ BLOBHASH access
7. ✅ BLOBBASEFEE queries
8. ✅ Complex transient storage patterns
9. ✅ Via-IR dispatch patterns
10. ✅ Real-world contract parsing

## Examples

### Example 1: Modern Solidity Contract (0.8.20+)

Contracts compiled with Solidity 0.8.20+ using optimization will use PUSH0:

```solidity
// Solidity 0.8.20
pragma solidity ^0.8.20;

contract Example {
    function test() public pure returns (uint) {
        uint x = 0;  // Compiled to PUSH0
        return x;
    }
}
```

**Bytecode**:
```
5f  # PUSH0 (instead of 6000 for PUSH1 0)
```

### Example 2: Reentrancy Guard with Transient Storage

```solidity
// Much cheaper reentrancy protection
contract ReentrancyGuard {
    uint256 private constant LOCKED = 1;
    uint256 private constant UNLOCKED = 0;
    
    modifier nonReentrant() {
        require(tload(0) == UNLOCKED, "Reentrant call");
        tstore(0, LOCKED);
        _;
        tstore(0, UNLOCKED);
    }
    
    function withdraw() external nonReentrant {
        // Protected function
    }
}
```

**Bytecode Pattern**:
```
60005c      # PUSH1 0, TLOAD → Load lock status
...         # Check if unlocked
600160005d  # PUSH1 1, PUSH1 0, TSTORE → Set lock
...         # Function body
600060005d  # PUSH1 0, PUSH1 0, TSTORE → Release lock
```

### Example 3: L2 Rollup with Blob Data

```solidity
contract L2Rollup {
    event BatchPosted(uint256 indexed batchId, bytes32 blobHash);
    
    function postBatch(uint256 batchId) external {
        // Get hash of blob containing batch data
        bytes32 hash = blobhash(0);
        require(hash != bytes32(0), "No blob");
        
        emit BatchPosted(batchId, hash);
    }
}
```

**Bytecode**:
```
60004900  # PUSH1 0, BLOBHASH → Get blob hash at index 0
```

## Implementation Details

### Files Modified

1. **panoramix/utils/opcode_dict.py**
   - Added opcode mappings (0x49, 0x4a, 0x5c, 0x5d, 0x5e, 0x5f)
   - Added stack_diffs for all new opcodes

2. **panoramix/vm.py**
   - Added handlers in `apply_stack()` method
   - Proper stack management for each opcode
   - Trace generation for debugging

3. **Documentation**
   - Updated README.md with changelog
   - Expanded OPCODES.md with EIP references
   - Created this comprehensive reference

### Stack Effects

| Opcode | Stack Before | Stack After | Stack Diff |
|--------|-------------|-------------|-----------|
| PUSH0 | ... | ..., 0 | +1 |
| TLOAD | ..., key | ..., value | 0 |
| TSTORE | ..., key, value | ... | -2 |
| MCOPY | ..., dest, src, len | ... | -3 |
| BLOBHASH | ..., index | ..., hash | 0 |
| BLOBBASEFEE | ... | ..., fee | +1 |

## References

### Official EIPs

1. **EIP-3855 (PUSH0)**: https://eips.ethereum.org/EIPS/eip-3855
2. **EIP-1153 (Transient Storage)**: https://eips.ethereum.org/EIPS/eip-1153
3. **EIP-5656 (MCOPY)**: https://eips.ethereum.org/EIPS/eip-5656
4. **EIP-4844 (Blob Transactions)**: https://eips.ethereum.org/EIPS/eip-4844
5. **EIP-7516 (BLOBBASEFEE)**: https://eips.ethereum.org/EIPS/eip-7516

### Hard Fork Specifications

- **Shanghai**: https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md
- **Cancún**: https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/cancun.md

### Additional Resources

- **Solidity 0.8.20 Release**: https://blog.soliditylang.org/2023/05/10/solidity-0.8.20-release-announcement/
- **Transient Storage Use Cases**: https://ethereum-magicians.org/t/eip-1153-transient-storage-opcodes/553
- **Blob Transactions Explained**: https://www.eip4844.com/
- **EVM Opcodes Reference**: https://www.evm.codes/

## Compatibility

### Solidity Version Support

| Solidity Version | PUSH0 | Transient Storage | MCOPY | Blob Opcodes |
|-----------------|-------|-------------------|-------|--------------|
| < 0.8.20 | ❌ | ❌ | ❌ | ❌ |
| 0.8.20 - 0.8.23 | ✅ | ❌ | ❌ | ❌ |
| 0.8.24+ | ✅ | ✅ | ✅ | ✅ |

### Network Support

| Network | Shanghai | Cancún |
|---------|----------|--------|
| Mainnet | Mar 2023 | Mar 2024 |
| Goerli | Mar 2023 | Jan 2024 |
| Sepolia | Feb 2023 | Jan 2024 |

## Future Work

Potential improvements for future versions:

1. **Better transient storage analysis**: Identify patterns and provide high-level abstractions
2. **Blob data visualization**: Show relationships between blob hashes and contract calls
3. **MCOPY optimization detection**: Identify where MCOPY provides benefits vs alternatives
4. **Via-IR pattern recognition**: Better handling of Solidity via-IR compilation artifacts
5. **Gas optimization suggestions**: Recommend PUSH0 over PUSH1 0, etc.

## Contributing

To add support for new opcodes in future hard forks:

1. Update `opcode_dict` in `panoramix/utils/opcode_dict.py`
2. Add stack_diff in same file
3. Implement handler in `vm.py` `apply_stack()` method
4. Add tests in `tests/test_new_opcodes.py`
5. Update documentation (README.md, OPCODES.md, this file)
6. Test with real-world contracts

---

**Last Updated**: October 2025
**Panoramix Version**: 0.7.0 (Upcoming)
**Maintained by**: Community Fork

