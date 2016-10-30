def serialize(message, sender, time, request_id) -> str:
    return ";".join([str(message), str(sender), str(time), str(request_id)])


def deserialize(message: str):
    message, sender, time, request_id = (int(x) for x in message.split(";"))
    return message, sender, time, request_id
