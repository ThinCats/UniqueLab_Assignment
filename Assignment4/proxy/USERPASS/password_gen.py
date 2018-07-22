import hmac

from faker import Faker

fake_gen = Faker("en_US")

f_pass = open("password_lst", "w")
f_token = open("token_lst", "w")
f_pass.write("{\n")
f_token.write("{\n")

length = 600
name_set = set()
i = 0
while i < length:
    name = fake_gen.name().split()[0].strip().lower()
    password = fake_gen.word() + fake_gen.year()
    if name in name_set:
        continue

    name_set.add(name)
    print(password)
    print("{}:{}".format(name, password))
    token = hmac.new(password.strip().encode("ascii"), name.strip().encode("ascii")).hexdigest()
    if i == length-1:
        end = ""
    else:
        end = ","
    f_pass.write("\"{}\" : \"{}\"{}\n".format(name, password, end))
    f_token.write("\"{}\" : \"{}\"{}\n".format(name, token, end))
    i += 1

f_pass.write("}\n")
f_token.write("}\n")
f_pass.close()
f_token.close()
