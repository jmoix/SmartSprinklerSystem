import time
import json
import Util


class SprinklerController:

    def __init__(self):
        self.schedule_start = ''
        self.schedule_stop = ''
        self.mqttClient = Util.initMqttClient(
            'smart-sprinkler-controller-{}'.format(Util.UUID),
            Util.MQTT_USERNAME,
            Util.MQTT_PASSWORD,
            Util.MQTT_BROKER,
            Util.MQTT_PORT)

        self.getSoilConditions()
        self.mqttClient.loop_start()
        self.subscribe(Util.topicSprinklerSchedule)
        self.publish()

        print("Running")

    def subscribe(self, topic):

        def on_message(client, userdata, msg):

            msg_topic = msg.topic
            msg = msg.payload.decode()

            print(f"Received `{msg}` from `{msg_topic}` topic")
            self.setSchedule(json.loads(msg))

        self.mqttClient.on_message = on_message

        self.mqttClient.subscribe(topic)

    def publish(self):

        msg_count = 0
        while True:
            time.sleep(3)
            soil_conditions = self.getSoilConditions()
            result = self.mqttClient.publish(Util.topicSoilCondition, soil_conditions)

            status = result[0]
            if status == 0:
                print(f"Sent `{soil_conditions}` to topic `{Util.topicSoilCondition}`")
            else:
                print(f"Failed to send message to topic {Util.topicSoilCondition}")

            msg_count += 1

    def setSchedule(self, schedule):
        self.schedule_start = schedule[Util.time_start_key]
        self.schedule_stop = schedule[Util.time_stop_key]
        print("Sprinklers set to start at {} and end at {}.".format(self.schedule_start, self.schedule_stop))

    def getSoilConditions(self):

        # TODO
        # Write method for getting soil conditions from sensors

        return Util.sample_soil_conditions


if __name__ == '__main__':
    api = SprinklerController()






