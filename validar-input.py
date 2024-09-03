import sys

def main():
    print(f"action: test_echo_server | result: {'success' if sys.argv[2] == sys.argv[1] else 'fail'}")
    return

main()