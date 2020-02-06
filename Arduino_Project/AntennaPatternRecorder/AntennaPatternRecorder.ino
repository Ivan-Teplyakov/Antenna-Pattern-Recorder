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
#define INTERRUPT_PIN_2     2
#define INTERRUPT_PIN_3     3
#define PIN_8               8
#define PIN_9               9
#define PIN_10              10
#define PIN_11              11
#define BAUDE_RATE          9600
#define STEPS               30 // change this to the number of steps on your motor
#define TIME                24383
#define LENGTH              5
#define STOP                0
#define RIGHT_ROTATION      1
#define LEFT_ROTATION       -1
#define STEP_MOTOR_SPEED    500
#define ADC                 A0
#define MAX_COMMAND_LENGTH  20
#define SPEED_NUMBER        6


///========================================================================================
/// Types
///========================================================================================
typedef enum motor_state_e {
    ACTIVE_L = 7, 
    ACTIVE_R = 9,
    INACTIVE = 8
};

typedef struct motor_state_s {
    motor_state_e last_state;
    motor_state_e current_state;
};

enum speed_e {
    ZERO_SPEED = 0,
    FIRST_SPEED = 1,
    SECOND_SPEED = 2,
    THIRD_SPEED = 3,
    FOURTH_SPEED = 4,
    FIFTH_SPEED = 5
};

///========================================================================================
/// Global variables
///========================================================================================

Stepper stepper(STEPS, PIN_8, PIN_10, PIN_9, PIN_11); //Instance of the step \
//motor (number of steps and the pins it's attached to)
volatile motor_state_s motor_state;
int speed_motor[SPEED_NUMBER] = {0, 100, 200, 300, 400, 500};
volatile int velocity = speed_motor[ZERO_SPEED];

///========================================================================================
/// Global functions
///========================================================================================


/**
 * @brief:  interruptPinSetup()
 * The function is intended for initializing of interrupts for digital pins.
 *
 * @param:  void
 * @return: int
 */
int interruptPinSetup(void) {
    pinMode(INTERRUPT_PIN_2, INPUT);
    pinMode(INTERRUPT_PIN_3, INPUT);
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN_2), stopMotor, RISING);
    attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN_3), stopMotor, RISING);
    return 0;
}

/**
 * @brief:  serialSetup()
 * The function is intended for initializing of serial port.
 *
 * @param:  void
 * @return: int
 */
int serialSetup(void) {
    Serial.begin(BAUDE_RATE);
    return 0;
}

/**
 * @brief:  timerSetup()
 * The function is intended for initializing of timer and timer interrupt.
 *
 * @param:  void
 * @return: int
 */
int timerSetup(void) {
    Timer1.initialize(TIME);              // Interrupt will be arised every TIME ticks
    Timer1.attachInterrupt(data_receive); // data_receive function will be called during \
                                          //timers interrupts 
    return 0;
}

/**
 * @brief:  motorSetup()
 * The function is intended for initializing of stepper motor.
 *
 * @param:  void
 * @return: int
 */
int motorSetup(void) {
    while(velocity == ZERO_SPEED) {
      char command;
      if (Serial.available() > 0) {  
        command = (char)Serial.read();
        switch(command) {

            case '0':
            velocity = speed_motor[ZERO_SPEED];
            stepper.setSpeed(velocity);
            
            case '1':
            velocity = speed_motor[FIRST_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '2':
            velocity = speed_motor[SECOND_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '3':
            velocity = speed_motor[THIRD_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '4':
            velocity = speed_motor[FOURTH_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '5':
            velocity = speed_motor[FIFTH_SPEED];
            stepper.setSpeed(velocity);
            break;
        }
        }
    }
    stepper.setSpeed(velocity);   // Set the speed of the motor to 500 RPMs
    motor_state.last_state = INACTIVE;
    motor_state.current_state = INACTIVE;
    return 0;
}

/**
 * @brief:  setup()
 * The function manages initializing of serial port, pin modes, timer, stepper motor etc.
 *
 * @param:  void
 * @return: void
 */
void setup(void) {
    int error = 1;
    while(error != 0) {
        error = serialSetup();
        error += timerSetup();
        error += interruptPinSetup();
        error += motorSetup();
    }       
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
    Serial.println("serialEvent");
    char command;
    if (Serial.available() > 0) {  
        command = (char)Serial.read();
        switch(command) {
            case '8':
            motor_state.current_state = INACTIVE;
            break;
            
            case '7':
            if(digitalRead(INTERRUPT_PIN_2) != 1)
            motor_state.current_state = ACTIVE_L;
            break;
            
            case '9':
            if(digitalRead(INTERRUPT_PIN_3) != 1)
            motor_state.current_state = ACTIVE_R;
            break;

            case '0':
            velocity = speed_motor[ZERO_SPEED];
            stepper.setSpeed(velocity);
            motor_state.current_state = INACTIVE;
            break;

            case '1':
            velocity = speed_motor[FIRST_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '2':
            velocity = speed_motor[SECOND_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '3':
            velocity = speed_motor[THIRD_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '4':
            velocity = speed_motor[FOURTH_SPEED];
            stepper.setSpeed(velocity);
            break;

            case '5':
            velocity = speed_motor[FIFTH_SPEED];
            stepper.setSpeed(velocity);
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
