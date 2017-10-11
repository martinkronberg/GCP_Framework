import datetime
import time
import jwt
import paho.mqtt.client as mqtt

import mraa
from upm import pyupm_grove as grove
from upm import pyupm_temperature as upm
from upm import pyupm_mic as upmMicrophone

mraa.addSubplatform(mraa.GENERIC_FIRMATA, "/dev/ttyACM0");

temp = upm.Temperature(1+512)
light = grove.GroveLight(0+512)
sound = mraa.Aio(2+512)


cur_time = datetime.datetime.utcnow()

def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': 'intel-webinar'
  }

  with open('/home/nuc-user/intel_webinar_private.pem', 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, algorithm='RS256')



_CLIENT_ID = 'projects/intel-webinar/locations/us-central1/registries/intel-webinar-registry/devices/intel_gateway'
_MQTT_TOPIC = '/devices/intel_gateway/events'

client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever
client.username_pw_set(
    username='unused',
    password=create_jwt())

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(ca_certs='/home/nuc-user/roots.pem')
client.connect('mqtt.googleapis.com', 8883)
client.loop_start()

while 1:
  payload = '{{ "ts": {}, "temperature": {}, "sound": {}, "light": {} }}'.format(int(time.time()), temp.value(), sound.read(), light.value())
  client.publish(_MQTT_TOPIC, payload, qos=1)
  time.sleep(1)

client.loop_stop()
