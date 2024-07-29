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

class TrialType {
public:
    bool airpuff; // 0 = CS-, 1 = CS+
    int signal;

    TrialType(bool airpuff, int signal) : airpuff(airpuff), signal(signal) {}
};

const TrialType NO_PUFF_NEGATIVE(false, 0);
const TrialType NO_PUFF_POSITIVE(false, 1);
const TrialType PUFF_NEGATIVE(true, 0);
const TrialType PUFF_POSITIVE(true, 1);

const TrialType* trialTypeObjects[] = {
    &NO_PUFF_NEGATIVE,  // ID 0
    &PUFF_POSITIVE,    // ID 1
    &PUFF_NEGATIVE,    // ID 2
    &NO_PUFF_POSITIVE  // ID 3
};

const char* trialTypeStrings[] = {
    "no_puff_CS-",  // ID 0
    "puff_CS+",      // ID 1
    "no_puff_CS+",  // ID 2
    "puff_CS-",     // ID 3
};

#endif
