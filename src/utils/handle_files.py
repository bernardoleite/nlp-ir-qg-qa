import random
import os
def create_file(nameFile, index_lines):
    file = open(nameFile, "w") 
    for index in index_lines:
        file.write(str(index)+"\n")
    file.close()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def read_file(file_num):
    #with open(os.path.dirname(__file__) + '/../texts/{:02}.txt'.format(file_num), "r") as f:
    with open(file_num, "r") as f:
     
        lines = {}
        i = 0
        for line in f:
            lines[i] = line
            i += 1
    return lines

def create_files(nr_lines, nr_files, nr_linesPerfile):
    i = 1
    list_lines = list(range(nr_lines))

    totalLines = nr_linesPerfile*nr_files

    chosen_lines = random.sample(list_lines, totalLines)

    l=0
    m=len(chosen_lines)
    count=0

    dataset = open("datasets/wikisent2.txt", "r") 
    dataset_lines=dataset.readlines()
    while i <= nr_files and count < m:

        file = open("files/"+'{:02}'.format(str(i))+".txt", "w") 
        for index in chosen_lines[l:l+nr_linesperfile]:
            file.write(dataset_lines[index])
        file.close()

        l=l+nr_linesPerfile
        count=count+nr_linesPerfile
        i+=1

    dataset.close()
  
    print(chosen_lines)

    return ""

def main():
    print("Hello Files")
    nr_lines = file_len("datasets/wikisent2.txt")
    create_files(nr_lines, 50, 20)

if __name__== "__main__":
    #main()
    d = read_file(51)
    for k,v in d.items():
        print(v)