import json, requests, colorsys

def create_lamps(ip_addr, api_key, num_lamps):
        """Creates num_lamps Lamp() instances which represent one lightbulb each"""
        return [Lamp(f"http://{ip_addr}/api/{api_key}/lights/{i}") for i in range(num_lamps)]

class APIError(Exception):
        pass

class Lamp(object):
        """A single hue bulb"""
        def __init__(self, control_url):
                self.control_url = control_url
                self.on = False
                self.info = {}

        def _send(self, state, transition=None):
                if transition != None:
                        state['transitiontime'] = transition
                r = requests.put(f"{self.control_url}/state", json.dumps(state))
                if not r.ok:
                        raise APIError(r.json())

        def save_state(self):
                self.info = requests.get(self.control_url).json()['state']
                self.on = self.info['on']

                prev_state = {}
                if self.on:
                        if self.info['colormode'] == 'ct':
                                prev_state['ct'] = self.info['ct']
                        elif self.info['colormode']== 'xy':
                                prev_state['xy'] = self.info['xy']
                        else:
                                prev_state['hue'] = self.info['hue']
                                prev_state['sat'] = self.info['bri']
                        prev_state['bri'] = self.info['bri']
                else:
                        prev_state['on'] = False
                return prev_state

        def restore_state(self, state, transition=None):
                self._send(state, transition)

        def brightness(self, new_brightness, transition=None):
                self.info['bri'] = new_brightness
                control_obj = {"bri" : new_brightness}
                self._send(control_obj, transition)

        def color(self, red, green, blue, brightness=None, transition=None ):
                (h,l,s) = colorsys.rgb_to_hls(red,green,blue)
                self.info['hue'] = min ( (int(h * 65535.0), 65535) )
                self.info['bri'] = min ( (int(l * 255.0), 255) )
                self.info['sat'] = min ( (int(s * 255.0), 255) )
                if brightness != None:
                        self.info['bri'] = brightness
                control_obj = {"hue" : self.info['hue'], "sat" : self.info['sat'], "bri" : self.info['bri'] }
                self._send(control_obj, transition)

        def xy(self, x, y, transition=None):
                control_obj = {"xy" : [x,y]}
                self.info['xy'] = (x,y)
                self._send(control_obj, transition)

        def turn_off(self,transition=None):
                control_obj = {"on" : False}
                self.on = False
                self._send(control_obj, transition)

        def turn_on(self):
                control_obj = {"on" : True}
                self.on = True
                self._send(control_obj)

if __name__ == "__main__":
        pass
