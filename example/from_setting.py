from use_notify import useNotify

settings = {
    "wecom": {
        "token": "__TOKEN__",
    }
}

notify = useNotify.from_settings(settings)
notify.publish("content")
