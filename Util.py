from paho.mqtt import client as mqtt_client

UUID = '90e22294-92c6-4998-976e-816f0585d3f6'
MAPS_API_KEY = 'AIzaSyCMwFpRy3GmlCsw6N4-4xgkJ22zVWyL3fI'
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_USERNAME = 'emqx'
MQTT_PASSWORD = 'public'

topicSoilCondition = 'sprinkler-topic-soil-condition'
topicSprinklerSchedule = 'sprinkler-next-schedule'

uuid_key = 'uuid'
grass_type_key = 'grass_type'
soil_condition_key = 'condition'
time_start_key = 'time_start'
time_stop_key = 'time_stop'

sample_schedule = '{"' + time_start_key + '": "2022-06-28T06:00:00-04:00", "' + time_stop_key + '": "2022-06-28T18:00:00-04:00"}'
sample_soil_conditions = '{"uuid": "' + UUID + '", "' + grass_type_key + '": "bermuda", "' + soil_condition_key + '": "very dry"}'


def initMqttClient(client_id, username, password, broker, port):

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

