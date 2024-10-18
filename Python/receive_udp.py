import socket 


def parseMessage(message,tockaSkoki,idTab):
    sk = []
    for i in range(len(message)):
        if(message[i] == "J" and message[i+1] == "I"):
            sk.append(int(message[i+2:i+5]))    
        if(message[i] == "J" and message[i+1] == "T"):
            sk.append(int(message[i+2:i+10]))
        if(message[i] == "F" and message[i+1] == "T"):
            sk.append(int(message[i+2:i+6]))
            if sk[0] not in idTab:
                idTab.append(sk[0])
                tockaSkoki.append(sk)
                print(sk)
            sk = []
         
     
UDP_IP = "" 
UDP_PORT = 123123
     
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
sock.bind((UDP_IP, UDP_PORT)) 

tockaSkoki = []
idTab = []
setSkoki = []
tekmaSkoki = []

st = 0
while True:
    st = st+1
    data, addr = sock.recvfrom(1024) 
    print(str(data))
    parseMessage(str(data), tockaSkoki,idTab)
    if(st > 100):
        break


