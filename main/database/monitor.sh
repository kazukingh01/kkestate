#!/bin/bash

HOMEDIR="/home/ubuntu"
LOGDIR="${HOMEDIR}/kkestate/main/log/"
MODULE="${HOMEDIR}/kkestate/main/database/suumo.py"
PYTHON="${HOMEDIR}/venv/bin/python"

NUM=$1
if [ -z "$NUM" ]; then
    echo "Please add number."
    exit 1
fi

DATE1=$(date +%Y%m)
DAY=$(date +%d)
DATE2=$2
if [ -z "$DATE2" ]; then
    if [ "$DAY" -lt 15 ]; then
    DATE2="${DATE1}01"
    else
    DATE2="${DATE1}15"
    fi
else
    if [[ ${DATE2} =~ ^[0-9]{8}$ ]]; then
        :
    else   
        echo "wrong date ${DATE2}"
        exit 1
    fi
fi
echo "set date ${DATE2}"

if [ $NUM -eq 1 ]; then
    LOGFILE="${LOGDIR}run_updateurls.`date "+%Y%m%d"`.log"
    COMMAND="${MODULE} --updateurls --update"
elif [ $NUM -eq 2 ]; then
    LOGFILE="${LOGDIR}run_main.`date "+%Y%m%d"`.log"
    COMMAND="${MODULE} --runmain --update"
elif [ $NUM -eq 3 ]; then
    LOGFILE="${LOGDIR}run_detail.`date "+%Y%m%d"`.log"
    COMMAND="${MODULE} --rundetail --datefrom ${DATE2} --skipsuccess --update"
else
    echo "The number must be in [1,2,3]"
    exit 1
fi

if ! ps aux | grep -v grep | grep python | grep "${COMMAND}" > /dev/null; then
    mkdir -p ${LOGDIR}
    echo "Process: ${COMMAND} not found! Restarting..."
    pkill python
    touch ${LOGFILE}
    nohup ${PYTHON} ${COMMAND} >> ${LOGFILE} 2>&1 &
else
    echo "Process: ${COMMAND} is running."
fi
