#!/bin/bash

# =====================================================================================
#
#       Filename:  testARMAX.sh
#        Created:  2/12/14 
#
#         Author:  Josue Pagan (), jpagan@ucm.es
#    Description:  Apply different TESTS
#
# =====================================================================================



## FUCNTIONS
function usage {
    echo -ne '\E[1;31m'"Usage: $0\n\033[0m" ;
    echo -ne "Usage: $0 [FILES_DIR]... [PARAMETERS]... \n\n" ;
    echo -ne "Parameters are:\n"
    echo -ne "-h, --help\t Print this help and finish\n"
    echo -ne "-i, --input\t (Required) File directory where data exist\n"
    echo -ne "-m, --mode\t (Required) create or validate. To create or validate an ARMAX model. Case validate, as parameter, introduce the model name without extension\n"
    echo -ne "-nx, --order\t When create a model select the order, the number of states desired. If none is selected then best is choosen as paremeter\n"
    echo -ne "-o, --output\t (Required) Output variable to be correlated against the selected variables\n"
    echo -ne "-p --pf\t (Required to validate models) Future prediction time\n"
    echo -ne "-t, --target\t (Required) Target. Problem to be solved by the parsing code.\n"
    echo -ne "-v, --variables\t (Required) Variables under test\n\t\t Format: var1 var2 .. varN\n"
echo -ne "All the possible options for MATLAB's ARMAX algorithm. Do it in pairs name-value (no key sensitive); e.g. -InitialState estimate -N4Weight CVA\n"
    echo -ne "Example of usage:\n"
    echo -ne "./runARMAX.sh -m validate model_2na3nb5nc0nk_TEMP_EDA -i ../raw_data/patients/patient_2/data/data_201406021630-201406030230 -v TEMP EDA -o output\n"
}

# CHECK PROGRAM MODE
function check_mode {
    if [ "$programMode" == "" ]; then 
	echo -en '\E[1;31m'"Error:\n\033[0m"
	echo -en "You must choose to create or to validate a model\nTry -m create or -m validate\n" 
	usage
	exit 1
    elif [ "$programMode" != "create" ] && [ "$programMode" != "validate" ]; then 
	echo -en '\E[1;31m'"Error:\n\033[0m"
	echo -en "Bad program model. You must choose to create or to validate a model\nTry -m create or -m validate\n" 
	usage
	exit 1
    fi
}

# CHECK PREDICTION TIME
function check_predictionTime {
    if [ "$programMode" == "validate"  ] && [ "$predictionTime" == "" ]; then 
	echo -en '\E[1;31m'"Error:\n\033[0m"
	echo -en "You must give a prediction Time\n" 
	usage
	exit 1
    fi
}

# CHECK TARGET
function check_target {
    case $target in
	migraine) 
	    generalInputDataPath=$MIGRAINE_RAW_FILES_PATH
	    CASES_PATH=$generalInputDataPath/patients ;;
	*) 
	    echo -en '\E[1;31m'"Error:\n\033[0m"
	    echo -ne "$target doesn't exist as target\n"
	    usage
	    exit 1
    esac;
echo -ne "Target: $target\n"
}

function check_input {
    if [ "xselectedInputInCommandLine" == "x" ]; then 	# Choose one case
	echo -en '\E[1;31m'"Error:\n\033[0m"
	echo -ne "Please write the input path to read variables\n"
	usage;
	exit 1
    else				# Yet selected cases
	inputDataPath=$selectedInputInCommandLine;
	if [ ! -d "$inputDataPath" ]; then
	    echo -en '\E[1;31m'"Error:\n\033[0m"
	    echo -en $inputDataPath "Isn't a valid path. Please check if data exist.\n";  
	    usage
	    exit;
	fi;
    fi;
}

function adapt_var_for_Matlab () {
    local variablesNoStoredYet=
    while [ "$1" != "" ]; do
	variablesNoStoredYet="$variablesNoStoredYet'$1' "
	shift
    done ;
    echo "$variablesNoStoredYet" # Return 
}

function check_vars {
    if [ "$variablesInput" == "" ]; then 	# Choose one case
	echo -en '\E[1;31m'"Error:\n\033[0m"
	echo -ne "Please write at least one variable\n"
	usage;
	exit 1
    else
	variablesInputNoOutput=$variablesInput
	# Check if some variable was already calculated and refuse it
	variables=$(adapt_var_for_Matlab $variablesInputNoOutput)
    fi;
    echo -ne "Variables: $variables\n"
}


function check_domainData {
    if [ "$programMode" == "create"  ]; then
	if [ "$domainData" == "" ]; then 
	    domainData=`echo "'Time';'seconds';60;0.2"`
	    echo -en '\E[38;5;202m'"Warning:\n\033[0m" # Orange text
	    echo -ne "Domain data options set to default:\n\tdomain: Time\n\tUnitTime: seconds\n\tStorageRate: 60 sec\n\tfs: 0.2 Hz\n"
	else
	    echo -ne "Domain data options: $domainData\n"
	fi;
    fi;

    newLine="domainData,$domainData,"
    echo "$newLine" > /tmp/auxNewLineFile.csv
    cat /tmp/optionsARMAX.csv /tmp/auxNewLineFile.csv > /tmp/optionsARMAXTemp.csv

    mv /tmp/optionsARMAXTemp.csv /tmp/optionsARMAX.csv  
}


## Create a temporal CSV file with options and its values
function check_orderARMAX {
    if [ "$nx" == "" ]; then 
	nx=`echo "best"`
	echo -en '\E[38;5;202m'"Warning:\n\033[0m" # Orange text
	echo -ne "ARMAX order set as: $nx\n"
    else
	echo -ne "ARMAX order: $nx\n"
    fi;

    newLine="orderARMAX,$nx,"
    echo "$newLine" > /tmp/auxNewLineFile.csv
    cat /tmp/optionsARMAX.csv /tmp/auxNewLineFile.csv > /tmp/optionsARMAXTemp.csv
    cp /tmp/optionsARMAXTemp.csv /tmp/optionsARMAX.csv
    check_domainData;
}


function create_options_file {
    rm /tmp/auxNewLineFile.csv /tmp/optionsARMAX.csv 
    touch /tmp/optionsARMAX.csv  /tmp/optionsARMAXTemp.csv
    if (( "num_rows" > "0" )); then
	for ((i=1;i<=num_rows;i++)) do
	newLine="${optionsNamesArray[$i]},${optionsValuesArray[$i]},"
	echo "$newLine" > /tmp/auxNewLineFile.csv
	cat /tmp/optionsARMAX.csv /tmp/auxNewLineFile.csv > /tmp/optionsARMAXTemp.csv
	cp /tmp/optionsARMAXTemp.csv /tmp/optionsARMAX.csv
	newLine=
	done
    else
    # Empty file
	echo "$newLine" > /tmp/optionsARMAX.csv
    fi

    check_orderARMAX;
}




### MAIN
# Init variables
algorithName="armax"
declare -A optionsNamesArray
declare -A optionsValuesArray

selectedInputInCommandLine=
variablesInput=
target=
programMode=
modelName=
predictionTime= 

newLine=
optionsCounter=1
auxvar=0


while [ "$1" != "" ]; do
    case $1 in
	-d | --domain)
	    shift
	    domainData=`echo "$1" | sed 's/,/;/g;s/\[//g;s/\]//g'`
	    shift
	    ;;	    
	-h | --help) 
	    usage
	    exit
	    ;;
	-i | --input)
	    shift
	    selectedInputInCommandLine=$1
	    shift
	    ;;
	-m | --mode)
	    shift
	    programMode=$1
	    case $programMode in
		validate)
		    shift
		    modelName=$1;
		    ;;
		*)
	    esac
	    shift
	    ;;
	-nx | --order)
	    shift
	    nx=$1
	    shift
	    ;;
	-o | --output)
	    shift
	    output=$1
	    shift ;;
	-p | --pf)
	    shift
	    predictionTime=$1
	    shift ;;
	-t | --target)
	    shift 
	    target=$1
	    shift ;;
	-v | --variables)
	    shift
	    while [ "$1" != "" ] && [ "$auxvar" -ne "1" ] ; do
		case $1 in
		    -* | --*) 
			auxvar=1 ; 
			break ;;
		    * )
			variablesInput="$variablesInput$1 "
			shift ;;
		esac;
	    done 
	    auxvar=0 ;;
	-InitialState | -Focus | -Display)
	    name=`echo "$1" | sed 's/-//g'`
	    optionsNamesArray[$optionsCounter]=$name
	    echo -ne "Option name: ${optionsNamesArray[$optionsCounter]}\t"
	    shift
	    case $name in
		N4Horizon)
		    optionsValuesArray[$optionsCounter]=`echo "$1" | sed 's/,/;/g;s/\[//g;s/\]//g'`
		    ;;
		*)
		    optionsValuesArray[$optionsCounter]=$1		 
	    esac
	    echo -ne "Option value: ${optionsValuesArray[$optionsCounter]}\n"	    
	    shift
	    ((optionsCounter+=1))
	    ;;
	* ) echo -en '\E[1;31m'"Error:\n\033[0m"
	    echo -en "Bad option '$1'. Please check options.\n" 
	    exit 1
    esac
done

# CALL FUNCTIONS
check_mode; # Check if create or validate model have been selected
check_predictionTime; # Check if selected or not
check_target; # CHECK TARGET
check_input; # Ask for cases to work with
check_vars; 
# Create CSV file
num_rows=$((optionsCounter-1))
create_options_file;

# Metric:
if [ "$metric" == "" ]; then
    metric=fit
    echo -en '\E[38;5;202m'"Warning:\n\033[0m" # Orange text
    echo -ne "Metric set as: $metric\n"
fi

# MATLAB
case $programMode in
    create )
	functionToCall=runAlgorithms"('$algorithName','$programMode','$metric','$inputDataPath/',{$variables},{'$output'})"
	;;
    validate )	
	functionToCall=runAlgorithms"('$algorithName','$programMode','$metric','$modelName',$predictionTime,'$inputDataPath/',{$variables},{'$output'})"
	;;
    *)	
esac;

echo -ne "\nLaunching Matlab with these parameters...:\n\n"
echo -ne "$functionToCall\n\n"

#matlab -nosplash -nodisplay -r "$functionToCall,quit()" > logMATLAB.txt
matlab -r "$functionToCall,quit()" > logMATLAB.txt

functionToCall=
echo -ne "\n...Matlab finished\n\n"
