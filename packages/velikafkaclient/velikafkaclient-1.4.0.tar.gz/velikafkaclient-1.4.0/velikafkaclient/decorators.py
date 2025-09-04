import functools

from velilogger import generate_tracing_id


def tracing(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        kafka_event = args[0]
        kafka_event_tracing_id = kafka_event.tracing_id
        generate_tracing_id(kafka_event_tracing_id)
        result = await func(*args, **kwargs)
        return result

    return wrapper


"""
    Used for class methods
"""


def ctracing(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        kafka_event = args[1]
        kafka_event_tracing_id = kafka_event.tracing_id
        generate_tracing_id(kafka_event_tracing_id)
        result = await func(*args, **kwargs)
        return result

    return wrapper
