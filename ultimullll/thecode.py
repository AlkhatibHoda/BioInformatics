import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

nucleotides = ['A', 'C', 'G', 'T']
S1 = "ATCGATTCGATATCATACACGTAT"
S2 = "CTCGACTAGTATGAAGTCCACGCTTG"
S_test = "CAGGTTGGAAACGTAA"

def get_probabilities(seq):
    counts = {n1: {n2: 1 for n2 in nucleotides} for n1 in nucleotides}
    for i in range(len(seq) - 1):
        counts[seq[i]][seq[i+1]] += 1
    df = pd.DataFrame(counts).T
    return df.div(df.sum(axis=1), axis=0)

prob_plus = get_probabilities(S1)
prob_minus = get_probabilities(S2)

log_likelihood_matrix = prob_plus.div(prob_minus).map(math.log2)

plt.figure(figsize=(8, 6))
sns.heatmap(log_likelihood_matrix, annot=True, cmap='RdYlGn', center=0, fmt='.3f')
plt.title("Log-Likelihood Matrix (Green=CpG Island, Red=Non-Island)")
plt.xlabel("Next Nucleotide")
plt.ylabel("Current Nucleotide")
plt.show()

score = 0
for i in range(len(S_test) - 1):
    score += log_likelihood_matrix.loc[S_test[i], S_test[i+1]]

print(f"Sequence: {S_test}")
print(f"Final Score: {score:.4f}")

if score > 0:
    print("Result: CpG Island")
else:
    print("Result: Non-CpG Island")