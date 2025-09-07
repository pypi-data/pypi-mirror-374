import random,string
from printslow import printslow#LOOOOOL

def encryptext():
    encodec(fetchdata("chars"), fetchdata("key"), input("Enter a message to encrypt: "))

def decryptext():
    encodec(fetchdata("key"),fetchdata("chars"), input("Enter a message to decrypt: "))

def generatekeychar():
    chars = list(" " + string.punctuation + string.digits + string.ascii_letters)
    random.shuffle(chars)
    key = chars.copy()
    random.shuffle(key)
    while True:
        if key == chars:
            random.shuffle(key)
        else:
            break
    setdata("chars",chars)
    setdata("key",key)
    #you need both chars.txt and key.txt as the key cipher text matches to the chars cipher to find out the mapping
    #the next step would be to shift the key.txt every letter to make it an enigma machine with two rotors

    printslow("Done.")
    printslow("OUTPUT TO FILE:" + "cannot show...")

#repeating code block methods
def fetchdata(filename):
    try:
        file = open(filename+".txt", "r")
    except FileNotFoundError:
        printslow("FILE NOT FOUND: CRITICAL ERROR... TERMINATING...", 0.05)
        return 0
    temp_data = file.readlines()
    file.close()
    counter = 0
    for char in temp_data:
        temp_data[counter] = char.strip("\n")
        counter += 1
    return temp_data

def setdata(filename,charset1):
    file = open(filename+".txt", "w")
    random.shuffle(charset1)
    for carrier in charset1:
        file.write(carrier + "\n")
    file.close()


def encodec(charset1,charset2,text1):#the charset1 is the pair that matches with the type of writing text1 is (if text1 is encrypted then charset1 is the key.txt file)
    text2 = ""

    for letter in text1:
        index = charset1.index(letter)
        text2 += charset2[index]

    printslow("Done.")

    number = ""
    for carrier in range(0, 20):
        number += str(random.randint(0, 9))

    if save:
        passwordfile = open("output " + number + ".txt", "w")
        passwordfile.write(text2)
        passwordfile.flush()#force buffer to write always after a write command instead of leaving in buffer until forced to write by a close signal (exit() or quit() etc.)
        passwordfile.close()
        printslow("OUTPUT TO FILE:" + text2)
    else:
        printslow("OUTPUT:" + text2)
#end of repeating code block methods

def run():
    #main code
    printslow("Encryptext V4: MESSAGE ENCRYPT AND DECRYPTOR")
    global save
    save = False#refers to creating a save file output
    while True:
        i = input("type command to run: encrypt(e), decrypt(d), generate key and char(g), toggle saving to external file in same directory(s) and exit(q)")
        if i == 'g':
            generatekeychar()
        elif i == 'd':
            decryptext()
        elif i == 'e':
            encryptext()
        elif i == 'q':
            exit()
        elif i == 'h':
            printslow("WIP")
        elif i == 's':
            if save == True:
                save = False
            else:
                save = True
            printslow("Saving set to: " + str(save))