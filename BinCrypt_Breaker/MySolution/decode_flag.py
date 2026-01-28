encoded_flag = "RV{r15]_vcP3o]L_tazmfSTaa3s0"
Half_A = encoded_flag[:int(len(encoded_flag)/2)]
Half_B = encoded_flag[int(len(encoded_flag)/2):]

def shuffle_and_XOR(param: str,XOR_key: int) -> str:
    shuffle_1 = [9,12,2,10,4,1,6,3,8,5,7,11,0,13]
    shuffle_2 = [2,4,6,8,11,13]
    shuffled_result = ['\0'] * 14
    
    param = list(param)
    for i in shuffle_2: 
        param[i] = chr(ord(param[i]) ^ XOR_key)
    param = "".join(param)
    
    for _ in range(8): # Shuffle for 8 times
        for z in range(14):
            shuffled_result[shuffle_1[z]] = param[z]
        #print(shuffled_result)
        param = "".join(shuffled_result)
    return param

def swap(param: str, start: int, end: int) -> str:
    param = list(param)
    temp_value = param[start]
    param[start] = param[end]
    param[end] = temp_value
    return "".join(param)

deobfus_A = shuffle_and_XOR(Half_A,2)
deobfus_B = shuffle_and_XOR(Half_B,3)
Deobfus_flag = deobfus_A + deobfus_B

Deobfus_flag = swap(Deobfus_flag,0,12)
Deobfus_flag = swap(Deobfus_flag,14,26)
Deobfus_flag = swap(Deobfus_flag,4,8)
Deobfus_flag = swap(Deobfus_flag,20,23)
print(Deobfus_flag)
