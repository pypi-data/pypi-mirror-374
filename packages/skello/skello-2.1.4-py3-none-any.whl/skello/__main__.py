from .core.cli import main

# Entry point for `python -m skello`
# (ensures module execution runs the CLI instead of showing __main__.py in help)
if __name__ == "__main__":
    main()
