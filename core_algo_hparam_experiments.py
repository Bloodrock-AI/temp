import random
import string
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations

random.seed(42)  # For reproducibility

def needleman_wunsch(predicted, gold,
                     k_ins=1.0, k_del=1.0, k_sub=1.0,
                     sim=None):
    """
    Compute weighted global alignment cost between `predicted` and `gold`.
    - k_ins: cost to insert a symbol in predicted
    - k_del: cost to delete a symbol from predicted
    - k_sub: max cost to substitute one symbol for another
    - sim(a,b): similarity in [0,1]; default is exact-match (1 if a==b else 0).
    """
    if sim is None:
        sim = lambda a, b: 1.0 if a == b else 0.0

    m, n = len(predicted), len(gold)
    # dp[i][j] = min cost to align predicted[:i] to gold[:j]
    dp = [[0.0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        dp[i][0] = i * k_del
    for j in range(1, n+1):
        dp[0][j] = j * k_ins

    for i in range(1, m+1):
        for j in range(1, n+1):
            cost_del = dp[i-1][j] + k_del
            cost_ins = dp[i][j-1] + k_ins
            sub_cost = k_sub * (1.0 - sim(predicted[i-1], gold[j-1]))
            cost_sub = dp[i-1][j-1] + sub_cost
            dp[i][j] = min(cost_del, cost_ins, cost_sub)

    return dp[m][n]


def kendall_tau_coefficient(predicted, gold):
    """
    Compute Kendall Tau coefficient over the order of matched symbols.
    Only symbols appearing in both sequences are considered, in the order
    they appear in `predicted`. Result is clamped to [0,1]:
      - 1.0 means perfect agreement
      - 0.0 means no agreement or complete reversal
    """
    # get unique matched symbols in predicted order
    seen = set()
    matched = []
    for s in predicted:
        if s in gold and s not in seen:
            seen.add(s)
            matched.append(s)

    n = len(matched)
    if n < 2:
        return 1.0

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
    # clamp to [0,1]
    return max(0.0, min(1.0, tau))


def function_call_metric(predicted,
                         gold,
                         k_ins=1.0, k_del=1.0, k_sub=1.0,
                         k_fail=1.0, k_scramble=1.0,
                         fail_symbols=None,
                         sim=None,
                         normalize=False):
    """
    Compute the total penalty and its components for the custom function-call metric.

    Parameters
    ----------
    predicted : list of symbols
    gold      : list of symbols
    k_ins     : insertion cost
    k_del     : deletion cost
    k_sub     : substitution cost weight
    k_fail    : per-fail-symbol penalty
    k_scramble: scrambling penalty weight
    fail_symbols : iterable of symbols to treat as 'fail' (default: [])
    sim       : similarity function sim(a,b) in [0,1] (default exact match)
    normalize : if True, also return a similarity score = 1/(1 + total_penalty)

    Returns
    -------
    dict with keys
      - 'alignment_cost'
      - 'fail_penalty'
      - 'scrambling_penalty'
      - 'total_penalty'
      - 'similarity' (only if normalize=True)
    """
    if fail_symbols is None:
        fail_symbols = []
    if sim is None:
        sim = lambda a, b: 1.0 if a == b else 0.0

    # 1. Alignment cost
    C_align = needleman_wunsch(predicted, gold,
                               k_ins=k_ins, k_del=k_del,
                               k_sub=k_sub, sim=sim)
    

    # 2. Fail-state penalty
    N_fail = sum(1 for s in predicted if s in fail_symbols)
    C_fail = k_fail * N_fail

    # 3. Scrambling penalty
    tau = kendall_tau_coefficient(predicted, gold)
    C_scramble = k_scramble * (1.0 - tau)

    total = C_align + C_fail + C_scramble
    result = {
        'alignment_cost':     C_align,
        'fail_penalty':       C_fail,
        'scrambling_penalty': C_scramble,
        'total_penalty':      total
    }
    if normalize:
        result['similarity'] = 1.0 / (1.0 + total)

    return result


# Example usage
if __name__ == '__main__':
    gold      = ['A', 'B', 'C', 'D']
    predicted = ['A', 'B', 'C']
    # simple sim: Aʹ vs A has sim=0.3 to reflect a "near match"
    def sim_fn(a, b):
        return 0.3 if (a, b) == ('Aʹ', 'A') else float(a == b)

    res = function_call_metric(
        predicted, gold,
        k_ins=1, k_del=1, k_sub=1,
        k_fail=3, k_scramble=1,
        fail_symbols=['X'], sim=sim_fn,
        normalize=True
    )
    print(res)
    # Expected: alignment_cost≈0.7+1, fail_penalty=3, scrambling_penalty=0,
    # total_penalty≈4.7, similarity≈1/5.7



def LD(s1, s2, insertion_cost=1, deletion_cost=1, substitution_cost=1):
    """
    Calculate Levenshtein Distance with customizable operation costs.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        insertion_cost (int/float): Cost of inserting a character (default: 1)
        deletion_cost (int/float): Cost of deleting a character (default: 1)
        substitution_cost (int/float): Cost of substituting a character (default: 1)
    
    Returns:
        int/float: Levenshtein distance with custom costs
    """
    m, n = len(s1), len(s2)
    # Initialize matrix of size (m+1) x (n+1)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize first row and column
    for i in range(m + 1):
        dp[i][0] = i * deletion_cost
    for j in range(n + 1):
        dp[0][j] = j * insertion_cost

    # Fill the matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = substitution_cost
            dp[i][j] = min(
                dp[i - 1][j] + deletion_cost,      # Deletion
                dp[i][j - 1] + insertion_cost,     # Insertion
                dp[i - 1][j - 1] + cost           # Substitution
            )

    return dp[m][n]

def norm_LD(s1, s2, insertion_cost=1, deletion_cost=1, substitution_cost=1):
    """
    Calculate normalized Levenshtein Distance with customizable operation costs.
    
    Args:
        s1 (str): First string
        s2 (str): Second string
        insertion_cost (int/float): Cost of inserting a character (default: 1)
        deletion_cost (int/float): Cost of deleting a character (default: 1)
        substitution_cost (int/float): Cost of substituting a character (default: 1)
    
    Returns:
        float: Normalized Levenshtein distance with custom costs
    """
    ld = LD(s1, s2, insertion_cost, deletion_cost, substitution_cost)
    return (2 * ld) / (len(s1) + len(s2) + ld)

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

def scramble_sequence(seq):
    """
    Scramble the sequence by shuffling its characters.
    
    Args:
        seq (str): The sequence to scramble
        
    Returns:
        str: Scrambled sequence
    """
    seq_list = list(seq)
    random.shuffle(seq_list)
    return ''.join(seq_list)

def scramble_sequence_circular(seq, level):
    """
    Scramble a continuous portion of the sequence in a circular manner.
    
    Args:
        seq (str): The sequence to scramble
        level (float): Scrambledness level from 0 to 1
        
    Returns:
        str: Scrambled sequence
    """
    if level == 0:
        return seq
    if level == 1:
        return scramble_sequence(seq)  # Full scramble
    
    seq_list = list(seq)
    n = len(seq)
    
    # Calculate how many characters to scramble
    scramble_length = max(1, int(level * n))
    
    # Choose random starting position for circular scrambling
    start_pos = random.randint(0, n - 1)
    
    # Extract the portion to scramble (circular)
    indices_to_scramble = [(start_pos + i) % n for i in range(scramble_length)]
    chars_to_scramble = [seq_list[i] for i in indices_to_scramble]
    
    # Scramble the extracted characters
    random.shuffle(chars_to_scramble)
    
    # Put them back
    for i, char in zip(indices_to_scramble, chars_to_scramble):
        seq_list[i] = char
    
    return ''.join(seq_list)

def add_fail_states(seq, sparcity: float):
    """
    Add fail states to the sequence based on a given sparcity level.
    
    Args:
        seq (str): The original sequence
        sparcity (float): Sparcity level from 0 to 1
        
    Returns:
        str: Sequence with fail states added
    """
    if sparcity == 0:
        return seq
    
    n = len(seq)
    num_fail_states = int(sparcity * n)
    
    # Randomly choose positions to insert fail states
    fail_positions = random.sample(range(n), num_fail_states)
    
    if not fail_positions:
        print("Warning: No fail states added due to sparcity level.")
        return None

    # Insert '0' (zero) as fail state at chosen positions
    seq_list = list(seq)
    for pos in sorted(fail_positions, reverse=True):
        seq_list.insert(pos, '0')
    return ''.join(seq_list)

OUTPUT_SAMPLE_SIZE = 10

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

if __name__ == "__main__":
    
    # Hyperparameter ranges for grid search
    INSERTION_COSTS = [0.5, 1.0, 1.5, 2.0]
    DELETION_COSTS = [0.5, 1.0, 1.5, 2.0]
    SUBSTITUTION_COSTS = [0.5, 1.0, 1.5, 2.0]
    
    # Create results directory
    import os
    results_dir = "hparam_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Grid search over hyperparameters
    total_combinations = len(INSERTION_COSTS) * len(DELETION_COSTS) * len(SUBSTITUTION_COSTS)
    current_combination = 0
    
    for insertion_cost in INSERTION_COSTS:
        for deletion_cost in DELETION_COSTS:
            for substitution_cost in SUBSTITUTION_COSTS:
                current_combination += 1
                print(f"\n{'='*60}")
                print(f"Grid Search Progress: {current_combination}/{total_combinations}")
                print(f"Testing hyperparameters:")
                print(f"  Insertion Cost: {insertion_cost}")
                print(f"  Deletion Cost: {deletion_cost}")
                print(f"  Substitution Cost: {substitution_cost}")
                print(f"{'='*60}")
                
                # Clear previous data
                TARGET_SEQUENCES = []
                SCRAMBLED_BIN = []
                FAIL_STATES_BIN = []
                COMBINED_BIN = []
                
                # Generate sequences
                for length in range (2, 10):
                  for complexity in range(2, 15):
                    # print(f"Generating sequences with complexity {complexity} and length {length}")
                    TARGET_SEQUENCES.extend(generate_unique_sequences(complexity, length, COUNT))

                # Generate sequences
                for length in range (2, 10):
                  for complexity in range(2, 15):
                    # print(f"Generating sequences with complexity {complexity} and length {length}")
                    TARGET_SEQUENCES.extend(generate_unique_sequences(complexity, length, COUNT))

                for seq in TARGET_SEQUENCES:
                  for level in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
                      scrambled_seq = scramble_sequence_circular(seq, level)
                      SCRAMBLED_BIN.append((scrambled_seq, seq, level))
                        
                for seq in TARGET_SEQUENCES:
                  for sparcity in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
                      fail_seq = add_fail_states(seq, sparcity)
                      if fail_seq is not None:
                          FAIL_STATES_BIN.append((fail_seq, seq, sparcity))

                for seq in TARGET_SEQUENCES:
                  for level in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
                      scrambled_seq = scramble_sequence_circular(seq, level)
                      for sparcity in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
                          fail_seq = add_fail_states(scrambled_seq, sparcity)
                          if fail_seq is None:
                            continue
                          COMBINED_BIN.append((fail_seq, seq, level, sparcity))

                # Print the generated sequences
                print(f"Generated {len(TARGET_SEQUENCES)} target sequences.")
                print(f"Generated {len(SCRAMBLED_BIN)} scrambled sequences.")
                print(f"Generated {len(FAIL_STATES_BIN)} fail states sequences.")
                print(f"Generated {len(COMBINED_BIN)} combined sequences.")
                
                # Calculate norm_LD for each bin with current hyperparameters
                print("Calculating norm_LD for all bins...")
                
                # SCRAMBLED_BIN: (scrambled_seq, original_seq, scrambledness_level)
                scrambled_data = []
                for scrambled_seq, original_seq, level in SCRAMBLED_BIN:
                    norm_ld = norm_LD(scrambled_seq, original_seq, insertion_cost, deletion_cost, substitution_cost)
                    length = len(original_seq)
                    scrambled_data.append((level, norm_ld, length))
                
                # FAIL_STATES_BIN: (fail_seq, original_seq, sparcity)
                fail_states_data = []
                for fail_seq, original_seq, sparcity in FAIL_STATES_BIN:
                    norm_ld = norm_LD(fail_seq, original_seq, insertion_cost, deletion_cost, substitution_cost)
                    length = len(original_seq)
                    fail_states_data.append((sparcity, norm_ld, length))
                
                # COMBINED_BIN: (combined_seq, original_seq, scrambledness_level, sparcity)
                combined_data = []
                for combined_seq, original_seq, level, sparcity in COMBINED_BIN:
                    norm_ld = norm_LD(combined_seq, original_seq, insertion_cost, deletion_cost, substitution_cost)
                    length = len(original_seq)
                    combined_data.append((level, sparcity, norm_ld, length))

                print(f"Calculated norm_LD for {len(scrambled_data)} scrambled sequences.")
                print(f"Calculated norm_LD for {len(fail_states_data)} fail states sequences.")
                print(f"Calculated norm_LD for {len(combined_data)} combined sequences.")

                # Create filename suffix for this hyperparameter combination
                filename_suffix = f"ins{insertion_cost}_del{deletion_cost}_sub{substitution_cost}".replace('.', 'p')
                
                # Create plots and save them
                print("Creating and saving plots...")
                
                # --- Scrambled Bin Only Plots ---
                plt.figure(figsize=(12, 8))
                # 1. x: scrambledness level, y: norm_LD
                plt.subplot(2, 2, 1)
                scrambled_levels = [x[0] for x in scrambled_data]
                scrambled_norm_lds = [x[1] for x in scrambled_data]
                plt.scatter(scrambled_levels, scrambled_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Scrambledness Level')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Scrambledness Level (Scrambled Bin)')
                plt.grid(True, alpha=0.3)
                # 2. x: length, y: norm_LD
                plt.subplot(2, 2, 2)
                scrambled_lengths = [x[2] for x in scrambled_data]
                plt.scatter(scrambled_lengths, scrambled_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Sequence Length')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Sequence Length (Scrambled Bin)')
                plt.grid(True, alpha=0.3)
                # 3. 3D: x: length, y: scrambledness, z: norm_LD
                ax = plt.subplot(2, 2, 3, projection='3d')
                ax.scatter(scrambled_lengths, scrambled_levels, scrambled_norm_lds, alpha=0.6, s=10)
                ax.set_xlabel('Length')
                ax.set_ylabel('Scrambledness')
                ax.set_zlabel('norm_LD')
                ax.set_title('3D: Length vs Scrambledness vs norm_LD (Scrambled Bin)')
                plt.suptitle(f'Scrambled Bin Plots\nHyperparameters: Ins={insertion_cost}, Del={deletion_cost}, Sub={substitution_cost}', fontsize=13, y=0.98)
                plt.tight_layout()
                scrambled_plot_filename = f"{results_dir}/scrambled_plots_{filename_suffix}.png"
                plt.savefig(scrambled_plot_filename, dpi=300, bbox_inches='tight')
                plt.close()

                # --- Fail State Bin Only Plots ---
                plt.figure(figsize=(12, 8))
                # 1. x: fail state sparcity, y: norm_LD
                plt.subplot(2, 2, 1)
                fail_sparcities = [x[0] for x in fail_states_data]
                fail_norm_lds = [x[1] for x in fail_states_data]
                plt.scatter(fail_sparcities, fail_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Fail State Sparcity')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Fail State Sparcity (Fail State Bin)')
                plt.grid(True, alpha=0.3)
                # 2. x: length, y: norm_LD
                plt.subplot(2, 2, 2)
                fail_lengths = [x[2] for x in fail_states_data]
                plt.scatter(fail_lengths, fail_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Sequence Length')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Sequence Length (Fail State Bin)')
                plt.grid(True, alpha=0.3)
                # 3. 3D: x: length, y: fail state level, z: norm_LD
                ax = plt.subplot(2, 2, 3, projection='3d')
                ax.scatter(fail_lengths, fail_sparcities, fail_norm_lds, alpha=0.6, s=10)
                ax.set_xlabel('Length')
                ax.set_ylabel('Fail State Level')
                ax.set_zlabel('norm_LD')
                ax.set_title('3D: Length vs Fail State vs norm_LD (Fail State Bin)')
                plt.suptitle(f'Fail State Bin Plots\nHyperparameters: Ins={insertion_cost}, Del={deletion_cost}, Sub={substitution_cost}', fontsize=13, y=0.98)
                plt.tight_layout()
                failstate_plot_filename = f"{results_dir}/failstate_plots_{filename_suffix}.png"
                plt.savefig(failstate_plot_filename, dpi=300, bbox_inches='tight')
                plt.close()

                # --- Combined Bin Only Plots ---
                plt.figure(figsize=(12, 10))
                # 1. x: fail state sparcity, y: norm_LD
                plt.subplot(2, 3, 1)
                combined_sparcities = [x[1] for x in combined_data]
                combined_norm_lds = [x[2] for x in combined_data]
                plt.scatter(combined_sparcities, combined_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Fail State Sparcity')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Fail State Sparcity (Combined Bin)')
                plt.grid(True, alpha=0.3)
                # 2. x: scrambledness level, y: norm_LD
                plt.subplot(2, 3, 2)
                combined_levels = [x[0] for x in combined_data]
                plt.scatter(combined_levels, combined_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Scrambledness Level')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Scrambledness Level (Combined Bin)')
                plt.grid(True, alpha=0.3)
                # 3. x: length, y: norm_LD
                plt.subplot(2, 3, 3)
                combined_lengths = [x[3] for x in combined_data]
                plt.scatter(combined_lengths, combined_norm_lds, alpha=0.6, s=10)
                plt.xlabel('Sequence Length')
                plt.ylabel('Normalized Levenshtein Distance')
                plt.title('norm_LD vs Sequence Length (Combined Bin)')
                plt.grid(True, alpha=0.3)
                # 4. 3D: x: length, y: scrambledness, z: norm_LD
                ax = plt.subplot(2, 3, 4, projection='3d')
                ax.scatter(combined_lengths, combined_levels, combined_norm_lds, alpha=0.6, s=10)
                ax.set_xlabel('Length')
                ax.set_ylabel('Scrambledness')
                ax.set_zlabel('norm_LD')
                ax.set_title('3D: Length vs Scrambledness vs norm_LD (Combined Bin)')
                # 5. 3D: x: length, y: fail state level, z: norm_LD
                ax = plt.subplot(2, 3, 5, projection='3d')
                ax.scatter(combined_lengths, combined_sparcities, combined_norm_lds, alpha=0.6, s=10)
                ax.set_xlabel('Length')
                ax.set_ylabel('Fail State Level')
                ax.set_zlabel('norm_LD')
                ax.set_title('3D: Length vs Fail State vs norm_LD (Combined Bin)')
                # 6. 3D: x: fail state level, y: scrambledness level, z: norm_LD
                ax = plt.subplot(2, 3, 6, projection='3d')
                ax.scatter(combined_sparcities, combined_levels, combined_norm_lds, alpha=0.6, s=10)
                ax.set_xlabel('Fail State Level')
                ax.set_ylabel('Scrambledness Level')
                ax.set_zlabel('norm_LD')
                ax.set_title('3D: Fail State vs Scrambledness vs norm_LD (Combined Bin)')
                plt.suptitle(f'Combined Bin Plots\nHyperparameters: Ins={insertion_cost}, Del={deletion_cost}, Sub={substitution_cost}', fontsize=13, y=0.98)
                plt.tight_layout()
                combined_plot_filename = f"{results_dir}/combined_plots_{filename_suffix}.png"
                plt.savefig(combined_plot_filename, dpi=300, bbox_inches='tight')
                plt.close()

                # Save statistics to file (as before)
                stats_filename = f"{results_dir}/stats_{filename_suffix}.txt"
                with open(stats_filename, 'w') as f:
                    f.write(f"Hyperparameters:\n")
                    f.write(f"  Insertion Cost: {insertion_cost}\n")
                    f.write(f"  Deletion Cost: {deletion_cost}\n")
                    f.write(f"  Substitution Cost: {substitution_cost}\n\n")
                    f.write(f"Results:\n")
                    f.write(f"  Generated {len(TARGET_SEQUENCES)} target sequences\n")
                    f.write(f"  Generated {len(SCRAMBLED_BIN)} scrambled sequences\n")
                    f.write(f"  Generated {len(FAIL_STATES_BIN)} fail states sequences\n")
                    f.write(f"  Generated {len(COMBINED_BIN)} combined sequences\n\n")
                
                print(f"Scrambled plots saved to: {scrambled_plot_filename}")
                print(f"Fail state plots saved to: {failstate_plot_filename}")
                print(f"Combined plots saved to: {combined_plot_filename}")
                print(f"Statistics saved to: {stats_filename}")
    
    print(f"\n{'='*60}")
    print("Grid search completed!")
    print(f"Total combinations tested: {total_combinations}")
    print(f"Results saved in: {results_dir}/")
    print(f"{'='*60}")
