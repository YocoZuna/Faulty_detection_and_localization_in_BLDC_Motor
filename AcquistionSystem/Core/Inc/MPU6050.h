/*
 * MPU6050.h
 *
 *  Created on: Jan 9, 2023
 *      Author: Dawid Zadlo
 */


#ifndef INC_MPU6050_H
#define INC_MPU6050_H
#include <i2c_old.h>
#include <stdio.h>
/*
 *  Default connection of pin AD0 is pulling it to GND otherwise you have do define AD0_1 which means this pin is pulled HIGH
 */
#ifdef USE_DMA
#define POLLING 0
#else
#define POLLING 1
#endif


#ifdef AD0_1
#define MPU6050_DEV_ADDRESS (0x69<<1)
#else
#define MPU6050_DEV_ADDRESS (0x68<<1)
#endif

typedef struct
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
	uint8_t ACC_RANGE;
	uint8_t GYRO_RANGE;
	MPU6050_Interrupt_Config_Typdef Interrupt_Config;

}MPU6050_Config_TypeDef;




/*
 * 					GYRO CONFIG
 *
 * FS_SEL *	Full scale range * LSB sensitivity
 * 	  0	  *		+-250°/s	 *		131LSB/°/s
 * 	  1	  *		+-500°/s	 *		65.5/°/s
 *    2   *		+-1000°/s	 *		32.8/°/s
 *	  3   *     +-2000°/s    *		16.4/°/s
 */
#define MPU6050_GYRO_MEAS			(0x43U) //Size 6
#define MPU6050_GYRO_CONFIG			(0x1BU) //Size 1
#define MPU6050_GYRO_FS_250			 0// Reset value
#define MPU6050_GYRO_FS_500			(1<<3) //Bit
#define MPU6050_GYRO_FS_1000		(1<<4) //Bit
#define MPU6050_GYRO_FS_2000		(3<<3) //Bit
#define MPU6050_GYRO_Z_SELFTEST		(1<<5) //Bit
#define MPU6050_GYRO_Y_SELFTEST		(1<<6) //Bit
#define MPU6050_GYRO_X_SELFTEST		(1<<7) //Bit

/*
 * 					ACC CONFIG
 *
 * AFS_SEL *	Full scale range * LSB sensitivity
 * 	  0	   *		+-2g	     *		16384LSB /g
 * 	  1	   *		+-4g	     *		8192/g
 *    2    *		+-8g	     *		4096/g
 *	  3    *        +-16g        *		2048/g
 */

#define MPU6050_ACC_MEAS			(0x3BU) //Size 6
#define MPU6050_ACC_CONFIG			(0x1CU) //Size 1
#define MPU6050_ACC_AFS_2G			 0 // Reset value
#define MPU6050_ACC_AFS_4G			(1<<3) //Bit
#define MPU6050_ACC_AFS_8G			(1<<4) //Bit
#define MPU6050_ACC_AFS_16G			(3<<3) //Bit
#define MPU6050_ACC_Z_SELFTEST		(1<<5) //Bit
#define MPU6050_ACC_Y_SELFTEST		(1<<6) //Bit
#define MPU6050_ACC_X_SELFTEST		(1<<7) //Bit
/*
 * 			TEMP
 */
#define MPU6050_TEMP				(0x41U)	// Size 2



/*
 * 					DPLF CONFIG
 *
 * DPFL_VALUE *	             Acc 		   *              Gyro
 * 	  -	      *	Bandwidh (Hz) * Delay (ms) * Bandwidh (Hz)    * Delay (ms)   *    Fs (kHz) *
 * 	  0	      *		260   	  *		0	   * 	 256  	      *		0.98	 *		8	   *
 *    1       *		184    	  *		2	   * 	 188  	      *		1.9	     *		1	   *
 *	  2       *      94    	  *		3	   * 	  98          *		2.8	     *		1	   *
 *	  3       *      44    	  *		4.9	   * 	  42          *		4.8	     *		1	   *
 *	  4       *      21    	  *		8.5	   * 	  20          *		8.3	   	 *		1	   *
 *	  5       *      10    	  *	   13.8	   * 	  10          *		13.4	 *		1	   *
 *	  6       *       5   	  *		19	   * 	   5          *		18.6	 *		1	   *
 */
#define MPU6050_LOW_PASS_FILTER     (0x1AU) //Size 1
#define MPU6050_LOW_PASS_FILTER_0	 0// Reset value
#define MPU6050_LOW_PASS_FILTER_1	(1<<0) // Bit
#define MPU6050_LOW_PASS_FILTER_2	(1<<1) // Bit
#define MPU6050_LOW_PASS_FILTER_3	(1<<3) // Bit
#define MPU6050_LOW_PASS_FILTER_4	(2<<1) // Bit
#define MPU6050_LOW_PASS_FILTER_5	(1<<0) // Bit
#define MPU6050_LOW_PASS_FILTER_6	(3<<1) // Bit

#define MPU6050_SINGAL_RESET 			(0x68U) //Size 1
#define MPU6050_SINGAL_RESET_GYRO		(1<<2) // Bit 1
#define MPU6050_SINGAL_RESET_ACC		(1<<1) // Bit 1
#define MPU6050_SINGAL_RESET_TEMP		(1<<0) // Bit 1

#define MPU6050_USER_CONTROL 			(0x6AU) //Size 1
#define MPU6050_USER_RESET_ALL_SENS		(1<<0) // Bit 1

/*
 * 				POWER MANAGMENT CONFIG
  *

 * 	  0	   *		Internal 8MHz
 * 	  1	   *	PLL with X-gyro ref	 										*
 *    2    *	PLL with Y-gyro ref	 										*
 *	  3    *    PLL with Z-gyro ref	 										*
 * 	  4	   *	PLL with external 32.768kHz ref	 	   						*
 * 	  5	   *	PLL with external 19.2kHz ref	 							*
 *    6    *    Reserved													*
 *	  7    *    Stops the clock and keeps the timing generator in reset 	*
 */

#define MPU6050_POWER_MANAGMENT_1 	(0x6BU) //Size 1
#define MPU6050_CLOCK_SOURCE_0		 0// Reset value
#define MPU6050_CLOCK_SOURCE_1		(1<<0) //Bit
#define MPU6050_CLOCK_SOURCE_2		(1<<1) //Bit
#define MPU6050_CLOCK_SOURCE_3		(2<<0) //Bit
#define MPU6050_CLOCK_SOURCE_4		(1<<2) //Bit
#define MPU6050_CLOCK_SOURCE_5		(5<<0) //Bit
#define MPU6050_CLOCK_SOURCE_7		(7<<0) //Bit

#define MPU6050_DEVICE_RESET		(1<<7) //Bit
#define MPU6050_SLEEP				(1<<6) //Bit
#define MPU6050_TEMP_DIS			(1<<3) //Bit



#define MPU6050_WHOAMI 				(0x75U)	//Size 1
#define ENABLE 						1
#define DISABLE						0

/*
 *  TODO IMPLEMENT SELF-TEST
 */

/*
 * Interrupts
 */
#define MPU6050_INTERRUPT_CONFG						(0x37U)	//Size 1
#define MPU6050_INTERRUPT_PIN_PULL_UP				(1<<7) //Bit
#define MPU6050_INTERRUPT_PIN_PULL_DOWN				  0//Reset value
#define MPU6050_INTERRUPT_TI_MODE					  0//Reset value
#define MPU6050_INTERRUPT_PHTR						(1<<5) //Bit
#define MPU6050_INTERRUPT_CLEAR_ON_READ				(1<<4) //Bit
#define MPU6050_INTERRUPT_CLEAR_ON_READ_STATUS		  0//Reset value
#define MPU6050_INTERRUPT_CONFIG					(0x38U) //Size 1
#define MPU6050_INTERRUPT_STATUS					(0x3AU) //Size 1
#define MPU6050_DATA_SENSORS_READY					(1<<0)


void MPU6050_Get_Temp(I2C_HandleTypeDef* I2C,int16_t * tempr);
void MPU6050_Init(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050);
void MPU6050_Get_Acc_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* accvalue);
void MPU6050_Get_Gyro_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* gyrovalue);
void MPU6050_Get_Temp_Value(I2C_HandleTypeDef* I2C,float* tempr);

//oid MPU6050_Burst_Read_Acc_Gyro_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* gyrovalue,float* accvalue);void MPU6050_Burst_Read_Acc_Gyro_Value(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,float* gyroXvalue,float* accXvalue,float* gyroYvalue,float* accYvalue,float* gyroZvalue,float* accZvalue);

void MPU6050_Burst_Read_Acc_Gyro_Read(I2C_HandleTypeDef* I2C,MPU6050_Config_TypeDef* mpu6050,uint8_t* temp);

//void MPU6050_Burst_Read_Acc_Gyro_Convert(MPU6050_Config_TypeDef* mpu6050,uint8_t* temp,float* gyroXvalue,float* accXvalue,float* gyroYvalue,float* accYvalue,float* gyroZvalue,float* accZvalue,uint8_t countSamples);
void MPU6050_Burst_Read_Acc_Gyro_Convert(MPU6050_Config_TypeDef* mpu6050,uint8_t* temp,uint16_t* gyroXvalue,uint16_t* accXvalue,uint16_t* gyroYvalue,uint16_t* accYvalue,uint16_t* gyroZvalue,uint16_t* accZvalue,uint8_t countSamples);











#endif
