// include library's
//#include <arduino.h>
#include <Wire.h>                                      // I2C library

// define global variables
char buffer;                                           // buffer for char to choose the led
int percent;                                           // dim value of the led in percent
int previous_value;                                    // dim value of the led in percent from before
uint16_t fading_time;                              // fading time of the led
char text[20];                                         // text for serial console
char last_led;

// define global constants
#define REDPIN 3                                       // led pin's
#define GREENPIN 5
#define BLUEPIN 6
#define WHITEPIN 9
const char VALIDCOMMANDS[4] = {'r','g','b','w'};       // array of valid char to define led's // control: VALIDCOMMANDS[4] = {'1','2','3','p'}

// method to initialized I2C and UART bus and led pin's
void setup() 
{
  Wire.begin(8);                                       // join I2C bus with address 1
  Wire.onReceive(receiveEvent);                        // register I2C event method
  Serial.begin(9600);                                  // begin serial communication with baudrate of 9600
  pinMode(REDPIN, OUTPUT);                             // set led pins as output's
  pinMode(GREENPIN, OUTPUT);
  pinMode(BLUEPIN, OUTPUT);
  pinMode(WHITEPIN, OUTPUT);
  digitalWrite(REDPIN, LOW);                           // set led pins to initial value LOW
  digitalWrite(GREENPIN, LOW);
  digitalWrite(BLUEPIN, LOW);
  digitalWrite(WHITEPIN, LOW);
}

// main loop method
void loop() 
{
    // TEST LED FUNCTIONALITY
    //buffer = 'r';                                    // set buffer to 'r' (red)
    //percent = map(100, 0, 100, 0, 255);              // receive byte as an integer, map 50 procent to PWM range

    //if(last_led)
    //{
    //    last_led = NULL;
        set_led();

    //}
}

int set_led()
{
    if(buffer == VALIDCOMMANDS[0])  // controller 1 // red
    {
        if(percent > previous_value)
        {
            // what I'm trying to do is setup an LED to start at a low brightness,
            // fade to bright over a set time (fading_time+/-),
            for (int brightness = previous_value; brightness < percent; brightness++)
            {
                analogWrite(REDPIN, brightness);                  // set red led pin to value of percent
                delay(fading_time / (percent - previous_value));
            }
        }
        else if(percent <= previous_value)
        {
            Serial.println("percent <= previous_value");
            Serial.println(percent);
            // then fade to a low value, over the same time as above, so it just glows ,
            for (int brightness = previous_value; brightness >= percent; brightness--)
            {
                Serial.println(brightness);
                analogWrite(REDPIN, brightness);
                delay(fading_time / (previous_value - percent));
            }
        }

        if (Wire.available())                          // if I2C bus ist available
        {
            Wire.beginTransmission(1);                 // transmit to device 1
            Wire.write(buffer);                        // send led state
            Wire.write(map(percent, 0, 255, 0, 255));  // send led dim value
            Wire.endTransmission();                    // stop transmitting
        }
        
        buffer = NULL;
        if (percent >= 1)                              // if value of percent is >= 1 (led on)
        {
            sprintf(text,"RED ON AT %d!\n", 
                    map(percent, 0, 255, 0, 255));
            Serial.print(text);
        }
        else                                           // else led off
        {
            Serial.print("RED OFF!");
        }
    }
    else if(buffer == VALIDCOMMANDS[1])  // controller 2 // green blue
    {
        // int previous_value_green;
        // int previous_value_blue;
        // for delay calculation
        // previous_value = min(abs(percent - previous_value_green), abs(percent - previous_value_blue))
        // if(abs(percent - previous_value_green) <= abs(percent - previous_value_blue))
        // {
        //     previous_value = previous_value_green;      
        // }
        // else
        // {
        //     previous_value = previous_value_blue;
        // }
        if(percent > previous_value)
        {
            // what I'm trying to do is setup an LED to start at a low brightness,
            // fade to bright over a set time (fading_time+/-),
            for (int brightness = previous_value; brightness < percent; brightness++)
            {
                analogWrite(GREENPIN, brightness);
                analogWrite(BLUEPIN, brightness);                  // set red led pin to value of percent
                delay(fading_time / (percent - previous_value));
            }
        }
        else if(percent <= previous_value)
        {
            // then fade to a low value, over the same time as above, so it just glows ,
            for (int brightness = previous_value; brightness >= percent; brightness--)
            {
                analogWrite(GREENPIN, brightness);
                analogWrite(BLUEPIN, brightness);
                delay(fading_time / (previous_value - percent));
            }
        }

        if (Wire.available())                          // if I2C bus ist available
        {
            Wire.beginTransmission(1);                 // transmit to device 1
            Wire.write(buffer);                        // send led state
            Wire.write(map(percent, 0, 255, 0, 255));  // send led dim value
            Wire.endTransmission();                    // stop transmitting
        }
        
        buffer = NULL;
        if (percent >= 1)                              // if value of percent is >= 1 (led on)
        {
            sprintf(text,"GREEN-BLUE ON AT %d!\n", 
                    map(percent, 0, 255, 0, 255));
            Serial.print(text);
        }
        else                                           // else led off
        {
            Serial.print("GREEN-BLUE OFF!");
        }
    }
    else if(buffer == VALIDCOMMANDS[2])  // controller 3 & xbee other // red green blue white
    {
        // int previous_value_red;
        // int previous_value_green;
        // int previous_value_blue;
        // int previous_value_white;
        // for delay calculation
        // previous_value = min(abs(percent - previous_value_green), abs(percent - previous_value_blue))
        // if(abs(percent - previous_value_red) <= (abs(percent - previous_value_green) || (abs(percent - previous_value_blue) || (abs(percent - previous_value_white))
        // {
        //     previous_value = previous_value_red;      
        // }
        // if(abs(percent - previous_value_green) <= (abs(percent - previous_value_red) || (abs(percent - previous_value_blue) || (abs(percent - previous_value_white))
        // {
        //     previous_value = previous_value_green;      
        // }
        // if(abs(percent - previous_value_blue) <= (abs(percent - previous_value_red) || (abs(percent - previous_value_blue) || (abs(percent - previous_value_white))
        // {
        //     previous_value = previous_value_blue;      
        // }
        // else
        // {
        //     previous_value = previous_value_white;
        // }
        if(percent > previous_value)
        {
            // what I'm trying to do is setup an LED to start at a low brightness,
            // fade to bright over a set time (fading_time+/-),
            for (int brightness = previous_value; brightness < percent; brightness++)
            {
                analogWrite(REDPIN, brightness);
                analogWrite(GREENPIN, brightness);
                analogWrite(BLUEPIN, brightness);
                analogWrite(WHITEPIN, brightness);                  // set red led pin to value of percent
                delay(fading_time / (percent - previous_value));
            }
        }
        else if(percent <= previous_value)
        {
            // then fade to a low value, over the same time as above, so it just glows ,
            for (int brightness = previous_value; brightness >= percent; brightness--)
            {
                analogWrite(REDPIN, brightness);
                analogWrite(GREENPIN, brightness);
                analogWrite(BLUEPIN, brightness);
                analogWrite(WHITEPIN, brightness);
                delay(fading_time / (previous_value - percent));
            }
        }

        if (Wire.available())                          // if I2C bus ist available
        {
            Wire.beginTransmission(1);                 // transmit to device 1
            Wire.write(buffer);                        // send led state
            Wire.write(map(percent, 0, 255, 0, 255));  // send led dim value
            Wire.endTransmission();                    // stop transmitting
        }
        
        buffer = NULL;
        if (percent >= 1)                              // if value of percent is >= 1 (led on)
        {
            sprintf(text,"RED-GREEN-BLUE-WHITE ON AT %d!\n", 
                    map(percent, 0, 255, 0, 255));
            Serial.print(text);
        }
        else                                           // else led off
        {
            Serial.print("RED-GREEN-BLUE-WHITE OFF!");
        }
    }
    else if(buffer == VALIDCOMMANDS[3])  // xbee pc // blue
    {
        if(percent > previous_value)
        {
            // what I'm trying to do is setup an LED to start at a low brightness,
            // fade to bright over a set time (fading_time+/-),
            for (int brightness = previous_value; brightness < percent; brightness++)
            {
                analogWrite(BLUEPIN, brightness);                  // set red led pin to value of percent
                delay(fading_time / (percent - previous_value));
            }
        }
        else if(percent <= previous_value)
        {
            // then fade to a low value, over the same time as above, so it just glows ,
            for (int brightness = previous_value; brightness >= percent; brightness--)
            {
                analogWrite(BLUEPIN, brightness);
                delay(fading_time / (previous_value - percent));
            }
        }

        if (Wire.available())                          // if I2C bus ist available
        {
            Wire.beginTransmission(1);                 // transmit to device 1
            Wire.write(buffer);                        // send led state
            Wire.write(map(percent, 0, 255, 0, 255));  // send led dim value
            Wire.endTransmission();                    // stop transmitting
        }

        buffer = NULL;
        if (percent >= 1)                              // if value of percent is >= 1 (led on)
        {
            sprintf(text,"BLUE ON AT %d!\n", 
                    map(percent, 0, 255, 0, 255));
            Serial.print(text);
        }
        else                                           // else led off
        {
            Serial.print("BLUE OFF!");
        }
    }                 
}

int setzeZahlZusammen(unsigned int zahlHigh, unsigned int zahlLow) 
{
 
  int kombiniert;
  kombiniert = zahlHigh;
  kombiniert = kombiniert * 256;
  kombiniert |= zahlLow;
  return kombiniert;
}

// function that executes whenever data is received from master
// this function is registered as an event, see in setup()-method (L20)
void receiveEvent(int howMany)
{
  while(1 < Wire.available())                          // loop through all but the last byte from I2C bus
  {
    buffer = Wire.read();                              // receive byte as an character and save into buffer
    Serial.print("I2C RECEIVE LED: ");                 // print the character to serial console
    Serial.print(buffer);
    Serial.print("\n");
  
    percent = map(Wire.read(), 0, 255, 0, 255);          // receive byte as an integer, map to PWM range
    Serial.print("I2C RECEIVE LED VALUE: ");                 // print the int value to serial console
    Serial.print(percent);
    Serial.print("\n");

    uint8_t fading_time_msb= Wire.read();          // receive byte as an integer, map to PWM range
    Serial.print("I2C RECEIVE MSB FADING TIME: ");                 // print the int value to serial console
    Serial.print(fading_time_msb);
    Serial.print("\n");

    uint8_t fading_time_lsb = Wire.read();          // receive byte as an integer, map to PWM range
    Serial.print("I2C RECEIVE LSB FADING TIME: ");                 // print the int value to serial console
    Serial.print(fading_time_lsb);
    Serial.print("\n");
    
    fading_time = (uint16_t) (fading_time_msb << 8 | fading_time_lsb);
    fading_time = fading_time * 100;

    previous_value = map(Wire.read(), 0, 255, 0, 255);          // receive byte as an integer, map to PWM range
    Serial.print("I2C RECEIVE LED PREVIOUS VALUE: ");                 // print the int value to serial console
    Serial.print(previous_value);
    Serial.print("\n");
  }
  /*
    last_led = Wire.read();          // receive byte as an integer, map to PWM range
    Serial.print("I2C RECEIVE LAST LED: ");                 // print the int value to serial console
    Serial.print(last_led);
    Serial.print("\n");
  */
  
  // debug prints
  /*
  Serial.print("\n");
  Serial.print("LED VALUE:         ");
  Serial.print(buffer);
  Serial.print("\n");
  Serial.print("PERCENT VALUE:     ");
  Serial.print(percent);
  Serial.print("\n");
  Serial.print("MSB VALUE: ");
  Serial.print(fading_time_msb);
  Serial.print("\n");
  Serial.print("LSB TIME VALUE: ");
  Serial.print(fading_time_lsb);
  Serial.print("\n");
  Serial.print("FADING TIME VALUE: ");
  Serial.print(fading_time/100);
  Serial.print("\n");
  Serial.print("PREVIOUS VALUE:    ");
  Serial.print(previous_value);
  Serial.print("\n");
  */

}
