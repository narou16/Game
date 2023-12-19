import socket
import threading
import json

class RPSClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = host, port
        self.exit_flag = False #variable pour determiner si le joueur doit terminer

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            exit()
            #connecter au serveur

    def receive_messages(self): #delai d'attente du receptions des messages
        self.client_socket.settimeout(1)

        while not self.exit_flag:
            try:  #recevoir les donnees json
                json_data = self.client_socket.recv(1024).decode("utf-8")
                data = json.loads(json_data)
                #verifier si le jeu est termine
                if "game_over" in data and data["game_over"]:
                    self.exit_flag = True
                    break
                #afficher le message reçu du serveur
                print(data["message"])

            except socket.timeout: #si le timeout>1
                pass
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_choice(self, choice): #enviyer le choix au serveur
        self.client_socket.send(choice.encode("utf-8"))

    def play_game(self):
        try:  #demmarer le thread pour recevoir les massages su serveur
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            while True:
                choice = input(" ") #entrer son choix 
                self.send_choice(choice)

                if choice.lower() == "quit":
                    print("Exiting...")
                    self.exit_flag = True
                    receive_thread.join()
                    self.client_socket.close()
                    break

        except KeyboardInterrupt:
            print("Exiting...")
            self.exit_flag = True
            receive_thread.join()
            self.client_socket.close()

if __name__ == "__main__":
    host, port = '127.0.0.1', 8921

    client = RPSClient(host, port)
    client.connect_to_server() 
    client.play_game()
