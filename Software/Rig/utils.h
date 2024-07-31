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

void intArrayToChar(const int* arr, int size){
    char* result;
    result[0] = '\0';
    char temp[12];

    for (int i = 0; i < size; ++i) {
        // Convert each integer to a string and append it to the result
        sprintf(temp, "%d", arr[i]);
        strcat(result, temp);
    }
    return result;
}

class TrialType {
public:
    bool airpuff; // 0 = CS-, 1 = CS+
    int signal;
    int hasSignal;

    TrialType(bool airpuff, int signal, int hasSignal) : 
    airpuff(airpuff), signal(signal), hasSignal(hasSignal) {}
};

const TrialType NO_PUFF_NEGATIVE(false, 0, 1);
const TrialType NO_PUFF_POSITIVE(false, 1, 1);
const TrialType PUFF_NEGATIVE(true, 0, 1);
const TrialType PUFF_POSITIVE(true, 1, 1);
const TrialType NO_PUFF_NO_SIGNAL(true, 0, 0);

const TrialType* trialTypeObjects[] = {
    &NO_PUFF_NEGATIVE,  // ID 0
    &PUFF_POSITIVE,    // ID 1
    &NO_PUFF_POSITIVE,  // ID 2
    &PUFF_NEGATIVE,     // ID 3
    &NO_PUFF_NO_SIGNAL // ID 4
};

const char* trialTypeStringIdx[] = {
    "no_puff_CS-",  // ID 0
    "puff_CS+",      // ID 1
    "no_puff_CS+",  // ID 2
    "puff_CS-",     // ID 3
    "no_puff_no_signal" //ID 4
};



#endif
