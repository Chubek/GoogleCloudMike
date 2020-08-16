o = open("test.txt", "r+")

last_index = int(o.readlines()[-1])

for i in range(last_index, last_index + 50):
    o.write(f"\n{i}")
