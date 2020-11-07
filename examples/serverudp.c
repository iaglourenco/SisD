#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <netdb.h>
#include <stdlib.h>
#include <strings.h>

#define PORTA 1046


struct mensagem{
  int codigo;
  int resposta;
  long ip;
  int porta;
};

main()
{
  int sock, length;
  int contador=0;
  struct mensagem msg;
  struct sockaddr_in name;
  char buf[1024];

        /* Cria o socket de comunicacao */
  sock = socket(AF_INET, SOCK_DGRAM, 0);
  if(sock<0) {
  /*
  /- houve erro na abertura do socket
  */
    perror("opening datagram socket");
    exit(1);
  }
  /* Associa */
  name.sin_family = AF_INET;
  name.sin_addr.s_addr = INADDR_ANY;
  name.sin_port = htons(PORTA);

  if (bind(sock,(struct sockaddr *)&name, sizeof name ) < 0) {
    perror("binding datagram socket");
    exit(1);
  }
        /* Imprime o numero da porta */
  length = sizeof(name);
  if (getsockname(sock,(struct sockaddr *)&name, &length) < 0) {
    perror("getting socket name");
    exit(1);
  }
  printf("Socket port #%d\n",ntohs(name.sin_port));

  /* Le */
  //if (read(sock,buf,1024)<0)
  //
  //              perror("receiving datagram packet");

while (1){

recvfrom(sock, (char *)&msg, sizeof (msg), 0, (struct sockaddr *)&name, &length);
printf("SSSSSS  Recebi a mensagem de: %s porta: %d\n", inet_ntoa (name.sin_addr), name.sin_port);

contador++;
msg.resposta=contador;

sendto(sock, (char *)&msg, sizeof(msg), 0, (struct sockaddr *)&name, sizeof(name));

}

       // printf("  %s\n", buf);
        close(sock);
        exit(0);
}