#!/usr/bin/env python3
"""Test the new quick functions."""

import sys
sys.path.insert(0, 'src')

try:
    import exonware.xsystem as xs
    print("✅ Module imported successfully")
    print(f"✅ Version: {xs.__version__}")
    
    # Test if functions exist
    functions = [x for x in dir(xs) if x.startswith('quick')]
    print(f"✅ Quick functions found: {functions}")
    
    if hasattr(xs, 'quick_hash'):
        result = xs.quick_hash('test')
        print(f"✅ quick_hash test: {result[:16]}...")
    else:
        print("❌ quick_hash not found")
    
    if hasattr(xs, 'quick_serialize'):
        result = xs.quick_serialize({'test': 'data'}, 'json')
        print(f"✅ quick_serialize test: {result}")
    else:
        print("❌ quick_serialize not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
