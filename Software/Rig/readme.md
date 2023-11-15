# Arduino software components for the trace-fear conditioning rig.

Upload `Rig.ino` to the Arduino. This is the main program that runs the rig.

TODO:
* Block water delivery during the ITI!!!
* need an approximation for the max possible session lenght in order to set up the imaging session
* need two versions of this script: one for the training wihc has only the CS and the US tones and no air puff, and one which has the CS, the US and the air puff.
* Can we add a `MAX_REWARD_NUMBER` which sets the maximum number of water deliveries in a row? This is to prevent the animal from drinking too much water. Let's say we set it to 5, then the animal can only get 5 rewards in a row, then a few sec later it can get reawards again. 
* Documetation -- Doxygen?
* need a way to daisy chain multiple arduinos together and run the same script on then simultanelously.