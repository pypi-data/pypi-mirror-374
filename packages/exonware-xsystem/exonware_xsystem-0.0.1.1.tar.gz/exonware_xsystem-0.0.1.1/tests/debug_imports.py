#!/usr/bin/env python3
"""Debug import issues."""

import sys
sys.path.insert(0, 'src')

print("Testing imports step by step...")

try:
    print("1. Importing basic modules...")
    import logging
    from typing import TYPE_CHECKING
    print("✅ Basic imports OK")
    
    print("2. Testing config.logging_setup...")
    from exonware.xsystem.config.logging_setup import get_logger, setup_logging
    print("✅ Logging setup OK")
    
    print("3. Testing serialization imports...")
    from exonware.xsystem.serialization import get_serializer
    print("✅ Serialization imports OK")
    
    print("4. Testing security imports...")
    from exonware.xsystem.security.crypto import SecureHash
    print("✅ Security imports OK")
    
    print("5. Testing full module import...")
    import exonware.xsystem
    print("✅ Full module import OK")
    
    print("6. Checking what's available...")
    attrs = [x for x in dir(exonware.xsystem) if not x.startswith('_')]
    print(f"Available attributes: {len(attrs)}")
    print(f"First 10: {attrs[:10]}")
    
    # Check if our functions are defined in the module
    print("7. Looking for our functions in the source...")
    import inspect
    source_file = inspect.getfile(exonware.xsystem)
    print(f"Source file: {source_file}")
    
    with open(source_file, 'r') as f:
        content = f.read()
        if 'def quick_serialize' in content:
            print("✅ quick_serialize found in source")
        else:
            print("❌ quick_serialize NOT found in source")
            
        if 'def quick_hash' in content:
            print("✅ quick_hash found in source")
        else:
            print("❌ quick_hash NOT found in source")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
