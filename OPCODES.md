## Opcodes Documentation

### Mask Operations

(mask_shl, size, offset, shl, value)
(mask_shl, 256, 0, 0, val) == val
(mask_shl, 255, 0, 1) == 2 * val
(mask_shl, 254, 0, 2) == 4 * val
(mask_shl, 255, 1, -1) == val / 2
everything is in bits

### Shanghai Era Opcodes (EIP-3855)

#### PUSH0 (0x5f)
- **EIP**: [EIP-3855](https://eips.ethereum.org/EIPS/eip-3855)
- **Fork**: Shanghai
- **Description**: Pushes the constant value 0 onto the stack
- **Gas**: 2 (vs 3 for PUSH1 0x00)
- **Stack**: ∅ → 0
- **Benefits**: More efficient than `PUSH1 0x00`, commonly used in function dispatch and initialization

### Cancún Era Opcodes

#### Transient Storage (EIP-1153)

##### TLOAD (0x5c)
- **EIP**: [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153)
- **Fork**: Cancún
- **Description**: Load value from transient storage
- **Gas**: Warm access (100)
- **Stack**: key → value
- **Use cases**: Reentrancy locks, temporary variables within transaction

##### TSTORE (0x5d)
- **EIP**: [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153)
- **Fork**: Cancún
- **Description**: Store value to transient storage (cleared after transaction)
- **Gas**: 100
- **Stack**: key, value → ∅
- **Benefits**: Cheaper than SSTORE, automatically cleared after transaction

#### Memory Operations (EIP-5656)

##### MCOPY (0x5e)
- **EIP**: [EIP-5656](https://eips.ethereum.org/EIPS/eip-5656)
- **Fork**: Cancún
- **Description**: Efficiently copy memory from one location to another
- **Gas**: Variable based on size (cheaper than manual copying)
- **Stack**: destOffset, srcOffset, length → ∅
- **Benefits**: More efficient than loop-based copying, handles overlapping regions

#### Blob Transactions (EIP-4844)

##### BLOBHASH (0x49)
- **EIP**: [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)
- **Fork**: Cancún (Proto-Danksharding)
- **Description**: Returns versioned hash of the blob at the given index
- **Gas**: 3
- **Stack**: index → hash
- **Context**: Part of proto-danksharding for L2 scaling

##### BLOBBASEFEE (0x4a)
- **EIP**: [EIP-7516](https://eips.ethereum.org/EIPS/eip-7516)
- **Fork**: Cancún
- **Description**: Returns the current blob base fee
- **Gas**: 2
- **Stack**: ∅ → baseFee
- **Use cases**: Fee calculation for blob transactions

### Implementation Notes

1. **PUSH0**: Commonly seen in Solidity 0.8.20+ contracts compiled with optimization
2. **TLOAD/TSTORE**: Used for reentrancy guards and temporary storage patterns
3. **MCOPY**: More efficient than CODECOPY → MSTORE loops
4. **BLOBHASH/BLOBBASEFEE**: Primarily used by L2 rollups and blob-carrying transactions

### Via-IR Compilation

Modern Solidity compilers (0.8.20+) using `--via-ir` flag often generate different patterns:
- Heavy use of PUSH0 for initialization
- More optimized dispatch logic
- Different stack management strategies

Panoramix now handles these patterns correctly.
