/**
 * @file:     AntennaPatternRecorder.ino
 *
 * @brief:    Software for antenna pattern recorder based on Arduino Uno
 *
 * @data:     January, 2020
 * @author:   Department of Electronics and Information Technology (LPNU) 
 */

#include <Stepper.h>
#include <TimerOne.h>

///========================================================================================
/// Defines
///========================================================================================
#define interruptPin_2    2
#define interruptPin_3    3
#define PIN_8             8
#define PIN_9             9
#define PIN_10            10
#define PIN_11            11
#define BAUDE_RATE        9600
#define STEPS             30 // change this to the number of steps on your motor
#define TIME              24383
#define LENGTH            5
#define STOP              0
#define RIGHT_ROTATION    1
#define LEFT_ROTATION     -1
#define STEP_MOTOR_SPEED  500
#define ADC               A0


///========================================================================================
/// Types
///========================================================================================
typedef enum motor_state_e {
    ACTIVE_L = -1, 
    ACTIVE_R = 1,
    INACTIVE = 0
};

typedef struct motor_state_s {
    motor_state_e last_state;
    motor_state_e current_state;
};


///========================================================================================
/// Global variables
///========================================================================================

Stepper stepper(STEPS, PIN_8, PIN_10, PIN_9, PIN_11); //Instance of the step \
//motor (number of steps and the pins it's attached to)
volatile motor_state_s motor_state;

///========================================================================================
/// Global functions
///========================================================================================

/**
 * @brief:  setup()
 * The function is intended for initializing of serial port, pin modes, timer, etc.
 *
 * @param:  void
 * @return: void
 */
void setup(void) {
  stepper.setSpeed(STEP_MOTOR_SPEED);   // Set the speed of the motor to 500 RPMs
  Serial.begin(BAUDE_RATE);
  Timer1.initialize(TIME);              // Interrupt will be arised every TIME ticks
  Timer1.attachInterrupt(data_receive); // data_receive function will be called during \
  //timers interrupts 
  motor_state.last_state = INACTIVE;
  motor_state.current_state = INACTIVE;
  pinMode(interruptPin_2, INPUT);
  pinMode(interruptPin_3, INPUT);
  attachInterrupt(digitalPinToInterrupt(interruptPin_2), stopMotor, RISING);
  attachInterrupt(digitalPinToInterrupt(interruptPin_3), stopMotor, RISING);
}

/**
 * @brief:  loop()
 * The function is intended for control of the Arduino board.
 *
 * @param:  void
 * @return: void
 */
void loop(void) {
    stateStepMotor();
}


///========================================================================================
/// Static functions
///========================================================================================

/**
 * @brief:  stateStepMotor()
 * The function defines the current state of a step motor
 * 
 * @param:  void
 * @return: void
 */
static void stateStepMotor(void) {
    static bool flag = false;
    switch(motor_state.current_state) {
        case ACTIVE_L:
        stepper.step(LEFT_ROTATION);
        if (flag == false) {
            motor_state.last_state = INACTIVE;
        }
        else {
            motor_state.last_state = ACTIVE_L;
        }
        flag = true;
        break;
        case ACTIVE_R:
        stepper.step(RIGHT_ROTATION);
        if (flag == false) {
            motor_state.last_state = INACTIVE;
        }
        else {
            motor_state.last_state = ACTIVE_R;
        }
        flag = true;
        break;
        
        case INACTIVE:
        if (motor_state.last_state == ACTIVE_L || motor_state.last_state == ACTIVE_R) {
            stepper.step(STOP);
        }
        motor_state.last_state = INACTIVE;
        motor_state.current_state = INACTIVE;
        break;
        
        default:
        if (motor_state.last_state == ACTIVE_L || motor_state.last_state == ACTIVE_R) {
            stepper.step(STOP);
        }
        motor_state.last_state = INACTIVE;
        motor_state.current_state = INACTIVE;
    }
}


///========================================================================================
/// Interrupt Service Routine
///========================================================================================

/**
 * @brief:  serialEvent()
 * The function is called when data brings to COM port.
 * It works like interrupt service routine
 *
 * @param:  void
 * @return: void
 */
void serialEvent(void){
    noInterrupts(); //Disable interrupts
    //Serial.println("serialEvent");
    char command;
    if (Serial.available() > 0) {  
        command = (char)Serial.read();
        switch(command) {
            case '0':
            motor_state.current_state = INACTIVE;
            break;
            case '1':
            if(digitalRead(interruptPin_2)!=1)
            motor_state.current_state = ACTIVE_L;
            break;
            case '2':
            if(digitalRead(interruptPin_3)!=1)
            motor_state.current_state = ACTIVE_R;
            break;
        }
    }
    else {
        motor_state.current_state = INACTIVE;
    }
    interrupts(); //Enable interrupts
}

/**
 * @brief:  data_receive()
 * It receives data from ADC and stores them into buffer. When data is stored 
 * the function transmits them to serial port. It is callback function.
 * It is called by timer like interrupt service routine.
 *
 * @param:  void
 * @return: void
 */
void data_receive(void) {
    int len = 0;
    int data = 0;
    char data_buff[LENGTH];
    
    noInterrupts(); //Disable interrupts
    data = analogRead(ADC);
    len += sprintf(data_buff, "%d", data);
    len += sprintf(data_buff + len, "\n");
    if (motor_state.last_state == ACTIVE_L || motor_state.last_state == ACTIVE_R){
    Serial.write(data_buff, len); 
    }
    interrupts(); //Enable interrupts
}

/**
 * @brief:  stopMotor()
 * The function is called when motor comes to one of two endings.
 * It stops motor.
 *
 * @param:  void
 * @return: void
 */

void stopMotor(void){
    noInterrupts(); //Disable interrupts
   // Serial.println("stopMotor");
    motor_state.current_state = INACTIVE;
    interrupts(); //Enable interrupts
}
