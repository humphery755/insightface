#!/bin/bash
#set -x
set -e
PRG="$0"
while [ -h "$PRG" ]; do
  ls=`ls -ld "$PRG"`
  link=`expr "$ls" : '.*-> \(.*\)$'`
  if expr "$link" : '/.*' > /dev/null; then
    PRG="$link"
  else
    PRG=`dirname "$PRG"`/"$link"
  fi
done
# Get standard environment variables
PRGDIR=`dirname "$PRG"`
# Only set NGX_HOME if not already set
[ -z "$PRG_HOME" ] && PRG_HOME=`cd "$PRGDIR/.." >/dev/null; pwd`
export PRG_HOME

export PYTHONPATH=$PYTHONPATH:$PRG_HOME/deploy

CMD="python $PRG_HOME/deploy/FeatureHttpServerProcess.py"
OPS="--filesvr=https://test.yimei.ai/fileSvr/get/ --model=./models/model-r100-ii/model,0 --port=8899 --process=2"
dev_test(){
$CMD $OPS
}

dev_start(){
nohup $CMD $OPS &
}

dev_stop(){
ps -ef|grep "$CMD"|grep -v grep|awk -F ' ' '{print $2}'|xargs kill -9
}

case $1 in
    "test")
            dev_test;
            ;;
    "start")
            dev_start;
            ;;
    "stop")
            dev_stop;
            ;;
    "restart")
            dev_stop;
            dev_start;
            ;;
    *) #default  ./php.sh src/index.php xxxxxxxxxscripts/config.conf start
            echo "Useage: bin/run.sh start|stop|restart|test"
esac
exit 0
