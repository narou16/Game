import socket
import select
import threading
import json

class RPSServer:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = host, port
        self.socket_list = [self.server_socket]
        self.clients = {}
        self.player_choices = {}
        self.continue_playing = True
        self.lock = threading.Lock()

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(2)

            print(f"Server listening on {self.host}:{self.port}")

            while True:
                read_list, _, _ = select.select(self.socket_list, [], [])

                for sock in read_list:
                    if sock == self.server_socket:
                        self.handle_new_connection()
                    else:
                        self.handle_client(sock)

        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server_socket.close()

    def handle_new_connection(self):
        client, address = self.server_socket.accept()
        self.socket_list.append(client)

        player_num = len(self.clients) + 1
        self.clients[f"Player{player_num}"] = client
        print(f"Player {player_num} connected from {address}\n")

        if player_num == 1:
            print("Waiting for Player 2 to connect...\n")
        elif player_num == 2:
            print("Both players connected. Starting the game...\n")
            game_thread = threading.Thread(target=self.handle_game, args=(self.clients["Player1"], self.clients["Player2"]))
            game_thread.start()

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024).decode("utf-8")

            if data.lower() == "quit":
                self.continue_playing = False

            with self.lock:
                self.player_choices[client_socket] = data

        except Exception as e:
            print(f"Error handling client: {e}")
            client_socket.close()
            self.socket_list.remove(client_socket)

    def send_to_player(self, player_socket, message):
        try:
            data = {"message": message}
            json_data = json.dumps(data)
            player_socket.send(json_data.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message to a player: {e}")

    def handle_game(self, player1, player2):
        choices = ["rock", "paper", "scissors"]

        while self.continue_playing:
            self.player_choices[player1], self.player_choices[player2] = "", ""

            self.send_to_player(player1, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
            self.send_to_player(player2, "Waiting for Player 1 to make a choice...\n")

            while not self.player_choices[player1]:
                pass

            self.send_to_player(player2, "Welcome to the Rock-Paper-Scissors game! Please enter your choice (rock, paper, scissors, or quit):")
            self.send_to_player(player1, "Waiting for Player 2 to make a choice...\n")

            while not self.player_choices[player2]:
                pass

            if "quit" in [self.player_choices[player1].lower(), self.player_choices[player2].lower()]:
                break

            result_message = {
                "player1_choice": self.player_choices[player1],
                "player2_choice": self.player_choices[player2],
                "result": "It's a tie!" if self.player_choices[player1].lower() == self.player_choices[player2].lower() else "Player 1 wins!" if (self.player_choices[player1].lower() == "rock" and self.player_choices[player2].lower() == "scissors") or \
                (self.player_choices[player1].lower() == "paper" and self.player_choices[player2].lower() == "rock") or \
                (self.player_choices[player1].lower() == "scissors" and self.player_choices[player2].lower() == "paper") else "Player 2 wins!"
            }

            json_result = json.dumps(result_message)
            self.send_to_player(player1, json_result)
            self.send_to_player(player2, json_result)

            p1_again = player1.recv(1024).decode("utf-8")
            p2_again = player2.recv(1024).decode("utf-8")

            if p1_again.lower() == "again" and p2_again.lower() == "again":
                self.continue_playing = True
            else:
                self.continue_playing = False

if __name__ == "__main__":
    host, port = '127.0.0.1', 8921
    server = RPSServer(host, port)
    server.start()