import socket
import logging
import signal
import sys
from common.utils import Bet, store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.down = False

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server

        signal.signal(signal.SIGTERM, self.__handle_sigterm)

        while not self.down:
            client_sock = self.__accept_new_connection()
            if self.down:
                return
            self.__handle_client_connection(client_sock)

   

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024)
            if msg[-1] != '\n':
                raise OSError
            msg = msg.rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            agency_id = msg.split(" ")[1].strip("]")
            bet_info = msg.split(" ")[3].split(",")
            if len(bet_info) < 5:
                raise OSError
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            client_bet = Bet(agency_id, bet_info[1], bet_info[2], bet_info[3], bet_info[4], bet_info[0])
            store_bets([client_bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {msg[7]} | numero: {msg[5]}')
            # TODO: Modify the send to avoid short-writes
            msg = "{}\n".format(msg).encode('utf-8')
            sent = 0
            while len(msg) != sent:
                bytes_sent = client_sock.send(msg[sent:])
                if bytes_sent == 0:
                    break
                sent += bytes_sent
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
            logging.error("action: apuesta_almacenada | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
        except OSError:
            return
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    
    def __handle_sigterm(self, _a, _b):
        "Close server socket and log info about it"

        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        self.down = True
        logging.info('action: handle_sigterm | result: success')