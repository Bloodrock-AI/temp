#!/usr/bin/env python3
"""
Grid Search Runner for Core Analysis

This script runs a comprehensive grid search over the following parameters:
- k_ins: Needleman-Wunsch insertion cost
- k_del: Needleman-Wunsch deletion cost  
- k_sub: Needleman-Wunsch substitution cost
- nw_coeff: Core function weighting coefficient

Results are saved to core_2_grid_search/ directory including:
- Individual analysis plots for each parameter combination
- Summary CSV with all results
- Summary plots showing parameter relationships
"""

import core_2

if __name__ == "__main__":
    print("Starting Grid Search Analysis...")
    print("This will test multiple parameter combinations and save all results.")
    print("Results will be saved to: core_2_grid_search/")
    
    results = core_2.grid_search_analysis()
    
    print(f"\nGrid search completed successfully!")
    print(f"Total combinations tested: {len(results)}")
    print("Check the core_2_grid_search/ directory for all results.")
