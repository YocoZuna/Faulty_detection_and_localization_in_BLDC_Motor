/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include <Mqtt_Connect.h>
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "MPU6050.h"

#include <stdint.h>
extern I2C_HandleTypeDef i2c1;
extern MPU6050_Config_TypeDef mpu6050;
extern ADC_HandleTypeDef hadc1;
extern ADC_HandleTypeDef hadc2;
extern ADC_HandleTypeDef hadc3;
extern TIM_HandleTypeDef htim6;
extern TIM_HandleTypeDef htim14;

extern mqtt_client_t* clientt;



extern CurrentToSend Data_Struct;
extern uint16_t adc_IA[ADC_BUFF_LEN];
extern uint16_t adc_IB[ADC_BUFF_LEN];
extern uint16_t adc_IC[ADC_BUFF_LEN];
extern float gyroXBuff[MPU6050_BUFF_LEN],accXBuff[MPU6050_BUFF_LEN],gyroYBuff[MPU6050_BUFF_LEN],accYBuff[MPU6050_BUFF_LEN],gyroZBuff[MPU6050_BUFF_LEN],accZBuff[MPU6050_BUFF_LEN];
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */

/* USER CODE END Variables */
osThreadId defaultTaskHandle;
osThreadId IMUTaskHandle;
/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */
extern int __io_putchar(int ch)
{
	ITM_SendChar(ch);
	return ch;
}
/* USER CODE END FunctionPrototypes */

void StartDefaultTask(void const * argument);
void IMUTask(void const * argument);
extern void MX_LWIP_Init(void);
void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/* GetIdleTaskMemory prototype (linked to static allocation support) */
void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize );

/* USER CODE BEGIN GET_IDLE_TASK_MEMORY */
static StaticTask_t xIdleTaskTCBBuffer;
static StackType_t xIdleStack[configMINIMAL_STACK_SIZE];

void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize )
{
  *ppxIdleTaskTCBBuffer = &xIdleTaskTCBBuffer;
  *ppxIdleTaskStackBuffer = &xIdleStack[0];
  *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
  /* place for user code */
}
/* USER CODE END GET_IDLE_TASK_MEMORY */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* definition and creation of defaultTask */
  osThreadDef(defaultTask, StartDefaultTask, osPriorityNormal, 0, 1800);
  defaultTaskHandle = osThreadCreate(osThread(defaultTask), NULL);


  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

}

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void const * argument)
{
  /* init code for LWIP */

  MX_LWIP_Init();
  /* USER CODE BEGIN StartDefaultTask */
   clientt = mqtt_client_new();



  if(clientt!=NULL)
	 	 MQTT_do_connect(clientt);

  HAL_TIM_Base_Start_IT(&htim14);
  HAL_ADC_Start_DMA(&hadc1,(uint32_t*) Data_Struct.a, ADC_BUFF_LEN);
  HAL_ADC_Start_DMA(&hadc2, (uint32_t*)Data_Struct.b, ADC_BUFF_LEN);
  HAL_ADC_Start_DMA(&hadc3,(uint32_t*)Data_Struct.c, ADC_BUFF_LEN);

  HAL_TIM_Base_Start_IT(&htim6);
  HAL_GPIO_WritePin(LD1_GPIO_Port, LD1_Pin, SET);
 // /* Infinite loop */
  for(;;)
  {
	  osSignalWait(1, osWaitForever);
	  if(clientt!=NULL)
		 	 MQTT_do_connect(clientt);




	   err_t err;
	   u8_t qos = 0; /* 0 1 or 2, see MQTT specification */
	   u8_t retain = 0; /* No don't retain such crappy payload... */

	   err = mqtt_publish(clientt, "Motor",&Data_Struct,sizeof(CurrentToSend), qos, retain, NULL, NULL);


  }
  /* USER CODE END StartDefaultTask */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{

 if (hadc->Instance == ADC3)
 {


		 osSignalSet(defaultTaskHandle, 1);
	 	 }
}



/* USER CODE END Application */

