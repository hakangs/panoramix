"""
Test suite for Shanghai and Cancún EVM opcodes.

Tests the following new opcodes:
- PUSH0 (0x5f) - EIP-3855 (Shanghai)
- TLOAD (0x5c) - EIP-1153 (Cancún) 
- TSTORE (0x5d) - EIP-1153 (Cancún)
- MCOPY (0x5e) - EIP-5656 (Cancún)
- BLOBHASH (0x49) - EIP-4844 (Cancún)
- BLOBBASEFEE (0x4a) - EIP-7516 (Cancún)
"""

import sys
import os

# Add parent directory to path to import panoramix
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panoramix.loader import Loader
from panoramix.vm import VM
from panoramix.utils.opcode_dict import opcode_dict, stack_diffs


def test_opcode_dict_shanghai_cancun():
    """Test that all new opcodes are present in opcode_dict."""
    
    # Shanghai opcodes
    assert 0x5f in opcode_dict, "PUSH0 (0x5f) not in opcode_dict"
    assert opcode_dict[0x5f] == "push0", f"Wrong opcode name: {opcode_dict[0x5f]}"
    
    # Cancún opcodes
    assert 0x49 in opcode_dict, "BLOBHASH (0x49) not in opcode_dict"
    assert opcode_dict[0x49] == "blobhash", f"Wrong opcode name: {opcode_dict[0x49]}"
    
    assert 0x4a in opcode_dict, "BLOBBASEFEE (0x4a) not in opcode_dict"
    assert opcode_dict[0x4a] == "blobbasefee", f"Wrong opcode name: {opcode_dict[0x4a]}"
    
    assert 0x5c in opcode_dict, "TLOAD (0x5c) not in opcode_dict"
    assert opcode_dict[0x5c] == "tload", f"Wrong opcode name: {opcode_dict[0x5c]}"
    
    assert 0x5d in opcode_dict, "TSTORE (0x5d) not in opcode_dict"
    assert opcode_dict[0x5d] == "tstore", f"Wrong opcode name: {opcode_dict[0x5d]}"
    
    assert 0x5e in opcode_dict, "MCOPY (0x5e) not in opcode_dict"
    assert opcode_dict[0x5e] == "mcopy", f"Wrong opcode name: {opcode_dict[0x5e]}"
    
    print("✓ All new opcodes present in opcode_dict")


def test_stack_diffs():
    """Test that stack_diffs are correct for new opcodes."""
    
    # PUSH0: takes 0 args, returns 1 value -> +1
    assert "push0" in stack_diffs, "push0 not in stack_diffs"
    assert stack_diffs["push0"] == 1, f"push0 stack_diff wrong: {stack_diffs['push0']}"
    
    # BLOBHASH: takes 1 arg, returns 1 value -> 0
    assert "blobhash" in stack_diffs, "blobhash not in stack_diffs"
    assert stack_diffs["blobhash"] == 0, f"blobhash stack_diff wrong: {stack_diffs['blobhash']}"
    
    # BLOBBASEFEE: takes 0 args, returns 1 value -> +1
    assert "blobbasefee" in stack_diffs, "blobbasefee not in stack_diffs"
    assert stack_diffs["blobbasefee"] == 1, f"blobbasefee stack_diff wrong: {stack_diffs['blobbasefee']}"
    
    # TLOAD: takes 1 arg, returns 1 value -> 0
    assert "tload" in stack_diffs, "tload not in stack_diffs"
    assert stack_diffs["tload"] == 0, f"tload stack_diff wrong: {stack_diffs['tload']}"
    
    # TSTORE: takes 2 args, returns 0 values -> -2
    assert "tstore" in stack_diffs, "tstore not in stack_diffs"
    assert stack_diffs["tstore"] == -2, f"tstore stack_diff wrong: {stack_diffs['tstore']}"
    
    # MCOPY: takes 3 args, returns 0 values -> -3
    assert "mcopy" in stack_diffs, "mcopy not in stack_diffs"
    assert stack_diffs["mcopy"] == -3, f"mcopy stack_diff wrong: {stack_diffs['mcopy']}"
    
    print("✓ All stack_diffs correct")


def test_push0_bytecode():
    """Test PUSH0 opcode execution."""
    # Simple contract: PUSH0, PUSH0, ADD, STOP
    # This pushes 0, then 0, adds them (0+0=0), and stops
    bytecode = "5f5f0100"  # PUSH0 PUSH0 ADD STOP
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Check that PUSH0 was parsed correctly (param should be 0, not None)
    assert (0, "push0", 0) in loader.parsed_lines, f"PUSH0 not parsed correctly: {loader.parsed_lines}"
    assert (1, "push0", 0) in loader.parsed_lines, "Second PUSH0 not parsed"
    
    print("✓ PUSH0 bytecode parses correctly")


def test_tload_tstore_bytecode():
    """Test TLOAD and TSTORE opcodes."""
    # Contract: PUSH1 0x42, PUSH1 0x00, TSTORE, PUSH1 0x00, TLOAD, STOP
    # Store 0x42 at transient slot 0, then load it back
    bytecode = "604260005d60005c00"  # PUSH1 0x42, PUSH1 0x00, TSTORE, PUSH1 0x00, TLOAD, STOP
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Check parsing
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    assert "tstore" in parsed_ops, "TSTORE not parsed"
    assert "tload" in parsed_ops, "TLOAD not parsed"
    
    print("✓ TLOAD/TSTORE bytecode parses correctly")


def test_mcopy_bytecode():
    """Test MCOPY opcode."""
    # Contract: PUSH1 0x20, PUSH1 0x00, PUSH1 0x40, MCOPY, STOP
    # Copy 32 bytes from memory[0] to memory[64]
    bytecode = "602060006040 5e 00"  # PUSH1 0x20, PUSH1 0x00, PUSH1 0x40, MCOPY, STOP
    
    loader = Loader()
    loader.load_binary(bytecode.replace(" ", ""))
    
    # Check parsing
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    assert "mcopy" in parsed_ops, "MCOPY not parsed"
    
    print("✓ MCOPY bytecode parses correctly")


def test_blobhash_bytecode():
    """Test BLOBHASH opcode."""
    # Contract: PUSH1 0x00, BLOBHASH, STOP
    # Get hash of blob at index 0
    bytecode = "60004900"  # PUSH1 0x00, BLOBHASH, STOP
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Check parsing
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    assert "blobhash" in parsed_ops, "BLOBHASH not parsed"
    
    print("✓ BLOBHASH bytecode parses correctly")


def test_blobbasefee_bytecode():
    """Test BLOBBASEFEE opcode."""
    # Contract: BLOBBASEFEE, STOP
    # Get current blob base fee
    bytecode = "4a00"  # BLOBBASEFEE, STOP
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Check parsing
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    assert "blobbasefee" in parsed_ops, "BLOBBASEFEE not parsed"
    
    print("✓ BLOBBASEFEE bytecode parses correctly")


def test_complex_transient_storage():
    """Test more complex transient storage operations."""
    # Contract that uses transient storage for temporary calculations
    # PUSH1 100, PUSH1 0, TSTORE     ; Store 100 at slot 0
    # PUSH1 200, PUSH1 1, TSTORE     ; Store 200 at slot 1
    # PUSH1 0, TLOAD                 ; Load from slot 0
    # PUSH1 1, TLOAD                 ; Load from slot 1
    # ADD                            ; Add them together
    # STOP
    bytecode = "606460005d60c860015d60005c60015c0100"
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Verify all opcodes were parsed
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    assert parsed_ops.count("tstore") == 2, f"Expected 2 TSTORE, got {parsed_ops.count('tstore')}"
    assert parsed_ops.count("tload") == 2, f"Expected 2 TLOAD, got {parsed_ops.count('tload')}"
    
    print("✓ Complex transient storage operations parse correctly")


def test_via_ir_dispatch_pattern():
    """Test improved handling of Solidity via-IR dispatch patterns."""
    # Modern Solidity compilers using via-IR can generate more complex
    # dispatch patterns. Test a simplified version.
    # This uses PUSH0 for efficiency in the dispatch logic.
    
    # Simplified dispatch: PUSH0, CALLDATALOAD, PUSH0, DUP2, EQ, JUMPI...
    bytecode = "5f355f8114"  # PUSH0, CALLDATALOAD, PUSH0, DUP2, EQ
    
    loader = Loader()
    loader.load_binary(bytecode)
    
    parsed_ops = [op for _, op, _ in loader.parsed_lines]
    
    # Should have PUSH0 opcodes
    assert parsed_ops.count("push0") >= 2, f"Expected at least 2 PUSH0, got {parsed_ops.count('push0')}"
    assert "calldataload" in parsed_ops, "Expected CALLDATALOAD"
    assert "eq" in parsed_ops, "Expected EQ"
    
    print("✓ Via-IR dispatch pattern with PUSH0 parses correctly")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*60)
    print("Testing Shanghai and Cancún EVM Opcodes")
    print("="*60 + "\n")
    
    tests = [
        test_opcode_dict_shanghai_cancun,
        test_stack_diffs,
        test_push0_bytecode,
        test_tload_tstore_bytecode,
        test_mcopy_bytecode,
        test_blobhash_bytecode,
        test_blobbasefee_bytecode,
        test_complex_transient_storage,
        test_via_ir_dispatch_pattern,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\nRunning {test.__name__}...")
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

