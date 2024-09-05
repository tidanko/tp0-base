# TP0: Docker + Comunicaciones + Concurrencia - Documentacion

## Parte 2
Para la segunda parte del ejercicio, se pidió formular un protocolo de comunicaciones entre clientes y servidor.

Inicialmente, para el envío de la información de las apuestas entre los mismos, se define un mensaje **Bet**, que contiene toda la información competente (nombre, apellido, fecha de nacimiento, número, agencia y documento).

Con el objetivo de enviar dicha información en chunks, en vez de tener que abrir y cerrar los canales de comunicación por cada mensaje transmitido por el cliente, se implementó un mensaje adicional **BetBatchEnd**. Gracias al mismo, el servidor puede leer varios bloques conjuntos de información sucesivamente, y es dicho mensaje el que indica cuando se debe detener la lectura para proceder a persistir la información.

Una vez los clientes envían todas las apuestas correspondientes a las agencias en cuestión, esto se comunica por medio del mensaje **ReadyForLottery**. Al trabajar en este caso con 5 agencias, el servidor almacena la cantidad de veces que fue recibido dicho mensaje hasta llegar a 5, momento en el cual se comienza con la lotería. Luego de enviar este mensaje, cada cliente espera indefinidamente hasta que todos los clientes en cuestion hayan terminado con sus envíos, momento en el cual reciben por parte del servidor el mensaje **Winners**, que contiene la cantidad de ganadores para la agencia que lo recibe.


## Parte 3
Para la tercera parte del ejercicio, se pidió que el servidor fuera capaz de aceptar nuevas conexiones y procesar solicitudes en paralelo.

Para realizar dicho ejercicio, se optó por el uso de la librería multiprocessing. De esta forma, por cada nueva conexión aceptada el servidor genera un nuevo proceso, que es el que se encarga de manejar dicha comunicación con uno de los clientes en específico.

Paralelizar estas acciones tiene un problema, y es que hay ciertas acciones que debemos evitar realizar simultáneamente por múltiples procesos, por lo cual se debió agregar un Lock para el acceso al archivo de apuestas: si escribieran varios procesos al mismo tiempo, podríamos tener grandes problemas.

Aparte de esto, es fundamental sincronizar los procesos de alguna forma para poder enviar los resultados de la lotería. Para ello, se agregó una Barrier. De esta manera, cada proceso espera una vez que el mensaje **ReadyForLottery** es recibido, hasta que los 5 procesos correspondientes a cada agencia alcanzan dicha barrera, siendo ahí el momento en que se procede a enviar los resultados.
