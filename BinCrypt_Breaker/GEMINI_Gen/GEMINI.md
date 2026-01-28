# Gemini Code Assistant Context: `rev_bincrypt_breaker` CTF

## Project Overview

This directory contains the solution and artifacts for a reverse engineering CTF challenge named `rev_bincrypt_breaker`. The challenge involves a two-stage obfuscated binary.

1.  **Stage 1 (`checker`):** An initial ELF binary that reads a data file (`file.bin`).
2.  **Stage 2 (`file.bin`):** An encrypted data file which, when decrypted, is another ELF binary (`decrypted_binary`). This second binary contains the actual flag validation logic.

The goal was to reverse engineer both binaries to ultimately find the correct flag.

**Technologies:**
*   **Binaries (`checker`, `decrypted_binary`):** 64-bit ELF executables, likely written in C.
*   **Solve Scripts:** Python scripts were created to automate the decryption and flag reconstruction process.

## Analysis and Solution Walkthrough

The solution process is documented in `CTF_Report.md`. The key steps were:

1.  **Static Analysis of `checker`:** Decompilation revealed that `checker` reads `file.bin`, performs a byte-wise XOR with the key `0xab`, and executes the result in memory.
2.  **Extraction of Stage 2:** The `decrypt_script.py` was created to perform the XOR decryption on `file.bin`, saving the output as `decrypted_binary`.
3.  **Static Analysis of `decrypted_binary`:** The second binary prompts for a flag and compares it to a hardcoded, obfuscated string: `"RV{r15]_vcP3o]L_tazmfSTaa3s0"`. The user's input undergoes a series of character swaps and permutations before the comparison.
4.  **Flag Reconstruction:** The transformations in `decrypted_binary` were reverse-engineered. The `final_solve.py` script applies the inverse transformations to the hardcoded string to reveal the true flag.

## Key Files

*   `checker`: The initial stage-1 challenge binary.
*   `file.bin`: The encrypted stage-2 binary.
*   `decrypted_binary`: The decrypted stage-2 binary, which performs the flag check.
*   `CTF_Report.md`: A full technical report detailing the analysis and solution steps.
*   `decrypt_script.py`: Script to decrypt `file.bin` -> `decrypted_binary`.
*   `final_solve.py`: Script to reverse the flag obfuscation logic in `decrypted_binary` and print the correct flag.

## Running the Solution

The flag can be obtained and verified with the following steps:

1.  **Create the decrypted binary:**
    ```bash
    python3 decrypt_script.py
    chmod +x decrypted_binary
    ```
2.  **Solve for the flag:**
    ```bash
    python3 final_solve.py
    ```
    This will print the flag: `cRyPto_r3V_15_aLways_aWeS0m3`

3.  **Verify the flag:**
    ```bash
    echo "cRyPto_r3V_15_aLways_aWeS0m3" | ./decrypted_binary
    ```
    This will output `Correct flag`.
