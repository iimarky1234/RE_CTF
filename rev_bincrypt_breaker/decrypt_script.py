with open('file.bin', 'rb') as f:
    encrypted_data = f.read()

decrypted_data = bytearray()
for byte in encrypted_data:
    decrypted_data.append(byte ^ 0xab)

# Save the decrypted data to a new file
with open('decrypted_binary', 'wb') as f:
    f.write(decrypted_data)

print("Decryption complete. Decrypted data saved to 'decrypted_binary'.")