def findTheAlphabet ( sequence:str ) :
    alphabet = []
    for char in sequence:
     if char not in alphabet:
        alphabet.append(char)
    return sorted(alphabet)

rna_seq = "AUGCUUAGGCUA"
print("RNA sequence:", rna_seq)
print("Alphabet found:", findTheAlphabet(rna_seq))

text_seq = "this is a loop"
print("\nText sequence:", text_seq)
print("Alphabet found:", findTheAlphabet(text_seq))