#!/bin/bash

# 检查项目是否存在
if [ ! -d "/startalk/qtalk_search" ]; then
  if [ ! -d "/startalk" ]; then
    mkdir /startalk
  fi
  cd /startalk
  echo "################################"
  echo "正在下载项目至/startalk/qtalk_search..."
  echo "################################"
  git clone https://github.com/qunarcorp/qtalk_search.git
  echo "################################"
  echo "项目下载完成"
  echo "################################"
fi

# 检查项目版本
cd /startalk/qtalk_search
GIT_TAG=`git describe`
if [ $GIT_TAG = "v2.0" ];then
  echo "项目为2.0"
else
  echo "################################"
  echo "项目过期, 正在获取最新项目"
  echo "################################"
  cd /home/binz.zhang/qtalk_search && git fetch --tags && git checkout v2.0

  GIT_TAG=`git describe`
  if [ $GIT_TAG = "v2.0" ];then
    echo "获取最新代码成功"
  else
    echo "获取最新代码失败, 请解决git冲突并再次运行脚本"
    exit 0
  fi
fi

# 检查python版本
CHECK_PYTHON=`python3.7 -V`
if [ $? -eq 0 ];then
 echo "################################"
 echo "python3.7 已安装于系统"
 echo "################################"
else
 if [ ! -f "/startalk/qtalk_search/venv/bin/python3.7" ]; then
   echo "################################"
   echo "python3.7 未安装, 即将安装python3.7"
   echo "################################"
   echo "################################"
   echo "下载python3.7....7"
   echo "################################"
   cd /tmp
   if [ ! -f "/tmp/Python-3.7.4.tgz" ]; then
     wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
     echo "################################"
     echo "解压中...."
     echo "################################"
   fi
   tar zxvf Python-3.7.4.tgz
   echo "################################"
   echo "配置python环境...."
   echo "################################"
   sudo yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel
   readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
   sudo yum install -y libffi-devel zlib-devel
   cd ./Python-3.7.4
   read -p "是否将python3.7独立安装(默认为y)?" yn
   case $yn in
           [Yy]* ) ./configure --prefix /startalk/qtalk_search/venv/python/;echo "安装python3.7于/startalk/qtalk_search/venv/python/";make && make altinstall;/startalk/qtalk_search/venv/python/bin/python3.7 -V;;
           [Nn]* ) ./configure;make && make install;python3.7 -V;;
           * ) ./configure --prefix /startalk/qtalk_search/venv/python/;echo "安装python3.7于/startalk/qtalk_search/venv/python/";make && make altinstall;/startalk/qtalk_search/venv/python/bin/python3.7 -V;;
   esac
   if [ $? -eq 0 ];then
   echo "################################"
   echo "python3.7 已安装于系统"
   echo "################################"
   else
   echo "################################"
   echo "python3.7 安装失败 请检查报错"
   echo "################################"
   fi
   echo "################################"
 else
   echo "################################"
   echo "python3.7 已安装于系统"
   echo "################################"
 fi
fi

# 检查虚拟环境
if [ ! -d "/startalk/qtalk_search/venv" ] || [ ! -f "/startalk/qtalk_search/venv/bin/activate" ]; then
   cd /startalk/qtalk_search
   /startalk/qtalk_search/venv/python/bin/pip3.7 install virtualenv
   /startalk/qtalk_search/venv/python/bin/virtualenv  --system-site-packages -p /startalk/qtalk_search/venv/python/bin/python3.7 ./venv
   source /startalk/qtalk_search/venv/bin/activate
   pip3 install -r /startalk/qtalk_search/requirements.txt
fi

# 检查服务状态
source /startalk/qtalk_search/venv/bin/activate
pip3 install -r /startalk/qtalk_search/requirements.txt
supervisorctl -c /startalk/qtalk_search/conf/supervisor.conf restart service
SERVICE_RESULT=`supervisorctl -c conf/supervisor.conf status service|awk -F ' ' '{print $2}'`
if [ $SERVICE_RESULT = "RUNNING" ]; then
  ECHO_RESULT=`curl -X GET '0.0.0.0:8884/searchecho'`
  if [ ECHO_RESULT = "OK" ]; then
    echo "################################"
    echo "服务正常启动"
    echo "################################"
  else
    echo "################################"
    echo "服务echo失败,请观察 /startalk/qtalk_search/log/access.log 查看报错"
    echo "################################"
    cat /startalk/qtalk_search/log/access.log | head -n 20
  fi
else
  echo "################################"
  echo "服务启动失败,请观察 /startalk/qtalk_search/log/access.log 查看报错"
  echo "################################"
  cat /startalk/qtalk_search/log/access.log | head -n 20
fi
exit 0


