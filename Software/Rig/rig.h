/* Define constants that might be setup or rig-specific here, including
 * pin numbers, baud rate, etc.
 *
 */

#ifndef RIG
#define RIG

// Arduino settings
const int BAUD_RATE = 9600;

// Trial pins
const int PIN_AIR_PUFF = 4;
const int PIN_WATER_SOLENOID = 5;
const int PIN_TONE_NEGATIVE = 9;
const int PIN_TONE_POSITIVE = 10;
// 11 for both rigs
// 6 on secondary rig at least for testing
const int PIN_BUTTON = 11;
const int PIN_LICK = 12;
const int PIN_CAMERA = 2;
const int PIN_MOUSE_LED = 3;
// Rig pins
const int PIN_SECONDARY_1 = 6;

#endif
