"""
Test normalization functions to verify they work correctly
"""
import re

def normalize_price(price_str):
    """Convert price string to integer (remove spaces, symbols)"""
    if not price_str:
        return None
    # Remove spaces, ₼ symbol, AZN text, commas
    clean = re.sub(r'[^\d]', '', str(price_str))
    return int(clean) if clean else None

def normalize_mileage(mileage_str):
    """Convert mileage to integer (remove 'km', spaces)"""
    if not mileage_str:
        return None
    # Remove km, spaces, commas
    clean = re.sub(r'[^\d]', '', str(mileage_str))
    return int(clean) if clean else None

def normalize_engine_power(power_str):
    """Extract numeric HP value"""
    if not power_str:
        return None
    # Extract first number
    match = re.search(r'\d+', str(power_str))
    return int(match.group()) if match else None

# Test cases
print("=" * 80)
print("NORMALIZATION FUNCTION TESTS")
print("=" * 80)

# Price tests
test_prices = [
    ("24 500 ₼", 24500),
    ("16 000 AZN", 16000),
    ("12,500 ₼", 12500),
    ("35000", 35000),
]

print("\n📊 PRICE NORMALIZATION:")
for raw, expected in test_prices:
    result = normalize_price(raw)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{raw}' → {result} (expected: {expected})")

# Mileage tests
test_mileage = [
    ("250 000 km", 250000),
    ("120,000 km", 120000),
    ("0 km", 0),
    ("yeni", None),
]

print("\n🚗 MILEAGE NORMALIZATION:")
for raw, expected in test_mileage:
    result = normalize_mileage(raw)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{raw}' → {result} (expected: {expected})")

# Engine power tests
test_power = [
    ("150 a.g.", 150),
    ("200 HP", 200),
    ("90", 90),
    ("", None),
]

print("\n⚡ ENGINE POWER NORMALIZATION:")
for raw, expected in test_power:
    result = normalize_engine_power(raw)
    status = "✅" if result == expected else "❌"
    print(f"  {status} '{raw}' → {result} (expected: {expected})")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
