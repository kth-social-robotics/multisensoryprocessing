import pika
import json

FURHAT_PARTICIPANT = 'A'


def calculate_angle(furhat_position, participant_position):

    return {'furhat_gaze_angle': None}


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=32777))
    channel = connection.channel()
    channel.exchange_declare(exchange='processor', type='topic')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='pre-processor', queue=queue_name, routing_key='mocap.data.*')

    furhat_position = None

    def callback(ch, method, properties, body):
        participant = method.routing_key.rsplit('.', 1)[1]
        data = json.loads(body)

        if participant == FURHAT_PARTICIPANT:
            furhat_position = data
        elif furhat_position:
            angle = calculate_angle(furhat_position, data)

            ch.basic_publish(
                exchange='pre-processor',
                routing_key='furhat_gaze_angle.data.{}'.format(participant),
                body=json.dumps(angle)
            )

    channel.basic_consume(callback, queue=queue_name)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
