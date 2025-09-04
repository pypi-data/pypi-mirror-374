"""Meta package entry for the niyamit-sphere distribution.

This package exists so the top-level distribution does not provide a
`sphere/__init__.py` file that could override the namespace package
provided by the sub-distributions (sphere-core, sphere-data, sphere-flood).
"""

def main() -> None:
    print("Hello from niyamit_sphere meta package!")
