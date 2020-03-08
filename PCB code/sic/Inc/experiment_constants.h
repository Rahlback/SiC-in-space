#define EXPERIMENTSIZE sizeof(experiments)
#define DACSTEPS 30
#define DACMAXVOLTAGE 3000 // millivolts
#define DACMINIMUMVOLTAGE 300 // millivolts
#define EXPERIMENTPOINTS (DACMAXVOLTAGE - DACMINIMUMVOLTAGE)/DACSTEPS
#define BUFFERLENGTH (EXPERIMENTPOINTS * 4 * 2)// Number of data points * 4 variables * 2 bytes per variable