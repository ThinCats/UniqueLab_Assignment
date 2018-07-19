
with open("white_list", "r") as f_in:
    with open("white_list_out", "w") as f_out:

        for line in f_in.readlines():
            line = line.replace("@", "")
            line = line.replace("|", "")
            line = line.replace("http://", "")
            line = line.replace("https://", "")
            print(line)
            f_out.write(line)


