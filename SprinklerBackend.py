import Util
import requests
import json


class SprinklerBackend:

    def __init__(self, init_mqtt=True):
        """
        Initialize Sprinkler Backend by Initializing MTQQClient
        and starting subscription.
        """

        if init_mqtt:
            # Connect to the MQTT service using the init method found in Util
            self.mqttClient = Util.initMqttClient(
                'smart-sprinkler-backend',
                Util.MQTT_USERNAME,
                Util.MQTT_PASSWORD,
                Util.MQTT_BROKER,
                Util.MQTT_PORT)

            # Subscribe to listen to messages related to soil condition
            self.subscribe(Util.topicSoilCondition)

            # Start continuous loop to listen for messages
            self.mqttClient.loop_forever()

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

        # Function to be executed when a subscribed message is received
        def on_message(client, userdata, msg):
            # Get topic and message for logging
            msg_topic = msg.topic
            msg = msg.payload.decode()
            print(f"Received `{msg}` from `{msg_topic}` topic")

            # Convert message from json to dict in order to extract values
            vals = json.loads(msg)

            # Get new sprinkler schedule based on message values
            schedule = self.getSprinklerSchedule(
                vals[Util.uuid_key],
                vals[Util.grass_type_key],
                vals[Util.soil_condition_key])

            # Push new schedule back to controller
            self.mqttClient.publish(Util.topicSprinklerSchedule, schedule)

        # Set function to use when message is received
        self.mqttClient.on_message = on_message

        # Subscribe to topic
        self.mqttClient.subscribe(topic)

    def getLoc(self, uuid):
        """
        Get location data for sprinkler system.

        Parameters
        ----------
        uuid : str
            Unique user identifier

        Returns
        -------
        loc : dict of str
            Latitude and Longitude of Sprinkler System
        """

        data = Util.sample_loc_data

        loc = data['lat_lng']

        return loc

    def getGPS(self, city, state):
        """
        Function to retrieve GPS coordinates of sprinkler system from Google Maps
        based on city and state.

        Parameters
        ----------
        city : str
            The city where the system resides
        state : str
            The state where the system resides

        Returns
        -------
        loc : dict of str
            The latitude and longitude of the sprinkler system
        """

        # http request string for getting location data
        query_string = 'https://maps.googleapis.com/maps/api/geocode/json?address=+{},+{}&key={}'.format(
            city.replace(' ', '+'),
            state.replace(' ', '+'),
            Util.MAPS_API_KEY
        )

        # request to get data, filtered to lat/lng
        loc = requests.get(query_string).json()['results'][0]['geometry']['location']

        # TODO
        # Write update to user data in RDS to add latitude and longitude

        return loc

    def getWeatherMetaData(self, uuid):
        """
        Function to retrieve weather meta-data from the weather.gov API

        Parameters
        ----------
        uuid : str
            Unique user identifier

        Returns
        -------
        forecast : dict of forecasts
            A listing of forecasts across several time periods
        """

        # Get GPS coordinates
        loc = self.getLoc(uuid)

        # Http request string
        query_string = 'https://api.weather.gov/points/{},{}'.format(loc['lat'], loc['lng'])

        # Get forecast url related to the target area
        forecast_url = requests.get(query_string).json()['properties']['forecast']

        # Query to forecast url for weather predictions
        forecast = requests.get(forecast_url).json()['properties']['periods']

        return forecast

    def getSprinklerSchedule(self, uuid, grass_type, soil_condition):
        """
        Function to create sprinkler schedule from soil, grass, weather, and geo-location

        Parameters
        ----------
        uuid : str
            Unique user identifier

        grass_type : str
            Current grass type being serviced

        soil_condition : str
            Current soil condition

        Returns
        -------
        schedule : json str
            String containing the start and stop time of the next watering
        """

        # Get weather data based on location
        forecast = self.getWeatherMetaData(uuid)
        print(forecast)

        # TODO
        # Write query to get schedule

        schedule = Util.sample_schedule

        return schedule


# Test output of SprinklerBackend.getSprinklerSchedule()
def test_getSprinklerSchedule():
    backend = SprinklerBackend(init_mqtt=False)
    schedule = backend.getSprinklerSchedule(Util.UUID, 'bermuda', 'very dry')
    assert schedule == Util.sample_schedule, "Wrong schedule"


# Test output of SprinklerBackend.getWeatherMetaData()
def test_get_weather_metadata():
    backend = SprinklerBackend(init_mqtt=False)
    forecast = backend.getWeatherMetaData(Util.UUID)
    assert len(forecast) > 5, "Something went wrong"


# Test output of SprinklerBackend.getGPS()
def test_get_gps():
    backend = SprinklerBackend(init_mqtt=False)
    gps = backend.getGPS('Little Rock', 'Arkansas')
    assert gps['lat'] == 34.7444618, "Wrong Latitude {}".format(gps['lat'])
    assert gps['lng'] == -92.2880157, "Wrong Longitude {}".format(gps['lng'])


# Test output of SprinklerBackend.getLoc()
def test_get_loc():
    backend = SprinklerBackend(init_mqtt=False)
    loc = backend.getLoc(Util.UUID)
    assert float(loc['lat']) == 34.7444618, "Wrong Latitude {}".format(loc['lat'])
    assert float(loc['lng']) == -92.2880157, "Wrong Longitude {}".format(loc['lng'])


if __name__ == '__main__':
    api = SprinklerBackend()
