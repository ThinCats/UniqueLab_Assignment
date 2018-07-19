

with open("black_list_out", "r") as f_in:
    with open("black_list_derep", "w") as f_out:
        out_set = set()
        for line in f_in.readlines():
            words = line.split(".")
            if len(words) == 1:
                continue
            word = words[-2] + "." + words[-1].split("/")[0].rstrip() + "\n"
            print(word)
            out_set.add(word)
        for word in out_set:
            f_out.write(word)



