
def reverse_transform(s, key):
    s = list(s)
    # Inverse of XOR is XOR
    xor_indices = [2, 4, 6, 8, 11, 13]
    for i in xor_indices:
        s[i] = chr(ord(s[i]) ^ key)

    # Inverse permutation table
    # P_inv[P[i]] = i
    # P = [9, 12, 2, 10, 4, 1, 6, 3, 8, 5, 7, 11, 0, 13]
    inv_p = [12, 5, 2, 7, 4, 9, 6, 10, 8, 0, 3, 11, 1, 13]

    # Apply inverse permutation 8 times
    for _ in range(8):
        temp = s[:]
        for i in range(14):
            temp[i] = s[inv_p[i]]
        s = temp
    
    return "".join(s)

part1_encrypted = "RV{r15]_vcP3o]"
part2_encrypted = "L_tazmfSTaa3s0"

part1_intermediate = reverse_transform(part1_encrypted, 2)
part2_intermediate = reverse_transform(part2_encrypted, 3)

print(f"Part 1 intermediate: {part1_intermediate}")
print(f"Part 2 intermediate: {part2_intermediate}")
print(f"Combined: {part1_intermediate}{part2_intermediate}")
