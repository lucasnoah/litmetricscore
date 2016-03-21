This folder should contain at least:

ReadMe.txt - this file.
run.command - to run VARD 2 on Mac OSX (if you get a message like: “run.command” can’t be opened because it is from an unidentified developer, hold down "ctrl", click "run.command" again and select "Open".)
run.sh - to run VARD 2 on Linux ("chmod a+x run.sh" first)
run.bat - to run VARD 2 on Windows. (May appear just as "run")
gui.jar - graphical interface, do not run directly, use run.command/run.bat.
clui.jar - batch command line interface.
1clui.jar - single file command line interface.
vardstdin.jar - STDIN command line interface.
model.jar - the background system for VARD, cannot be run directly.
scowl directory - dictionaries used by VARD.

If all of the above are not present please download VARD 2 again. http://www.comp.lancs.ac.uk/~barona/vard2/.

To run VARD 2 use "run.bat" in Windows, "run.command" in MAC OSX and run.sh in Linux/Unix OS's. The java runtime environment will be needed to run the tool.
This is available for free at http://www.java.com/getjava/.

Alternatively, open a command prompt, locate the VARD directory and type the following command:

java -Xms256M -Xmx512M -jar gui.jar

This will open the graphical user interface. 256 and 512 indicate the memory allocated to the Java Virtual Machine. The default values should be
sufficient for most uses of VARD 2, however if your system only has 512MB of memory, these can be reduced to 128 and 256. It is not recommended lowering
these values any further than 128/256. The higher figure should be no more than half of your system memory, the lower value should usually be half of the 
higher value.

You can replace gui.jar with clui.jar, 1clui.jar or vardstdin.jar to run any of the of the command line interfaces to VARD. You will be given an error message detailing the parameters you need to add after "....jar".

Further instructions for using VARD 2 are available at http://www.comp.lancs.ac.uk/~barona/vard2/userguide.php.