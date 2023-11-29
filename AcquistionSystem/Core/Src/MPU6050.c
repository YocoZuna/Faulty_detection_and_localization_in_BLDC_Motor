/*
 * MPU6050.c
 *
 *  Created on: Jan 10, 2023
 *      Author: Dawid Zadlo
 */

#include <i2c.h>
#include <stdint.h>
#include "MPU6050.h"
#include <math.h>

float AccLookUpTable[25] = {[0]=16384.00,[8]=8192.00,[16]=4096.00,[24]=4096.00};
float GyroLookUpTable[25] = {[0]=131.00,[8]=65.50,[16]=32.80,[24]=16.40};
#define ROUND_UP_VALUE(x)  (roudn)

void MPU6050_Get_Temp(I2C_HandleTypeDef* I2C,int16_t * tempr);
void MPU6050_Init(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050);
void MPU6050_Get_Acc_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* accvalue);
void MPU6050_Get_Gyro_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* gyrovalue);
//void MPU6050_Get_Temp_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* tempr);
void MPU6050_Burst_Read_Acc_Gyro_Read(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,uint8_t* temp);

//void MPU6050_Burst_Read_Acc_Gyro_Convert(MPU6050_Config_TypeDef* mpu6050,uint8_t* temp,float* gyroXvalue,float* accXvalue,float* gyroYvalue,float* accYvalue,float* gyroZvalue,float* accZvalue,uint8_t countSamples);
void MPU6050_Burst_Read_Acc_Gyro_Convert(MPU6050_Config_TypeDef* mpu6050,uint8_t* temp,uint16_t* gyroXvalue,uint16_t* accXvalue,uint16_t* gyroYvalue,uint16_t* accYvalue,uint16_t* gyroZvalue,uint16_t* accZvalue,uint8_t countSamples);

static void MPU6050_Get_Gyro_RAW(I2C_HandleTypeDef* I2C,int16_t* gyroBuff);
static void MPU6050_Get_Acc_RAW(I2C_HandleTypeDef* I2C,int16_t* acc);


/** @ MPU6050_Init
  * @{
  */

/**
  * @brief  Initialization of MPU6050 register
  *
  *
  * @param
  * I2C_HandleTypeDef I2C -> handler to I2C hardware
  * MPU6050_Config_TypeDef mpu6050 - > handler to MPU6050 configuration structure
  * @retval None
  *
	  * typedef struct
	{
		uint8_t PIN_PULL;
		uint8_t PIN_SIGNAL;
		uint8_t ISR_CLEAR_ON;


	}MPU6050_Interrupt_Config_Typdef;


	typedef struct
	{
		uint8_t CLOCK;
		uint8_t FILTER;
		uint8_t TEMP_ON_OFF;
		MPU6050_Interrupt_Config_Typdef Interrupt_Config;

	}MPU6050_Config_TypeDef;
  *
  */
void MPU6050_Init(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050)
{
	uint8_t temp = 0;

	/* Check if MPU6050 is present under 0x68 slave address */
	HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_WHOAMI, 1, &temp, 1, 1000);
	if (temp == 0x68)
	{
		/* Restart of the device */
		uint8_t write_temp = 0xFF;
		HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_POWER_MANAGMENT_1, 1, &temp, 1, 1000);
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_POWER_MANAGMENT_1, 1,&write_temp,1, 1000);

		HAL_Delay(100);
		write_temp = 0x00;
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_POWER_MANAGMENT_1, 1,&write_temp,1, 1000);
		HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_POWER_MANAGMENT_1, 1, &temp, 1, 1000);

		HAL_Delay(100);
		/* Initialization of clock and tempr sensor */
		if (mpu6050->TEMP_ON_OFF == DISABLE)
		{
			temp  |= mpu6050->CLOCK + MPU6050_TEMP_DIS;
		}
		else
		{
			temp  = mpu6050->CLOCK;
		}
		/* Restart all sensors */
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_USER_CONTROL, 1,(uint8_t*) MPU6050_USER_RESET_ALL_SENS, 1, 1000);
		/* Set lowpass filter ad dpfl */
		temp = mpu6050->FILTER;
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_LOW_PASS_FILTER, 1,&temp, 1, 1000);

		/* Setting range for accelerometer and gyroscope */
		temp = mpu6050->ACC_RANGE;
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_ACC_CONFIG, 1,&temp, 1, 1000);
		temp = mpu6050->GYRO_RANGE;
		HAL_I2C_Mem_Write(I2C, MPU6050_DEV_ADDRESS, MPU6050_GYRO_CONFIG, 1,&temp, 1, 1000);

		HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_POWER_MANAGMENT_1, 1, &temp, 1, 1000);

		/*
		 * TODO Configuration of Interrupts
		 */
	}
	else
	{
		NVIC_SystemReset();
	}
}

/** @ MPU6050_Get_Gyro_RAW
  * @{
  */

/**
  * @brief  Getting raw data from gyroscope measurment data register
  *
  *
  * @param
  * I2C_HandleTypeDef I2C -> handler to I2C hardware
  * int16_t* gyroBuff -> pointer to gyroscope data array
  * where [0] = X axis, [1] = Y axis, [2] = Z axis
  * @retval None
  */
static void MPU6050_Get_Gyro_RAW(I2C_HandleTypeDef* I2C,int16_t* gyroBuff)
{

	uint8_t temp[6];
	HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_GYRO_MEAS, 1, temp, 6, 1000);

	gyroBuff[0] = (int16_t) (temp[0]<<8) | temp[1];
	gyroBuff[1] = (int16_t) (temp[2]<<8) | temp[3];
	gyroBuff[2] = (int16_t) (temp[4]<<8) | temp[5];

}

/** @ MPU6050_Get_Acc_RAW
  * @{
  */

/**
  * @brief  Getting raw data from gyroscope measurment data register
  *
  *
  * @param
  * I2C_HandleTypeDef I2C -> handler to I2C hardware
  * int16_t* accBuff -> pointer to acceleroscope data array
  * where [0] = X axis, [1] = Y axis, [2] = Z axis
  * @retval None
  */
static void MPU6050_Get_Acc_RAW(I2C_HandleTypeDef* I2C,int16_t* accBuff)
{

	uint8_t temp[6];
	HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_ACC_MEAS, 1, temp, 6, 1000);

	accBuff[0] = (int16_t) (temp[0]<<8) | temp[1];
	accBuff[1] = (int16_t) (temp[2]<<8) | temp[3];
	accBuff[2] = (int16_t) (temp[4]<<8) | temp[5];

}

/** @ MPU6050_Get_Temp
  * @{
  */

/**
  * @brief  Getting  data from temperature measurment data register
  *
  *
  * @param
  * I2C_HandleTypeDef I2C -> handler to I2C hardware
  * int16_t* tempr -> pointer to temperature variable
  * @retval None
  */
void MPU6050_Get_Temp(I2C_HandleTypeDef* I2C,int16_t * tempr)
{

	uint8_t temp[2];
	HAL_I2C_Mem_Read(I2C, MPU6050_DEV_ADDRESS, MPU6050_TEMP, 1, temp, 2, 1000);

	*tempr = (int16_t) (temp[1]<<8) | temp[0];

}

void MPU6050_Get_Acc_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* accvalue)
{
	int16_t accBuff[3];
	assert_param(sizeof(accvalue)==12);
	MPU6050_Get_Acc_RAW(I2C, accBuff);
	if (mpu6050->ACC_RANGE == MPU6050_ACC_AFS_2G)
		for ( int i=0;i<3;i++)
		{
			accvalue[i]  =  (float)accBuff[i]/16384.00;

		}
	if (mpu6050->ACC_RANGE == MPU6050_ACC_AFS_4G)
		for ( int i=0;i<3;i++)
		{
			accvalue[i]  =  (float)accBuff[i]/8192.00;
		}
	if (mpu6050->ACC_RANGE == MPU6050_ACC_AFS_8G)
		for ( int i=0;i<3;i++)
		{
			accvalue[i]  =  (float)accBuff[i]/4096.00;
		}
	if (mpu6050->ACC_RANGE == MPU6050_ACC_AFS_16G)
		for ( int i=0;i<3;i++)
		{
			accvalue[i]  =  (float)accBuff[i]/2048.00;
		}

}
void MPU6050_Get_Gyro_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* gyrovalue)
{
	int16_t gyroBuff[3];
	assert_param(sizeof(gyrovalue)==12);
	MPU6050_Get_Gyro_RAW(I2C, gyroBuff);
	if (mpu6050->GYRO_RANGE == MPU6050_GYRO_FS_250)
		for ( int i=0;i<3;i++)
		{
			gyrovalue[i]  = (float)gyroBuff[i]/131.00;
		}
	if (mpu6050->GYRO_RANGE == MPU6050_GYRO_FS_500)
		for ( int i=0;i<3;i++)
		{
			gyrovalue[i]  = (float)gyroBuff[i]/65.500;
		}
	if (mpu6050->GYRO_RANGE == MPU6050_GYRO_FS_1000)
		for ( int i=0;i<3;i++)
		{
			gyrovalue[i]  = (float)gyroBuff[i]/32.80;
		}
	if (mpu6050->GYRO_RANGE == MPU6050_GYRO_FS_2000)
		for ( int i=0;i<3;i++)
		{
			gyrovalue[i]  = (float)gyroBuff[i]/16.40;
		}

}

void MPU6050_Get_Roll_Pitch(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,int16_t* accvalue,int16_t* rollpitch)
{
	int16_t roll = atan(accvalue[1]/accvalue[2]);
	int16_t pitch = atan((-accvalue[0])/sqrt((accvalue[1]^2)+(accvalue[2]^2)));

	rollpitch[0] = roll;
	rollpitch[1] = pitch;

}

void MPU6050_Burst_Read_Acc_Gyro_Read(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,uint8_t* temp)
{




	HAL_I2C_Mem_Read_IT(I2C, MPU6050_DEV_ADDRESS, MPU6050_ACC_MEAS, 1, temp, 14);

}
void MPU6050_Burst_Read_Acc_Gyro_Convert(MPU6050_Config_TypeDef* mpu6050,uint8_t* temp,uint16_t* gyroXvalue,uint16_t* accXvalue,uint16_t* gyroYvalue,uint16_t* accYvalue,uint16_t* gyroZvalue,uint16_t* accZvalue,uint8_t countSamples)
{

	static uint8_t  countSampless=0;
	countSampless +=1;
	int16_t gyroBuff[3],accBuff[3];
	accBuff[0] = (int16_t) (temp[0]<<8) | temp[1];
	accBuff[1] = (int16_t) (temp[2]<<8) | temp[3];
	accBuff[2] = (int16_t) (temp[4]<<8) | temp[5];
	gyroBuff[0] = (int16_t) (temp[8]<<8) | temp[9];
	gyroBuff[1] = (int16_t) (temp[10]<<8) | temp[11];
	gyroBuff[2] = (int16_t) (temp[12]<<8) | temp[13];
//
	if (countSampless==MPU6050_BUFF_LEN+1)
	{
		countSampless =1;
	}
	accXvalue[countSampless-1] = accBuff[0];
	accYvalue[countSampless-1] = accBuff[1];
	accZvalue[countSampless-1] = accBuff[2];

	gyroXvalue[countSampless-1] = gyroBuff[0];
	gyroYvalue[countSampless-1] = gyroBuff[1];
	gyroZvalue[countSampless-1] = gyroBuff[2];


}

