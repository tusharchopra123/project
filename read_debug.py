
try:
    with open('debug_output.txt', 'r', encoding='utf-16') as f:
        for line in f:
            if "Score" in line or "Last Point" in line or "Benchmark:" in line or "DEBUG" in line:
                print(line.strip())
except Exception as e:
    print(f"UTF-16 failed: {e}")
    try:
        with open('debug_output.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if "Score" in line or "Last Point" in line or "Benchmark:" in line or "DEBUG" in line:
                    print(line.strip())
    except Exception as e2:
        print(f"UTF-8 failed: {e2}")
