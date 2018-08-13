# Research-Scripts
Research Scripts Session 

Understanding the script environment

The scripts that Cole and Glenda developed are written in Python and are run from the command line. This means that the scripts do not have a graphical interface and you will need to type the commands into a Windows Terminal.
In order to analyze the data being gathered in the field, you will need to install and use several pieces of software.

●	Wget – this is used to copy the data from the server to your local hard drive.
●	MongoDB – this is the database where the CLIx data is stored.
●	Python – this is the programming language used to develop the scripts.
●	Scripts – these are Python scripts that go through the data in the MongoDB and collect selected pieces of information.
●	Windows Terminal – sometime called the “command prompt”, the Windows Terminal is where you will type in the script commands.


Running the Scripts

The following scripts developed by Cole and Glenda, analyze the raw MongoDB database files to create CSV files that can be used for CLIx research analytics. There are three scripts.

1.	Student activity / timestamp CSV with interactives
2.	Assessment / click-log CSV
3.	OST / RKR click-log CSV

Results for each of these files is e-mailed to the provided email address, if the script is run within the MIT network (on the internet within MIT - the email address can be a non-MIT address and still run within the MIT network). The results are then deleted afterwards. If the script is not run on the MIT network, an error message will appear in the terminal and the output files will be available in the folder where the scripts are located. Look for a file with the extension ‘.csv’ 

All three of these scripts are run from the command-line inside of the Sandbox environment. This is very important. These scripts will only run from Sandbox environment you created (clix-data or whatever you named your sandbox) because the Sandbox environment you created has the libraries installed that the scripts will need. 
