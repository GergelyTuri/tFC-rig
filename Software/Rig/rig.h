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
const int PIN_BUTTON = 11;
const int PIN_LICK = 12;

// Rig pins
const int PIN_SECONDARY_1 = 13;

#endif
