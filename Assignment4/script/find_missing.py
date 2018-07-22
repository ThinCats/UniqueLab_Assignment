

f_a = open("a", "r")
f_b = open("b", "r")

b_lines = f_b.readlines()
# b_out = [x.split(".")[0].strip() for x in b_lines]
i = 0
for line in f_a.readlines():
    if not line in b_lines:
        print(line)

f_a.close()
f_b.close()
