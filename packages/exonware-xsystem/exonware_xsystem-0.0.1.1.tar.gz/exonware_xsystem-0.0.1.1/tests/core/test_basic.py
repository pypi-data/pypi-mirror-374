#!/usr/bin/env python3
"""Basic functionality test for xsystem new features."""

# Test caching
print("Testing caching...")
from src.exonware.xsystem.caching.lru_cache import LRUCache
cache = LRUCache(capacity=10)
cache.put('test', 'value')
result = cache.get('test')
print(f"✓ Caching works: {result}")

# Test validation
print("\nTesting validation...")
from src.exonware.xsystem.validation.declarative import xModel, Field

class User(xModel):
    name: str
    age: int = Field(ge=0)

try:
    user = User(name='John', age='25')  # String should coerce to int
    print(f"✓ Validation works: {user.name}, age={user.age} (type: {type(user.age)})")
except Exception as e:
    print(f"✗ Validation failed: {e}")

# Test CLI colors
print("\nTesting CLI colors...")
try:
    from src.exonware.xsystem.cli.colors import colorize, Colors
    colored_text = colorize("Hello World", Colors.GREEN)
    print(f"✓ CLI colors work (length: {len(colored_text)})")
except Exception as e:
    print(f"✗ CLI colors failed: {e}")

# Test datetime humanization
print("\nTesting datetime...")
try:
    from src.exonware.xsystem.datetime.humanize import humanize_timedelta
    from datetime import timedelta
    result = humanize_timedelta(timedelta(hours=2, minutes=30))
    print(f"✓ DateTime humanization works: {result}")
except Exception as e:
    print(f"✗ DateTime failed: {e}")

# Test system monitoring
print("\nTesting system monitoring...")
try:
    from src.exonware.xsystem.monitoring.system_monitor import get_cpu_usage
    cpu = get_cpu_usage(interval=0.1)
    print(f"✓ System monitoring works: CPU usage ~{cpu:.1f}%")
except Exception as e:
    print(f"✗ System monitoring failed: {e}")

print("\n🎉 Basic functionality test completed!")
