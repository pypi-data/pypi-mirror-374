#!/usr/bin/env python3
"""
Starship2 - Stepwise Refinement automation loop for Claude Code
Based on Niklaus Wirth's 1971 paper on stepwise refinement methodology
Creates product-plan.md and systematically implements it
"""

import sys
from .starship_base import run_starship

def main():
    """Main entry point for starship2 command"""
    # Parse command line arguments
    init_string = None
    if len(sys.argv) > 1:
        # Join all arguments into a single string (in case it has spaces)
        init_string = ' '.join(sys.argv[1:])
    
    # Run the starship with config 'starship2'
    run_starship('starship2', init_string)

if __name__ == "__main__":
    main()