import socket
import logging
import signal
import sys
from common.utils import Bet, store_bets, load_bets, has_won

NUMBER_AGENCIES = 5

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.clients_finished = 0
        self.clients_sockets = {}
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
        bets_amount = 0
        try:
            bets_list = []
            keep_going = True
            while keep_going:
                for msg in self.__read_message(client_sock):
                    if msg.split()[2] == 'ReadyForLottery':
                        self.__manage_ready_for_lottery(client_sock, msg)
                        return
                    if msg.split()[2] == 'BetBatchEnd':
                        store_bets(bets_list)
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {bets_amount}')
                        self.__send_message(client_sock, msg)
                        keep_going = False
                        break
                    addr = client_sock.getpeername()
                    agency_id = msg.split(" ")[1].strip("]")
                    bet_info = " ".join(msg.split(" ")[3:]).split(",")
                    if len(bet_info) < 5:
                        raise OSError
                    logging.debug(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                    bets_list.append(Bet(agency_id, bet_info[1], bet_info[2], bet_info[3], bet_info[4], bet_info[0]))
                    bets_amount += 1                         
                    logging.debug(f'action: apuesta_almacenada | result: success | dni: {bet_info[3]} | numero: {bet_info[0]}')

            client_sock.close()

        except OSError as e:
            logging.error(f'action: mensaje_enviado | result: fail | error: {e}')


    def __manage_ready_for_lottery(self, client_sock, msg):
        self.clients_finished += 1
        self.clients_sockets[msg.split(" ")[1].strip("]")] = client_sock
        if self.clients_finished == NUMBER_AGENCIES:
            logging.info('action: sorteo | result: success')
            self.__send_lottery_results()

    def __send_lottery_results(self):
        bets = load_bets()
        amount_winners_by_agency = {}
        for bet in bets:
            if has_won(bet):
                amount_winners_by_agency[bet.agency] = amount_winners_by_agency.get(bet.agency, 0) + 1
        for agency in self.clients_sockets:
            self.__send_message(self.clients_sockets[agency], f"Winners {amount_winners_by_agency[int(agency)] if int(agency) in amount_winners_by_agency else 0}")
            self.clients_sockets[agency].close()       

    def __read_message(self, client_sock):
        msg = ''
        while msg == '' or msg[-1] != '\n':
            received = client_sock.recv(1024).decode('utf-8')
            if received == '':
                raise OSError
            msg += received
        return msg.rstrip().split('\n')

    def __send_message(self, client_sock, msg):
        msg = "{}\n".format(msg).encode('utf-8')
        sent = 0
        while len(msg) != sent:
            bytes_sent = client_sock.send(msg[sent:])
            if bytes_sent == 0:
                break
            sent += bytes_sent

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