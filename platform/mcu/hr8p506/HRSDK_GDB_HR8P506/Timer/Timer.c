/*
 * Copyright (C) 2015-2017 Alibaba Group Holding Limited
 */

#include <k_api.h>
#include <stdio.h>
#include <stdlib.h>
#include <aos/aos.h>
#include "lib_config.h"

/*--define ---------------------------------------------------*/
#define DEMO_TASK_STACKSIZE    512 //512*cpu_stack_t = 2048byte
#define TASK_PRIORITY     20

/*--typedef ---------------------------------------------------*/
extern void sdk_init(void);
void timer_printf(void *timer, void *arg);
void start_task(void *arg);

cpu_stack_t start_task_buf[DEMO_TASK_STACKSIZE];

ktask_t start_task_obj;
ktimer_t timer_obj;

/*--function -------------------------------------------------*/

/**
  * @brief main
  */
int main(void)
{
	/*Ӳ����ʼ��*/
	sdk_init();
	/*��ʼ��alios*/
	krhino_init();
	/*������ʼ����*/
	krhino_task_create(&start_task_obj,  //start_task���� ���ƿ�
						"start_task",    //����
						0,               //start_task�������
						TASK_PRIORITY,   //���ȼ�
						50,              //ʱ��Ƭ
						start_task_buf,  //�����ջ��ַ
						DEMO_TASK_STACKSIZE, //�����ջ��С
						start_task,      //start_task��ڵ�ַ
						1);              //autorun
	/*alios start*/
	krhino_start();    
	return 0;
}

/**
  * @brief start_task
  */
void start_task(void *arg)
{
	/*������ʱ��*/
	krhino_timer_create(&timer_obj,
						"timer",
						(timer_cb_t)timer_printf,
						RHINO_CONFIG_TICKS_PER_SECOND,     //1s
						RHINO_CONFIG_TICKS_PER_SECOND*2,   //2s
						0,
						0);
	/*��ʼ��ʱ*/
	krhino_timer_start(&timer_obj);
	/*ɾ����ʼ����*/
	krhino_task_del(&start_task_obj);
	
	while(1){
		printf("start_task del fail!\n\r");
	}
}

/**
  * @brief timer_printf
  */
static int count;
void timer_printf(void *timer, void *arg)
{
	if(timer == &timer_obj){
		count++;
		printf("timer run\n\r");
		printf("the value of count is:%d \n\r",count);
		krhino_timer_start(&timer_obj);
	}
}

