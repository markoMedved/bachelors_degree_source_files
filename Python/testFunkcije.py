

def parseMessage(message,tockaSkoki,idTab):
    sk = []
    for i in range(len(message)):
        if(message[i] == "J" and message[i+1] == "I"):
            sk.append(int(message[i+2:i+5]))    
        if(message[i] == "J" and message[i+1] == "T"):
            print(sk)
            sk.append(int(message[i+2:i+10]))
            print(sk)
        if(message[i] == "F" and message[i+1] == "T"):
            sk.append(int(message[i+2:i+6]))
            if sk[0] not in idTab:
                idTab.append(sk[0])
                tockaSkoki.append(sk)
            sk = []
                
                

   
                

tockaSkoki = []
idTabela = [5]
tockaSkoki.append([5,180060,525])

