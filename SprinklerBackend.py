import Util
import requests
import json


class SprinklerBackend:

    def __init__(self):

        self.mqttClient = Util.initMqttClient(
            'smart-sprinkler-backend',
            Util.MQTT_USERNAME,
            Util.MQTT_PASSWORD,
            Util.MQTT_BROKER,
            Util.MQTT_PORT)
        self.subscribe(Util.topicSoilCondition)
        self.mqttClient.loop_forever()

    def subscribe(self, topic):

        def on_message(client, userdata, msg):
            msg_topic = msg.topic
            msg = msg.payload.decode()
            print(f"Received `{msg}` from `{msg_topic}` topic")
            vals = json.loads(msg)
            print(vals[Util.uuid_key])
            schedule = self.getSprinklerSchedule(
                vals[Util.uuid_key],
                vals[Util.grass_type_key],
                vals[Util.soil_condition_key])
            self.mqttClient.publish(Util.topicSprinklerSchedule, schedule)

        self.mqttClient.on_message = on_message

        self.mqttClient.subscribe(topic)

    def getLoc(self, uuid):

        data = {
            'uuid': 'AIzaSyCMwFpRy3GmlCsw6N4-4xgkJ22zVWyL3fI',
            'city_state': {'city': 'Little Rock', 'state': 'Arkansas'},
            'lat_lng': {'lat': '34.7444618', 'lng': '-92.2880157'}}
        return data['lat_lng']

    def getGPS(self, city, state):

        query_string = 'https://maps.googleapis.com/maps/api/geocode/json?address=+{},+{}&key={}'.format(
            city.replace(' ', '+'),
            state.replace(' ', '+'),
            Util.MAPS_API_KEY
        )

        loc = requests.get(query_string).json()['results'][0]['geometry']['location']

        # TODO
        # Write update to user data to add latitude and longitude

        return loc

    def getWeatherMetaData(self, uuid):

        loc = self.getLoc(uuid)

        query_string = 'https://api.weather.gov/points/{},{}'.format(loc['lat'], loc['lng'])

        forecast_url = requests.get(query_string).json()['properties']['forecast']

        forecast = requests.get(forecast_url).json()['properties']['periods']

        return forecast

    def getSprinklerSchedule(self, uuid, grass_type, soil_condition):
        forecast = self.getWeatherMetaData(uuid)
        print(forecast)

        # TODO
        # Write query to get schedule

        return Util.sample_schedule


if __name__ == '__main__':
    api = SprinklerBackend()

