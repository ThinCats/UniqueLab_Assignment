import sys
with open("gfwlist.txt", "r+") as f:
    if f.readline().rstrip() == "PRE_HANDLED":
        print("Has yet been pre handled")
        f.close()
        sys.exit(0)
    # Open white_list, black_list:
    white_f = open("white_list", "w")
    black_f = open("black_list", "w")

    for line in f.readlines():
        # Ignore
        if len(line) == 1:
            continue
        if line[0] == "!" or line[0] == "[":
            continue
        elif line[1] == "@":
            white_f.write(line)
        else:
            black_f.write(line)
	# Write header to gfwlist
    f.seek(0)
    old = f.read()
    f.seek(0)
    f.write("PRE_HANDLED")
    f.write('\n')
    f.write(old)
    # Close
    white_f.close()
    black_f.close()
