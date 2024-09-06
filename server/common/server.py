import socket
import logging
import signal
import sys
from multiprocessing import Process, Lock, Barrier
from common.utils import Bet, store_bets, load_bets, has_won

NUMBER_AGENCIES = 5

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.file_lock = Lock()
        self.barrier = Barrier(NUMBER_AGENCIES)
        self.down = False

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        signal.signal(signal.SIGTERM, self.__handle_sigterm)

        processes = []
        while not self.down:
            client_sock = self.__accept_new_connection()
            if self.down:
                return
            p = Process(target=self.__handle_client_connection, args=(client_sock,))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            agency_id = ""
            bets_list = []
            bets_amount = 0
            while True:
                for msg in self.__read_message(client_sock):
                    splitted_msg = msg.split()
                    if splitted_msg[2] == 'ReadyForLottery':
                        self.barrier.wait()
                        self.__send_lottery_results(client_sock, agency_id)
                        return
                    if splitted_msg[2] == 'BetBatchEnd':
                        self.file_lock.acquire()
                        store_bets(bets_list)
                        self.file_lock.release()
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {bets_amount}')
                        self.__send_message(client_sock, msg)
                        bets_list = []
                        bets_amount = 0
                        continue
                    addr = client_sock.getpeername()
                    agency_id = splitted_msg[1].strip("]")
                    bet_info = " ".join(splitted_msg[3:]).split(",")
                    if len(bet_info) < 5:
                        raise OSError
                    logging.debug(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                    bets_list.append(Bet(agency_id, bet_info[1], bet_info[2], bet_info[3], bet_info[4], bet_info[0]))
                    bets_amount += 1                         
                    logging.debug(f'action: apuesta_almacenada | result: success | dni: {bet_info[3]} | numero: {bet_info[0]}')

        except OSError as e:
            logging.error(f'action: mensaje_enviado | result: fail | error: {e}')

    def __send_lottery_results(self, client_sock, agency_id):
        amount_winners_agency = 0
        for bet in load_bets():
            if bet.agency == int(agency_id) and has_won(bet):
                amount_winners_agency += 1
        self.__send_message(client_sock, f"Winners {amount_winners_agency}")
        client_sock.close()     

    def __read_message(self, client_sock):
        msg = b''
        while True:
            received = client_sock.recv(1024)
            msg += received
            try:
                if msg.decode('utf-8')[-1] == '\n':
                    break
            except:
                continue
        return msg.decode('utf-8').rstrip().split('\n')

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