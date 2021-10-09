#include <conio.h>
#include <iostream>

using namespace ::std;

void calculatePlots(float driveSize, int k32C, int k33C, int k34C, int k35C);
void calculateSize(float driveSize, int i, int j, int k, int l);
void printConfig(float driveSize);

// actual sizes are usually <1% lower than this but it's better to not overflow
float k32 = 102.837,
      k33 = 210.2277,
      k34 = 461.535,
      k35 = 949.356,
      maxPercentage = -1,
      maxSize = -1;

int plotCount[4] = {0, 0, 0, 0};
float maxPlots[4] = {0, 0, 0, 0};

int main()
{
    cout << "Chia plot planner, only plans for plots k32-35, assuming sizes\nk32: "
         << k32 << " GB\nk33: " << k33 << " GB\nk34: "
         << k34 << " GB\nk35: " << k35 << " GB\n"
         << endl;
    cout << "Enter your plot drive capacity in GB: ";

    float plotDriveSize;
    cin >> plotDriveSize;
    //plotDriveSize *= 1024;

    maxPlots[0] = plotDriveSize / k32;
    maxPlots[1] = plotDriveSize / k33;
    maxPlots[2] = plotDriveSize / k34;
    maxPlots[3] = plotDriveSize / k35;

    // only counts k32
    calculatePlots(plotDriveSize, 0, -1, -1, -1);
    printConfig(plotDriveSize);

    // only counts k32 and k33
    calculatePlots(plotDriveSize, 0, 0, -1, -1);
    printConfig(plotDriveSize);

    // only counts k32, k33 and k34
    calculatePlots(plotDriveSize, 0, 0, 0, -1);
    printConfig(plotDriveSize);

    // counts all k32, k33, k34 and k35 plots
    calculatePlots(plotDriveSize, 0, 0, 0, 0);
    printConfig(plotDriveSize);

    cout << "Press any key to exit..." << endl;
    _getch();
}

// set the counter values (eg. k33C) to -1 if you wish to exclude them from the calculation
void calculatePlots(float driveSize, int k32C, int k33C, int k34C, int k35C)
{
    // when maximum number of plots for the size is reached, return
    if (k32C >= maxPlots[0] || k33C >= maxPlots[1] || k34C >= maxPlots[2] || k35C >= maxPlots[3])
        return;

    // prevents k32C from incrementing when on bigger sizes
    if (k32C != -1 && k33C <= 0 && k34C <= 0 && k35C <= 0)
        calculatePlots(driveSize, k32C + 1, k33C, k34C, k35C);

    // prevents k33C from incrementing when on bigger sizes
    if (k33C != -1 && k34C <= 0 && k35C <= 0)
        calculatePlots(driveSize, k32C, k33C + 1, k34C, k35C);

    // prevents k34C from incrementing when on bigger sizes
    if (k34C != -1 && k35C <= 0)
        calculatePlots(driveSize, k32C, k33C, k34C + 1, k35C);

    if (k35C != -1)
        calculatePlots(driveSize, k32C, k33C, k34C, k35C + 1);

    // gets size of current plot configuration and save it into global variable if it's the current highest size
    calculateSize(driveSize, k32C, k33C, k34C, k35C);
    return;
}

void calculateSize(float driveSize, int i, int j, int k, int l)
{
    // rounds up to 0 in case of -1 values counting towards negative sizes
    i = max(i, 0);
    j = max(j, 0);
    k = max(k, 0);
    l = max(l, 0);

    float popSize = k32 * i + k33 * j + k34 * k + k35 * l;

    if (popSize > driveSize)
        return;

    if ((popSize / driveSize) > maxPercentage && popSize > 0)
    {
        maxPercentage = (popSize / driveSize);
        maxSize = popSize;
        plotCount[0] = i;
        plotCount[1] = j;
        plotCount[2] = k;
        plotCount[3] = l;
    }
}

// prints config w/ driveSize in GB
void printConfig(float driveSize)
{
    cout << "Plot configuration:\nk32: " << plotCount[0] << "\nk33: " << plotCount[1] << "\nk34: " << plotCount[2] << "\nk35: " << plotCount[3] << endl
         << "Using " << maxSize << " / " << driveSize << " GB (" << maxPercentage * 100 << "% filled)\n"
         << endl;
}