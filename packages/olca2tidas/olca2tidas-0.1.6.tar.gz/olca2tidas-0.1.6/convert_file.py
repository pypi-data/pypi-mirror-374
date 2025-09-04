
#!/usr/bin/env python
# Thin proxy so `python convert_file.py ...` works as in user's example.
import sys
from olca2tidas.cli import run

if __name__ == "__main__":
    # Forward all arguments after script name directly to the wrapper
    sys.exit(run(sys.argv[1:]))
