import sys

# Print the first 9 bytes this process actually receives on stdin, as hex.
print(sys.stdin.buffer.read(9).hex(" ").upper())
