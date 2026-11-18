for n in range(256):
    print(f"\033[38;5;{n}m{n:3}\033[0m", end="  ")
    if (n + 1) % 16 == 0:
        print()
