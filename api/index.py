import os
import sys

# Make the repo root importable so `from app import server` works
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app import server as app  # noqa: E402  (Vercel's Python runtime looks for `app`)
