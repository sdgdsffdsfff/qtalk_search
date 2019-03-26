#### ***搜索系统***
--------------------------------------------------------------------------------
#### **准备**：
#### *前提*:
        python3 (3.6)
        外网接口活着nginx等转发服务转发
        postgresql10，相关字段参考qtalk
        所需模块见requirements.txt<br />
#### *安装：*:
        1)配置configure.ini
        2)pip install -r requirements.txt （推荐新建虚拟环境）
        3)nohup python search.py &
--------------------------------------------------------------------------------
#### **请求**
#### *POST( application/json )*:
#### **传参**:
        {
            "key":"he",
            "qtalkId":"jingyu.he",
            "cKey":"xxxxxxmyckey",
            "groupid":"",
            "start":10,
            "length":0
        }
            *大小写重要, 都是string

            key     :  搜索关键字
            qtalkId :  搜索人qtalk id
            cKey    :  xxxxxxxx ckey规则
            groupid :  Q01-Q07 限定搜索内容
            start   :  偏移量
            length  :  长度
#### **返回**:
        application / json
        {
            "data": [
                {
                    "defaultportrait": "default_single_avatar_url.png",
                    "groupId": "Q01",
                    "groupLabel": "联系人列表",
                    "groupPriority": 0,
                    "hasMore": true,
                    "info": [
                        {
                            "content": "/dep1/dep2",
                            "icon": "aaa.jpg",
                            "label": "个人签名",
                            "name": "张三",
                            "qtalkname": "jingyu.he",
                            "uri": "jingyu.he@domain"
                        }
                    ],
                    "todoType": 0
                },
                {
                    "defaultportrait": "default_avatar_url.png",
                    "groupId": "Q02",
                    "groupLabel": "群组列表",
                    "groupPriority": 0,
                    "hasMore": false,
                    "info": [
                        {
                            "content": "群公告",
                            "icon": "bbb.png",
                            "label": "张三,李四",
                            "uri": "weffijw328f2@conference.domain"
                        }
                    ],
                    "todoType": 1
                },
                {
                    "defaultportrait": "default_avatar_url.png",
                    "groupId": "Q07",
                    "groupLabel": "共同群组",
                    "groupPriority": 0,
                    "hasMore": false,
                    "info": [
                        {
                            "content": "群公告",
                            "icon": "bbb.png",
                            "label": "张三,李四",
                            "uri": "weffijw328f2@conference.domain"
                        }
                    ],
                    "todoType": 1
                }
            ],
            "errcode": 0,
            "msg": ""
        }<br />
--------------------------------------------------------------------------------
#### **其它**:
#### *配置文件*:(search/conf/configure.ini)<br />
#### *日志配置文件*:(search/utils/logger_conf.py)<br />
#### *日志文件*:(search/log/yyyy_mm_dd_{module}.log)<br />
        为了避免日志过于冗长，日志会打印当前请求用户的userid+ckey并且打印上一个ip的最后一次请求
