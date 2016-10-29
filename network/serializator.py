def serialize(message, sender, time) -> str:
    return ";".join([str(message), str(sender), str(time)])


def deserialize(message: str):
    message, sender, time = (int(x) for x in message.split(";"))
    return message, sender, time
