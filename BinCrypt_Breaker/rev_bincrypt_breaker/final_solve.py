
def swap(s_list, i, j):
    s_list[i], s_list[j] = s_list[j], s_list[i]

intermediate_str = "5RyP3o_rtV_1c_mLwayseaW_S0a3"
flag_list = list(intermediate_str)

# Reverse the swaps in the opposite order they were applied
swap(flag_list, 20, 23)
swap(flag_list, 4, 8)
swap(flag_list, 14, 26)
swap(flag_list, 0, 12)

final_flag = "".join(flag_list)
print(final_flag)
