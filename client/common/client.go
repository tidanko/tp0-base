package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	down bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		down: false,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
    signalChannel := make(chan os.Signal, 1)
    // catch SIGETRM or SIGINTERRUPT
    signal.Notify(signalChannel, syscall.SIGTERM)
	go func() {
		s := <-signalChannel
		switch s {
        default:
			c.conn.Close()
			c.down = true
			log.Infof("action: handle_sigterm | result: success")
			return
		}
	} ()

	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		if c.down {
			return
		}

		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()
		
		msg_to_send, err := sendMessage(c.conn, fmt.Sprintf(
			"[AGENCY %v] Bet %v,%v,%v,%v,%v\n",
			c.config.ID,
			os.Getenv("NUMERO"),
			os.Getenv("NOMBRE"),
			os.Getenv("APELLIDO"),
			os.Getenv("DOCUMENTO"),
			os.Getenv("NACIMIENTO"),
		))

		if err != nil {
			return
		}

		msg, err := receiveMessage(c.conn)

		if err != nil {
			return
		}

		c.conn.Close()

		if msg_to_send != msg {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v | error: %v",
				os.Getenv("DOCUMENTO"),
				os.Getenv("NUMERO"),
				"Incorrect message received from server.",
			)
			return
		}

		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			os.Getenv("DOCUMENTO"),
			os.Getenv("NUMERO"),
		)

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	if !c.down {
		log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
	}
}

func receiveMessage(conn net.Conn) (string, error){
	reader := bufio.NewReader(conn)
	var msg string

	for {
		line, err := reader.ReadString('\n')
		msg += line

		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v | error: %v",
				os.Getenv("DOCUMENTO"),
				os.Getenv("NUMERO"),
				err,
			)
			return msg, err
		}

		if len(line) > 0 && line[len(line)-1] == '\n' {
			return msg, err
		}
	}
}

func sendMessage(conn net.Conn, msg string) (string, error){
	sent := 0

	for {
		bytes_sent, err := fmt.Fprint(
			conn,
			msg,
		)

		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v | error: %v",
				os.Getenv("DOCUMENTO"),
				os.Getenv("NUMERO"),
				err,
			)
			return msg, err
		}

		sent += bytes_sent
		if sent == len(msg) {
			break
		}
	}

	return msg, nil
}