from use_notify import useNotify

settings = {
    "bark": {
        "token": "YOUR_BARK_TOKEN",
    }
}

notify = useNotify.from_settings(settings)
notify.publish("content")