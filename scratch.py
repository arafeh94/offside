file = open("test.txt", 'r')
write = open('337.txt', 'w')
while True:
    line = file.readline()
    if '4830' in line:
        write.write(line)
        write.flush()
