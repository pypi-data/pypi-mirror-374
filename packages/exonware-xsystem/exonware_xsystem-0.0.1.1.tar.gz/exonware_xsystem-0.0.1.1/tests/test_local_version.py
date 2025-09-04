#!/usr/bin/env python3
"""Test the local version of xsystem with our new functions."""

import sys
import os

# Remove any existing xsystem from sys.modules to force reload
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('exonware')]
for module in modules_to_remove:
    del sys.modules[module]

# Add our local src to the FRONT of the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔍 Testing local xsystem version...")
print(f"Python path: {sys.path[0]}")

try:
    import exonware.xsystem as xs
    print(f"✅ Module loaded from: {xs.__file__}")
    print(f"✅ Version: {xs.__version__}")
    
    # Check if our functions exist
    quick_functions = [x for x in dir(xs) if x.startswith('quick')]
    print(f"✅ Quick functions found: {quick_functions}")
    
    if quick_functions:
        print("\n🚀 Testing convenience functions:")
        
        # Test quick_hash
        if hasattr(xs, 'quick_hash'):
            result = xs.quick_hash('hello world')
            print(f"✅ quick_hash('hello world') = {result[:32]}...")
        
        # Test quick_serialize  
        if hasattr(xs, 'quick_serialize'):
            data = {'name': 'xSystem', 'version': '0.0.1'}
            result = xs.quick_serialize(data, 'json')
            print(f"✅ quick_serialize(data, 'json') = {result}")
            
        # Test quick_deserialize
        if hasattr(xs, 'quick_deserialize'):
            json_str = '{"test": "data"}'
            result = xs.quick_deserialize(json_str, 'json')
            print(f"✅ quick_deserialize(json_str) = {result}")
            
        print("\n🎉 All convenience functions working!")
    else:
        print("❌ No quick functions found - there may be an import error")
        
    # Test some existing functionality
    print("\n🔧 Testing existing functionality:")
    if hasattr(xs, 'SecureHash'):
        hash_result = xs.SecureHash.sha256('test')
        print(f"✅ SecureHash.sha256('test') = {hash_result[:32]}...")
    
    if hasattr(xs, 'JsonSerializer'):
        serializer = xs.JsonSerializer()
        result = serializer.dumps({'existing': 'functionality'})
        print(f"✅ JsonSerializer works: {result}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
