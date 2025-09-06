#!/usr/bin/env python3
"""
Starship1 - BDD-focused automation loop for Claude Code
Continuously runs BDD testing and improvement commands
"""

import sys
from .starship_base import run_starship

def main():
    """Main entry point for starship1 command"""
    # Parse command line arguments
    init_string = None
    if len(sys.argv) > 1:
        # Join all arguments into a single string (in case it has spaces)
        init_string = ' '.join(sys.argv[1:])
    
    # Run the starship with config 'starship1'
    run_starship('starship1', init_string)

if __name__ == "__main__":
    main()