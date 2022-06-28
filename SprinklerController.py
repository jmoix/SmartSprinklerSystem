import time
import json
import Util


class SprinklerController:

    def __init__(self, init_mqtt=True):

        """
        Initialize Sprinkler Controller by
            1. Initializing MTQQClient.
            2. Starting a subscription for schedule updates from the backend.
            3. Getting Initial soil conditions from sensors.
            4. Beginning the loop to publish soil condition updates.

        MQTTClient shouldn't be initialized when running unit tests.
        """

        self.schedule_start = ''
        self.schedule_stop = ''

        if init_mqtt:
            self.mqttClient = Util.initMqttClient(
                'smart-sprinkler-controller-{}'.format(Util.UUID),
                Util.MQTT_USERNAME,
                Util.MQTT_PASSWORD,
                Util.MQTT_BROKER,
                Util.MQTT_PORT)

            self.mqttClient.loop_start()
            self.subscribe(Util.topicSprinklerSchedule)
            self.publish()

        print("Running")

    def subscribe(self, topic):

        """
        Subscribe to topic

        Parameters
        ----------
        topic : str
            String value of topic to subscribe to

        Returns
        -------
        Null
        """

        # Function describing what to do when a message is received
        def on_message(client, userdata, msg):

            msg_topic = msg.topic
            msg = msg.payload.decode()

            print(f"Received `{msg}` from `{msg_topic}` topic")

            # Unpack json to get new schedule times and assign to variables
            self.setSchedule(json.loads(msg))

        # Assigning on_message function to describe what to do when a message is received
        self.mqttClient.on_message = on_message

        # Subscribe to topic
        self.mqttClient.subscribe(topic)

    def publish(self):

        """
        Publishing loop to publish soil condition updates to the backend every 24 hours.
        """

        # Keep looping until process is killed
        while True:

            # Get current soil conditions from sensors
            soil_conditions = self.getSoilConditions()

            # Publish soil conditions to backend via MQTT
            result = self.mqttClient.publish(Util.topicSoilCondition, soil_conditions)

            # Status reflects success or error
            status = result[0]
            if status == 0:
                print(f"Sent `{soil_conditions}` to topic `{Util.topicSoilCondition}`")
            else:
                print(f"Failed to send message to topic {Util.topicSoilCondition}")

            # Time delay between updates currently set to 10 seconds for informational purposes.
            # time.sleep(86400)
            time.sleep(10)

    def setSchedule(self, schedule):

        """
        Function to set a new sprinkler schedule

        Parameters
        ----------
        schedule : dict of str
            Start and Stop times for running the sprinklers

        Returns
        -------
        Null
        """

        self.schedule_start = schedule[Util.time_start_key]
        self.schedule_stop = schedule[Util.time_stop_key]

        # Log update
        print("Sprinklers set to start at {} and end at {}.".format(self.schedule_start, self.schedule_stop))

    def getSoilConditions(self):

        """
        Function for getting the current soil condition from sensors.

        Returns
        -------
        schedule : list of str
            JSON formatted list of soil conditions
        """

        # TODO
        # Write method for getting soil conditions from sensors

        return Util.sample_soil_conditions


# Test output of SprinklerController.getSoilConditions()
def test_getSoilConditions():
    controller = SprinklerController(init_mqtt=False)
    conditions = controller.getSoilConditions()
    assert conditions == Util.sample_soil_conditions


# Test output of SprinklerController.setSchedule()
def test_setSchedule():
    controller = SprinklerController(init_mqtt=False)
    controller.setSchedule(json.loads(Util.sample_schedule))
    assert controller.schedule_start == '2022-06-28T06:00:00-04:00', "Wrong start time: {}"\
        .format(controller.schedule_start)
    assert controller.schedule_stop == '2022-06-28T18:00:00-04:00', "Wrong start time: {}"\
        .format(controller.schedule_stop)


if __name__ == '__main__':
    api = SprinklerController()






