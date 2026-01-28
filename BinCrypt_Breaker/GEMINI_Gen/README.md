# CTF Binary Analysis Report: rev_bincrypt_breaker

## 1. Initial Assessment

The challenge involved two files: `checker` and `file.bin`.

### Binary Characteristics of `checker`:
- **File Type:** ELF 64-bit LSB pie executable, x86-64, dynamically linked, not stripped.
- **Security Protections:**
    - **Partial RELRO:** Global Offset Table is partially read-only.
    - **Canary Found:** Stack canaries are present.
    - **NX Enabled:** Non-executable stack.
    - **PIE Enabled:** Position-Independent Executable (ASLR for code).
    - **Symbols:** 34 symbols present (as confirmed by `checksec` and `file`).

### Summary:
The `checker` binary is a 64-bit Linux executable with standard mitigations (Canary, NX, PIE) but is not stripped, which greatly aids static analysis.

## 2. Analysis Methods

The analysis was performed in two main stages:
1.  **Analysis of `checker`:** To understand how `file.bin` is processed.
2.  **Analysis of `decrypted_binary` (from `file.bin`):** To identify the flag validation logic.

### Static Analysis (using `ghidra_mcp` and manual analysis):

#### `checker` Binary:
- **`main` function:** The `main` function (decompiled output below) was identified to call a function named `decrypt`. The return value of `decrypt` (a file descriptor) was then used to construct a path to `/proc/self/fd/%d`, which was subsequently executed using `fexecve`. This indicated `decrypt` was responsible for generating an executable.

```c
bool main(EVP_PKEY_CTX *param_1,uchar *param_2,size_t *param_3,uchar *param_4,size_t param_5)
{
  uint __fd;
  int iVar1;
  int __fd_00;
  long in_FS_OFFSET;
  char *local_1030;
  char *local_1028;
  undefined8 local_1020;
  char local_1018 [4104];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  __fd = decrypt(param_1,param_2,param_3,param_4,param_5); // Call to decrypt
  iVar1 = snprintf(local_1018,0x1000,"/proc/self/fd/%d",(ulong)__fd);
  if (-1 < iVar1) {
    __fd_00 = open(local_1018,0);
    close(__fd);
    local_1028 = "<anonymous>";
    local_1020 = 0;
    local_1030 = (char *)0x0;
    fexecve(__fd_00,&local_1028,&local_1030); // Execution of decrypted program
  }
  else {
    perror("formatting");
  }
  // ... stack canary check ...
  return -1 >= iVar1;
}
```

- **`decrypt` function:** This function was found to open `file.bin`, read its contents byte by byte, XOR each byte with `0xab`, and write the result to an unnamed temporary file (using `O_TMPFILE`) via a file descriptor. This file descriptor was then returned.

```c
int decrypt(EVP_PKEY_CTX *ctx,uchar *out,size_t *outlen,uchar *in,size_t inlen)
{
  long in_FS_OFFSET;
  uint local_20;
  int local_1c;
  FILE *local_18;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_18 = fopen("file.bin","rb"); // Opens "file.bin"
  // ... error handling ...
  local_1c = open(".",0x490201,0x1ed); // Creates temporary file (O_TMPFILE)
  // ... error handling ...
  while( true ) {
    local_20 = fgetc(local_18); // Reads byte from file.bin
    if (local_20 == 0xffffffff) break;
    local_20 = local_20 ^ 0xab; // XOR decryption with 0xab
    write(local_1c,&local_20,1); // Writes decrypted byte
  }
  fclose(local_18);
  // ... stack canary check ...
  return local_1c; // Returns file descriptor
}
```

#### `decrypted_binary` (generated from `file.bin`):
- After extracting `file.bin` using the XOR key `0xab`, it was found to be another ELF executable.
- The `main` function of this binary (`FUN_001015f3` after renaming) prompts the user for a flag and calls `FUN_001014a1` to validate it.

```c
undefined8 FUN_001015f3(void) // Renamed to main_decrypted_binary
{
  int iVar1;
  long in_FS_OFFSET;
  char local_38 [40]; // Buffer for user input
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Enter the flag (without `HTB{}`): "); // Prompt
  __isoc99_scanf("%28s",local_38); // Reads input
  iVar1 = FUN_001014a1(local_38); // Calls validation function
  if (iVar1 == 0) {
    puts("Correct flag"); // Success message
  }
  else {
    puts("Wrong flag"); // Failure message
  }
  // ... stack canary check ...
  return 0;
}
```
- **`FUN_001014a1`:** This function takes the user's input, applies a series of transformations, and then compares the result to a hardcoded string `RV{r15]_vcP3o]L_tazmfSTaa3s0` using `strcmp`.
    - It first calls `FUN_0010127d` on the entire input.
    - Then, it splits the (transformed) input into two 14-character halves using `FUN_0010121f`.
    - Each half is then passed to `FUN_001012e4` with different keys (2 and 3 respectively).
    - The results from `FUN_001012e4` are concatenated and compared with `"RV{r15]_vcP3o]L_tazmfSTaa3s0"`.

- **`FUN_001012e4`:** This function applies a byte-wise XOR with `param_2` at specific indices and performs a character permutation 8 times.
    - **XOR Indices:** `[2, 4, 6, 8, 11, 13]`
    - **Permutation:** Defined by `local_58 = [9, 12, 2, 10, 4, 1, 6, 3, 8, 5, 7, 11, 0, 13]`

- **`FUN_0010127d`:** This function applies a series of character swaps using `FUN_001011c9`.
    - `swap(0, 12)`
    - `swap(14, 26)`
    - `swap(4, 8)`
    - `swap(20, 23)`

- **`FUN_001011c9`:** A simple character swap function.

## 3. Vulnerability Identification

The core "vulnerability" is the obfuscation/encryption scheme. The program has two layers:
1.  **Outer Layer:** `file.bin` is XOR-encrypted with `0xab` to produce an executable flag-checker.
2.  **Inner Layer:** The flag-checker itself performs a series of transformations (swaps, permutations, and XORs) on the user's input before comparing it to a hardcoded string. Reversing these transformations reveals the original flag.

## 4. Exploitation Walkthrough

### Step 1: Decrypt `file.bin`

`file.bin` was XOR-ed with `0xab`. A Python script was used to decrypt it:
```python
with open('file.bin', 'rb') as f:
    encrypted_data = f.read()

decrypted_data = bytearray()
for byte in encrypted_data:
    decrypted_data.append(byte ^ 0xab)

with open('decrypted_binary', 'wb') as f:
    f.write(decrypted_data)
```
The resulting `decrypted_binary` was made executable using `chmod +x decrypted_binary`.

### Step 2: Reverse `FUN_001012e4` transformations

The `strcmp` in `FUN_001014a1` compares the transformed user input with `"RV{r15]_vcP3o]L_tazmfSTaa3s0"`. This target string needed to be reversed through the `FUN_001012e4` transformations.

The string was split into two 14-character parts:
- `part1_encrypted = "RV{r15]_vcP3o]"` (processed with key 2)
- `part2_encrypted = "L_tazmfSTaa3s0"` (processed with key 3)

The reversal involved:
- **Inverse XOR:** XORing specific characters with the respective key (2 or 3).
- **Inverse Permutation:** Applying the inverse permutation (`P_inv = [12, 5, 2, 7, 4, 9, 6, 10, 8, 0, 3, 11, 1, 13]`) eight times.

A Python script `solve_partial.py` was created:
```python
def reverse_transform(s, key):
    s = list(s)
    xor_indices = [2, 4, 6, 8, 11, 13]
    for i in xor_indices:
        s[i] = chr(ord(s[i]) ^ key)

    inv_p = [12, 5, 2, 7, 4, 9, 6, 10, 8, 0, 3, 11, 1, 13]
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

# Output:
# Part 1 intermediate: 5RyP3o_rtV_1c_
# Part 2 intermediate: mLwayseaW_S0a3
# Combined: 5RyP3o_rtV_1c_mLwayseaW_S0a3
```
This gave the intermediate string: `5RyP3o_rtV_1c_mLwayseaW_S0a3`.

### Step 3: Reverse `FUN_0010127d` (Swap) transformations

The intermediate string was then reversed through the swap operations performed by `FUN_0010127d`. The swaps were applied in reverse order:
1.  `swap(20, 23)`
2.  `swap(4, 8)`
3.  `swap(14, 26)`
4.  `swap(0, 12)`

A Python script `final_solve.py` was used:
```python
def swap(s_list, i, j):
    s_list[i], s_list[j] = s_list[j], s_list[i]

intermediate_str = "5RyP3o_rtV_1c_mLwayseaW_S0a3"
flag_list = list(intermediate_str)

swap(flag_list, 20, 23) # Reversing swap(20, 23)
swap(flag_list, 4, 8)   # Reversing swap(4, 8)
swap(flag_list, 14, 26) # Reversing swap(14, 26)
swap(flag_list, 0, 12)  # Reversing swap(0, 12)

final_flag = "".join(flag_list)
# Output: cRyPto_r3V_15_aLways_aWeS0m3
```

### Step 4: Verify the Flag

The final flag was provided to the `decrypted_binary`:
`echo "cRyPto_r3V_15_aLways_aWeS0m3" | ./decrypted_binary`

Output:
`Enter the flag (without `HTB{}`): Correct flag`

## 5. Extracted Flags

The flag is: `cRyPto_r3V_15_aLways_aWeS0m3`