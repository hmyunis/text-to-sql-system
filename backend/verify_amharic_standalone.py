import sys
from deep_translator import GoogleTranslator

def test():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    # Amharic: ደንበኞችን አሳይ
    q1 = "\u12f0\u1295\u1260\u129b\u127d\u1295 \u12a0\u1233\u12e9"
    print(f"Original: {q1}")
    try:
        t1 = GoogleTranslator(source='auto', target='en').translate(q1)
        print(f"Translated: {t1}")
    except Exception as e:
        print(f"Error: {e}")

    q2 = "Show me customers"
    print(f"Original: {q2}")
    try:
        t2 = GoogleTranslator(source='auto', target='en').translate(q2)
        print(f"Translated: {t2}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
