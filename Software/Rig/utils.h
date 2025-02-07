#ifndef UTILS
#define UTILS

#include <string.h>

int getArrayIndex(const char* trialType, const char** arr, int size) {
    for (int i = 0; i < size; ++i) {
        if (strcmp(trialType, arr[i]) == 0) {
            return i;
        }
    }
    return -1;  // Return -1 if string not found
}

void intArrayToChar(const int* arr, int size, char* result){
    result[0] = '\0';
    char temp[12];

    for (int i = 0; i < size; ++i) {
        // Convert each integer to a string and append it to the result
        sprintf(temp, "%d", arr[i]);
        strcat(result, temp);
    }
}

class TrialType {
public:
    bool water; // 0 = CS-, 1 = CS+
    int signal;
    int hasSignal;

    TrialType(bool water, int signal, int hasSignal) : 
    water(water), signal(signal), hasSignal(hasSignal) {}
};

const TrialType NO_WATER_NEGATIVE(false, 0, 1);
const TrialType NO_WATER_POSITIVE(false, 1, 1);
const TrialType WATER_NEGATIVE(true, 0, 1);
const TrialType WATER_POSITIVE(true, 1, 1);
const TrialType NO_WATER_NO_SIGNAL(true, 0, 0);

const TrialType* trialTypeObjects[] = {
    &NO_WATER_NEGATIVE,  // ID 0
    &WATER_POSITIVE,     // ID 1
    &NO_WATER_POSITIVE,  // ID 2
    &WATER_NEGATIVE,     // ID 3
    &NO_WATER_NO_SIGNAL  // ID 4
};

const char* trialTypesCharIdx[] = {
    "no_water_CS-",      // ID 0
    "water_CS+",         // ID 1
    "no_water_CS+",      // ID 2
    "water_CS-",         // ID 3
    "no_water_no_signal" // ID 4
};



#endif
