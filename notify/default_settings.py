# 通知渠道配置项
CHANNELS = {
    'DING': {
        'ACCESS_TOKEN': "ee45bea8e9b5029a9c71*********6f0d98cff232a6b35e52df2",
        'AT_ALL': True
    },
    'WECHAT': {
        'ACCESS_TOKEN': "b2567442-*******-fa89e9f584da"
    },
    'EMAIL': {
        'HOST': 'smtp.163.com',
        'PORT': 465,
        'USER': '****@163.com',
        'PWD': '****',
        'RECEIVERS': ['10001@qq.com']
    }
}

# 触发器 设置哪些通知渠道允许发布消息
# 触发器的值为字典类型，键名为包路径，键值为优先级，值越小优先级越高
TRIGGERS = {
    'notify.channels.ding.Ding': 100,
}