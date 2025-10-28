"""
Test the sample contract provided by the user.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panoramix.loader import Loader


def test_sample_contract_loading():
    """Test that the sample contract bytecode can be loaded and parsed."""
    
    # Read the sample contract bytecode
    bytecode_path = "/Users/hakanmoray/Desktop/0x99a4031a2e32181d8848d4a9f03dd00131449e5b.bin"
    
    try:
        with open(bytecode_path, 'r') as f:
            bytecode = f.read().strip()
    except FileNotFoundError:
        print("⚠ Sample contract file not found, skipping test")
        return
    
    # Load and parse the bytecode
    loader = Loader()
    loader.load_binary(bytecode)
    
    # Check that we got some parsed lines
    assert len(loader.parsed_lines) > 0, "No lines parsed from bytecode"
    
    # Extract all opcodes used
    opcodes_used = set(op for _, op, _ in loader.parsed_lines)
    
    print(f"✓ Sample contract loaded successfully")
    print(f"  - Total instructions: {len(loader.parsed_lines)}")
    print(f"  - Unique opcodes: {len(opcodes_used)}")
    print(f"  - Jump destinations: {len(loader.jump_dests)}")
    
    # Check if any new opcodes are present
    new_opcodes = {"push0", "tload", "tstore", "mcopy", "blobhash", "blobbasefee"}
    found_new = opcodes_used.intersection(new_opcodes)
    
    if found_new:
        print(f"  - New opcodes found: {', '.join(found_new)}")
    else:
        print(f"  - No new Shanghai/Cancún opcodes in this contract")
    
    # Show a sample of the disassembly
    print("\n  First 10 instructions:")
    for i, (line_no, op, param) in enumerate(loader.parsed_lines[:10]):
        param_str = f" {hex(param) if isinstance(param, int) and param > 9 else param}" if param is not None else ""
        print(f"    {line_no:4d}: {op}{param_str}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Sample Contract")
    print("="*60 + "\n")
    
    try:
        test_sample_contract_loading()
        print("\n✓ Test passed")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

