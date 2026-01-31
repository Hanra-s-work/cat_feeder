file = "./include/colours.hpp"

data = ""
with open(file, "r", encoding="utf-8") as f:
    data = f.read()

data_list=data.split("\n")
data_list.sort()
cleared_data = "\n".join(data_list)

with open(file, "w", encoding="utf-8", newline="\n") as f:
    f.write(cleared_data)
