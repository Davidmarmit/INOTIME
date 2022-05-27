import signal
import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.199.32", 4444))
server.listen()
print("Servidor creat.")



def Signal_Handler(signal, frame):
    print("Tancant servidor.")
    server.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, Signal_Handler)
    img_count = 0
    os.system("rmdir /s /q img ")
    os.system("mkdir img")
    while True:
        # Socket connection that recieves the image from the raspberry pi 4
        print("Esperant connexions...")
        client_socket, client_address = server.accept()
        # if img_count > 4:
        #     os.system("cd img && del imatge" + str(img_count - 5) + ".jpg")
        #     os.system("cd shadows && del imatge" + str(img_count - 5) + ".png")
        file = open('img/imatge' + str(img_count) + '.jpg', "wb+")
        img_count += 1
        image_chunk = client_socket.recv(2048)

        while image_chunk:
            file.write(image_chunk)
            image_chunk = client_socket.recv(2048)
        file.close()
        print("Foto rebuda.")
