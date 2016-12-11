# bot.py

# speechrecognition, pyaudio, brew install portaudio
import sys
sys.path.append("./")

import requests
import datetime
import dateutil.parser
import json
import traceback
from myemail import sendemail
from nlg import NLG
from speech import Speech
from knowledge import Knowledge

target_language = "hi"

my_name = "Ritesh"
notes_file_name = "/Users/rimittal/Desktop/class_details.txt"
launch_phrase = "ok penny"
use_launch_phrase = False
weather_api_token = "4540323a300d14157ef8062cac9d59f9"
wit_ai_token = "Bearer SWDNJL2D3NFN5YNMS2PQGFXPF72OQQBK"
debugger_enabled = True
camera = 0


class Bot(object):
    def __init__(self):
        self.nlg = NLG(user_name=my_name)
        self.speech = Speech(launch_phrase=launch_phrase, debugger_enabled=debugger_enabled)
        self.knowledge = Knowledge(weather_api_token)

    def start(self):
        """
        Main loop. Waits for the launch phrase, then decides an action.
        :return:
        """
        while True:
            #requests.get("http://localhost:8080/clear")
            if use_launch_phrase:
                recognizer, audio = self.speech.listen_for_audio()
                if self.speech.is_call_to_action(recognizer, audio):
                    self.__acknowledge_action()
                    self.decide_action()
            else:
                self.decide_action()

    def decide_action(self):
        """
        Recursively decides an action based on the intent.
        :return:
        """
        recognizer, audio = self.speech.listen_for_audio()

        # received audio data, now we'll recognize it using Google Speech Recognition
        speech = self.speech.google_speech_recognition(recognizer, audio)

        if speech is not None:
           try:
            requests.get("http://localhost:8080/clear")
            if 'monica' in speech or 'Monica' in speech or 'monika' in speech or "Monika" in speech:
######## EMAIL ###########
                if 'email' in speech or 'Email' in speech:
	            problems = sendemail(from_addr    = "ad9001055@gmail.com",
                                              to_addr_list = ['ritsgenx@gmail.com'],
                     	                      cc_addr_list = ['ritsnx@gmail.com'],
                                              subject      = 'Class notes',
                                              message      = 'hello',
                                              login        = 'ad9001055',
                                              password     = 'dubey!@#$') 
                    print problems
                    return
######################
                r = requests.get('https://api.wit.ai/message?v=20160918&q=%s' % speech,
                                 headers={"Authorization": wit_ai_token})
                print r.text
                json_resp = json.loads(r.text)
                entities = None
                intent = None
                if 'entities' in json_resp and 'Intent' in json_resp['entities']:
                    entities = json_resp['entities']
                    intent = json_resp['entities']['Intent'][0]["value"]

                print intent
                if intent == 'greeting':
                    self.__text_action(self.nlg.greet())
                elif intent == 'weather':
                    self.__weather_action(entities)
                elif intent == 'maps':
                    self.__maps_action(entities)
                elif intent == 'appreciation':
                    self.__appreciation_action()
                    return
                else: # No recognized intent
                    print speech
                    #self.__text_action("I am sorry, I dont know about that yet");
                #    elif speech == 'kannada':
                #       target_language = "kn"
                #    elif speech == 'urdu':
                #       target_language = "ur"
                #    elif speech == 'tamil':
                #       target_language = "ta"
                #    elif speech == 'bengali':
                #       target_language = "bn"
#TRANSALATE
            else:
                t_r = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20161210T135343Z.01cdf9d8fa100c94.c04eb36979d30f2e792953e790efc391db86ed80&text=%s&lang=en-%s&format=plain&'  % (speech, target_language) )
                print t_r.text
                tr_json_resp = json.loads(t_r.text)
                final_string = tr_json_resp["text"][0]
                self.__text_action(final_string)
                target = open(notes_file_name, 'ab+')
                target.write(speech)
                target.write("\n")
                target.close()
#TRANSALTE
           except Exception as e:
                print "Failed wit!"
                print(e)
                traceback.print_exc()
                #self.__text_action("I'm sorry, I couldn't understand what you meant by that")
                return
            #self.decide_action()
    
    def __appreciation_action(self):
        self.__text_action(self.nlg.appreciation())

    def __acknowledge_action(self):
        self.__text_action(self.nlg.acknowledge())

    def __text_action(self, text=None):
        if text is not None:
            requests.get("http://localhost:8080/statement?text=%s" % text)
            self.speech.synthesize_text(text)

    def __maps_action(self, nlu_entities=None):

        location = None
        map_type = None
        if nlu_entities is not None:
            if 'location' in nlu_entities:
                location = nlu_entities['location'][0]["value"]
            if "Map_Type" in nlu_entities:
                map_type = nlu_entities['Map_Type'][0]["value"]

        if location is not None:
            maps_url = self.knowledge.get_map_url(location, map_type)
            maps_action = "Sure. Here's a map of %s." % location
            body = {'url': maps_url}
            requests.post("http://localhost:8080/image", data=json.dumps(body))
            self.speech.synthesize_text(maps_action)
        else:
            self.__text_action("I'm sorry, I couldn't understand what location you wanted.")

if __name__ == "__main__":
    bot = Bot()
    bot.start()
