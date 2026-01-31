import sys
from deep_translator import GoogleTranslator

def test():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    phrases = [
        "ደንበኞችን አሳይ",         # Show customers
        "ሁሉንም ደንበኞች አሳይ",     # Show all customers
        "ደንበኞችን ዘርዝር",         # List customers
        "የአክሱም ደንበኞች",         # Axum customers
        "ምርቶችን አሳይ",           # Show products
        "Get all customers"      # English check
    ]

    for p in phrases:
        try:
            # Test auto detection
            t = GoogleTranslator(source='auto', target='en').translate(p)
            print(f"'{p}' (auto) -> '{t}'")
            
            # Test explicit Amharic
            if p != "Get all customers":
                t_am = GoogleTranslator(source='am', target='en').translate(p)
                print(f"'{p}' (am)   -> '{t_am}'")
        except Exception as e:
            print(f"Error for '{p}': {e}")
        print("---")

if __name__ == "__main__":
    test()
