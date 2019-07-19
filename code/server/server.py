import socket
import os


def update(id):
    """Function for id detection"""
    lst = os.listdir("./markers")
    for i in lst:
        id.append(int(i.split('_')[1].split('.')[0]))
    return id


def Main():
    host = '127.0.0.1'
    port = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    id = []
    update(id)

    # database initialization
    # key - id of marker, value - history of messages separated by \n
    db = {}
    for i in id:
        db[i] = ""

    # first and last symb delete [1:-1]
    print("Server started")
    # ERROR_1 - Incorrect message
    # ERROR_2 - Id not exists
    # ERROR_3 - Incorrect separators
    # OK - No errors
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print(f"Message from: {addr}")
        print(f"From connected user: {data}")
        if data == "update":
            print("Update request received, updating...")
            update(id)
            s.sendto("OK".encode('utf-8'), addr)
            continue
        elif data[:4] == "get:":
            req_id = int(data.split(':')[1])
            print(f"History of messages for id {req_id} requested")
            if req_id in id:
                print(f"All OK, sending history for {req_id}")
                s.sendto(db[req_id].encode('utf-8'), addr)
                continue
            else:
                print(f"Status: ERROR_2")
                s.sendto("ERROR_2".encode('utf-8'), addr)
                continue
        else:
            if ':' in data:
                data = data.split(':')
                if int(data[0]) in id:
                    if str(data[1]).__len__() != 0 and str(data[1]).__len__() < 50:
                        print(f"Status: OK\nMessage: {data} received\n")
                        db[int(data[0])] += f"{data[1]}\n"
                        s.sendto("OK".encode('utf-8'), addr)
                        continue
                    else:
                        print(f"Status: ERROR_1")
                        s.sendto("ERROR_1".encode('utf-8'), addr)
                        continue
                else:
                    print(f"Status: ERROR_2")
                    s.sendto("ERROR_2".encode('utf-8'), addr)
                    continue
            else:
                print(f"Status: ERROR_3")
                s.sendto("ERROR_3".encode('utf-8'), addr)
                continue


if __name__ == '__main__':
    Main()
