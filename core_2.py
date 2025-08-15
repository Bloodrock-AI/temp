import random
import string
import os
import sys
from math import comb
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np

random.seed(42)  # For reproducibility

def needleman_wunsch(predicted, gold,
                        k_ins=1.0, k_del=1.0, k_sub=1.0,
                        sim=None):
    if sim is None:
        sim = lambda a, b: 1.0 if a == b else 0.0

    m, n = len(predicted), len(gold)
    dp = [[0.0]*(n+1) for _ in range(m+1)]
    back = [[None]*(n+1) for _ in range(m+1)]     # ← NEW

    for i in range(1, m+1):
        dp[i][0] = i * k_del
        back[i][0] = '↑'
    for j in range(1, n+1):
        dp[0][j] = j * k_ins
        back[0][j] = '←'

    for i in range(1, m+1):
        for j in range(1, n+1):
            choices = [
                (dp[i-1][j] + k_del, '↑'),                         # delete
                (dp[i][j-1] + k_ins, '←'),                         # insert
                (dp[i-1][j-1] + k_sub*(1 - sim(predicted[i-1],
                                                gold[j-1])), '↖')  # sub/ match
            ]
            dp[i][j], back[i][j] = min(choices, key=lambda x: x[0])

    # --- back-track to count alignment columns ---
    i, j, L = m, n, 0
    while i > 0 or j > 0:
        move = back[i][j]
        L += 1
        if move == '↖':
            i, j = i-1, j-1
        elif move == '↑':
            i -= 1
        else:  # '←'
            j -= 1

    cost = dp[m][n]
    avg_cost = cost / L
    return avg_cost

def ktc(predicted, gold, verbose=False):
    """
    Compute Kendall Tau coefficient over the order of matched symbols.
    Only symbols appearing in both sequences are considered, in the order
    they appear in `predicted`. Result is clamped to [0,1]:
      - 1.0 means perfect agreement
      - 0.0 means no agreement or complete reversal
    """
    predicted = list(predicted)
    gold = list(gold)
    
    
    # get unique matched symbols in predicted order
    seen = set()
    matched = []
    for s in predicted:
        if s in gold and s not in seen:
            seen.add(s)
            matched.append(s)

    n = len(matched)
    if n < 2:
        if verbose:
            print(f"Matched symbols: {matched}, n: {n}, returning 0.0")
        return 0.0, []

    # map each symbol to its index in gold
    rank = {s: i for i, s in enumerate(gold) if s in seen}
    # build list of ranks in the order of matched
    ranks = [rank[s] for s in matched]

    nc = nd = 0
    for i, j in combinations(range(n), 2):
        if (ranks[i] - ranks[j]) * (i - j) > 0:
            nc += 1
        else:
            nd += 1

    tau = (nc - nd) / (0.5 * n * (n - 1))
    
    norm_tau = (tau + 1) / 2.0  # Normalize to [0,1]
    
    # clamp to [0,1]
    out = max(0.0, min(1.0, tau))
    # print(f"Matched symbols: {matched}, Ranks: {ranks}, nc: {nc}, nd: {nd}, tau: {tau}, norm_tau: {norm_tau}, clamped: {out}")
    # return out
    return norm_tau, matched

def core(predicted, gold, nw_coeff=0.5, verbose=False):
    """
    Core function to compute the average cost of alignment
    between predicted and gold sequences.
    """ 
    
    avg_cost = needleman_wunsch(predicted, gold)
    ktc_value, matched_symbols = ktc(predicted, gold)
    
    if verbose:
        print(f"Average cost for alignment: {avg_cost}")
        print(f"Kendall Tau coefficient: {ktc_value}, Matched symbols: {matched_symbols}")
    
    return nw_coeff * avg_cost + (1-nw_coeff) * ktc_value

def scramble_with_kendall(strings, D, randomize=False):
    """
    Return a new list that is exactly D Kendall-τ inversions away
    from the original `strings` list.

    strings   : list of str  – the reference order to scramble
    D         : int          – desired Kendall distance (0 … n(n-1)//2)
    randomize : bool         – if True, pick inversions randomly;
                               if False (default), use a deterministic
                               greedy construction.
    """
    n = len(strings)
    if not (0 <= D <= comb(n, 2)):
        raise ValueError(f"D must be between 0 and {comb(n, 2)} for n={n}")

    # ---------- Build a Lehmer (inversion) vector ----------
    remaining = D
    lehmer = []
    for i in range(n):
        max_inv = n - i - 1                  # most inversions position i can add
        upper = min(remaining, max_inv)
        ci = random.randint(0, upper) if randomize else upper
        lehmer.append(ci)
        remaining -= ci

    # ---------- Convert Lehmer vector → permutation ----------
    available = list(range(n))
    perm_indices = []
    for ci in lehmer:
        perm_indices.append(available.pop(ci))

    # ---------- Map indices back onto the original strings ----------
    return [strings[i] for i in perm_indices]

def add_fail_states(sequence, sparcity):
    """
    Add fail states to a sequence based on sparcity level.
    
    Args:
        sequence (str): Original sequence
        sparcity (float): Fraction of positions to replace with fail states (0.0 to 1.0)
    
    Returns:
        str or None: Modified sequence with fail states, or None if invalid
    """
    if not (0.0 <= sparcity <= 1.0):
        return None
    
    if len(sequence) == 0:
        return sequence
    
    # Convert to list for easier manipulation
    seq_list = list(sequence)
    seq_length = len(seq_list)
    
    # Calculate number of positions to replace
    num_fail_states = int(seq_length * sparcity)
    
    # Skip if the combination is invalid (e.g., length=2, sparcity=0.3 would give 0 fail states)
    if sparcity > 0 and num_fail_states == 0:
        return None
    
    if num_fail_states > 0:
        # Randomly select positions to replace with fail states
        fail_positions = random.sample(range(seq_length), num_fail_states)
        
        # Replace selected positions with '0' (fail state marker)
        for pos in fail_positions:
            seq_list[pos] = '0'
    
    return ''.join(seq_list)

def generate_unique_sequences(a, b, c):
    """
    Generate unique random sequences.

    Args:
        a (int): number of different symbols to use from alphabet
        b (int): length of each output sequence
        c (int): number of output sequences to generate

    Returns:
        list: list of c unique sequences, each of length b using a symbols

    Example:
        generate_unique_sequences(3, 4, 5) might return:
        ['abca', 'bcab', 'cabc', 'acba', 'baca']
    """
    # Use first 'a' letters of the alphabet
    symbols = string.ascii_lowercase[:a]

    sequences = set()
    max_attempts = 10000  # Prevent infinite loop
    attempts = 0

    while len(sequences) < c and attempts < max_attempts:
        # Generate a random sequence of length b using symbols
        sequence = ''.join(random.choices(symbols, k=b))
        sequences.add(sequence)
        attempts += 1

    if len(sequences) < c:
        print(f"Warning: Could only generate {len(sequences)} unique sequences out of {c} requested")

    return list(sequences)



if __name__ == "__main__":
    COUNT = 35
    TARGET_SEQUENCES = []
    # List of increasingly scrambled sequences of all lengths and complexities (produced using TARGET_SEQUENCES)
    SCRAMBLED_BIN = []
    # List of sequences with fail states added of all length and complexities (produced using TARGET_SEQUENCES)
    # invalid length-sparcity combinations will be ignored (e.g. length=2, sparcity=0.3)
    FAIL_STATES_BIN = []
    # List of sequences with both fail states and scrambled sequences of all lengths and complexities
    # invalid length-sparcity combinations will be ignored (e.g. length=2, sparcity=0.3)
    COMBINED_BIN = []

    for length in range (2, 10):
        for complexity in range(2, 15):
            # print(f"Generating sequences with complexity {complexity} and length {length}")
            TARGET_SEQUENCES.extend(generate_unique_sequences(complexity, length, COUNT))

    for seq in TARGET_SEQUENCES:
        # Scramble each sequence with a random Kendall distance
        for scramble_length in range(0, comb(len(seq), 2) + 1):
            scrambled = scramble_with_kendall(seq, scramble_length, randomize=True)
            # print(f"Scrambled sequence: {scrambled}")
            
            # Calculate Kendall Tau for the scrambled sequence
            tau_value, _ = ktc(scrambled, seq)
            # print(f"Kendall Tau for scrambled sequence: {tau_value}")

            SCRAMBLED_BIN.append((scrambled, seq, tau_value))

    for seq in TARGET_SEQUENCES:
        # Add fail states to each sequence with varying sparcity levels
        for sparcity in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            fail_seq = add_fail_states(seq, sparcity)
            if fail_seq is not None:
                FAIL_STATES_BIN.append((fail_seq, seq, sparcity))

    print("Generating sequences and plotting...")
    
    # Create output directory for saving plots
    output_dir = "core_2_experiments"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving plots to {output_dir}/ directory")
    
    # Calculate core values for all scrambled sequences
    kendall_tau_values = []
    core_values = []
    
    print(f"Processing {len(SCRAMBLED_BIN)} scrambled sequences...")
    
    for i, (scrambled, original, tau_value) in enumerate(SCRAMBLED_BIN):
        if i % 1000 == 0:  # Progress indicator
            print(f"Processed {i}/{len(SCRAMBLED_BIN)} sequences")
        
        # Calculate core value using the core function
        core_value = core(scrambled, original)
        
        kendall_tau_values.append(tau_value)
        core_values.append(core_value)
    
    # Create the main plot
    plt.figure(figsize=(15, 6))
    
    # First subplot: Overall relationship
    plt.subplot(1, 2, 1)
    plt.scatter(kendall_tau_values, core_values, alpha=0.6, s=20)
    plt.xlabel('Kendall Tau')
    plt.ylabel('Core Function Value')
    plt.title('Overall Relationship: Kendall Tau vs Core Function')
    plt.grid(True, alpha=0.3)
    
    # Add correlation statistics
    correlation = np.corrcoef(kendall_tau_values, core_values)[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Second subplot: Relationship by sequence length
    plt.subplot(1, 2, 2)
    
    # Group data by sequence length
    length_data = {}
    for i, (scrambled, original, tau_value) in enumerate(SCRAMBLED_BIN):
        seq_length = len(original)
        if seq_length not in length_data:
            length_data[seq_length] = {'tau': [], 'core': []}
        length_data[seq_length]['tau'].append(tau_value)
        length_data[seq_length]['core'].append(core_values[i])
    
    # Get all available lengths and sample uniformly
    all_lengths = list(length_data.keys())
    # Sample 5-6 lengths uniformly across the range
    num_samples = min(6, len(all_lengths))
    sampled_lengths = sorted(random.sample(all_lengths, num_samples))
    
    # Create color map
    colors = plt.cm.tab10(np.linspace(0, 1, len(sampled_lengths)))
    
    # Plot each length with different colors
    for i, length in enumerate(sampled_lengths):
        tau_vals = length_data[length]['tau']
        core_vals = length_data[length]['core']
        plt.scatter(tau_vals, core_vals, alpha=0.7, s=25, 
                   color=colors[i], label=f'Length {length}')
    
    plt.xlabel('Kendall Tau')
    plt.ylabel('Core Function Value')
    plt.title('Relationship by Sequence Length')
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/kendall_tau_overview.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_dir}/kendall_tau_overview.png")
    
    # Create separate graphs for each sampled length
    print(f"\nCreating separate graphs for each length...")
    
    # Calculate grid dimensions for subplots
    n_lengths = len(sampled_lengths)
    cols = 3  # 3 columns
    rows = (n_lengths + cols - 1) // cols  # Calculate rows needed
    
    plt.figure(figsize=(15, 5 * rows))
    
    for i, length in enumerate(sampled_lengths):
        plt.subplot(rows, cols, i + 1)
        
        tau_vals = length_data[length]['tau']
        core_vals = length_data[length]['core']
        
        plt.scatter(tau_vals, core_vals, alpha=0.7, s=30, color=colors[i])
        plt.xlabel('Kendall Tau')
        plt.ylabel('Core Function Value')
        plt.title(f'Length {length} (n={len(tau_vals)} points)')
        plt.grid(True, alpha=0.3)
        
        # Calculate and display correlation for this length
        if len(tau_vals) > 1:
            length_correlation = np.corrcoef(tau_vals, core_vals)[0, 1]
            plt.text(0.05, 0.95, f'Corr: {length_correlation:.3f}', 
                     transform=plt.gca().transAxes, 
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Set consistent axis limits across all subplots for better comparison
        plt.xlim(0, 1)
        if core_vals:  # Check if there are values
            global_min = min(core_values)
            global_max = max(core_values)
            plt.ylim(global_min * 0.95, global_max * 1.05)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/kendall_tau_by_length.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_dir}/kendall_tau_by_length.png")
    
    print(f"Plotted {len(kendall_tau_values)} data points")
    print(f"Kendall Tau range: [{min(kendall_tau_values):.3f}, {max(kendall_tau_values):.3f}]")
    print(f"Core value range: [{min(core_values):.3f}, {max(core_values):.3f}]")
    print(f"Correlation coefficient: {correlation:.3f}")
    
    # Plot relationship between core value and fail state sparcity
    print(f"\nProcessing {len(FAIL_STATES_BIN)} fail state sequences...")
    
    fail_sparcity_values = []
    fail_core_values = []
    
    for i, (fail_seq, original, sparcity) in enumerate(FAIL_STATES_BIN):
        if i % 1000 == 0:  # Progress indicator
            print(f"Processed {i}/{len(FAIL_STATES_BIN)} fail state sequences")
        
        # Calculate core value using the core function
        core_value = core(fail_seq, original)
        
        fail_sparcity_values.append(sparcity)
        fail_core_values.append(core_value)
    
    # Create fail states plot
    plt.figure(figsize=(12, 8))
    
    # Main scatter plot
    plt.subplot(2, 2, 1)
    plt.scatter(fail_sparcity_values, fail_core_values, alpha=0.6, s=20)
    plt.xlabel('Fail State Sparcity')
    plt.ylabel('Core Function Value')
    plt.title('Core Value vs Fail State Sparcity')
    plt.grid(True, alpha=0.3)
    
    # Add correlation statistics
    fail_correlation = np.corrcoef(fail_sparcity_values, fail_core_values)[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {fail_correlation:.3f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Box plot by sparcity level
    plt.subplot(2, 2, 2)
    unique_sparcities = sorted(list(set(fail_sparcity_values)))
    sparcity_groups = []
    sparcity_labels = []
    
    for sparcity in unique_sparcities:
        group_values = [fail_core_values[i] for i, s in enumerate(fail_sparcity_values) if s == sparcity]
        if group_values:  # Only add if there are values
            sparcity_groups.append(group_values)
            sparcity_labels.append(f'{sparcity:.1f}')
    
    plt.boxplot(sparcity_groups, labels=sparcity_labels)
    plt.xlabel('Sparcity Level')
    plt.ylabel('Core Function Value')
    plt.title('Core Value Distribution by Sparcity')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Trend line
    plt.subplot(2, 2, 3)
    # Calculate mean core value for each sparcity level
    sparcity_means = []
    sparcity_stds = []
    
    for sparcity in unique_sparcities:
        group_values = [fail_core_values[i] for i, s in enumerate(fail_sparcity_values) if s == sparcity]
        if group_values:
            sparcity_means.append(np.mean(group_values))
            sparcity_stds.append(np.std(group_values))
        else:
            sparcity_means.append(0)
            sparcity_stds.append(0)
    
    plt.errorbar(unique_sparcities, sparcity_means, yerr=sparcity_stds, 
                marker='o', capsize=5, capthick=2, linewidth=2)
    plt.xlabel('Fail State Sparcity')
    plt.ylabel('Mean Core Function Value')
    plt.title('Mean Core Value vs Sparcity (with std dev)')
    plt.grid(True, alpha=0.3)
    
    # Histogram of sparcity values
    plt.subplot(2, 2, 4)
    plt.hist(fail_sparcity_values, bins=20, alpha=0.7, edgecolor='black')
    plt.xlabel('Fail State Sparcity')
    plt.ylabel('Frequency')
    plt.title('Distribution of Sparcity Values')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/fail_states_analysis.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_dir}/fail_states_analysis.png")
    
    print(f"Fail states analysis:")
    print(f"Sparcity range: [{min(fail_sparcity_values):.3f}, {max(fail_sparcity_values):.3f}]")
    print(f"Core value range: [{min(fail_core_values):.3f}, {max(fail_core_values):.3f}]")
    print(f"Fail states correlation coefficient: {fail_correlation:.3f}")
    print(f"Number of fail state data points: {len(fail_sparcity_values)}")


def run_analysis_with_params(k_ins, k_del, k_sub, nw_coeff, output_dir):
    """
    Run the complete analysis with specified parameters and save results.
    """
    print(f"Running analysis with k_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}")
    
    # Modified core function with custom NW parameters
    def core_with_params(predicted, gold, verbose=False):
        avg_cost = needleman_wunsch(predicted, gold, k_ins=k_ins, k_del=k_del, k_sub=k_sub)
        ktc_value, matched_symbols = ktc(predicted, gold)
        
        if verbose:
            print(f"Average cost for alignment: {avg_cost}")
            print(f"Kendall Tau coefficient: {ktc_value}, Matched symbols: {matched_symbols}")
        
        return nw_coeff * avg_cost + (1-nw_coeff) * ktc_value
    
    # Calculate core values for all scrambled sequences
    kendall_tau_values = []
    core_values = []
    
    for i, (scrambled, original, tau_value) in enumerate(SCRAMBLED_BIN):
        core_value = core_with_params(scrambled, original)
        kendall_tau_values.append(tau_value)
        core_values.append(core_value)
    
    # Calculate correlation for scrambled sequences
    scrambled_correlation = np.corrcoef(kendall_tau_values, core_values)[0, 1] if len(kendall_tau_values) > 1 else 0.0
    
    # Analyze fail states
    fail_sparcity_values = []
    fail_core_values = []
    
    for i, (fail_seq, original, sparcity) in enumerate(FAIL_STATES_BIN):
        core_value = core_with_params(fail_seq, original)
        fail_sparcity_values.append(sparcity)
        fail_core_values.append(core_value)
    
    # Calculate correlation for fail states
    fail_correlation = np.corrcoef(fail_sparcity_values, fail_core_values)[0, 1] if len(fail_sparcity_values) > 1 else 0.0
    
    # Save detailed plots for this parameter combination
    param_str = f"k_ins{k_ins}_k_del{k_del}_k_sub{k_sub}_nw{nw_coeff}"
    
    # Create main plot
    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    plt.scatter(kendall_tau_values, core_values, alpha=0.6, s=20)
    plt.xlabel('Kendall Tau')
    plt.ylabel('Core Function Value')
    plt.title(f'Kendall Tau vs Core\nk_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}')
    plt.grid(True, alpha=0.3)
    plt.text(0.05, 0.95, f'Correlation: {scrambled_correlation:.3f}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.subplot(1, 2, 2)
    plt.scatter(fail_sparcity_values, fail_core_values, alpha=0.6, s=20, color='orange')
    plt.xlabel('Fail State Sparcity')
    plt.ylabel('Core Function Value')
    plt.title(f'Core vs Sparcity\nCorrelation: {fail_correlation:.3f}')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/analysis_{param_str}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Return summary statistics
    return {
        'k_ins': k_ins,
        'k_del': k_del, 
        'k_sub': k_sub,
        'nw_coeff': nw_coeff,
        'scrambled_correlation': scrambled_correlation,
        'fail_correlation': fail_correlation,
        'core_value_min': min(core_values),
        'core_value_max': max(core_values),
        'core_value_mean': np.mean(core_values),
        'core_value_std': np.std(core_values),
        'fail_core_min': min(fail_core_values),
        'fail_core_max': max(fail_core_values),
        'fail_core_mean': np.mean(fail_core_values),
        'fail_core_std': np.std(fail_core_values)
    }


def grid_search_analysis():
    """
    Perform grid search over all parameter combinations and save results.
    """
    print("\n" + "="*50)
    print("Starting Grid Search Analysis...")
    print("="*50)
    
    # Define parameter ranges
    k_ins_values = [0.5, 1.0, 1.5, 2.0]
    k_del_values = [0.5, 1.0, 1.5, 2.0]
    k_sub_values = [0.5, 1.0, 1.5, 2.0]
    nw_coeff_values = [0.2, 0.5, 0.8]
    
    # Create main grid search directory
    grid_output_dir = "core_2_grid_search"
    os.makedirs(grid_output_dir, exist_ok=True)
    
    # Store all results
    all_results = []
    total_combinations = len(k_ins_values) * len(k_del_values) * len(k_sub_values) * len(nw_coeff_values)
    current_combination = 0
    
    print(f"Total parameter combinations: {total_combinations}")
    print(f"Saving results to: {grid_output_dir}/")
    
    for k_ins in k_ins_values:
        for k_del in k_del_values:
            for k_sub in k_sub_values:
                for nw_coeff in nw_coeff_values:
                    current_combination += 1
                    print(f"\n--- Combination {current_combination}/{total_combinations} ---")
                    
                    # Run analysis for this parameter combination
                    result = run_analysis_with_params(k_ins, k_del, k_sub, nw_coeff, grid_output_dir)
                    all_results.append(result)
    
    # Save summary results to CSV
    import csv
    csv_path = f"{grid_output_dir}/grid_search_results.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = all_results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)
    
    print(f"\nGrid search complete!")
    print(f"Summary CSV saved: {csv_path}")
    
    # Create summary analysis plots
    create_grid_search_summary_plots(all_results, grid_output_dir)
    
    return all_results


def create_grid_search_summary_plots(results, output_dir):
    """
    Create summary plots analyzing the grid search results.
    """
    print("Creating grid search summary plots...")
    
    # Convert results to arrays for easier analysis
    k_ins_vals = [r['k_ins'] for r in results]
    k_del_vals = [r['k_del'] for r in results]
    k_sub_vals = [r['k_sub'] for r in results]
    nw_coeff_vals = [r['nw_coeff'] for r in results]
    scrambled_corrs = [r['scrambled_correlation'] for r in results]
    fail_corrs = [r['fail_correlation'] for r in results]
    
    # Create comprehensive summary plot
    plt.figure(figsize=(16, 12))
    
    # 1. Scrambled correlation vs parameters
    plt.subplot(3, 3, 1)
    plt.scatter(k_ins_vals, scrambled_corrs, alpha=0.7)
    plt.xlabel('k_ins')
    plt.ylabel('Scrambled Correlation')
    plt.title('Scrambled Correlation vs k_ins')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 2)
    plt.scatter(k_del_vals, scrambled_corrs, alpha=0.7)
    plt.xlabel('k_del')
    plt.ylabel('Scrambled Correlation')
    plt.title('Scrambled Correlation vs k_del')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 3)
    plt.scatter(k_sub_vals, scrambled_corrs, alpha=0.7)
    plt.xlabel('k_sub')
    plt.ylabel('Scrambled Correlation')
    plt.title('Scrambled Correlation vs k_sub')
    plt.grid(True, alpha=0.3)
    
    # 2. Fail correlation vs parameters
    plt.subplot(3, 3, 4)
    plt.scatter(k_ins_vals, fail_corrs, alpha=0.7, color='orange')
    plt.xlabel('k_ins')
    plt.ylabel('Fail Correlation')
    plt.title('Fail Correlation vs k_ins')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 5)
    plt.scatter(k_del_vals, fail_corrs, alpha=0.7, color='orange')
    plt.xlabel('k_del')
    plt.ylabel('Fail Correlation')
    plt.title('Fail Correlation vs k_del')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 6)
    plt.scatter(k_sub_vals, fail_corrs, alpha=0.7, color='orange')
    plt.xlabel('k_sub')
    plt.ylabel('Fail Correlation')
    plt.title('Fail Correlation vs k_sub')
    plt.grid(True, alpha=0.3)
    
    # 3. nw_coeff effects
    plt.subplot(3, 3, 7)
    plt.scatter(nw_coeff_vals, scrambled_corrs, alpha=0.7)
    plt.xlabel('nw_coeff')
    plt.ylabel('Scrambled Correlation')
    plt.title('Scrambled Correlation vs nw_coeff')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 3, 8)
    plt.scatter(nw_coeff_vals, fail_corrs, alpha=0.7, color='orange')
    plt.xlabel('nw_coeff')
    plt.ylabel('Fail Correlation')
    plt.title('Fail Correlation vs nw_coeff')
    plt.grid(True, alpha=0.3)
    
    # 4. Correlation comparison
    plt.subplot(3, 3, 9)
    plt.scatter(scrambled_corrs, fail_corrs, alpha=0.7, color='green')
    plt.xlabel('Scrambled Correlation')
    plt.ylabel('Fail Correlation')
    plt.title('Scrambled vs Fail Correlations')
    plt.grid(True, alpha=0.3)
    
    # Add diagonal line
    min_corr = min(min(scrambled_corrs), min(fail_corrs))
    max_corr = max(max(scrambled_corrs), max(fail_corrs))
    plt.plot([min_corr, max_corr], [min_corr, max_corr], 'r--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/grid_search_summary.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # Find best parameter combinations
    best_scrambled_idx = np.argmax(scrambled_corrs)
    best_fail_idx = np.argmax(fail_corrs)
    
    print(f"\nBest parameters for scrambled correlation ({scrambled_corrs[best_scrambled_idx]:.3f}):")
    print(f"  k_ins={results[best_scrambled_idx]['k_ins']}, k_del={results[best_scrambled_idx]['k_del']}, k_sub={results[best_scrambled_idx]['k_sub']}, nw_coeff={results[best_scrambled_idx]['nw_coeff']}")
    
    print(f"\nBest parameters for fail correlation ({fail_corrs[best_fail_idx]:.3f}):")
    print(f"  k_ins={results[best_fail_idx]['k_ins']}, k_del={results[best_fail_idx]['k_del']}, k_sub={results[best_fail_idx]['k_sub']}, nw_coeff={results[best_fail_idx]['nw_coeff']}")
    
    print(f"Grid search summary plot saved: {output_dir}/grid_search_summary.png")


# Run grid search if this is the main execution
if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "grid_search":
    grid_search_analysis()
elif __name__ == "__main__":
    # Original analysis code here - but we should call grid search by default
    print("To run original analysis, use: python core_2.py original")
    print("To run grid search, use: python core_2.py grid_search")
    print("Running grid search by default...")
    grid_search_analysis()
    
    def run_analysis_with_params(k_ins, k_del, k_sub, nw_coeff, output_dir):
        """
        Run the complete analysis with specified parameters and save results.
        
        Args:
            k_ins, k_del, k_sub: Needleman-Wunsch parameters
            nw_coeff: Core function parameter
            output_dir: Directory to save results
        
        Returns:
            dict: Summary statistics from the analysis
        """
        print(f"Running analysis with k_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}")
        
        # Modified core function with custom NW parameters
        def core_with_params(predicted, gold, verbose=False):
            avg_cost = needleman_wunsch(predicted, gold, k_ins=k_ins, k_del=k_del, k_sub=k_sub)
            ktc_value, matched_symbols = ktc(predicted, gold)
            
            if verbose:
                print(f"Average cost for alignment: {avg_cost}")
                print(f"Kendall Tau coefficient: {ktc_value}, Matched symbols: {matched_symbols}")
            
            return nw_coeff * avg_cost + (1-nw_coeff) * ktc_value
        
        # Calculate core values for all scrambled sequences
        kendall_tau_values = []
        core_values = []
        
        for i, (scrambled, original, tau_value) in enumerate(SCRAMBLED_BIN):
            if i % 5000 == 0:  # Less frequent progress updates for grid search
                print(f"  Processed {i}/{len(SCRAMBLED_BIN)} scrambled sequences")
            
            core_value = core_with_params(scrambled, original)
            kendall_tau_values.append(tau_value)
            core_values.append(core_value)
        
        # Calculate correlation for scrambled sequences
        scrambled_correlation = np.corrcoef(kendall_tau_values, core_values)[0, 1] if len(kendall_tau_values) > 1 else 0.0
        
        # Create main plot for this parameter set
        plt.figure(figsize=(15, 6))
        
        # First subplot: Overall relationship
        plt.subplot(1, 2, 1)
        plt.scatter(kendall_tau_values, core_values, alpha=0.6, s=20)
        plt.xlabel('Kendall Tau')
        plt.ylabel('Core Function Value')
        plt.title(f'Kendall Tau vs Core\nk_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}')
        plt.grid(True, alpha=0.3)
        
        # Add correlation statistics
        plt.text(0.05, 0.95, f'Correlation: {scrambled_correlation:.3f}', 
                 transform=plt.gca().transAxes, 
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Group data by sequence length for second subplot
        length_data = {}
        for i, (scrambled, original, tau_value) in enumerate(SCRAMBLED_BIN):
            seq_length = len(original)
            if seq_length not in length_data:
                length_data[seq_length] = {'tau': [], 'core': []}
            length_data[seq_length]['tau'].append(tau_value)
            length_data[seq_length]['core'].append(core_values[i])
        
        # Second subplot: By length (sample a few lengths)
        plt.subplot(1, 2, 2)
        all_lengths = list(length_data.keys())
        num_samples = min(5, len(all_lengths))
        sampled_lengths = sorted(random.sample(all_lengths, num_samples))
        colors = plt.cm.tab10(np.linspace(0, 1, len(sampled_lengths)))
        
        for i, length in enumerate(sampled_lengths):
            tau_vals = length_data[length]['tau']
            core_vals = length_data[length]['core']
            plt.scatter(tau_vals, core_vals, alpha=0.7, s=25, 
                       color=colors[i], label=f'Length {length}')
        
        plt.xlabel('Kendall Tau')
        plt.ylabel('Core Function Value')
        plt.title('Relationship by Sequence Length')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        # Save scrambled sequences plot
        param_str = f"k_ins{k_ins}_k_del{k_del}_k_sub{k_sub}_nw{nw_coeff}"
        plt.savefig(f"{output_dir}/scrambled_{param_str}.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Analyze fail states
        fail_sparcity_values = []
        fail_core_values = []
        
        for i, (fail_seq, original, sparcity) in enumerate(FAIL_STATES_BIN):
            if i % 5000 == 0:
                print(f"  Processed {i}/{len(FAIL_STATES_BIN)} fail state sequences")
            
            core_value = core_with_params(fail_seq, original)
            fail_sparcity_values.append(sparcity)
            fail_core_values.append(core_value)
        
        # Calculate correlation for fail states
        fail_correlation = np.corrcoef(fail_sparcity_values, fail_core_values)[0, 1] if len(fail_sparcity_values) > 1 else 0.0
        
        # Create fail states plot
        plt.figure(figsize=(12, 8))
        
        # Main scatter plot
        plt.subplot(2, 2, 1)
        plt.scatter(fail_sparcity_values, fail_core_values, alpha=0.6, s=20)
        plt.xlabel('Fail State Sparcity')
        plt.ylabel('Core Function Value')
        plt.title(f'Core vs Sparcity\nk_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}')
        plt.grid(True, alpha=0.3)
        
        plt.text(0.05, 0.95, f'Correlation: {fail_correlation:.3f}', 
                 transform=plt.gca().transAxes, 
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Box plot by sparcity level
        plt.subplot(2, 2, 2)
        unique_sparcities = sorted(list(set(fail_sparcity_values)))
        sparcity_groups = []
        sparcity_labels = []
        
        for sparcity in unique_sparcities:
            group_values = [fail_core_values[i] for i, s in enumerate(fail_sparcity_values) if s == sparcity]
            if group_values:
                sparcity_groups.append(group_values)
                sparcity_labels.append(f'{sparcity:.1f}')
        
        plt.boxplot(sparcity_groups, labels=sparcity_labels)
        plt.xlabel('Sparcity Level')
        plt.ylabel('Core Function Value')
        plt.title('Core Value Distribution by Sparcity')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Trend line
        plt.subplot(2, 2, 3)
        sparcity_means = []
        sparcity_stds = []
        
        for sparcity in unique_sparcities:
            group_values = [fail_core_values[i] for i, s in enumerate(fail_sparcity_values) if s == sparcity]
            if group_values:
                sparcity_means.append(np.mean(group_values))
                sparcity_stds.append(np.std(group_values))
            else:
                sparcity_means.append(0)
                sparcity_stds.append(0)
        
        plt.errorbar(unique_sparcities, sparcity_means, yerr=sparcity_stds, 
                    marker='o', capsize=5, capthick=2, linewidth=2)
        plt.xlabel('Fail State Sparcity')
        plt.ylabel('Mean Core Function Value')
        plt.title('Mean Core Value vs Sparcity')
        plt.grid(True, alpha=0.3)
        
        # Summary statistics
        plt.subplot(2, 2, 4)
        plt.text(0.1, 0.9, f'Scrambled Correlation: {scrambled_correlation:.3f}', transform=plt.gca().transAxes, fontsize=12)
        plt.text(0.1, 0.8, f'Fail States Correlation: {fail_correlation:.3f}', transform=plt.gca().transAxes, fontsize=12)
        plt.text(0.1, 0.7, f'Core Value Range: [{min(core_values):.3f}, {max(core_values):.3f}]', transform=plt.gca().transAxes, fontsize=10)
        plt.text(0.1, 0.6, f'Fail Core Range: [{min(fail_core_values):.3f}, {max(fail_core_values):.3f}]', transform=plt.gca().transAxes, fontsize=10)
        plt.text(0.1, 0.5, f'Scrambled Points: {len(core_values)}', transform=plt.gca().transAxes, fontsize=10)
        plt.text(0.1, 0.4, f'Fail State Points: {len(fail_core_values)}', transform=plt.gca().transAxes, fontsize=10)
        plt.text(0.1, 0.2, f'Parameters:', transform=plt.gca().transAxes, fontsize=12, weight='bold')
        plt.text(0.1, 0.1, f'k_ins={k_ins}, k_del={k_del}, k_sub={k_sub}, nw_coeff={nw_coeff}', transform=plt.gca().transAxes, fontsize=10)
        plt.axis('off')
        plt.title('Summary Statistics')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/failstates_{param_str}.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Return summary statistics
        return {
            'k_ins': k_ins,
            'k_del': k_del, 
            'k_sub': k_sub,
            'nw_coeff': nw_coeff,
            'scrambled_correlation': scrambled_correlation,
            'fail_correlation': fail_correlation,
            'core_value_min': min(core_values),
            'core_value_max': max(core_values),
            'core_value_mean': np.mean(core_values),
            'core_value_std': np.std(core_values),
            'fail_core_min': min(fail_core_values),
            'fail_core_max': max(fail_core_values),
            'fail_core_mean': np.mean(fail_core_values),
            'fail_core_std': np.std(fail_core_values),
            'num_scrambled_points': len(core_values),
            'num_fail_points': len(fail_core_values)
        }

    def grid_search_analysis():
        """
        Perform grid search over all parameter combinations and save results.
        """
        print("Starting Grid Search Analysis...")
        
        # Define parameter ranges
        k_ins_values = [0.5, 1.0, 1.5, 2.0]
        k_del_values = [0.5, 1.0, 1.5, 2.0]
        k_sub_values = [0.5, 1.0, 1.5, 2.0]
        nw_coeff_values = [0.2, 0.5, 0.8]
        
        # Create main grid search directory
        grid_output_dir = "core_2_grid_search"
        os.makedirs(grid_output_dir, exist_ok=True)
        
        # Store all results
        all_results = []
        total_combinations = len(k_ins_values) * len(k_del_values) * len(k_sub_values) * len(nw_coeff_values)
        current_combination = 0
        
        print(f"Total parameter combinations: {total_combinations}")
        
        for k_ins in k_ins_values:
            for k_del in k_del_values:
                for k_sub in k_sub_values:
                    for nw_coeff in nw_coeff_values:
                        current_combination += 1
                        print(f"\n--- Combination {current_combination}/{total_combinations} ---")
                        
                        # Run analysis for this parameter combination
                        result = run_analysis_with_params(k_ins, k_del, k_sub, nw_coeff, grid_output_dir)
                        all_results.append(result)
        
        # Save summary results to CSV
        import csv
        with open(f"{grid_output_dir}/grid_search_results.csv", 'w', newline='') as csvfile:
            fieldnames = all_results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in all_results:
                writer.writerow(result)
        
        print(f"\nGrid search complete! Results saved to {grid_output_dir}/")
        print(f"Summary CSV: {grid_output_dir}/grid_search_results.csv")
        
        # Create summary analysis plots
        create_grid_search_summary_plots(all_results, grid_output_dir)
        
        return all_results

    def create_grid_search_summary_plots(results, output_dir):
        """
        Create summary plots analyzing the grid search results.
        """
        print("Creating grid search summary plots...")
        
        # Convert results to arrays for easier analysis
        k_ins_vals = [r['k_ins'] for r in results]
        k_del_vals = [r['k_del'] for r in results]
        k_sub_vals = [r['k_sub'] for r in results]
        nw_coeff_vals = [r['nw_coeff'] for r in results]
        scrambled_corrs = [r['scrambled_correlation'] for r in results]
        fail_corrs = [r['fail_correlation'] for r in results]
        
        # Create comprehensive summary plot
        plt.figure(figsize=(16, 12))
        
        # 1. Scrambled correlation vs parameters
        plt.subplot(3, 3, 1)
        plt.scatter(k_ins_vals, scrambled_corrs, alpha=0.7)
        plt.xlabel('k_ins')
        plt.ylabel('Scrambled Correlation')
        plt.title('Scrambled Correlation vs k_ins')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(3, 3, 2)
        plt.scatter(k_del_vals, scrambled_corrs, alpha=0.7)
        plt.xlabel('k_del')
        plt.ylabel('Scrambled Correlation')
        plt.title('Scrambled Correlation vs k_del')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(3, 3, 3)
        plt.scatter(k_sub_vals, scrambled_corrs, alpha=0.7)
        plt.xlabel('k_sub')
        plt.ylabel('Scrambled Correlation')
        plt.title('Scrambled Correlation vs k_sub')
        plt.grid(True, alpha=0.3)
        
        # 2. Fail correlation vs parameters
        plt.subplot(3, 3, 4)
        plt.scatter(k_ins_vals, fail_corrs, alpha=0.7, color='orange')
        plt.xlabel('k_ins')
        plt.ylabel('Fail Correlation')
        plt.title('Fail Correlation vs k_ins')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(3, 3, 5)
        plt.scatter(k_del_vals, fail_corrs, alpha=0.7, color='orange')
        plt.xlabel('k_del')
        plt.ylabel('Fail Correlation')
        plt.title('Fail Correlation vs k_del')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(3, 3, 6)
        plt.scatter(k_sub_vals, fail_corrs, alpha=0.7, color='orange')
        plt.xlabel('k_sub')
        plt.ylabel('Fail Correlation')
        plt.title('Fail Correlation vs k_sub')
        plt.grid(True, alpha=0.3)
        
        # 3. nw_coeff effects
        plt.subplot(3, 3, 7)
        plt.scatter(nw_coeff_vals, scrambled_corrs, alpha=0.7)
        plt.xlabel('nw_coeff')
        plt.ylabel('Scrambled Correlation')
        plt.title('Scrambled Correlation vs nw_coeff')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(3, 3, 8)
        plt.scatter(nw_coeff_vals, fail_corrs, alpha=0.7, color='orange')
        plt.xlabel('nw_coeff')
        plt.ylabel('Fail Correlation')
        plt.title('Fail Correlation vs nw_coeff')
        plt.grid(True, alpha=0.3)
        
        # 4. Correlation comparison
        plt.subplot(3, 3, 9)
        plt.scatter(scrambled_corrs, fail_corrs, alpha=0.7, color='green')
        plt.xlabel('Scrambled Correlation')
        plt.ylabel('Fail Correlation')
        plt.title('Scrambled vs Fail Correlations')
        plt.grid(True, alpha=0.3)
        
        # Add diagonal line
        min_corr = min(min(scrambled_corrs), min(fail_corrs))
        max_corr = max(max(scrambled_corrs), max(fail_corrs))
        plt.plot([min_corr, max_corr], [min_corr, max_corr], 'r--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/grid_search_summary.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Find best parameter combinations
        best_scrambled_idx = np.argmax(scrambled_corrs)
        best_fail_idx = np.argmax(fail_corrs)
        
        print(f"\nBest parameters for scrambled correlation ({scrambled_corrs[best_scrambled_idx]:.3f}):")
        print(f"  k_ins={results[best_scrambled_idx]['k_ins']}, k_del={results[best_scrambled_idx]['k_del']}, k_sub={results[best_scrambled_idx]['k_sub']}, nw_coeff={results[best_scrambled_idx]['nw_coeff']}")
        
        print(f"\nBest parameters for fail correlation ({fail_corrs[best_fail_idx]:.3f}):")
        print(f"  k_ins={results[best_fail_idx]['k_ins']}, k_del={results[best_fail_idx]['k_del']}, k_sub={results[best_fail_idx]['k_sub']}, nw_coeff={results[best_fail_idx]['nw_coeff']}")
