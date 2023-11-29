/*
 * Mqtt_Connect.c
 *
 *  Created on: Jul 22, 2023
 *      Author: dawid
 *
 * source code https://www.nongnu.org/lwip/2_0_x/group__mqtt.html
 *
 */

#include <Mqtt_Connect.h>

ip4_addr_t mqtt_broker;


void MQTT_do_connect(mqtt_client_t *client)
{
  struct mqtt_connect_client_info_t ci;


  err_t err;
  /* IP brokera */
  IP4_ADDR(&mqtt_broker,192,168,1,6);

  memset(&ci, 0, sizeof(ci));

  /* Nazwa klienta */

  ci.client_id = "motor_failure_analzys";
  ci.keep_alive = 60;



  err = mqtt_client_connect(client, &mqtt_broker, MQTT_PORT, NULL, 0, &ci);


}


