def dna_composition(seq: str):
    alphabet = []
    for char in seq:
        if char not in alphabet:
            alphabet.append(char)

    composition = {}
    length = len(seq)

    for char in alphabet:
        count = seq.count(char)
        percentage = (count / length) * 100
        composition[char] = round(percentage, 2)

    return sorted(alphabet), composition


S = "ACGGGCATATGCGC"

alphabet, composition = dna_composition(S)

print("DNA sequence:", S)
print("Alphabet:", alphabet)
print("Composition (%):")
for base, perc in composition.items():
    print(f"{base}: {perc}%")
