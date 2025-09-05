import collections as _collections
import threading as _threading
import traceback as _traceback
import inspect as _inspect
import copy as _copy
import json as _json
import time as _time
import sys as _sys
import io as _io
import re as _re

from deprecation import deprecated

from PIL import Image

from typing import Optional, Any, List, Union

import websocket as _websocket
import requests as _requests

import ssl
import certifi

import netsblox.common as _common
import netsblox.events as _events
import netsblox.rooms as _rooms

_websocket.enableTrace(False) # disable auto-outputting of socket events

_SNAP_IMAGE_REGEX = _re.compile(r'^<costume\b.*\bimage\s*=\s*"data:image/\w+;base64,(\S+)".*/>$')

class Client:
    '''
    Holds all the information and plumbing required to connect to netsblox, exchange messages, and call RPCs.
    '''

    def __init__(self, *, project_name: Optional[str] = None, project_id: Optional[str] = None, run_forever: bool = False):
        '''
        Opens a new client connection to NetsBlox, allowing you to access any of the NetsBlox services from python.

        `project_name` and `project_id` control the public name of your project from other programs.
        For instance, these are needed for other programs to send a message to your project.
        If you do not provide them, defaults will be generated (which will work),
        but the public id will change every time, which could be annoying if you need to frequently start/stop your project to make changes.

        `run_forever` prevents the python program from terminating even after the end of your script.
        This is useful if you have long-running programs that are based on message-passing rather than looping.
        Note: this does not stop the main thread of execution from terminating, which could be a problem in environments like Google Colab;
        instead, you can explicitly call `wait_till_disconnect()` at the end of your program.
        '''

        self._base_url = 'https://cloud.dev.netsblox.org'
        self._client_id = project_id or _common.generate_project_id()
        self._project_name = project_name or 'untitled'

        res = _json.loads(_requests.get(f'{self._base_url}/configuration').text)
        self._services_url = res['servicesHosts'][0]['url']

        self._room_handle = None

        # set these up before the websocket since it might send us messages
        self._message_cv = _threading.Condition(_threading.Lock())
        self._message_queue = _collections.deque()
        self._message_handlers = {}
        self._message_last = {} # maps msg type to {received_count, last_content, waiters (count)}
        self._message_stream_stopped = False

        # create a websocket and start it before anything non-essential (has some warmup communication)
        self._ws_lock = _threading.Lock()
        self._ws = _websocket.WebSocketApp(f'{self._base_url.replace("http", "ws")}/network/{self._client_id}/connect',
            on_open=self._ws_open, on_close=self._ws_close, on_error=self._ws_error, on_message=self._ws_message)
        def run_ws():
            opt = {
                'cert_reqs': ssl.CERT_OPTIONAL,
                'ca_certs': certifi.where(),
            }
            self._ws.run_forever(sslopt = opt)
        self._ws_thread = _threading.Thread(target = run_ws)
        self._ws_thread.setDaemon(not run_forever)
        self._ws_thread.start()

        # create a thread to manage the message queue
        self._message_thread = _threading.Thread(target = self._message_router)
        self._message_thread.setDaemon(True)
        self._message_thread.start()

        res = _json.loads(_requests.post(f'{self._base_url}/projects/',
            _common.small_json({ 'clientId': self._client_id, 'name': self._project_name }),
            headers = { 'Content-Type': 'application/json' }).text)
        self._project_id = res['id']
        role = next(iter(res['roles'].items()))
        self._role_id = role[0]
        self._role_name = role[1]['name']

        _requests.post(f'{self._base_url}/network/{self._client_id}/state',
            _common.small_json({ 'state': { 'external': { 'address': self._project_name, 'appId': 'py' } } }),
            headers = { 'Content-Type': 'application/json' })

        self.air_quality = AirQuality(self)
        '''
        The AirQuality Service provides access to real-time air quality data using the AirNowAPI.
        For more information, check out https://docs.airnowapi.org/.
        '''

        self.alexa = Alexa(self)
        '''
        The Alexa service provides capabilities for building your own Alexa skills!
        
        An Alexa skill consists of some general information (such as the name to use
        for invocation) as well as a list of supported intents. An intent is a command
        or question to which the skill can respond. Intents consist of a name, list of
        utterances, and any required slots. Utterances are examples of how the user might
        phrase questions or commands. Slots are used to define placeholders for concepts
        like names, cities, etc.
        
        When Alexa determines that a request was made to a given intent, the slots are
        resolved to their corresponding values and then passed to the "handler" for the
        intent.
        '''

        self.autograders = Autograders(self)
        '''
        The Autograders service enables users to create custom autograders for
        use within NetsBlox.
        
        For more information, check out https://editor.netsblox.org/docs/services/Autograders/index.html
        '''

        self.base_x = BaseX(self)
        '''
        The BaseX Service provides access to an existing BaseX instance.
        '''

        self.battleship = Battleship(self)
        '''
        The Battleship Service provides helpful utilities for building a distributed
        game of battleship.
        
        Overview
        --------
        
        Like regular Battleship, the Battleship service has two states: placing ships and shooting at ships.
        During placement, it expects each role to place each ship on his/her board and will not allow the game to proceed to the shooting phase until each role has placed all his/her ships.
        Placement, firing and starting blocks will return true if successful or an error message if it fails.
        
        Blocks
        ------
        
        - place <ship> at <row> <column> facing <direction> - Places a ship on your board with the front at the given row and column facing the given direction. Returns true if placed successfully (eg, on the board and not overlapping another ship). Also, placing a ship twice results in a move (not duplicates).
        - start game - Try to start the game. If both users have all their ships placed, it should return true and send start messages to all roles. Otherwise, it will return with a message saying that it is waiting on a specific role.
        - fire at <row> <column> - This block allows the user to try to fire at the given row and column. It returns true if it was a valid move; otherwise it will return an error message like it's not your turn!. On a successful move, the server will send either a hit or miss message to everyone in the room. Then it will send a your turn message to the player to play next.
        - active ships for <role> - This block returns a list of all ships that are still afloat for the given role. If no role is specified, it defaults to the sender's role.
        - all ships - Returns a list of all ship names. Useful in programmatically placing ships.
        - ship length <ship> - Returns the length of the given ship.
        - restart game - Restarts the given game (all boards, etc)
        
        Message Types
        -------------
        
        - start - Received when start game finishes successfully for any role. After game has officially started, users can no longer move ships.
        - your turn - Received when the given role's turn starts.
        - hit - role is the owner of the ship that has been hit. ship is the name of the ship that has been hit, and row and column provide the location on the board where it was hit. sunk provides a true/false value for if the ship was sunk.
        - miss - role is the owner of the board receiving the shot and row and column correspond to the board location or the shot.
        '''

        self.bing_traffic = BingTraffic(self)
        '''
        The Traffic Service provides access to real-time traffic data using the Bing Traffic API.
        For more information, check out https://msdn.microsoft.com/en-us/library/hh441725.aspx
        '''

        self.covid19 = COVID19(self)
        '''
        The COVID-19 Service provides access to the 2019-nCoV dataset compiled by Johns Hopkins University.
        This dataset includes deaths, confirmed cases, and recoveries related to the COVID-19 pandemic.
        Vaccination data is provided by Our World in Data.
        
        For more information, check out https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases
        and https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations.
        '''

        self.chart = Chart(self)
        '''
        A charting service powered by gnuplot.
        '''

        self.cloud_variables = CloudVariables(self)
        '''
        The CloudVariables Service provides support for storing variables on the cloud.
        Variables can be optionally password-protected or stored only for the current user.
        
        Cloud variables that are inactive (no reads or writes) for 30 days are subject to deletion.
        '''

        self.common_words = CommonWords(self)
        '''
        The CommonWords service provides access to common words in a variety of languages.
        Words were discovered by retrieving the top 5000 words in each language
        '''

        self.connect_n = ConnectN(self)
        '''
        The ConnectN Service provides helpers for building games like Connect-4 and Tic-Tac-Toe.
        '''

        self.connect_nai = ConnectNAI(self)
        '''
        The ConnectN AI service allows you to create games like Connect-4 or Tic-Tac-Toe and play against an AI that improves over time.
        '''

        self.core_nlp = CoreNLP(self)
        '''
        Use CoreNLP to annotate text.
        For more information, check out https://stanfordnlp.github.io/CoreNLP/.
        '''

        self.daily_word_guess = DailyWordGuess(self)
        '''
        A Wordle-like word guessing game with a single daily word for all users.
        '''

        self.dev = Dev(self)
        

        self.earth_orbit = EarthOrbit(self)
        '''
        Access to Astronomical Solutions for Earth Paleoclimates. There are three researches (in 1993, 2004, and 2010) about
        earth orbital parameters' data. This service only uses the 2004 data.
        
        For more information, check out
        http://vo.imcce.fr/insola/earth/online/earth/earth.html.
        
        Original datasets are available at:
        
        - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.100.ASC
        - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.250.ASC
        - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.ASC
        - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLP.LA2004.BTL.ASC
        - http://vo.imcce.fr/webservices/miriade/proxy.php?file=http://145.238.217.35//tmp/insola/insolaouto7Yk3u&format=text
        - http://vo.imcce.fr/webservices/miriade/proxy.php?file=http://145.238.217.38//tmp/insola/insolaouteXT96X&format=text
        '''

        self.earthquakes = Earthquakes(self)
        '''
        The Earthquakes Service provides access to historical earthquake data.
        For more information, check out https://earthquake.usgs.gov/.
        '''

        self.eclipse2017 = Eclipse2017(self)
        '''
        The Eclipse2017 Service provides access to US weather data along the path of the Great American Eclipse.
        For more information about the eclipse, check out https://www.greatamericaneclipse.com/.
        '''

        self.execute = Execute(self)
        '''
        The Execute Service provides capabilities for executing blocks on the NetsBlox
        server. This is particularly useful for batching RPC requests.
        '''

        self.genius = Genius(self)
        '''
        The Genius service provides access to the Genius API, the world's
        biggest collection of song lyrics and musical knowledge.
        
        For more information, check out https://genius.com.
        '''

        self.geolocation = Geolocation(self)
        '''
        The Geolocation Service provides access to the Google Places API and geocoding capabilities.
        For more information, check out https://developers.google.com/places/
        
        Terms of service: https://developers.google.com/maps/terms
        '''

        self.global_biodiversity = GlobalBiodiversity(self)
        '''
        The GlobalBiodiversity service provides information on millions of species from around the globe.
        '''

        self.google_maps = GoogleMaps(self)
        '''
        The GoogleMaps Service provides access to the Google Maps API along with helper functions for interacting with the maps (such as converting coordinates).
        For more information, check out https://developers.google.com/maps/documentation/static-maps/intro
        
        Terms of use: https://developers.google.com/maps/terms
        '''

        self.google_street_view = GoogleStreetView(self)
        '''
        The GoogleStreetView Service provides access to the Google Street View Image API
        For more information, check out https://developers.google.com/maps/documentation/streetview/intro
        
        Terms of use: https://developers.google.com/maps/terms
        '''

        self.hangman = Hangman(self)
        '''
        The Hangman Service provides helpers for mediating a distributed game of hangman.
        '''

        self.historical_temperature = HistoricalTemperature(self)
        '''
        Access to Berkeley Earth data.
        See http://berkeleyearth.org/data/ for additional details.
        
        These RPCs take a region argument, which can either be a country
        or one of the following special values:
        
        - all land - get data for all landmasses around the world
        - global - get data for the entire Earth (including oceans)
        - northern hemisphere - only northern landmasses
        - southern hemisphere - only southern landmasses
        '''

        self.human_mortality_database = HumanMortalityDatabase(self)
        '''
        This service accesses data from the human mortality database which tabulates
        death rates broken down by age group and gender for various countries.
        
        For more information, see https://www.mortality.org/.
        
        Note: for countries that don't report separate male and female death counts,
        the gender breakdowns are just the total multiplied by a rough estimate
        of the percent of people in that country who are male/female.
        '''

        self.hurricane_data = HurricaneData(self)
        '''
        The HurricaneData service provides access to the revised Atlantic hurricane
        database (HURDAT2) from the National Hurricane Center (NHC).
        
        For more information, check out https://www.aoml.noaa.gov/hrd/data_sub/re_anal.html
        '''

        self.ice_core_data = IceCoreData(self)
        '''
        Access to NOAA Paleoclimatology ice core data.
        
        For more information, check out
        https://www.ncdc.noaa.gov/data-access/paleoclimatology-data/datasets/ice-core.
        
        Original datasets are available at:
        
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2composite.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2law.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2wais.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/co2nat.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/deutnat.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/epica_domec/edc3deuttemp2007.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/greenland/summit/grip/isotopes/gripd18o.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/gt4nat.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/law/law2012d18o.txt
        - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/wdc05a2013d18o.txt
        '''

        self.io_t_scape = IoTScape(self)
        '''
        The IoTScape Service enables remote devices to provide custom services. Custom
        Services can be found under the "Community/Devices" section using the call <RPC>
        block.
        '''

        self.key_value_store = KeyValueStore(self)
        '''
        The KeyValueStore Service provides basic storage functionality using a hierarchical
        key-value storage (similar to CloudVariables).
        '''

        self.mauna_loa_co2_data = MaunaLoaCO2Data(self)
        '''
        Access to NOAA Earth System Research Laboratory data collected from Mauna Loa, Hawaii.
        
        See https://www.esrl.noaa.gov/gmd/ccgg/trends/ for additional details.
        '''

        self.met_museum = MetMuseum(self)
        '''
        Access the Metropolitan Museum of Art's collection.
        For explanation on the different attributes for each object,
        visit https://metmuseum.github.io.
        '''

        self.midi_data = MidiData(self)
        '''
        This service allows users to access midi files of different songs.
        '''

        self.movebank = Movebank(self)
        '''
        Access to Movebank, a free, online database of animal tracking data hosted by the Max Planck Institute of Animal Behavior.
        '''

        self.movie_db = MovieDB(self)
        '''
        The MovieDB Service provides access to movie data using TMDB (The MovieDB API).
        For more information, check out https://www.themoviedb.org/
        
        Terms of use: https://www.themoviedb.org/documentation/api/terms-of-use
        '''

        self.nasa = NASA(self)
        '''
        The NASA Service provides access to planetary pictures and mars weather data.
        For more information, check out https://api.nasa.gov/.
        '''

        self.n_player = NPlayer(self)
        '''
        The NPlayer Service provides helpers RPCs for ensuring round-robin turn taking
        among the roles in the project's room.
        
        Each role will receive a "start game" message at the start and then "start turn"
        message when it is the given role's turn to act.
        '''

        self.new_york_times = NewYorkTimes(self)
        '''
        The NewYorkTimes service provides access to the New York Times API including access
        to Moview Reviews, Top Stories, and their Semantic API.
        '''

        self.ocean_data = OceanData(self)
        '''
        The OceanData service provides access to scientific ocean data including
        temperature and sea level.
        
        For more information, check out:
        
        - http://www.columbia.edu/~mhs119/Sensitivity+SL+CO2/
        - https://www.paleo.bristol.ac.uk/~ggdjl/warm_climates/hansen_etal.pdf.
        '''

        self.paleocean_oxygen_isotopes = PaleoceanOxygenIsotopes(self)
        '''
        Access to NOAA Global Pliocene-Pleistocene Benthic d18O Stack.
        
        For more information, check out
        https://www.ncdc.noaa.gov/paleo-search/study/5847
        
        Original datasets are available at:
        https://www1.ncdc.noaa.gov/pub/data/paleo/contributions_by_author/lisiecki2005/lisiecki2005.txt.
        '''

        self.parallel_dots = ParallelDots(self)
        '''
        Uses ParallelDots AI to process or compare text for a variety of features.
        See the API documentation, at
        http://apis.paralleldots.com/text_docs/index.html
        
        Terms of use: https://www.paralleldots.com/terms-and-conditions
        '''

        self.phone_iot = PhoneIoT(self)
        '''
        PhoneIoT is a service in NetsBlox (https://netsblox.org/) that's meant to teach Internet of Things (IoT) topics as early as K-12 education.
        It allows you to programmatically access your smartphone's sensors and display.
        This includes accessing hardware sensors such as the accelerometer, gyroscope, microphone, camera, and many others depending on the device.
        PhoneIoT also allows you to control a customizable interactive display, enabling you to use your device as a custom remote control, or even create and run distributed (multiplayer) applications.
        The limits are up to your imagination!
        
        To get started using PhoneIoT, download the PhoneIoT app on your mobile device, available for Android (https://play.google.com/store/apps/details?id=org.netsblox.phoneiot) and iOS, and then go to the NetsBlox editor (https://editor.NetsBlox.org).
        In the top left of the editor, you should see a grid of several colored tabs.
        Under the Network tab, grab a call block and place it in the center script area.
        Click the first dropdown on the call block and select the PhoneIoT service.
        The second dropdown selects the specific *Remote Procedure Call* (RPC) to execute - see the table of contents  for information about the various RPCs.
        
        Inside the PhoneIoT app on your mobile device, click the button at the top left to open the menu, and then click connect.
        If you successfully connected, you should get a small popup message at the bottom of the screen.
        If you don't see this message, make sure you have either Wi-Fi or mobile data turned on and try again.
        Near the top of the menu, you should see an ID and password, which will be needed to connect to the device from NetsBlox.
        
        Back in NetsBlox, select the setCredentials RPC and give it your ID and password.
        For convenience, you might want to save the ID in a variable (e.g. device), as it will be referenced many times.
        If you click the call block to run it, you should get an OK result, meaning you successfully connected.
        If you don't see this, make sure you entered the ID and password correctly.
        
        You're now ready to start using the other RPCs in PhoneIoT to communicate with the device!
        '''

        self.pixabay = Pixabay(self)
        '''
        The Pixabay Service provides access to free images released under Creative Commons CC0.
        For more information, check out https://pixabay.com
        '''

        self.project_gutenberg = ProjectGutenberg(self)
        '''
        The Project Gutenberg service provides access to public domain books. For more information, check out https://project-gutenberg.org/.
        '''

        self.public_roles = PublicRoles(self)
        '''
        The PublicRoles Service provides access to the user's public role
        ID programmatically. This enables communication between projects.
        '''

        self.rain_viewer = RainViewer(self)
        '''
        This service provides access to the RainViewer (https://www.rainviewer.com/api.html) aggregated database.
        RainViewer provides access to recent and forecasted weather radar maps all around the world.
        '''

        self.robo_scape = RoboScape(self)
        

        self.service_creation = ServiceCreation(self)
        '''
        The ServiceCreation Service enables users to create custom services. Custom
        Services can be found under the "Community" section using the call <RPC>
        block.
        '''

        self.shared_canvas = SharedCanvas(self)
        '''
        SharedCanvas is a service that lets all NetsBlox users view and edit a shared canvas (image).
        Users can view the canvas, or edit it pixel by pixel.
        However, there is a cooldown between canvas edits, meaning one user cannot dominate the entire canvas.
        
        SharedCanvas was inspired by Place (https://en.wikipedia.org/wiki/R/place), which was
        a social experiment started on Reddit that functioned in much the same way. Place came to capture
        Reddit's online culture through the combined efforts of many users striving to control the canvas
        and display their own images.
        '''

        self.simple_hangman = SimpleHangman(self)
        '''
        The SimpleHangman Service provides RPCs for playing single player hangman.
        The service will choose a word for the player to guess using the given RPCs.
        '''

        self.sound_clips = SoundClips(self)
        '''
        This service allows users to play songs.
        '''

        self.star_map = StarMap(self)
        '''
        The StarMap Service provides access to astronomy data using Sloan Digital Sky Survey.
        For more information, check out http://skyserver.sdss.org/dr14/en/home.aspx
        '''

        self.thingspeak = Thingspeak(self)
        '''
        The ThingSpeak Service provides access to the ThingSpeak IoT analytics platform.
        For more information, check out https://thingspeak.com/.
        
        Terms of use: https://thingspeak.com/pages/terms
        '''

        self.this_x_does_not_exist = ThisXDoesNotExist(self)
        '''
        This service uses Artificial Intelligence (AI) to make random, realistic images.
        For a list of example websites, see https://thisxdoesnotexist.com/.
        These are typically made by a Generative Adversarial neural Network (GAN).
        Put simply, this involves two AIs: one to make images and another to guess if they're real or fake, and making them compete to mutually improve.
        For more information, see https://en.wikipedia.org/wiki/Generative_adversarial_network.
        '''

        self.time_sync = TimeSync(self)
        '''
        TimeSync is a tool for measuring the latency and clock offset between your NetsBlox client and the NetsBlox server.
        This can be used to have more precise timings for message passing and other time-based synchronization tasks.
        
        To use this service, you first call TimeSync.prepare, followed by performing several (e.g., 100) calls
        to TimeSync.step, and then finishing with TimeSync.complete to get the computed timing metrics.
        
        Note that the calls to TimeSync.step are intended to be back-to-back.
        You should perform this in a loop that does nothing else.
        In particular, you should not sleep/wait inside the loop; if you need this,
        you may provide a sleepTime to TimeSync.prepare and it will do the sleeping/waiting for you (do not also sleep yourself).
        '''

        self.translation = Translation(self)
        '''
        Uses Microsoft's Azure Cognitive Services API to translate text.
        For more information, check out https://azure.microsoft.com/en-us/pricing/details/cognitive-services/translator-text-api/.
        
        Terms of use: https://www.microsoft.com/en-us/servicesagreement
        '''

        self.trivia = Trivia(self)
        '''
        The Trivia Service provides access to trivia questions using the jservice API.
        For more information, check out https://jservice.io.
        '''

        self.twenty_questions = TwentyQuestions(self)
        '''
        The TwentyQuestions Service aids in the creation of a multiplayer
        game of twenty questions.
        '''

        self.water_watch = WaterWatch(self)
        '''
        The WaterWatch Service provides access to real-time water data.
        For more information, check out https://waterservices.usgs.gov/
        '''

        self.weather = Weather(self)
        '''
        The Weather Service provides access to real-time weather data using OpenWeatherMap.
        For more information, check out https://openweathermap.org/.
        
        Terms of Service: https://openweathermap.org/terms
        '''

        self.wildcam = Wildcam(self)
        '''
        Wildcam provides access to wildlife images from around the world.
        
        Current data sources:
        
        - Zooniverse (https://classroom.zooniverse.org/#/wildcam-gorongosa-lab/explorers/map/)
        '''

        self.word_guess = WordGuess(self)
        '''
        A simple Wordle-like word guessing game.
        '''


    def _ws_open(self, ws):
        with self._ws_lock:
            ws.send(_common.small_json({ 'type': 'set-uuid', 'clientId': self._client_id }))

    def _ws_close(self, ws, status, message):
        print('ws close', file = _sys.stderr)
    def _ws_error(self, ws, error):
        print('ws error:', error, file = _sys.stderr)

    def _ws_message(self, ws, message):
        try:
            message = _json.loads(message)
            ty = message['type']

            if ty == 'connected': # currently unused
                return
            elif ty == 'ping':
                with self._ws_lock:
                    ws.send(_common.small_json({ 'type': 'pong' }))
                    return
            elif ty == 'message':
                with self._message_cv:
                    self._message_queue.append(message)
                    self._message_cv.notify()
        except:
            pass

    def set_room(self, room: Optional[_rooms.RuntimeRoomManager]) -> None:
        '''
        Sets the room that this client should be part of.
        Unless you know what you're doing, you should probably not use this function directly.
        The PyBlox IDE will manage this for you automatically.
        '''
        assert self._room_handle is None
        self._room_handle = room

    @property
    def public_id(self) -> str:
        '''
        Gets the public id, which can be used as a target for `send_message()` to directly send a message to you.
        '''
        return f'{self._project_name}@{self._client_id}#py'
    def send_message(self, msg_type: str, target: Union[str, List[str]] = 'local', **values):
        '''
        Sends a message of the given type to the target(s), which is either the public id of a single target
        or a list of multiple ids for multiple targets.
        The default value for target, `'local'`, will send the message to your own project (not just the sprite that sends the message).
        You can receive messages with `@nb.on_message`.

        This is similar to broadcast/receive in Snap! except that you can send messages over the internet
        and the messages can contain fields/values.
        To send a field, simply pass it as a keyword argument in the function call.
        For instance, the following example sends a message called `'message'` with a field called `'msg'`:

        ```
        nb.send_message('message', 'local', msg = 'hello world')
        ```
        '''
        values = { k: _common.prep_send(v) for k, v in values.items() }
        targets = [target] if isinstance(target, str) else target
        my_addr = self.public_id

        role_info = []
        def get_roles():
            if len(role_info) != 0: return role_info[0]
            role_info.append({} if self._room_handle is None else self._room_handle.get_roles())
            return role_info[0]

        extern_targets = []
        local_count = 0
        for target in targets:
            if '@' in target:
                extern_targets.append(target)
            elif target == 'local':
                local_count += 1
            elif target == 'everyone in room' or target == 'others in room':
                for addrs in get_roles().values():
                    for addr in addrs:
                        if addr != my_addr: extern_targets.append(addr)
                if target == 'everyone in room':
                    local_count += 1
            else:
                for addr in get_roles().get(target, []):
                    if addr != my_addr: extern_targets.append(addr)
                    else: local_count += 1

        if local_count > 0:
            copies = [_copy.deepcopy(values) for _ in range(local_count)]
            with self._message_cv:
                for copy in copies:
                    self._message_queue.append({
                        'msgType': msg_type,
                        'content': copy,
                    })
                self._message_cv.notify()
        if len(extern_targets) > 0:
            with self._ws_lock:
                self._ws.send(_common.small_json({
                    'type': 'message',
                    'msgType': msg_type,
                    'content': values,
                    'dstId': extern_targets,
                    'srcId': my_addr,
                }))

    @staticmethod
    def _check_handler(handler, content):
        argspec = _inspect.getfullargspec(handler.wrapped())
        unused_params = set(content.keys())
        for arg in argspec.args + argspec.kwonlyargs:
            if arg not in content and arg != 'self':
                return f'    unknown param: \'{arg}\' typo?\n    available params: {list(content.keys())}'
            unused_params.discard(arg)
        return { k: content[k] for k in content.keys() if k not in unused_params } if unused_params and argspec.varkw is None else content
    def _message_get_last_assume_locked(self, msg_type):
        if msg_type not in self._message_last:
            self._message_last[msg_type] = { 'received_count': 0, 'last_content': {}, 'waiters': 0 }
        return self._message_last[msg_type]
    def _message_router(self):
        while True:
            try:
                message = None
                handlers = None
                with self._message_cv:
                    # if no more messages and stream has stopped, kill the thread
                    if not self._message_queue and self._message_stream_stopped:
                        return
                    # wait for a message or kill signal
                    while not self._message_queue and not self._message_stream_stopped:
                        self._message_cv.wait()
                    # if we didn't get a message, kill the thread
                    if not self._message_queue:
                        return

                    message = self._message_queue.popleft()
                    handlers = self._message_handlers.get(message['msgType'])
                    handlers = handlers[:] if handlers is not None else [] # iteration without mutex needs a (shallow) copy

                    last = self._message_get_last_assume_locked(message['msgType'])
                    last['received_count'] += 1
                    last['last_content'] = message['content']
                    if last['waiters'] > 0:
                        last['waiters'] = 0
                        self._message_cv.notify_all()

                content = message['content']
                for handler in handlers: # without mutex lock so we don't block new ws messages or on_message()
                    try:
                        packet = Client._check_handler(handler, content)
                        if type(packet) == str:
                            print(f'\'{message["msgType"]}\' message handler error:\n{packet}', file = _sys.stderr)
                            continue

                        handler.schedule(**packet)
                    except:
                        _traceback.print_exc(file = _sys.stderr)
            except:
                _traceback.print_exc(file = _sys.stderr)

    def wait_for_message(self, msg_type: str) -> dict:
        '''
        Waits until we receive the next message of the given type.
        Returns the received message upon resuming.

        You can trigger this manually by sending a message to yourself.
        '''
        with self._message_cv:
            last = self._message_get_last_assume_locked(msg_type)
            last['waiters'] += 1
            v = last['received_count']
            while last['received_count'] <= v:
                self._message_cv.wait()
            return last['last_content']

    def _on_message(self, msg_type: str, handler):
        with self._message_cv:
            handlers = self._message_handlers.get(msg_type)
            if handlers is None:
                handlers = []
                self._message_handlers[msg_type] = handlers
            handlers.append(_events.get_event_wrapper(handler))
    def on_message(self, *msg_types: str):
        '''
        This is a decorator that can be applied to a sprite/stage method or a function
        to cause the function to be executed when a message of the given type is received from NetsBlox.
        You can receive message fields by specifying input parameters.

        ```
        @nb.on_message('start')
        def on_start():
            print('started')

        @nb.on_message('left', 'right')
        def on_left_or_right(self, distance):
            print('moved', distance, 'cm')
        ```
        '''
        def wrapper(f):
            if _common.is_method(f):
                if not hasattr(f, '__run_on_message'):
                    setattr(f, '__run_on_message', [])
                # mark it for the constructor to handle when an instance is created
                def stupid_closure_semantics(_msg_type):
                    return lambda x: self._on_message(_msg_type, x)
                getattr(f, '__run_on_message').extend([stupid_closure_semantics(msg_type) for msg_type in msg_types])
            else:
                for msg_type in msg_types:
                    self._on_message(msg_type, f)

            return f
        return wrapper

    def call(self, service: str, rpc: str, **kwargs) -> Any:
        '''
        Directly calls the specified NetsBlox RPC based on its name.
        This is needed to access unofficial or dynamically-generated (like create-a-service) services.

        Note that the `service` and `rpc` names must match those in NetsBlox,
        rather than the renamed versions used in the Python wrappers here.

        The keyword arguments are the values to send to the RPC.
        Note that these names must match those stated in NetsBlox, rather than the snake_case names used by PyBlox RPC wrappers.
        From NetsBlox, you can inspect the argument names from an empty call block (arg names shown as hint text),
        or by visiting the official [NetsBlox documentation](https://editor.netsblox.org/docs/services/GoogleMaps/index.html).

        If an RPC input would not be a valid python identifier (variable name), such as `'city*'`,
        you can use keyword argument unpacking notation like `**{'city*': value}`.
        However, you should avoid unpacking notation if possible.

        ```
        # the following are equivalent
        nb.call('Googlemaps', 'getEarthCoordinates', x = my_x, y = my_y)
        nb.call('Googlemaps', 'getEarthCoordinates', **{'x': my_x, 'y': my_y})
        ```
        '''
        arguments = { k: _common.prep_send(v) for k, v in kwargs.items() }

        time = round(_time.time() * 1000)
        url = f'{self._services_url}/{service}/{rpc}?clientId={self._client_id}&t={time}'
        res = _requests.post(url,
            _common.small_json(arguments), # if the json has unnecessary white space, request on the server will hang for some reason
            headers = { 'Content-Type': 'application/json' })

        if res.status_code == 200:
            try:
                if 'Content-Type' in res.headers:
                    ty = res.headers['Content-Type']
                    if ty.startswith('image/'):
                        return Image.open(_io.BytesIO(res.content)).convert('RGBA')
                m = _SNAP_IMAGE_REGEX.match(res.text)
                if m is not None:
                    return _common.decode_image(m[1]).convert('RGBA')
                return _json.loads(res.text)
            except:
                return res.text # strings are returned unquoted, so they'll fail to parse as json
        else:
            raise _common.NetsBloxError(res.text)

    def disconnect(self):
        '''
        Disconnects the client from the NetsBlox server.
        If the client was created with run_forever, this will allow the program to terminate.
        '''
        with self._ws_lock:
            self._ws.close() # closing the websocket will kill the ws thread
        with self._message_cv:
            self._message_stream_stopped = True # send the kill signal
            self._message_cv.notify()
    def wait_till_disconnect(self):
        '''
        This function waits until the client is disconnected and all queued messages have been handled.
        Other (non-waiting) code can call disconnect() to trigger this manually.
        This is useful if you have long-running code using messaging, e.g., a server.

        If you want similar behavior without having to actually disconnect the client, you can use a Signal instead.

        Note that calling this function is not equivalent to setting the run_forever option when creating the client, as that does not block the main thread.
        This can be used in place of run_forever, and is needed if other code waits for the main thread to finish (e.g., Google Colab).

        Note: you should not call this from a message handler (or any function that a message handler calls),
        as that will suspend the thread that handles messages, and since this waits until all messages have been handled, it will end up waiting forever.
        '''
        self._message_thread.join()

class AirQuality:
    '''
    The AirQuality Service provides access to real-time air quality data using the AirNowAPI.
    For more information, check out https://docs.airnowapi.org/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    @deprecated()
    def _aqi(self, latitude: float, longitude: float) -> float:
        '''
        Get air quality index of closest reporting location for coordinates
        
        :latitude: latitude of location
        
        :longitude: Longitude of location
        
        :returns: AQI of closest station
        '''
        res = self._client.call('AirQuality', 'aqi', **{ 'latitude': latitude, 'longitude': longitude })
        return float(res)
    def quality_index(self, latitude: float, longitude: float) -> float:
        '''
        Get air quality index of closest reporting location for coordinates
        
        :latitude: latitude of location
        
        :longitude: Longitude of location
        
        :returns: AQI of closest station
        '''
        res = self._client.call('AirQuality', 'qualityIndex', **{ 'latitude': latitude, 'longitude': longitude })
        return float(res)
    def quality_index_by_zip_code(self, zip_code: int) -> float:
        '''
        Get air quality index of closest reporting location for ZIP code
        
        :zip_code: ZIP code of location
        
        :returns: AQI of closest station
        '''
        res = self._client.call('AirQuality', 'qualityIndexByZipCode', **{ 'zipCode': zip_code })
        return float(res)
class Alexa:
    '''
    The Alexa service provides capabilities for building your own Alexa skills!
    
    An Alexa skill consists of some general information (such as the name to use
    for invocation) as well as a list of supported intents. An intent is a command
    or question to which the skill can respond. Intents consist of a name, list of
    utterances, and any required slots. Utterances are examples of how the user might
    phrase questions or commands. Slots are used to define placeholders for concepts
    like names, cities, etc.
    
    When Alexa determines that a request was made to a given intent, the slots are
    resolved to their corresponding values and then passed to the "handler" for the
    intent.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def create_skill(self, configuration: dict) -> str:
        '''
        Create an Alexa Skill from a configuration.
        
        :configuration: 
        
          - :name: (str) The name of the skill
        
          - :invocation: (str) The name to use to invoke the skill (eg, "tell <invocation> to <intent>")
        
          - :intents: (List[dict]) Intents (ie, commands) supported by the skill.
        
          - :description: (str) 
        
          - :category: (str) 
        
          - :keywords: (List[str]) 
        
          - :summary: (str) 
        
          - :examples: (List[str]) 
        
        :returns: ID
        '''
        res = self._client.call('Alexa', 'createSkill', **{ 'configuration': configuration })
        return str(res)
    def delete_skill(self, id: str):
        '''
        Delete the given Alexa Skill (created within NetsBlox).
        
        :id: ID of the Alexa skill to delete
        '''
        return self._client.call('Alexa', 'deleteSkill', **{ 'ID': id })
    def get_skill(self, id: str):
        '''
        Get the configuration of the given Alexa Skill.
        
        :id: 
        '''
        return self._client.call('Alexa', 'getSkill', **{ 'ID': id })
    def get_skill_categories(self):
        '''
        Get a list of all valid categories for Alexa skills.
        '''
        return self._client.call('Alexa', 'getSkillCategories', **{  })
    def get_slot_types(self):
        '''
        Get a list of all valid slot types that can be added to an intent.
        For more information, check out https://developer.amazon.com/en-US/docs/alexa/custom-skills/slot-type-reference.html
        '''
        return self._client.call('Alexa', 'getSlotTypes', **{  })
    def invoke_skill(self, id: str, utterance: str) -> str:
        '''
        Invoke the skill with the given utterance using the closest intent.
        
        :id: Alexa Skill ID to send utterance to
        
        :utterance: Text to send to skill
        
        :returns: ID
        '''
        res = self._client.call('Alexa', 'invokeSkill', **{ 'ID': id, 'utterance': utterance })
        return str(res)
    def list_skills(self) -> List[str]:
        '''
        List the IDs of all the Alexa Skills created in NetsBlox for the given user.
        
        :returns: IDs
        '''
        res = self._client.call('Alexa', 'listSkills', **{  })
        return _common.vectorize(str)(res)
    def update_skill(self, id: str, configuration: dict):
        '''
        Update skill configuration with the given ID.
        
        :id: ID of the skill to update
        
        :configuration: 
        
          - :name: (str) The name of the skill
        
          - :invocation: (str) The name to use to invoke the skill (eg, "tell <invocation> to <intent>")
        
          - :intents: (List[dict]) Intents (ie, commands) supported by the skill.
        
          - :description: (str) 
        
          - :category: (str) 
        
          - :keywords: (List[str]) 
        
          - :summary: (str) 
        
          - :examples: (List[str]) 
        '''
        return self._client.call('Alexa', 'updateSkill', **{ 'ID': id, 'configuration': configuration })
class Autograders:
    '''
    The Autograders service enables users to create custom autograders for
    use within NetsBlox.
    
    For more information, check out https://editor.netsblox.org/docs/services/Autograders/index.html
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def add_lti_consumer(self, autograder: str, consumer: str):
        '''
        Add an LTI (v1.1) consumer to an existing autograder.
        
        :autograder: name of the autograder to update
        
        :consumer: name of the consumer to add (eg, Coursera)
        '''
        return self._client.call('Autograders', 'addLTIConsumer', **{ 'autograder': autograder, 'consumer': consumer })
    def create_autograder(self, configuration: dict):
        '''
        Create an autograder using the supplied configuration.
        
        :configuration: 
        '''
        return self._client.call('Autograders', 'createAutograder', **{ 'configuration': configuration })
    def get_autograder_config(self, name: str):
        '''
        Fetch the autograder configuration.
        
        :name: 
        '''
        return self._client.call('Autograders', 'getAutograderConfig', **{ 'name': name })
    def get_autograders(self):
        '''
        List the autograders for the given user.
        '''
        return self._client.call('Autograders', 'getAutograders', **{  })
    def get_lti_consumers(self, autograder: str):
        '''
        List LTI (v1.1) consumers for an existing autograder.
        
        :autograder: name of the autograder to update
        '''
        return self._client.call('Autograders', 'getLTIConsumers', **{ 'autograder': autograder })
    def remove_lti_consumer(self, autograder: str, consumer: str):
        '''
        Remove an LTI (v1.1) consumer from an existing autograder.
        
        :autograder: name of the autograder to update
        
        :consumer: name of the consumer to add (eg, Coursera)
        '''
        return self._client.call('Autograders', 'removeLTIConsumer', **{ 'autograder': autograder, 'consumer': consumer })
class BaseX:
    '''
    The BaseX Service provides access to an existing BaseX instance.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def command(self, url: str, command: str, username: Optional[str] = None, password: Optional[str] = None):
        '''
        Execute a single database command.
        
        A list of commands can be found at http://docs.basex.org/wiki/Commands
        
        :url: 
        
        :command: 
        
        :username: 
        
        :password: 
        '''
        return self._client.call('BaseX', 'command', **{ 'url': url, 'command': command, 'username': username, 'password': password })
    def query(self, url: str, database: str, query: str, username: Optional[str] = None, password: Optional[str] = None):
        '''
        Evaluate an XQuery expression.
        
        :url: 
        
        :database: 
        
        :query: 
        
        :username: 
        
        :password: 
        '''
        return self._client.call('BaseX', 'query', **{ 'url': url, 'database': database, 'query': query, 'username': username, 'password': password })
class Battleship:
    '''
    The Battleship Service provides helpful utilities for building a distributed
    game of battleship.
    
    Overview
    --------
    
    Like regular Battleship, the Battleship service has two states: placing ships and shooting at ships.
    During placement, it expects each role to place each ship on his/her board and will not allow the game to proceed to the shooting phase until each role has placed all his/her ships.
    Placement, firing and starting blocks will return true if successful or an error message if it fails.
    
    Blocks
    ------
    
    - place <ship> at <row> <column> facing <direction> - Places a ship on your board with the front at the given row and column facing the given direction. Returns true if placed successfully (eg, on the board and not overlapping another ship). Also, placing a ship twice results in a move (not duplicates).
    - start game - Try to start the game. If both users have all their ships placed, it should return true and send start messages to all roles. Otherwise, it will return with a message saying that it is waiting on a specific role.
    - fire at <row> <column> - This block allows the user to try to fire at the given row and column. It returns true if it was a valid move; otherwise it will return an error message like it's not your turn!. On a successful move, the server will send either a hit or miss message to everyone in the room. Then it will send a your turn message to the player to play next.
    - active ships for <role> - This block returns a list of all ships that are still afloat for the given role. If no role is specified, it defaults to the sender's role.
    - all ships - Returns a list of all ship names. Useful in programmatically placing ships.
    - ship length <ship> - Returns the length of the given ship.
    - restart game - Restarts the given game (all boards, etc)
    
    Message Types
    -------------
    
    - start - Received when start game finishes successfully for any role. After game has officially started, users can no longer move ships.
    - your turn - Received when the given role's turn starts.
    - hit - role is the owner of the ship that has been hit. ship is the name of the ship that has been hit, and row and column provide the location on the board where it was hit. sunk provides a true/false value for if the ship was sunk.
    - miss - role is the owner of the board receiving the shot and row and column correspond to the board location or the shot.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def all_ships(self) -> List[str]:
        '''
        Get list of ship types
        
        :returns: Types of ships
        '''
        res = self._client.call('Battleship', 'allShips', **{  })
        return _common.vectorize(str)(res)
    def fire(self, row: float, column: float) -> bool:
        '''
        Fire a shot at the board
        
        :row: Row to fire at
        
        :column: Column to fire at
        
        :returns: If ship was hit
        '''
        res = self._client.call('Battleship', 'fire', **{ 'row': row, 'column': column })
        return bool(res)
    def place_ship(self, ship: str, row: float, column: float, facing: str) -> bool:
        '''
        Place a ship on the board
        
        :ship: Ship type to place
        
        :row: Row to place ship in
        
        :column: Column to place ship in
        
        :facing: Direction to face
        
        :returns: If piece was placed
        '''
        res = self._client.call('Battleship', 'placeShip', **{ 'ship': ship, 'row': row, 'column': column, 'facing': facing })
        return bool(res)
    def remaining_ships(self, role_id: str) -> int:
        '''
        Get number of remaining ships of a role
        
        :role_id: Name of role to use
        
        :returns: Number of remaining ships
        '''
        res = self._client.call('Battleship', 'remainingShips', **{ 'roleID': role_id })
        return int(res)
    def reset(self) -> bool:
        '''
        Resets the game by clearing the board and reverting to the placing phase
        
        :returns: If game was reset
        '''
        res = self._client.call('Battleship', 'reset', **{  })
        return bool(res)
    def ship_length(self, ship: str) -> int:
        '''
        Get length of a ship type
        
        :ship: Type of ship
        
        :returns: Length of ship type
        '''
        res = self._client.call('Battleship', 'shipLength', **{ 'ship': ship })
        return int(res)
    def start(self) -> bool:
        '''
        Begins the game, if board is ready
        
        :returns: If game was started
        '''
        res = self._client.call('Battleship', 'start', **{  })
        return bool(res)
class BingTraffic:
    '''
    The Traffic Service provides access to real-time traffic data using the Bing Traffic API.
    For more information, check out https://msdn.microsoft.com/en-us/library/hh441725.aspx
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def search(self, west_longitude: float, north_latitude: float, east_longitude: float, south_latitude: float):
        '''
        Search for traffic accidents in a given region. Results are sent as messages in the format:
        
        Message type: Traffic
        fields: latitude, longitude, type
        
        :west_longitude: 
        
        :north_latitude: 
        
        :east_longitude: 
        
        :south_latitude: 
        '''
        return self._client.call('BingTraffic', 'search', **{ 'westLongitude': west_longitude, 'northLatitude': north_latitude, 'eastLongitude': east_longitude, 'southLatitude': south_latitude })
    def stop(self):
        '''
        Stop any pending requested messages (search results).
        '''
        return self._client.call('BingTraffic', 'stop', **{  })
class COVID19:
    '''
    The COVID-19 Service provides access to the 2019-nCoV dataset compiled by Johns Hopkins University.
    This dataset includes deaths, confirmed cases, and recoveries related to the COVID-19 pandemic.
    Vaccination data is provided by Our World in Data.
    
    For more information, check out https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases
    and https://github.com/owid/covid-19-data/tree/master/public/data/vaccinations.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_confirmed_counts(self, country: str, state: Optional[str] = None, city: Optional[str] = None):
        '''
        Get number of confirmed cases of COVID-19 by date for a specific country and state.
        
        Date is in month/day/year format.
        
        :country: Country or region
        
        :state: State or province
        
        :city: City
        '''
        return self._client.call('COVID-19', 'getConfirmedCounts', **{ 'country': country, 'state': state, 'city': city })
    def get_death_counts(self, country: str, state: Optional[str] = None, city: Optional[str] = None):
        '''
        Get number of cases of COVID-19 resulting in death by date for a specific country and state.
        
        Date is in month/day/year format.
        
        :country: Country or region
        
        :state: State or province
        
        :city: City
        '''
        return self._client.call('COVID-19', 'getDeathCounts', **{ 'country': country, 'state': state, 'city': city })
    def get_location_coordinates(self, country: str, state: Optional[str] = None, city: Optional[str] = None):
        '''
        Get the latitude and longitude for a location with data available.
        
        :country: 
        
        :state: 
        
        :city: City
        '''
        return self._client.call('COVID-19', 'getLocationCoordinates', **{ 'country': country, 'state': state, 'city': city })
    def get_locations_with_data(self) -> list:
        '''
        Get a list of all countries (and states, cities) with data available.
        
        :returns: an array of [country, state, city] for each location with data available
        '''
        return self._client.call('COVID-19', 'getLocationsWithData', **{  })
    def get_recovered_counts(self, country: str, state: Optional[str] = None, city: Optional[str] = None):
        '''
        Get number of cases of COVID-19 in which the person recovered by date for a specific country and state.
        
        Date is in month/day/year format.
        
        :country: Country or region
        
        :state: State or province
        
        :city: City
        '''
        return self._client.call('COVID-19', 'getRecoveredCounts', **{ 'country': country, 'state': state, 'city': city })
    def get_vaccination_categories(self) -> List[str]:
        '''
        Get the list of options that can be entered in the getVaccinationData RPC
        
        :returns: 
        '''
        res = self._client.call('COVID-19', 'getVaccinationCategories', **{  })
        return _common.vectorize(str)(res)
    def get_vaccination_countries(self) -> List[str]:
        '''
        The list of countries that can be entered in the getVaccinationData RPC
        
        :returns: 
        '''
        res = self._client.call('COVID-19', 'getVaccinationCountries', **{  })
        return _common.vectorize(str)(res)
    def get_vaccination_data(self, country: str, state: Optional[str] = None, category: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list:
        '''
        Get all available vaccination data for a given country or state (if country is United States).
        Optionally, you can specify category to filter to only data for the given category.
        You can further filter your data by specifying startDate and endDate.
        
        :country: name of the country for which to get data
        
        :state: name of the state to get data for (if the country is United States)
        
        :category: the category of data to pull (see getVaccinationCategories), or nothing to get all data
        
        :start_date: earliest date to include in result (mm/dd/yyyy)
        
        :end_date: latest date to include in result (mm/dd/yyyy)
        
        :returns: the requested data
        '''
        return self._client.call('COVID-19', 'getVaccinationData', **{ 'country': country, 'state': state, 'category': category, 'startDate': start_date, 'endDate': end_date })
    def get_vaccination_states(self) -> List[str]:
        '''
        Get the list of US states that can be entered in the getVaccinationData RPC
        
        :returns: 
        '''
        res = self._client.call('COVID-19', 'getVaccinationStates', **{  })
        return _common.vectorize(str)(res)
class Chart:
    '''
    A charting service powered by gnuplot.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def default_options(self) -> dict:
        '''
        Get the default options for the Chart.draw RPC.
        
        :returns: the default draw options
        '''
        res = self._client.call('Chart', 'defaultOptions', **{  })
        return dict(res)
    def draw(self, lines: list, options: Optional[dict] = None) -> Image.Image:
        '''
        Create charts and histograms from data.
        
        :lines: a single line or list of lines. Each line should be [[x1,y1], [x2,y2], ...].
        
        :options: Configuration for graph title, axes, and more
        
          - :title: (str) title to show on the graph
        
          - :width: (float) width of the returned image
        
          - :height: (float) height of the returned image
        
          - :labels: (List[str]) labels for each line
        
          - :types: (List[str]) types for each line
        
          - :xRange: (List[float]) range of X values to graph
        
          - :yRange: (List[float]) range of Y values to graph
        
          - :xLabel: (str) label on the X axis
        
          - :yLabel: (str) label on the Y axis
        
          - :xTicks: (float) tick interval for the X axis
        
          - :isCategorical: (bool) true to enable categorical mode
        
          - :smooth: (bool) true to enable smoothing
        
          - :grid: (str) grid type to use
        
          - :isTimeSeries: (bool) true to enable time series mode
        
          - :timeInputFormat: (str) input time format for time series data
        
          - :timeDisplayFormat: (str) output time format for time series data
        
          - :logscale: (list) logscale settings to use
        
          - :fontSize: (int) font size to use for the title and axis labels (default 10).
        
          - :legendLocation: (str) the location of the legend
        
          - :lineWidth: (int) the width of the lines to draw
        
        :returns: the generated chart
        '''
        return self._client.call('Chart', 'draw', **{ 'lines': lines, 'options': options })
    @deprecated()
    def _draw_bar_chart(self, dataset: Any, x_axis_tag: Any, y_axis_tag: Any, dataset_tag: Any, title: Any):
        '''
        :dataset: 
        
        :x_axis_tag: 
        
        :y_axis_tag: 
        
        :dataset_tag: 
        
        :title: 
        '''
        return self._client.call('Chart', 'drawBarChart', **{ 'dataset': dataset, 'xAxisTag': x_axis_tag, 'yAxisTag': y_axis_tag, 'datasetTag': dataset_tag, 'title': title })
    @deprecated()
    def _draw_line_chart(self, dataset: Any, x_axis_tag: Any, y_axis_tag: Any, dataset_tag: Any, title: Any):
        '''
        :dataset: 
        
        :x_axis_tag: 
        
        :y_axis_tag: 
        
        :dataset_tag: 
        
        :title: 
        '''
        return self._client.call('Chart', 'drawLineChart', **{ 'dataset': dataset, 'xAxisTag': x_axis_tag, 'yAxisTag': y_axis_tag, 'datasetTag': dataset_tag, 'title': title })
class CloudVariables:
    '''
    The CloudVariables Service provides support for storing variables on the cloud.
    Variables can be optionally password-protected or stored only for the current user.
    
    Cloud variables that are inactive (no reads or writes) for 30 days are subject to deletion.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def delete_user_variable(self, name: str):
        '''
        Delete the user variable for the current user.
        
        :name: Variable name
        '''
        return self._client.call('CloudVariables', 'deleteUserVariable', **{ 'name': name })
    def delete_variable(self, name: str, password: Optional[str] = None):
        '''
        Delete a given cloud variable
        
        :name: Variable to delete
        
        :password: Password (if password-protected)
        '''
        return self._client.call('CloudVariables', 'deleteVariable', **{ 'name': name, 'password': password })
    def get_user_variable(self, name: str) -> Any:
        '''
        Get the value of a variable for the current user.
        
        :name: Variable name
        
        :returns: the stored value
        '''
        return self._client.call('CloudVariables', 'getUserVariable', **{ 'name': name })
    def get_variable(self, name: str, password: Optional[str] = None) -> Any:
        '''
        Get the value of a cloud variable
        
        :name: Variable name
        
        :password: Password (if password-protected)
        
        :returns: the stored value
        '''
        return self._client.call('CloudVariables', 'getVariable', **{ 'name': name, 'password': password })
    def listen_to_user_variable(self, name: str, msg_type: Any, duration: Optional[str] = None):
        '''
        Identical to CloudVariables.listenToVariable except that it listens for updates on a user variable.
        
        :name: Variable name
        
        :msg_type: Message type to send each time the variable is updated
        
        :duration: The maximum duration to listen for updates on the variable (default 1hr).
        '''
        return self._client.call('CloudVariables', 'listenToUserVariable', **{ 'name': name, 'msgType': msg_type, 'duration': duration })
    def listen_to_variable(self, name: str, msg_type: str, password: Optional[str] = None, duration: Optional[str] = None):
        '''
        Registers your client to receive messages each time the variable value is updated.
        name and password denote the variable to listen to.
        msgType is the name of the message that will be sent each time it is updated.
        
        The variable must already exist prior to calling this RPC.
        Update events will cease when the variable is deleted.
        
        Message Fields
        
        - name - the name of the variable that was updated
        - value - the new value of the variable
        
        :name: Variable name
        
        :msg_type: Message type to send each time the variable is updated
        
        :password: Password (if password-protected)
        
        :duration: The maximum duration to listen for updates on the variable (default 1hr).
        '''
        return self._client.call('CloudVariables', 'listenToVariable', **{ 'name': name, 'msgType': msg_type, 'password': password, 'duration': duration })
    def lock_variable(self, name: str, password: Optional[str] = None):
        '''
        Lock a given cloud variable.
        
        A locked variable cannot be changed by anyone other than the person
        who locked it. A variable cannot be locked for more than 5 seconds.
        
        :name: Variable to lock
        
        :password: Password (if password-protected)
        '''
        return self._client.call('CloudVariables', 'lockVariable', **{ 'name': name, 'password': password })
    def set_user_variable(self, name: str, value: Any):
        '''
        Set the value of the user cloud variable for the current user.
        
        :name: Variable name
        
        :value: Value to store in variable
        '''
        return self._client.call('CloudVariables', 'setUserVariable', **{ 'name': name, 'value': value })
    def set_variable(self, name: str, value: Any, password: Optional[str] = None):
        '''
        Set a cloud variable.
        If a password is provided on creation, the variable will be password-protected.
        
        :name: Variable name
        
        :value: Value to store in variable
        
        :password: Password (if password-protected)
        '''
        return self._client.call('CloudVariables', 'setVariable', **{ 'name': name, 'value': value, 'password': password })
    def unlock_variable(self, name: str, password: Optional[str] = None):
        '''
        Unlock a given cloud variable.
        
        A locked variable cannot be changed by anyone other than the person
        who locked it. A variable cannot be locked for more than 5 minutes.
        
        :name: Variable to delete
        
        :password: Password (if password-protected)
        '''
        return self._client.call('CloudVariables', 'unlockVariable', **{ 'name': name, 'password': password })
class CommonWords:
    '''
    The CommonWords service provides access to common words in a variety of languages.
    Words were discovered by retrieving the top 5000 words in each language
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_languages(self):
        '''
        Get a list of supported languages.
        '''
        return self._client.call('CommonWords', 'getLanguages', **{  })
    def get_words(self, language: str, start: Optional[int] = None, end: Optional[int] = None):
        '''
        Get a (sub) list of common words in a given language.
        
        :language: 
        
        :start: Index to start from (default 1)
        
        :end: Index of last word to include (default 10)
        '''
        return self._client.call('CommonWords', 'getWords', **{ 'language': language, 'start': start, 'end': end })
class ConnectN:
    '''
    The ConnectN Service provides helpers for building games like Connect-4 and Tic-Tac-Toe.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def is_full_board(self) -> bool:
        '''
        Check if every position on the current board is occupied.
        
        :returns: true if the board is full, otherwise false
        '''
        res = self._client.call('ConnectN', 'isFullBoard', **{  })
        return bool(res)
    def is_game_over(self) -> bool:
        '''
        Check if the current game is over.
        
        :returns: true if game over, otherwise false
        '''
        res = self._client.call('ConnectN', 'isGameOver', **{  })
        return bool(res)
    def new_game(self, row: Optional[float] = None, column: Optional[float] = None, num_dots_to_connect: Optional[float] = None):
        '''
        Create a new ConnectN game
        
        :row: The number of rows on the game board
        
        :column: The number of columns on the game board
        
        :num_dots_to_connect: The number of connected tiles required to win
        '''
        return self._client.call('ConnectN', 'newGame', **{ 'row': row, 'column': column, 'numDotsToConnect': num_dots_to_connect })
    def play(self, row: int, column: int):
        '''
        Play at the given row, column to occupy the location.
        
        :row: The given row at which to move
        
        :column: The given column at which to move
        '''
        return self._client.call('ConnectN', 'play', **{ 'row': row, 'column': column })
class ConnectNAI:
    '''
    The ConnectN AI service allows you to create games like Connect-4 or Tic-Tac-Toe and play against an AI that improves over time.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_ai_moves(self, player: str) -> list:
        '''
        Gets the AI to suggest the next best move for the specified player.
        
        :player: The player to make the recommendation for.
        
        :returns: A list of recommended moves, each being [value, row, column]. These are already sorted in descending value, so the recommended move is the first one.
        '''
        return self._client.call('ConnectNAI', 'getAIMoves', **{ 'player': player })
    def make_move(self, row: int, col: int, player: str) -> list:
        '''
        Makes a move for the specified player.
        
        :row: The row to play at.
        
        :col: The column to play at.
        
        :player: The player to make the move for.
        
        :returns: Location (row/column) and result of the move. The location may not be the same as the input if gravity is enabled (see newGame).
        '''
        return self._client.call('ConnectNAI', 'makeMove', **{ 'row': row, 'col': col, 'player': player })
    def new_game(self, rows: int, cols: int, n: int, gravity: bool):
        '''
        Starts a new game with the existing AI session.
        
        :rows: The number of rows in the game
        
        :cols: The number of columns in the game
        
        :n: The number of consecutive pieces needed to win
        
        :gravity: Whether or not to use gravity when placing pieces, which makes them fall down to the lowest unoccupied row in the column
        '''
        return self._client.call('ConnectNAI', 'newGame', **{ 'rows': rows, 'cols': cols, 'n': n, 'gravity': gravity })
    def new_session(self):
        '''
        Creates a new AI session.
        This has the effect of resetting the AI to the point of knowing nothing about the game.
        '''
        return self._client.call('ConnectNAI', 'newSession', **{  })
    def use_max_difficulty(self):
        '''
        Sets the current session's AI to the maximum difficulty.
        '''
        return self._client.call('ConnectNAI', 'useMaxDifficulty', **{  })
class CoreNLP:
    '''
    Use CoreNLP to annotate text.
    For more information, check out https://stanfordnlp.github.io/CoreNLP/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def annotate(self, text: str, annotators: Optional[List[str]] = None) -> dict:
        '''
        Annotate text using the provided annotators.
        
        :text: the text to annotate
        
        :annotators: a list of the annotators to use
        
        :returns: structured data containing the annotation results
        '''
        res = self._client.call('CoreNLP', 'annotate', **{ 'text': text, 'annotators': annotators })
        return dict(res)
    def get_annotators(self) -> List[str]:
        '''
        Get a list of all the supported annotators.
        The complete list is available at https://stanfordnlp.github.io/CoreNLP/annotators.html.
        
        :returns: list of supported annotators
        '''
        res = self._client.call('CoreNLP', 'getAnnotators', **{  })
        return _common.vectorize(str)(res)
class DailyWordGuess:
    '''
    A Wordle-like word guessing game with a single daily word for all users.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_word_list(self) -> List[str]:
        '''
        Get a list of all the possible words
        
        :returns: word list
        '''
        res = self._client.call('DailyWordGuess', 'getWordList', **{  })
        return _common.vectorize(str)(res)
    def give_up(self) -> str:
        '''
        Give up on the current game and learn the target word
        
        :returns: Target word of daily game
        '''
        res = self._client.call('DailyWordGuess', 'giveUp', **{  })
        return str(res)
    def guess(self, word: str):
        '''
        Guess the word. Returns a list where each item is the feedback for
        the corresponding character. Feedback is a "3" if the character is
        correct, "2" if it is correct but in the wrong place, and "1" if the
        letter is not present in the word.
        
        :word: Guess for this round
        '''
        return self._client.call('DailyWordGuess', 'guess', **{ 'word': word })
    def time_remaining(self) -> str:
        '''
        The amount of time in hours:minutes:seconds remaining to attempt the current day's puzzle
        
        :returns: Amount of time remaining
        '''
        res = self._client.call('DailyWordGuess', 'timeRemaining', **{  })
        return str(res)
    def tries_remaining(self) -> float:
        '''
        The number (out of six) of attempts at the daily puzzle remaining
        
        :returns: Number of attempts remaining
        '''
        res = self._client.call('DailyWordGuess', 'triesRemaining', **{  })
        return float(res)
class Dev:
    
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def caller_info(self):
        '''
        Return the caller info as detected by the server.
        '''
        return self._client.call('Dev', 'callerInfo', **{  })
    def clear_logs(self):
        '''
        Fetch debug logs for debugging remotely.
        '''
        return self._client.call('Dev', 'clearLogs', **{  })
    def detect_abort(self):
        '''
        Sleep for 3 seconds and detect if the RPC was aborted.
        '''
        return self._client.call('Dev', 'detectAbort', **{  })
    def echo(self, argument: Any):
        '''
        A function responding with the provided argument.
        
        :argument: 
        '''
        return self._client.call('Dev', 'echo', **{ 'argument': argument })
    def echo_if_within(self, input: float):
        '''
        Echo if the input is within 10 and 20 (manual test for parameterized types)
        
        :input: 
        '''
        return self._client.call('Dev', 'echoIfWithin', **{ 'input': input })
    def echo_options_example(self, options: dict):
        '''
        Call an argument with a duck typed options object
        
        :options: 
        
          - :name: (str) 
        
          - :age: (float) 
        
          - :height: (float) 
        '''
        return self._client.call('Dev', 'echoOptionsExample', **{ 'options': options })
    def get_logs(self):
        '''
        Fetch debug logs for debugging remotely.
        '''
        return self._client.call('Dev', 'getLogs', **{  })
    def image(self):
        '''
        A function returning an image.
        '''
        return self._client.call('Dev', 'image', **{  })
    def send_message(self, address: str, message_type: str, contents: dict):
        '''
        Send a message from the services server to a specific address.
        
        :address: 
        
        :message_type: 
        
        :contents: 
        '''
        return self._client.call('Dev', 'sendMessage', **{ 'address': address, 'messageType': message_type, 'contents': contents })
    def send_message_to_client(self, message_type: str, contents: dict, delay: int):
        '''
        Broadcast a message from the services server to the current room.
        
        :message_type: 
        
        :contents: 
        
        :delay: # of seconds to wait before sending
        '''
        return self._client.call('Dev', 'sendMessageToClient', **{ 'messageType': message_type, 'contents': contents, 'delay': delay })
    def send_message_to_role(self, role: str, message_type: str, contents: dict):
        '''
        Send a message from the services server to a given role.
        
        :role: 
        
        :message_type: 
        
        :contents: 
        '''
        return self._client.call('Dev', 'sendMessageToRole', **{ 'role': role, 'messageType': message_type, 'contents': contents })
    def send_message_to_room(self, message_type: str, contents: dict):
        '''
        Broadcast a message from the services server to the current room.
        
        :message_type: 
        
        :contents: 
        '''
        return self._client.call('Dev', 'sendMessageToRoom', **{ 'messageType': message_type, 'contents': contents })
    def sum(self, numbers: List[float]):
        '''
        Return the sum of the inputs
        
        :numbers: 
        '''
        return self._client.call('Dev', 'sum', **{ 'numbers': numbers })
    def throw(self, msg: str):
        '''
        A function throwing an error.
        
        :msg: Error message
        '''
        return self._client.call('Dev', 'throw', **{ 'msg': msg })
class EarthOrbit:
    '''
    Access to Astronomical Solutions for Earth Paleoclimates. There are three researches (in 1993, 2004, and 2010) about
    earth orbital parameters' data. This service only uses the 2004 data.
    
    For more information, check out
    http://vo.imcce.fr/insola/earth/online/earth/earth.html.
    
    Original datasets are available at:
    
    - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.100.ASC
    - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.250.ASC
    - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.ASC
    - http://vo.imcce.fr/insola/earth/online/earth/La2004/INSOLP.LA2004.BTL.ASC
    - http://vo.imcce.fr/webservices/miriade/proxy.php?file=http://145.238.217.35//tmp/insola/insolaouto7Yk3u&format=text
    - http://vo.imcce.fr/webservices/miriade/proxy.php?file=http://145.238.217.38//tmp/insola/insolaouteXT96X&format=text
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_eccentricity(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get eccentricity by year. For more information about eccentricity, please visit:
        https://climate.nasa.gov/news/2948/milankovitch-orbital-cycles-and-their-role-in-earths-climate/
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: list of historical eccentricity values for each year
        '''
        return self._client.call('EarthOrbit', 'getEccentricity', **{ 'startyear': startyear, 'endyear': endyear })
    def get_insolation(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get insolation by year. Insolation here is the amount of solar radiation received at 65 N in June on Earth.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: list of historical insolation values for each year
        '''
        return self._client.call('EarthOrbit', 'getInsolation', **{ 'startyear': startyear, 'endyear': endyear })
    def get_longitude(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get longitude of perihelion from moving equinox by year. For more information about this, please visit:
        https://www.physics.ncsu.edu/classes/astron/orbits.html
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: longitude - longitude of perihelion from moving equinox
        '''
        return self._client.call('EarthOrbit', 'getLongitude', **{ 'startyear': startyear, 'endyear': endyear })
    def get_obliquity(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get obliquity by year. For more information about obliquity, please visit:
        https://climate.nasa.gov/news/2948/milankovitch-orbital-cycles-and-their-role-in-earths-climate/
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: list of historical obliquity values for each year
        '''
        return self._client.call('EarthOrbit', 'getObliquity', **{ 'startyear': startyear, 'endyear': endyear })
    def get_precession(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get precession by year. For more information about precession, please visit:
        https://climate.nasa.gov/news/2948/milankovitch-orbital-cycles-and-their-role-in-earths-climate/
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: list of historical precession values for each year
        '''
        return self._client.call('EarthOrbit', 'getPrecession', **{ 'startyear': startyear, 'endyear': endyear })
class Earthquakes:
    '''
    The Earthquakes Service provides access to historical earthquake data.
    For more information, check out https://earthquake.usgs.gov/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def by_region(self, min_latitude: float, max_latitude: float, min_longitude: float, max_longitude: float, start_time: Optional[str] = None, end_time: Optional[str] = None, min_magnitude: Optional[float] = None, max_magnitude: Optional[float] = None):
        '''
        Send messages for earthquakes within a given region
        
        :min_latitude: Minimum latitude of region
        
        :max_latitude: Maximum latitude of region
        
        :min_longitude: Minimum longitude of region
        
        :max_longitude: Maximum longitude of region
        
        :start_time: Minimum time
        
        :end_time: Maximum time
        
        :min_magnitude: Minimum magnitude of earthquakes to report
        
        :max_magnitude: Maximum magnitude of earthquakes to report
        '''
        return self._client.call('Earthquakes', 'byRegion', **{ 'minLatitude': min_latitude, 'maxLatitude': max_latitude, 'minLongitude': min_longitude, 'maxLongitude': max_longitude, 'startTime': start_time, 'endTime': end_time, 'minMagnitude': min_magnitude, 'maxMagnitude': max_magnitude })
    def stop(self):
        '''
        Stop sending earthquake messages
        '''
        return self._client.call('Earthquakes', 'stop', **{  })
class Eclipse2017:
    '''
    The Eclipse2017 Service provides access to US weather data along the path of the Great American Eclipse.
    For more information about the eclipse, check out https://www.greatamericaneclipse.com/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def available_stations(self, max_reading_median: float, max_distance_from_center: float, latitude: Optional[float] = None, longitude: Optional[float] = None, max_distance_from_point: Optional[float] = None):
        '''
        Get a list of reporting weather stations for the given arguments.
        
        :max_reading_median: 
        
        :max_distance_from_center: 
        
        :latitude: 
        
        :longitude: 
        
        :max_distance_from_point: 
        '''
        return self._client.call('Eclipse2017', 'availableStations', **{ 'maxReadingMedian': max_reading_median, 'maxDistanceFromCenter': max_distance_from_center, 'latitude': latitude, 'longitude': longitude, 'maxDistanceFromPoint': max_distance_from_point })
    @deprecated()
    def _condition(self, station_id: str):
        '''
        Get the latest conditions at a given weather station.
        
        :station_id: 
        '''
        return self._client.call('Eclipse2017', 'condition', **{ 'stationId': station_id })
    def condition_history(self, station_id: str, limit: str):
        '''
        Get the reported conditions for a given weather station.
        
        :station_id: 
        
        :limit: Number of results to return (max is 3000)
        '''
        return self._client.call('Eclipse2017', 'conditionHistory', **{ 'stationId': station_id, 'limit': limit })
    def condition_history_range(self, station_id: str, start_time: str, end_time: str):
        '''
        Get the reported conditions during a given time for a given weather station.
        
        :station_id: 
        
        :start_time: 
        
        :end_time: 
        '''
        return self._client.call('Eclipse2017', 'conditionHistoryRange', **{ 'stationId': station_id, 'startTime': start_time, 'endTime': end_time })
    def eclipse_path(self):
        '''
        Get the path of the eclipse as a list of latitude, longitude, and time.
        '''
        return self._client.call('Eclipse2017', 'eclipsePath', **{  })
    def past_condition(self, station_id: str, time: str):
        '''
        Get historical conditions at a given weather station.
        
        :station_id: 
        
        :time: 
        '''
        return self._client.call('Eclipse2017', 'pastCondition', **{ 'stationId': station_id, 'time': time })
    def past_temperature(self, station_id: str, time: str):
        '''
        Get historical temperature for a given weather station.
        
        :station_id: 
        
        :time: 
        '''
        return self._client.call('Eclipse2017', 'pastTemperature', **{ 'stationId': station_id, 'time': time })
    def select_point_based(self):
        '''
        Get stations selected based on the points of the eclipse path.
        '''
        return self._client.call('Eclipse2017', 'selectPointBased', **{  })
    def select_section_based(self, num_sections: int, per_section: int):
        '''
        Divide the eclipse path into a number of sections and select weather stations from each section.
        
        :num_sections: Number of sections to divide the path into
        
        :per_section: Number of stations to select
        '''
        return self._client.call('Eclipse2017', 'selectSectionBased', **{ 'numSections': num_sections, 'perSection': per_section })
    def station_info(self, station_id: str):
        '''
        Get information about a given reporting station.
        
        :station_id: Reporting station ID (pws)
        '''
        return self._client.call('Eclipse2017', 'stationInfo', **{ 'stationId': station_id })
    def stations(self):
        '''
        Get a list of reporting stations IDs (pws field).
        '''
        return self._client.call('Eclipse2017', 'stations', **{  })
    def stations_info(self):
        '''
        Get information about all reporting weather stations.
        '''
        return self._client.call('Eclipse2017', 'stationsInfo', **{  })
    @deprecated()
    def _temperature(self, station_id: str):
        '''
        Get the latest temperature for a given weather station.
        
        :station_id: 
        '''
        return self._client.call('Eclipse2017', 'temperature', **{ 'stationId': station_id })
    def temperature_history(self, station_id: str, limit: str):
        '''
        Get the reported temperatures for a given weather station.
        
        :station_id: 
        
        :limit: Number of results to return (max is 3000)
        '''
        return self._client.call('Eclipse2017', 'temperatureHistory', **{ 'stationId': station_id, 'limit': limit })
    def temperature_history_range(self, station_id: str, start_time: str, end_time: str):
        '''
        Get the reported temperatures during a given time for a given weather station.
        
        :station_id: 
        
        :start_time: 
        
        :end_time: 
        '''
        return self._client.call('Eclipse2017', 'temperatureHistoryRange', **{ 'stationId': station_id, 'startTime': start_time, 'endTime': end_time })
class Execute:
    '''
    The Execute Service provides capabilities for executing blocks on the NetsBlox
    server. This is particularly useful for batching RPC requests.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def call(self, fn: Any) -> Any:
        '''
        Execute a function on the NetsBlox server.
        
        :fn: function (ringified blocks) to execute
        
        :returns: return value of fn
        '''
        return self._client.call('Execute', 'call', **{ 'fn': fn })
class Genius:
    '''
    The Genius service provides access to the Genius API, the world's
    biggest collection of song lyrics and musical knowledge.
    
    For more information, check out https://genius.com.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_artist(self, id: int) -> List[dict]:
        '''
        Get information about a given artist.
        
        :id: 
        
        :returns: 
        '''
        res = self._client.call('Genius', 'getArtist', **{ 'ID': id })
        return _common.vectorize(dict)(res)
    def get_song(self, id: int) -> List[dict]:
        '''
        Get information about a given song.
        
        :id: 
        
        :returns: 
        '''
        res = self._client.call('Genius', 'getSong', **{ 'ID': id })
        return _common.vectorize(dict)(res)
    def get_song_lyrics(self, id: int) -> str:
        '''
        Get the lyrics for a given song.
        
        :id: 
        
        :returns: 
        '''
        res = self._client.call('Genius', 'getSongLyrics', **{ 'ID': id })
        return str(res)
    def get_songs_by_artist(self, id: int) -> List[dict]:
        '''
        Get a list of songs performed by a given artist.
        
        :id: 
        
        :returns: 
        '''
        res = self._client.call('Genius', 'getSongsByArtist', **{ 'ID': id })
        return _common.vectorize(dict)(res)
    def search_songs(self, query: str) -> List[dict]:
        '''
        Search for a song.
        
        :query: 
        
        :returns: 
        '''
        res = self._client.call('Genius', 'searchSongs', **{ 'query': query })
        return _common.vectorize(dict)(res)
class Geolocation:
    '''
    The Geolocation Service provides access to the Google Places API and geocoding capabilities.
    For more information, check out https://developers.google.com/places/
    
    Terms of service: https://developers.google.com/maps/terms
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def city(self, latitude: float, longitude: float) -> str:
        '''
        Get the name of the city nearest to the given latitude and longitude.
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: city name
        '''
        res = self._client.call('Geolocation', 'city', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def country(self, latitude: float, longitude: float) -> str:
        '''
        Get the name of the country nearest to the given latitude and longitude.
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: country name
        '''
        res = self._client.call('Geolocation', 'country', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def country_code(self, latitude: float, longitude: float) -> str:
        '''
        Get the code for the country nearest to the given latitude and longitude.
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: country code
        '''
        res = self._client.call('Geolocation', 'countryCode', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def county(self, latitude: float, longitude: float) -> str:
        '''
        Get the name of the county (or closest equivalent) nearest to the given latitude and longitude.
        If the country does not have counties, it will return the corresponding division for administrative level 2.
        
        For more information on administrative divisions, check out https://en.wikipedia.org/wiki/List_of_administrative_divisions_by_country
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: county name
        '''
        res = self._client.call('Geolocation', 'county*', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def geolocate(self, address: str) -> dict:
        '''
        Geolocates the address and returns the coordinates
        
        :address: target address
        
        :returns: structured data representing the location of the address
        '''
        res = self._client.call('Geolocation', 'geolocate', **{ 'address': address })
        return dict(res)
    def info(self, latitude: float, longitude: float) -> list:
        '''
        Get administrative division information for the given latitude and longitude.
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: list of administrative level names
        '''
        return self._client.call('Geolocation', 'info', **{ 'latitude': latitude, 'longitude': longitude })
    def nearby_search(self, latitude: float, longitude: float, keyword: Optional[str] = None, radius: Optional[float] = None) -> List[dict]:
        '''
        Find places near an earth coordinate (latitude, longitude) (maximum of 10 results)
        
        :latitude: 
        
        :longitude: 
        
        :keyword: the keyword you want to search for, like pizza or cinema.
        
        :radius: search radius in meters (default 50km)
        
        :returns: list of nearby locations
        '''
        res = self._client.call('Geolocation', 'nearbySearch', **{ 'latitude': latitude, 'longitude': longitude, 'keyword': keyword, 'radius': radius })
        return _common.vectorize(dict)(res)
    def state(self, latitude: float, longitude: float) -> str:
        '''
        Get the name of the state (or closest equivalent) nearest to the given latitude and longitude.
        If the country does not have states, it will return the corresponding division for administrative level 1.
        
        For more information on administrative divisions, check out https://en.wikipedia.org/wiki/List_of_administrative_divisions_by_country
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: state name
        '''
        res = self._client.call('Geolocation', 'state*', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def state_code(self, latitude: float, longitude: float) -> str:
        '''
        Get the code for the state (or closest equivalent) nearest to the given latitude and longitude.
        If the country does not have states, it will return the corresponding division for administrative level 1.
        
        For more information on administrative divisions, check out https://en.wikipedia.org/wiki/List_of_administrative_divisions_by_country
        
        :latitude: latitude of the target location
        
        :longitude: longitude of the target location
        
        :returns: state code
        '''
        res = self._client.call('Geolocation', 'stateCode*', **{ 'latitude': latitude, 'longitude': longitude })
        return str(res)
    def street_address(self, address: str) -> str:
        '''
        Get the street address of a given target location.
        
        :address: the address string to look up
        
        :returns: the target street address
        '''
        res = self._client.call('Geolocation', 'streetAddress', **{ 'address': address })
        return str(res)
    def timezone(self, address: Any) -> dict:
        '''
        Get information about the timezone of the provided address or location.
        You can provide either a list of two values representing the latitude and longitude location, or a string address to look up.
        
        :address: target location - either a list representing [latitude, longitude], or an address string
        
        :returns: information about the target's timezone
        '''
        res = self._client.call('Geolocation', 'timezone', **{ 'address': address })
        return dict(res)
class GlobalBiodiversity:
    '''
    The GlobalBiodiversity service provides information on millions of species from around the globe.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_children(self, id: int, page: Optional[int] = None) -> List[dict]:
        '''
        Get the taxonomical children of a node/entry in the tree of life.
        
        Because a node may have many children, only up to 20 children are returned per call to this RPC.
        You can check if there are more children by increasing the page number of children to return.
        When there are no more children, an empty list is returned.
        
        :id: id of the taxonomy entry to get the children of
        
        :page: page number of results to return (default 1)
        
        :returns: taxonomical children of the entry
        '''
        res = self._client.call('GlobalBiodiversity', 'getChildren', **{ 'id': id, 'page': page })
        return _common.vectorize(dict)(res)
    def get_image(self, url: str) -> Image.Image:
        '''
        Get an image from an image URL returned by GlobalBiodiversity.getImageURLs.
        
        :url: URL of the image to load
        
        :returns: the downloaded image
        '''
        return self._client.call('GlobalBiodiversity', 'getImage', **{ 'url': url })
    def get_media_urls(self, id: int, type: Optional[str] = None, page: Optional[int] = None) -> List[str]:
        '''
        Get the URL of any media associated with a particular taxonomy node/entry in the tree of life.
        These URLs can then be passed to GlobalBiodiversity.getImage or GlobalBiodiversity.getSound to get the image/sound.
        
        Because there may be many associated media entries, only up to 20 entries are returned per call to this RPC (though each entry may have multiple URLs).
        You can check if there are more URLs by increasing the page number of results to return.
        When there are no more URLs, an empty list is returned.
        
        :id: id of the taxonomy node to get media from
        
        :type: the type of media to return
        
        :page: page number of results to return (default 1)
        
        :returns: zero or more associated media URLs
        '''
        res = self._client.call('GlobalBiodiversity', 'getMediaURLs', **{ 'id': id, 'type': type, 'page': page })
        return _common.vectorize(str)(res)
    def get_parent(self, id: int) -> dict:
        '''
        Get the taxonomical parent of a node/entry in the tree of life.
        
        :id: id of the taxonomy entry to get the parent of
        
        :returns: taxonomical parent of the entry
        '''
        res = self._client.call('GlobalBiodiversity', 'getParent', **{ 'id': id })
        return dict(res)
    def get_sound(self, url: str) -> Any:
        '''
        Get a sound from a sound URL returned by GlobalBiodiversity.getMediaURLs.
        
        :url: URL of the sound to load
        
        :returns: the downloaded sound
        '''
        return self._client.call('GlobalBiodiversity', 'getSound', **{ 'url': url })
    def search_species(self, name_type: str, name: str, page: Optional[int] = None) -> List[dict]:
        '''
        Search the database for species of the given common or scientific name.
        
        Because there may be many matches, only up to 20 search results are returned per call to this RPC.
        You can check if there are more matches by increasing the page number of results to return.
        When there are no more results, an empty list is returned.
        
        :name_type: the type of name to search for
        
        :name: name of the species to search for
        
        :page: page number of results to return (default 1)
        
        :returns: 
        '''
        res = self._client.call('GlobalBiodiversity', 'searchSpecies', **{ 'nameType': name_type, 'name': name, 'page': page })
        return _common.vectorize(dict)(res)
class GoogleMaps:
    '''
    The GoogleMaps Service provides access to the Google Maps API along with helper functions for interacting with the maps (such as converting coordinates).
    For more information, check out https://developers.google.com/maps/documentation/static-maps/intro
    
    Terms of use: https://developers.google.com/maps/terms
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_distance(self, start_latitude: float, start_longitude: float, end_latitude: float, end_longitude: float) -> float:
        '''
        Get the straight line distance between two points in meters.
        
        :start_latitude: Latitude of start point
        
        :start_longitude: Longitude of start point
        
        :end_latitude: Latitude of end point
        
        :end_longitude: Longitude of end point
        
        :returns: Distance in meters
        '''
        res = self._client.call('GoogleMaps', 'getDistance', **{ 'startLatitude': start_latitude, 'startLongitude': start_longitude, 'endLatitude': end_latitude, 'endLongitude': end_longitude })
        return float(res)
    def get_earth_coordinates(self, x: float, y: float) -> list:
        '''
        Get the earth coordinates [latitude, longitude] of a given point in the last requested map image [x, y].
        
        :x: x position of the point
        
        :y: y position of the point
        
        :returns: A list containing the latitude and longitude of the given point.
        '''
        return self._client.call('GoogleMaps', 'getEarthCoordinates', **{ 'x': x, 'y': y })
    def get_image_coordinates(self, latitude: float, longitude: float) -> list:
        '''
        Get the image coordinates [x, y] of a given location on the earth [latitude, longitude].
        
        :latitude: latitude of the point
        
        :longitude: longitude of the point
        
        :returns: A list containing the [x, y] position of the given point.
        '''
        return self._client.call('GoogleMaps', 'getImageCoordinates', **{ 'latitude': latitude, 'longitude': longitude })
    @deprecated()
    def _get_latitude(self, y: float) -> float:
        '''
        Convert y value of map image to latitude.
        
        :y: y value of map image
        
        :returns: Latitude of the y value from the image
        '''
        res = self._client.call('GoogleMaps', 'getLatitude', **{ 'y': y })
        return float(res)
    def get_latitude_from_y(self, y: float) -> float:
        '''
        Convert y value of map image to latitude.
        
        :y: y value of map image
        
        :returns: Latitude of the y value from the image
        '''
        res = self._client.call('GoogleMaps', 'getLatitudeFromY', **{ 'y': y })
        return float(res)
    @deprecated()
    def _get_longitude(self, x: float) -> float:
        '''
        Convert x value of map image to longitude.
        
        :x: x value of map image
        
        :returns: Longitude of the x value from the image
        '''
        res = self._client.call('GoogleMaps', 'getLongitude', **{ 'x': x })
        return float(res)
    def get_longitude_from_x(self, x: float) -> float:
        '''
        Convert x value of map image to longitude.
        
        :x: x value of map image
        
        :returns: Longitude of the x value from the image
        '''
        res = self._client.call('GoogleMaps', 'getLongitudeFromX', **{ 'x': x })
        return float(res)
    def get_map(self, latitude: float, longitude: float, width: int, height: int, zoom: int) -> Image.Image:
        '''
        Get a map image of the given region.
        
        :latitude: Latitude of center point
        
        :longitude: Longitude of center point
        
        :width: Image width
        
        :height: Image height
        
        :zoom: Zoom level of map image
        
        :returns: Map image
        '''
        return self._client.call('GoogleMaps', 'getMap', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'zoom': zoom })
    def get_satellite_map(self, latitude: float, longitude: float, width: int, height: int, zoom: int) -> Image.Image:
        '''
        Get a satellite map image of the given region.
        
        :latitude: Latitude of center point
        
        :longitude: Longitude of center point
        
        :width: Image width
        
        :height: Image height
        
        :zoom: Zoom level of map image
        
        :returns: Map image
        '''
        return self._client.call('GoogleMaps', 'getSatelliteMap', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'zoom': zoom })
    def get_terrain_map(self, latitude: float, longitude: float, width: int, height: int, zoom: int) -> Image.Image:
        '''
        Get a terrain map image of the given region.
        
        :latitude: Latitude of center point
        
        :longitude: Longitude of center point
        
        :width: Image width
        
        :height: Image height
        
        :zoom: Zoom level of map image
        
        :returns: Map image
        '''
        return self._client.call('GoogleMaps', 'getTerrainMap', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'zoom': zoom })
    def get_x_from_longitude(self, longitude: float) -> float:
        '''
        Convert longitude to the x value on the map image.
        
        :longitude: Longitude coordinate
        
        :returns: Map x coordinate of the given longitude
        '''
        res = self._client.call('GoogleMaps', 'getXFromLongitude', **{ 'longitude': longitude })
        return float(res)
    def get_y_from_latitude(self, latitude: float) -> float:
        '''
        Convert latitude to the y value on the map image.
        
        :latitude: Latitude coordinate
        
        :returns: Map y coordinate of the given latitude
        '''
        res = self._client.call('GoogleMaps', 'getYFromLatitude', **{ 'latitude': latitude })
        return float(res)
    def max_latitude(self) -> float:
        '''
        Get the maximum latitude of the current map.
        
        :returns: 
        '''
        res = self._client.call('GoogleMaps', 'maxLatitude', **{  })
        return float(res)
    def max_longitude(self) -> float:
        '''
        Get the maximum longitude of the current map.
        
        :returns: 
        '''
        res = self._client.call('GoogleMaps', 'maxLongitude', **{  })
        return float(res)
    def min_latitude(self) -> float:
        '''
        Get the minimum latitude of the current map.
        
        :returns: 
        '''
        res = self._client.call('GoogleMaps', 'minLatitude', **{  })
        return float(res)
    def min_longitude(self) -> float:
        '''
        Get the minimum longitude of the current map.
        
        :returns: 
        '''
        res = self._client.call('GoogleMaps', 'minLongitude', **{  })
        return float(res)
class GoogleStreetView:
    '''
    The GoogleStreetView Service provides access to the Google Street View Image API
    For more information, check out https://developers.google.com/maps/documentation/streetview/intro
    
    Terms of use: https://developers.google.com/maps/terms
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_info(self, latitude: float, longitude: float, fieldofview: float, heading: float, pitch: float) -> dict:
        '''
        Get Street View metadata of a location using coordinates.
        
        Status explanation:
        
        - OK - No errors occurred.
        - ZERO_RESULTS - No image could be found near the provided location.
        - NOT_FOUND - The location provided could not be found.
        
        :latitude: Latitude coordinate of location
        
        :longitude: Longitude coordinate of location
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: Metadata information about the requested Street View.
        '''
        res = self._client.call('GoogleStreetView', 'getInfo', **{ 'latitude': latitude, 'longitude': longitude, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
        return dict(res)
    def get_info_from_address(self, location: str, fieldofview: float, heading: float, pitch: float) -> dict:
        '''
        Get Street View metadata of a location using a location query.
        
        Status explanation:
        
        - OK - No errors occurred.
        - ZERO_RESULTS - No image could be found near the provided location.
        - NOT_FOUND - The location provided could not be found.
        
        :location: Address or Name of location
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: Metadata information about the requested Street View.
        '''
        res = self._client.call('GoogleStreetView', 'getInfoFromAddress', **{ 'location': location, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
        return dict(res)
    def get_view(self, latitude: float, longitude: float, width: float, height: float, fieldofview: float, heading: float, pitch: float) -> Image.Image:
        '''
        Get Street View image of a location using coordinates
        
        :latitude: Latitude coordinate of location
        
        :longitude: Longitude coordinate of location
        
        :width: Width of image
        
        :height: Height of image
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: Image of requested location with specified size and orientation
        '''
        return self._client.call('GoogleStreetView', 'getView', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
    def get_view_from_address(self, location: str, width: float, height: float, fieldofview: float, heading: float, pitch: float) -> Image.Image:
        '''
        Get Street View image of a location from a location string
        
        :location: Address or Name of location
        
        :width: Width of image
        
        :height: Height of image
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: Image of requested location with specified size and orientation
        '''
        return self._client.call('GoogleStreetView', 'getViewFromAddress', **{ 'location': location, 'width': width, 'height': height, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
    @deprecated()
    def _get_view_from_lat_long(self, latitude: float, longitude: float, width: float, height: float, fieldofview: float, heading: float, pitch: float) -> Image.Image:
        '''
        Get Street View image of a location using coordinates
        
        :latitude: Latitude coordinate of location
        
        :longitude: Longitude coordinate of location
        
        :width: Width of image
        
        :height: Height of image
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: Image of requested location with specified size and orientation
        '''
        return self._client.call('GoogleStreetView', 'getViewFromLatLong', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
    def is_available(self, latitude: float, longitude: float, fieldofview: float, heading: float, pitch: float) -> bool:
        '''
        Check for availability of imagery at a location using coordinates
        
        :latitude: Latitude coordinate of location
        
        :longitude: Longitude coordinate of location
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: true if imagery is available
        '''
        res = self._client.call('GoogleStreetView', 'isAvailable', **{ 'latitude': latitude, 'longitude': longitude, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
        return bool(res)
    def is_available_from_address(self, location: str, fieldofview: float, heading: float, pitch: float) -> bool:
        '''
        Check for availability of imagery at a location using an address
        
        :location: Address or Name of location
        
        :fieldofview: Field of View of image, maximum of 120
        
        :heading: Heading of view
        
        :pitch: Pitch of view, 90 to point up, -90 to point down
        
        :returns: true if imagery is available
        '''
        res = self._client.call('GoogleStreetView', 'isAvailableFromAddress', **{ 'location': location, 'fieldofview': fieldofview, 'heading': heading, 'pitch': pitch })
        return bool(res)
class Hangman:
    '''
    The Hangman Service provides helpers for mediating a distributed game of hangman.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_currently_known_word(self) -> str:
        '''
        Get current word for the game
        
        :returns: Current word in use
        '''
        res = self._client.call('Hangman', 'getCurrentlyKnownWord', **{  })
        return str(res)
    def get_wrong_count(self) -> int:
        '''
        Get number of wrong guesses made
        
        :returns: Number of wrong guesses
        '''
        res = self._client.call('Hangman', 'getWrongCount', **{  })
        return int(res)
    def guess(self, letter: str):
        '''
        Make a guess in the game
        
        :letter: Letter to guess
        '''
        return self._client.call('Hangman', 'guess', **{ 'letter': letter })
    def is_word_guessed(self) -> bool:
        '''
        Get if word has been guessed
        
        :returns: State of word
        '''
        res = self._client.call('Hangman', 'isWordGuessed', **{  })
        return bool(res)
    def set_word(self, word: str):
        '''
        Set current word for the game
        
        :word: New word to use
        '''
        return self._client.call('Hangman', 'setWord', **{ 'word': word })
class HistoricalTemperature:
    '''
    Access to Berkeley Earth data.
    See http://berkeleyearth.org/data/ for additional details.
    
    These RPCs take a region argument, which can either be a country
    or one of the following special values:
    
    - all land - get data for all landmasses around the world
    - global - get data for the entire Earth (including oceans)
    - northern hemisphere - only northern landmasses
    - southern hemisphere - only southern landmasses
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def annual_anomaly(self, region: str) -> List[list]:
        '''
        Get the 12 month averaged anomaly data for a region
        
        :region: Name of region/country
        
        :returns: Monthly data points
        '''
        return self._client.call('HistoricalTemperature', 'annualAnomaly', **{ 'region': region })
    def five_year_anomaly(self, region: str) -> List[list]:
        '''
        Get the 5-year averaged anomaly data for a region
        
        :region: Name of region/country
        
        :returns: Monthly data points
        '''
        return self._client.call('HistoricalTemperature', 'fiveYearAnomaly', **{ 'region': region })
    def monthly_anomaly(self, region: str) -> List[list]:
        '''
        Get the monthly anomaly data for a region
        
        :region: Name of region/country
        
        :returns: Monthly data points
        '''
        return self._client.call('HistoricalTemperature', 'monthlyAnomaly', **{ 'region': region })
    def ten_year_anomaly(self, region: str) -> List[list]:
        '''
        Get the 10-year averaged anomaly data for a region
        
        :region: Name of region/country
        
        :returns: Monthly data points
        '''
        return self._client.call('HistoricalTemperature', 'tenYearAnomaly', **{ 'region': region })
    def twenty_year_anomaly(self, region: str) -> List[list]:
        '''
        Get the 20-year averaged anomaly data for a region
        
        :region: Name of region/country
        
        :returns: Monthly data points
        '''
        return self._client.call('HistoricalTemperature', 'twentyYearAnomaly', **{ 'region': region })
class HumanMortalityDatabase:
    '''
    This service accesses data from the human mortality database which tabulates
    death rates broken down by age group and gender for various countries.
    
    For more information, see https://www.mortality.org/.
    
    Note: for countries that don't report separate male and female death counts,
    the gender breakdowns are just the total multiplied by a rough estimate
    of the percent of people in that country who are male/female.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_all_data(self) -> list:
        '''
        Get all the mortality data. This is potentially a lot of data.
        Only use this if you truly need access to all data.
        
        This is returned as structured data organized by country, then by date (mm/dd/yyyy), then by gender, then by category.
        
        :returns: all available data
        '''
        return self._client.call('HumanMortalityDatabase', 'getAllData', **{  })
    def get_all_data_for_country(self, country: str) -> list:
        '''
        Get all the data associated with the given country.
        This is an object organized by year, then by week, then broken down by gender.
        
        :country: Name of the country to look up
        
        :returns: the requested data
        '''
        return self._client.call('HumanMortalityDatabase', 'getAllDataForCountry', **{ 'country': country })
    def get_categories(self) -> list:
        '''
        Get a list of all the categories represented in the data.
        These can be used in a query.
        
        :returns: the requested data
        '''
        return self._client.call('HumanMortalityDatabase', 'getCategories', **{  })
    def get_countries(self) -> list:
        '''
        Get a list of all the countries represented in the data.
        These are not the country names, but a unique identifier for them.
        
        :returns: the requested data
        '''
        return self._client.call('HumanMortalityDatabase', 'getCountries', **{  })
    def get_genders(self) -> list:
        '''
        Get a list of all the valid genders represented in the data.
        These can be used in a query.
        
        :returns: the requested data
        '''
        return self._client.call('HumanMortalityDatabase', 'getGenders', **{  })
    def get_time_series(self, country: str, gender: Optional[str] = None, category: Optional[str] = None) -> list:
        '''
        Get the time series data for the given country, filtered to the specified gender and category
        in month/day/year format.
        
        :country: name of the country to look up
        
        :gender: gender group for filtering. Defaults to both.
        
        :category: category for filtering. Defaults to deaths total.
        
        :returns: the requested data
        '''
        return self._client.call('HumanMortalityDatabase', 'getTimeSeries', **{ 'country': country, 'gender': gender, 'category': category })
class HurricaneData:
    '''
    The HurricaneData service provides access to the revised Atlantic hurricane
    database (HURDAT2) from the National Hurricane Center (NHC).
    
    For more information, check out https://www.aoml.noaa.gov/hrd/data_sub/re_anal.html
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_hurricane_data(self, name: str, year: int) -> List[dict]:
        '''
        Get hurricane data including location, maximum winds, and central pressure.
        
        :name: name of the hurricane
        
        :year: year that the hurricane occurred in
        
        :returns: All recorded data for the given hurricane
        '''
        res = self._client.call('HurricaneData', 'getHurricaneData', **{ 'name': name, 'year': year })
        return _common.vectorize(dict)(res)
    def get_hurricanes_in_year(self, year: int) -> List[str]:
        '''
        Get the names of all hurricanes occurring in the given year.
        
        :year: 
        
        :returns: names
        '''
        res = self._client.call('HurricaneData', 'getHurricanesInYear', **{ 'year': year })
        return _common.vectorize(str)(res)
    def get_years_with_hurricane_named(self, name: str) -> List[int]:
        '''
        Get the years in which a hurricane with the given name occurred.
        
        :name: name of the hurricane to find the year(s) of
        
        :returns: years - list with all of the years that a particular name has been used for a hurricane
        '''
        res = self._client.call('HurricaneData', 'getYearsWithHurricaneNamed', **{ 'name': name })
        return _common.vectorize(int)(res)
class IceCoreData:
    '''
    Access to NOAA Paleoclimatology ice core data.
    
    For more information, check out
    https://www.ncdc.noaa.gov/data-access/paleoclimatology-data/datasets/ice-core.
    
    Original datasets are available at:
    
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2composite.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2law.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/antarctica2015co2wais.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/co2nat.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/deutnat.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/epica_domec/edc3deuttemp2007.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/greenland/summit/grip/isotopes/gripd18o.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/vostok/gt4nat.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/law/law2012d18o.txt
    - https://www1.ncdc.noaa.gov/pub/data/paleo/icecore/antarctica/wdc05a2013d18o.txt
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_carbon_dioxide_data(self, core: str, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get CO2 in ppm (parts per million) by year from the ice core.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :core: Core to get data from
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: the requested data
        '''
        return self._client.call('IceCoreData', 'getCarbonDioxideData', **{ 'core': core, 'startyear': startyear, 'endyear': endyear })
    def get_data_availability(self) -> List[list]:
        '''
        Get a table showing the amount of available data for each ice core.
        
        :returns: data availability table
        '''
        return self._client.call('IceCoreData', 'getDataAvailability', **{  })
    def get_delta18o_data(self, core: str, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get delta-O-18 in per mil (parts per thousand) by year from the ice core.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :core: Ice core to get data from
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: the requested data
        '''
        return self._client.call('IceCoreData', 'getDelta18OData', **{ 'core': core, 'startyear': startyear, 'endyear': endyear })
    def get_deuterium_data(self, core: str, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get deuterium in per mil (parts per thousand) by year from the ice core.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :core: Ice core to get data from
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: the requested data
        '''
        return self._client.call('IceCoreData', 'getDeuteriumData', **{ 'core': core, 'startyear': startyear, 'endyear': endyear })
    def get_ice_core_metadata(self, core: str) -> dict:
        '''
        Get metadata about an ice core including statistics about the available data.
        
        :core: Name of core to get metadata of
        
        :returns: ice core metadata
        '''
        res = self._client.call('IceCoreData', 'getIceCoreMetadata', **{ 'core': core })
        return dict(res)
    def get_ice_core_names(self) -> List[str]:
        '''
        Get names of ice cores with data available.
        
        :returns: list of ice core names
        '''
        res = self._client.call('IceCoreData', 'getIceCoreNames', **{  })
        return _common.vectorize(str)(res)
    def get_temperature_data(self, core: str, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get temperature difference in Celsius by year from the ice core.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :core: Ice core to get data from
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: the requested data
        '''
        return self._client.call('IceCoreData', 'getTemperatureData', **{ 'core': core, 'startyear': startyear, 'endyear': endyear })
class IoTScape:
    '''
    The IoTScape Service enables remote devices to provide custom services. Custom
    Services can be found under the "Community/Devices" section using the call <RPC>
    block.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_devices(self, service: str):
        '''
        List IDs of devices associated for a service
        
        :service: Name of service to get device IDs for
        '''
        return self._client.call('IoTScape', 'getDevices', **{ 'service': service })
    def get_message_types(self, service: str):
        '''
        List the message types associated with a service
        
        :service: Name of service to get events for
        '''
        return self._client.call('IoTScape', 'getMessageTypes', **{ 'service': service })
    def get_methods(self, service: str):
        '''
        List the methods associated with a service
        
        :service: Name of service to get methods for
        '''
        return self._client.call('IoTScape', 'getMethods', **{ 'service': service })
    def get_services(self):
        '''
        List all IoTScape services registered with the server
        '''
        return self._client.call('IoTScape', 'getServices', **{  })
    def send(self, service: str, id: str, command: str):
        '''
        Make a call to a device as a text command
        
        :service: Name of service to make call to
        
        :id: ID of device to make call to
        
        :command: Input to RPC
        '''
        return self._client.call('IoTScape', 'send', **{ 'service': service, 'id': id, 'command': command })
class KeyValueStore:
    '''
    The KeyValueStore Service provides basic storage functionality using a hierarchical
    key-value storage (similar to CloudVariables).
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def child(self, key: str, password: Optional[str] = None) -> List[str]:
        '''
        Get the IDs of the child keys.
        
        :key: 
        
        :password: Password (if password-protected)
        
        :returns: list of child key ids
        '''
        res = self._client.call('KeyValueStore', 'child', **{ 'key': key, 'password': password })
        return _common.vectorize(str)(res)
    def delete(self, key: str, password: Optional[str] = None):
        '''
        Delete the stored value for a key.
        
        :key: Key to remove from store
        
        :password: Password (if password-protected)
        '''
        return self._client.call('KeyValueStore', 'delete', **{ 'key': key, 'password': password })
    def get(self, key: str, password: Optional[str] = None) -> Any:
        '''
        Get the stored value for a key.
        
        :key: Fetch value for the given key
        
        :password: Password (if password-protected)
        
        :returns: the stored value
        '''
        return self._client.call('KeyValueStore', 'get', **{ 'key': key, 'password': password })
    def parent(self, key: str) -> str:
        '''
        Get the ID of the parent key.
        
        :key: key to get the parent of
        
        :returns: the parent key
        '''
        res = self._client.call('KeyValueStore', 'parent', **{ 'key': key })
        return str(res)
    def put(self, key: str, value: Any, password: Optional[str] = None):
        '''
        Set the stored value for a key.
        
        :key: Key to use for retrieving the variable
        
        :value: Value to associated with key
        
        :password: Password (if password-protected)
        '''
        return self._client.call('KeyValueStore', 'put', **{ 'key': key, 'value': value, 'password': password })
class MaunaLoaCO2Data:
    '''
    Access to NOAA Earth System Research Laboratory data collected from Mauna Loa, Hawaii.
    
    See https://www.esrl.noaa.gov/gmd/ccgg/trends/ for additional details.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_co2_trend(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get the mole fraction of CO2 (in parts per million) by year with the seasonal
        cycle removed.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: 
        '''
        return self._client.call('MaunaLoaCO2Data', 'getCO2Trend', **{ 'startyear': startyear, 'endyear': endyear })
    def get_raw_co2(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get the mole fraction of CO2 (in parts per million) by year. Missing measurements
        are interpolated.
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: last year of data to include
        
        :returns: 
        '''
        return self._client.call('MaunaLoaCO2Data', 'getRawCO2', **{ 'startyear': startyear, 'endyear': endyear })
class MetMuseum:
    '''
    Access the Metropolitan Museum of Art's collection.
    For explanation on the different attributes for each object,
    visit https://metmuseum.github.io.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def advanced_search(self, field: str, query: str, skip: Optional[float] = None, limit: Optional[float] = None) -> list:
        '''
        Search the Metropolitan Museum of Art
        
        :field: field to search in
        
        :query: text query to look for
        
        :skip: used to paginate the results, number of records to skip from the beginning
        
        :limit: limit the number of returned results (maximum of 50)
        
        :returns: results
        '''
        return self._client.call('MetMuseum', 'advancedSearch', **{ 'field': field, 'query': query, 'skip': skip, 'limit': limit })
    def fields(self) -> list:
        '''
        Get a list of available attributes for museum's objects
        
        :returns: available headers
        '''
        return self._client.call('MetMuseum', 'fields', **{  })
    def get_image_urls(self, id: float) -> list:
        '''
        Retrieves the image links for a public domain object
        Note: use costume loader library to load the images.
        
        :id: object id
        
        :returns: List of images
        '''
        return self._client.call('MetMuseum', 'getImageUrls', **{ 'id': id })
    def get_info(self, id: float) -> list:
        '''
        Retrieves extended information about a single object
        
        :id: object id
        
        :returns: List of images
        '''
        return self._client.call('MetMuseum', 'getInfo', **{ 'id': id })
    def search_by_artist_display_bio(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByArtistDisplayBio', **{ 'query': query })
    def search_by_artist_display_name(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByArtistDisplayName', **{ 'query': query })
    def search_by_classification(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByClassification', **{ 'query': query })
    def search_by_country(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByCountry', **{ 'query': query })
    def search_by_credit_line(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByCreditLine', **{ 'query': query })
    def search_by_department(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByDepartment', **{ 'query': query })
    def search_by_dimensions(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByDimensions', **{ 'query': query })
    def search_by_is_highlight(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByIsHighlight', **{ 'query': query })
    def search_by_medium(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByMedium', **{ 'query': query })
    def search_by_object_date(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByObjectDate', **{ 'query': query })
    def search_by_object_name(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByObjectName', **{ 'query': query })
    def search_by_repository(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByRepository', **{ 'query': query })
    def search_by_title(self, query: Any):
        '''
        :query: 
        '''
        return self._client.call('MetMuseum', 'searchByTitle', **{ 'query': query })
class MidiData:
    '''
    This service allows users to access midi files of different songs.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def find_song(self, composer: Optional[str] = None, style: Optional[str] = None, search: Optional[str] = None) -> list:
        '''
        Get songs based on query.
        
        :composer: 
        
        :style: 
        
        :search: 
        
        :returns: 
        '''
        return self._client.call('MidiData', 'findSong', **{ 'composer': composer, 'style': style, 'search': search })
    def get_song_data(self, name_of_song: Optional[str] = None):
        '''
        Get a song by name
        
        :name_of_song: 
        '''
        return self._client.call('MidiData', 'getSongData', **{ 'nameOfSong': name_of_song })
class Movebank:
    '''
    Access to Movebank, a free, online database of animal tracking data hosted by the Max Planck Institute of Animal Behavior.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_animals(self, study: dict) -> List[dict]:
        '''
        Get a list of all the animals that participated in a specific study.
        
        :study: A study object returned by Movebank.getStudies
        
        :returns: A list of animals
        '''
        res = self._client.call('Movebank', 'getAnimals', **{ 'study': study })
        return _common.vectorize(dict)(res)
    def get_events(self, study: dict, animal: dict, min_distance: Optional[float] = None) -> List[dict]:
        '''
        Get a chronological list of all the migration events for an animal in a specific study.
        
        :study: A study object returned by Movebank.getStudies
        
        :animal: An animal object returned by Movebank.getAnimals. The animal should be part of the same study.
        
        :min_distance: The minimum distance (in meters) between consecutive returned events (default 0, which gives all available data).
        
        :returns: A list of chronological migration events for the animal
        '''
        res = self._client.call('Movebank', 'getEvents', **{ 'study': study, 'animal': animal, 'minDistance': min_distance })
        return _common.vectorize(dict)(res)
    def get_sensor_types(self) -> List[str]:
        '''
        Get a list of all the sensor types supported by Movebank.
        
        :returns: A list of supported sensor types
        '''
        res = self._client.call('Movebank', 'getSensorTypes', **{  })
        return _common.vectorize(str)(res)
    def get_studies(self) -> List[dict]:
        '''
        Get a list of all the studies available for (public) viewing.
        
        :returns: A list of available studies
        '''
        res = self._client.call('Movebank', 'getStudies', **{  })
        return _common.vectorize(dict)(res)
    def get_studies_near(self, latitude: float, longitude: float, distance: float) -> List[dict]:
        '''
        Get a list of all the studies available for (public) viewing within a certain max distance of a point of interest.
        Note that some of the animals involved in these studies may travel outside of this distance.
        
        :latitude: Latitude of the point of interest
        
        :longitude: Longitude of the point of interest
        
        :distance: Max distance from the point of interest (in meters)
        
        :returns: A list of available studies near the point of interest
        '''
        res = self._client.call('Movebank', 'getStudiesNear', **{ 'latitude': latitude, 'longitude': longitude, 'distance': distance })
        return _common.vectorize(dict)(res)
class MovieDB:
    '''
    The MovieDB Service provides access to movie data using TMDB (The MovieDB API).
    For more information, check out https://www.themoviedb.org/
    
    Terms of use: https://www.themoviedb.org/documentation/api/terms-of-use
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_image(self, path: str) -> Image.Image:
        '''
        Get an image from a path.
        
        :path: location of the image
        
        :returns: the requested image
        '''
        return self._client.call('MovieDB', 'getImage', **{ 'path': path })
    def movie_backdrop_path(self, id: str) -> str:
        '''
        Get the image path for a given movie backdrop.
        
        :id: Movie ID
        
        :returns: the image path
        '''
        res = self._client.call('MovieDB', 'movieBackdropPath', **{ 'id': id })
        return str(res)
    def movie_budget(self, id: str):
        '''
        Get the budget for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieBudget', **{ 'id': id })
    def movie_cast_characters(self, id: str):
        '''
        Get the cast characters for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCastCharacters', **{ 'id': id })
    def movie_cast_names(self, id: str):
        '''
        Get the cast names for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCastNames', **{ 'id': id })
    def movie_cast_person_ids(self, id: str):
        '''
        Get the cast IDs for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCastPersonIDs', **{ 'id': id })
    def movie_cast_profile_paths(self, id: str):
        '''
        Get the cast profile paths for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCastProfilePaths', **{ 'id': id })
    def movie_crew_jobs(self, id: str):
        '''
        Get the crew jobs for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCrewJobs', **{ 'id': id })
    def movie_crew_names(self, id: str):
        '''
        Get the crew names for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCrewNames', **{ 'id': id })
    def movie_crew_person_ids(self, id: str):
        '''
        Get the crew IDs for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCrewPersonIDs', **{ 'id': id })
    def movie_crew_profile_paths(self, id: str):
        '''
        Get the crew profile paths for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieCrewProfilePaths', **{ 'id': id })
    def movie_genres(self, id: str):
        '''
        Get the genres of a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieGenres', **{ 'id': id })
    def movie_original_language(self, id: str):
        '''
        Get the original language of a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieOriginalLanguage', **{ 'id': id })
    def movie_original_title(self, id: str):
        '''
        Get the original title of a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieOriginalTitle', **{ 'id': id })
    def movie_overview(self, id: str):
        '''
        Get an overview for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieOverview', **{ 'id': id })
    def movie_popularity(self, id: str):
        '''
        Get the popularity for a given movie.
        
        For more information, check out https://developers.themoviedb.org/3/getting-started/popularity
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'moviePopularity', **{ 'id': id })
    def movie_poster_path(self, id: str):
        '''
        Get the poster path for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'moviePosterPath', **{ 'id': id })
    def movie_production_companies(self, id: str):
        '''
        Get the production companies for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieProductionCompanies', **{ 'id': id })
    def movie_production_countries(self, id: str):
        '''
        Get the countries in which a given movie was produced.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieProductionCountries', **{ 'id': id })
    def movie_release_date(self, id: str):
        '''
        Get the release data for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieReleaseDate', **{ 'id': id })
    def movie_revenue(self, id: str):
        '''
        Get the revenue for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieRevenue', **{ 'id': id })
    def movie_runtime(self, id: str):
        '''
        Get the runtime for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieRuntime', **{ 'id': id })
    def movie_spoken_languages(self, id: str):
        '''
        Get the spoken languages for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieSpokenLanguages', **{ 'id': id })
    def movie_tagline(self, id: str):
        '''
        Get the tagline for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieTagline', **{ 'id': id })
    def movie_title(self, id: str):
        '''
        Get the title for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieTitle', **{ 'id': id })
    def movie_vote_average(self, id: str):
        '''
        Get the average vote for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieVoteAverage', **{ 'id': id })
    def movie_vote_count(self, id: str):
        '''
        Get the vote count for a given movie.
        
        :id: Movie ID
        '''
        return self._client.call('MovieDB', 'movieVoteCount', **{ 'id': id })
    def person_biography(self, id: str):
        '''
        Get the biography for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personBiography', **{ 'id': id })
    def person_birthday(self, id: str):
        '''
        Get the birthday of a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personBirthday', **{ 'id': id })
    def person_cast_characters(self, id: str):
        '''
        Get the characters played by a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastCharacters', **{ 'id': id })
    def person_cast_movie_ids(self, id: str):
        '''
        Get the movies in which a given person was cast.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastMovieIDs', **{ 'id': id })
    def person_cast_original_titles(self, id: str):
        '''
        Get the original titles in which a given person was cast.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastOriginalTitles', **{ 'id': id })
    def person_cast_poster_paths(self, id: str):
        '''
        Get the cast poster paths for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastPosterPaths', **{ 'id': id })
    def person_cast_release_dates(self, id: str):
        '''
        Get the cast release dates for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastReleaseDates', **{ 'id': id })
    def person_cast_titles(self, id: str):
        '''
        Get the cast titles for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCastTitles', **{ 'id': id })
    def person_crew_jobs(self, id: str):
        '''
        Get the crew jobs for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewJobs', **{ 'id': id })
    def person_crew_movie_ids(self, id: str):
        '''
        Get the movie IDs for which a given person was a member of the crew.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewMovieIDs', **{ 'id': id })
    def person_crew_original_titles(self, id: str):
        '''
        Get the original titles for which a given person was a member of the crew.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewOriginalTitles', **{ 'id': id })
    def person_crew_poster_paths(self, id: str):
        '''
        Get the poster paths for movies in which a given person was a member of the crew.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewPosterPaths', **{ 'id': id })
    def person_crew_release_dates(self, id: str):
        '''
        Get the release dates for movies in which a given person was a member of the crew.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewReleaseDates', **{ 'id': id })
    def person_crew_titles(self, id: str):
        '''
        Get the crew titles for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personCrewTitles', **{ 'id': id })
    def person_deathday(self, id: str):
        '''
        Get the death date of a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personDeathday', **{ 'id': id })
    def person_gender(self, id: str):
        '''
        Get the gender of a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personGender', **{ 'id': id })
    def person_image_aspect_ratios(self, id: str):
        '''
        Get the image aspect ratios for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personImageAspectRatios', **{ 'id': id })
    def person_image_file_paths(self, id: str):
        '''
        Get the image paths for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personImageFilePaths', **{ 'id': id })
    def person_image_heights(self, id: str):
        '''
        Get the image heights for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personImageHeights', **{ 'id': id })
    def person_image_vote_counts(self, id: str):
        '''
        Get the image vote counts for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personImageVoteCounts', **{ 'id': id })
    def person_image_widths(self, id: str):
        '''
        Get the image widths for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personImageWidths', **{ 'id': id })
    def person_name(self, id: str):
        '''
        Get the name of a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personName', **{ 'id': id })
    def person_place_of_birth(self, id: str):
        '''
        Get the place of birth for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personPlaceOfBirth', **{ 'id': id })
    def person_popularity(self, id: str):
        '''
        Get the popularity of a given person.
        
        For more information, check out https://developers.themoviedb.org/3/getting-started/popularity
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personPopularity', **{ 'id': id })
    def person_profile_path(self, id: str):
        '''
        Get the profile path for a given person.
        
        :id: Person ID
        '''
        return self._client.call('MovieDB', 'personProfilePath', **{ 'id': id })
    def search_movie(self, title: str):
        '''
        Search for a given movie and return movie IDs.
        
        :title: Title of movie
        '''
        return self._client.call('MovieDB', 'searchMovie', **{ 'title': title })
    def search_person(self, name: str):
        '''
        Search for a given actor and return person IDs.
        
        :name: Name of person to search for
        '''
        return self._client.call('MovieDB', 'searchPerson', **{ 'name': name })
class NASA:
    '''
    The NASA Service provides access to planetary pictures and mars weather data.
    For more information, check out https://api.nasa.gov/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def apod(self):
        '''
        Fetch the "Astronomy Picture of the Day" from NASA
        '''
        return self._client.call('NASA', 'apod', **{  })
    def apod_details(self):
        '''
        Fetch additional information about the "Astronomy Picture of the Day"
        '''
        return self._client.call('NASA', 'apodDetails', **{  })
    def apod_media(self) -> str:
        '''
        NASA's 'Astronomy Picture of the Day' media
        
        :returns: 
        '''
        res = self._client.call('NASA', 'apodMedia', **{  })
        return str(res)
    @deprecated()
    def _mars_high_temp(self):
        '''
        Latest Mars data according to MAAS
        '''
        return self._client.call('NASA', 'marsHighTemp', **{  })
    @deprecated()
    def _mars_low_temp(self):
        '''
        
        '''
        return self._client.call('NASA', 'marsLowTemp', **{  })
    @deprecated()
    def _mars_weather(self):
        '''
        
        '''
        return self._client.call('NASA', 'marsWeather', **{  })
class NPlayer:
    '''
    The NPlayer Service provides helpers RPCs for ensuring round-robin turn taking
    among the roles in the project's room.
    
    Each role will receive a "start game" message at the start and then "start turn"
    message when it is the given role's turn to act.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def end_turn(self, next: Optional[str] = None):
        '''
        End your current turn.
        
        :next: Specify the player to go next
        '''
        return self._client.call('NPlayer', 'endTurn', **{ 'next': next })
    def get_active(self) -> str:
        '''
        Get the player whose turn it currently is.
        
        :returns: role id of the active player, or empty string if there are no players
        '''
        res = self._client.call('NPlayer', 'getActive', **{  })
        return str(res)
    def get_n(self) -> int:
        '''
        Get the number of detected players in the game.
        
        :returns: number of players
        '''
        res = self._client.call('NPlayer', 'getN', **{  })
        return int(res)
    def get_next(self) -> str:
        '''
        Get the player who will be active next.
        
        :returns: role id of the next player, or empty string if there are no players
        '''
        res = self._client.call('NPlayer', 'getNext', **{  })
        return str(res)
    def get_previous(self) -> str:
        '''
        Get the player who played last.
        
        :returns: role id of the previous player, or empty string if no previous player
        '''
        res = self._client.call('NPlayer', 'getPrevious', **{  })
        return str(res)
    def start(self) -> bool:
        '''
        Start a new turn-based game.
        
        :returns: true on successful start
        '''
        res = self._client.call('NPlayer', 'start', **{  })
        return bool(res)
class NewYorkTimes:
    '''
    The NewYorkTimes service provides access to the New York Times API including access
    to Moview Reviews, Top Stories, and their Semantic API.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_article_sections(self) -> List[str]:
        '''
        Get a list of all valid article sections.
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getArticleSections', **{  })
        return _common.vectorize(str)(res)
    def get_articles_with_concept(self, concept: dict) -> list:
        '''
        Fetch up to 10 articles containing the given concept.
        
        :concept: 
        
          - :name: (str) 
        
          - :type: (str) 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getArticlesWithConcept', **{ 'concept': concept })
    def get_best_seller_lists(self) -> List[str]:
        '''
        Get the best seller list names.
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getBestSellerLists', **{  })
        return _common.vectorize(str)(res)
    def get_best_sellers(self, list: str, date: Optional[str] = None) -> list:
        '''
        Get the best selling books for a given list and date.
        
        :list: 
        
        :date: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getBestSellers', **{ 'list': list, 'date': date })
    def get_concept_info(self, concept: dict) -> dict:
        '''
        Get additional information about a concept such as links to other concepts and
        geocodes.
        
        :concept: 
        
          - :name: (str) 
        
          - :type: (str) 
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getConceptInfo', **{ 'concept': concept })
        return dict(res)
    def get_concept_types(self) -> List[str]:
        '''
        Get a list of all concept types.
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getConceptTypes', **{  })
        return _common.vectorize(str)(res)
    def get_critics_picks(self, offset: Optional[float] = None) -> list:
        '''
        Get 20 movie reviews picked by critics starting at "offset".
        
        :offset: Must be a multiple of 20
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getCriticsPicks', **{ 'offset': offset })
    def get_latest_articles(self, section: str) -> List[str]:
        '''
        Get the latest articles in a given section.
        
        :section: 
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getLatestArticles', **{ 'section': section })
        return _common.vectorize(str)(res)
    def get_most_emailed_articles(self, period: str) -> list:
        '''
        Get the most emailed articles over the past day, week, or month.
        
        :period: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMostEmailedArticles', **{ 'period': period })
    def get_most_shared_articles(self, period: str) -> list:
        '''
        Get the articles shared most on Facebook over the past day, week, or month.
        
        :period: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMostSharedArticles', **{ 'period': period })
    def get_most_viewed_articles(self, period: str) -> list:
        '''
        Get the most viewed articles over the past day, week, or month.
        
        :period: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMostViewedArticles', **{ 'period': period })
    def get_movie_critic_info(self, name: str) -> list:
        '''
        Get information about a given movie critic.
        
        :name: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMovieCriticInfo', **{ 'name': name })
    def get_movie_critics(self) -> List[str]:
        '''
        Get a list of movie critics.
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getMovieCritics', **{  })
        return _common.vectorize(str)(res)
    def get_movie_reviews(self, offset: Optional[float] = None) -> list:
        '''
        Get 20 movie reviews starting at "offset".
        
        :offset: Must be a multiple of 20
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMovieReviews', **{ 'offset': offset })
    def get_movie_reviews_by_critic(self, critic: str, offset: Optional[float] = None) -> list:
        '''
        Get 20 movie reviews by a given critic starting at "offset".
        
        :critic: 
        
        :offset: Must be a multiple of 20
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getMovieReviewsByCritic', **{ 'critic': critic, 'offset': offset })
    def get_top_best_sellers(self, date: str) -> list:
        '''
        Get the top 5 books for all the best seller lists for a given date.
        
        :date: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'getTopBestSellers', **{ 'date': date })
    def get_top_stories(self, section: str) -> List[str]:
        '''
        Get the top stories for a given section.
        
        :section: 
        
        :returns: 
        '''
        res = self._client.call('NewYorkTimes', 'getTopStories', **{ 'section': section })
        return _common.vectorize(str)(res)
    def search_articles(self, query: str, offset: Optional[float] = None) -> list:
        '''
        Search for articles given a query. Up to 10 articles will be returned.
        More articles can be retrieved by specifying the "offset" or number of
        results to skip before returning the results.
        
        :query: 
        
        :offset: Must be a multiple of 10
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'searchArticles', **{ 'query': query, 'offset': offset })
    def search_best_sellers(self, title: Optional[str] = None, author: Optional[str] = None, offset: Optional[float] = None) -> list:
        '''
        Search for books on current or previous best seller lists.
        
        :title: 
        
        :author: 
        
        :offset: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'searchBestSellers', **{ 'title': title, 'author': author, 'offset': offset })
    def search_concepts(self, query: str) -> list:
        '''
        Search for concepts of interest.
        
        :query: 
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'searchConcepts', **{ 'query': query })
    def search_movie_reviews(self, query: str, offset: Optional[float] = None) -> list:
        '''
        Search for movie reviews starting at "offset". Returns up to 20 results.
        
        :query: 
        
        :offset: Must be a multiple of 20
        
        :returns: 
        '''
        return self._client.call('NewYorkTimes', 'searchMovieReviews', **{ 'query': query, 'offset': offset })
class OceanData:
    '''
    The OceanData service provides access to scientific ocean data including
    temperature and sea level.
    
    For more information, check out:
    
    - http://www.columbia.edu/~mhs119/Sensitivity+SL+CO2/
    - https://www.paleo.bristol.ac.uk/~ggdjl/warm_climates/hansen_etal.pdf.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_deep_ocean_temp(self, start_year: Optional[float] = None, end_year: Optional[float] = None) -> list:
        '''
        Get historical deep ocean temperatures in Celsius by year.
        
        If startYear or endYear is provided, only measurements within the given range will be returned.
        
        :start_year: earliest year to include in results
        
        :end_year: latest year to include in results
        
        :returns: a list of deep ocean temperatures by year
        '''
        return self._client.call('OceanData', 'getDeepOceanTemp', **{ 'startYear': start_year, 'endYear': end_year })
    def get_oxygen_ratio(self, start_year: Optional[float] = None, end_year: Optional[float] = None) -> list:
        '''
        Get historical oxygen isotope ratio values by year.
        
        If startYear or endYear is provided, only measurements within the given range will be returned.
        
        :start_year: earliest year to include in results
        
        :end_year: latest year to include in results
        
        :returns: a list of oxygen isotope ratios by year
        '''
        return self._client.call('OceanData', 'getOxygenRatio', **{ 'startYear': start_year, 'endYear': end_year })
    def get_sea_level(self, start_year: Optional[float] = None, end_year: Optional[float] = None) -> list:
        '''
        Get historical sea level in meters by year.
        
        If startYear or endYear is provided, only measurements within the given range will be returned.
        
        :start_year: earliest year to include in results
        
        :end_year: latest year to include in results
        
        :returns: a list of change in sea level (in meters) by year
        '''
        return self._client.call('OceanData', 'getSeaLevel', **{ 'startYear': start_year, 'endYear': end_year })
    def get_surface_temp(self, start_year: Optional[float] = None, end_year: Optional[float] = None) -> list:
        '''
        Get historical surface ocean temperatures in Celsius by year.
        
        If startYear or endYear is provided, only measurements within the given range will be returned.
        
        :start_year: earliest year to include in results
        
        :end_year: latest year to include in results
        
        :returns: a list of surface ocean temperatures by year
        '''
        return self._client.call('OceanData', 'getSurfaceTemp', **{ 'startYear': start_year, 'endYear': end_year })
class PaleoceanOxygenIsotopes:
    '''
    Access to NOAA Global Pliocene-Pleistocene Benthic d18O Stack.
    
    For more information, check out
    https://www.ncdc.noaa.gov/paleo-search/study/5847
    
    Original datasets are available at:
    https://www1.ncdc.noaa.gov/pub/data/paleo/contributions_by_author/lisiecki2005/lisiecki2005.txt.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_average_sedimentation_rates(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get average sedimentation rate value (unit: centimeter per kiloyear).
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: least year of data to include
        
        :returns: a list of average sedimentation rate by year
        '''
        return self._client.call('PaleoceanOxygenIsotopes', 'getAverageSedimentationRates', **{ 'startyear': startyear, 'endyear': endyear })
    def get_delta18o(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get delta 18O value (unit: per mill. It is a parts per thousand unit, often used directly to
        refer to isotopic ratios and calculated by calculating the ratio of isotopic concentrations in
        a sample and in a standard, subtracting one and multiplying by one thousand).
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: least year of data to include
        
        :returns: a list of delta 18O values by year
        '''
        return self._client.call('PaleoceanOxygenIsotopes', 'getDelta18O', **{ 'startyear': startyear, 'endyear': endyear })
    def get_delta18o_error(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get delta 18O error value (unit: per mill).
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: least year of data to include
        
        :returns: a list of delta 18O error values by year
        '''
        return self._client.call('PaleoceanOxygenIsotopes', 'getDelta18OError', **{ 'startyear': startyear, 'endyear': endyear })
    def get_normalized_sedimentation_rates(self, startyear: Optional[float] = None, endyear: Optional[float] = None) -> list:
        '''
        Get normalized sedimentation rate value (unit: dimensionless).
        
        If startyear or endyear is provided, only measurements within the given range will be returned.
        
        :startyear: first year of data to include
        
        :endyear: least year of data to include
        
        :returns: a list of normalized sedimentation rate by year
        '''
        return self._client.call('PaleoceanOxygenIsotopes', 'getNormalizedSedimentationRates', **{ 'startyear': startyear, 'endyear': endyear })
class ParallelDots:
    '''
    Uses ParallelDots AI to process or compare text for a variety of features.
    See the API documentation, at
    http://apis.paralleldots.com/text_docs/index.html
    
    Terms of use: https://www.paralleldots.com/terms-and-conditions
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_abuse(self, text: str) -> dict:
        '''
        Classify the given text as abusive, hate_speech, or neither.
        The returned structured data has confidence levels for each of these categories.
        
        :text: text to analyze
        
        :returns: structured data containing the confidence levels
        '''
        res = self._client.call('ParallelDots', 'getAbuse', **{ 'text': text })
        return dict(res)
    def get_emotion(self, text: str) -> dict:
        '''
        Find the emotion in the given text.
        This is returned as structured data containing confidence levels for each of the following emotions:
        excited, angry, bored, fear, sad, and happy.
        
        :text: text to analyze
        
        :returns: structured data with confidence levels for each emotion
        '''
        res = self._client.call('ParallelDots', 'getEmotion', **{ 'text': text })
        return dict(res)
    def get_intent(self, text: str) -> dict:
        '''
        Get the intent of the given text along with the confidence score.
        This is returned as structured data with confidence levels for each of the following intents:
        news, query, spam, marketing, and feedback.
        
        :text: text to analyze
        
        :returns: structured data with confidence levels for each intent
        '''
        res = self._client.call('ParallelDots', 'getIntent', **{ 'text': text })
        return dict(res)
    def get_keywords(self, text: str) -> list:
        '''
        Extract keywords from the given text along with their confidence score.
        
        :text: text to analyze
        
        :returns: information about keywords in the text
        '''
        return self._client.call('ParallelDots', 'getKeywords', **{ 'text': text })
    def get_named_entities(self, text: str) -> list:
        '''
        Identify named entities in the given text.
        
        :text: text to analyze
        
        :returns: speculated information about named entities in the text, including the confidence level
        '''
        return self._client.call('ParallelDots', 'getNamedEntities', **{ 'text': text })
    def get_sarcasm_probability(self, text: str) -> float:
        '''
        Compute the probability of sarcasm for the given text.
        
        :text: text to analyze
        
        :returns: predicted likelihood that the text is sarcastic
        '''
        res = self._client.call('ParallelDots', 'getSarcasmProbability', **{ 'text': text })
        return float(res)
    def get_sentiment(self, text: str) -> dict:
        '''
        Find the overall sentiment of the given text along with the confidence score.
        The returned structured data hasa confidence level for each of the following sentiment categories:
        negative, neutral, and positive.
        
        :text: text to analyze
        
        :returns: structured data with confidence level for each category
        '''
        res = self._client.call('ParallelDots', 'getSentiment', **{ 'text': text })
        return dict(res)
    def get_similarity(self, text1: str, text2: str) -> float:
        '''
        Get the level of similarity between two snippets of text.
        Note that the two pieces of text should be long, like full sentences (not just 2 words).
        
        :text1: the first piece of text
        
        :text2: a second piece of text
        
        :returns: the computed similarity level
        '''
        res = self._client.call('ParallelDots', 'getSimilarity', **{ 'text1': text1, 'text2': text2 })
        return float(res)
    def get_taxonomy(self, text: str) -> list:
        '''
        Classify the given text into IAB categories.
        
        For more information about IAB categories, see
        https://www.iab.com/guidelines/iab-quality-assurance-guidelines-qag-taxonomy/
        
        :text: text to analyze
        
        :returns: information about the category breakdown, along with confidence scores
        '''
        return self._client.call('ParallelDots', 'getTaxonomy', **{ 'text': text })
class PhoneIoT:
    '''
    PhoneIoT is a service in NetsBlox (https://netsblox.org/) that's meant to teach Internet of Things (IoT) topics as early as K-12 education.
    It allows you to programmatically access your smartphone's sensors and display.
    This includes accessing hardware sensors such as the accelerometer, gyroscope, microphone, camera, and many others depending on the device.
    PhoneIoT also allows you to control a customizable interactive display, enabling you to use your device as a custom remote control, or even create and run distributed (multiplayer) applications.
    The limits are up to your imagination!
    
    To get started using PhoneIoT, download the PhoneIoT app on your mobile device, available for Android (https://play.google.com/store/apps/details?id=org.netsblox.phoneiot) and iOS, and then go to the NetsBlox editor (https://editor.NetsBlox.org).
    In the top left of the editor, you should see a grid of several colored tabs.
    Under the Network tab, grab a call block and place it in the center script area.
    Click the first dropdown on the call block and select the PhoneIoT service.
    The second dropdown selects the specific *Remote Procedure Call* (RPC) to execute - see the table of contents  for information about the various RPCs.
    
    Inside the PhoneIoT app on your mobile device, click the button at the top left to open the menu, and then click connect.
    If you successfully connected, you should get a small popup message at the bottom of the screen.
    If you don't see this message, make sure you have either Wi-Fi or mobile data turned on and try again.
    Near the top of the menu, you should see an ID and password, which will be needed to connect to the device from NetsBlox.
    
    Back in NetsBlox, select the setCredentials RPC and give it your ID and password.
    For convenience, you might want to save the ID in a variable (e.g. device), as it will be referenced many times.
    If you click the call block to run it, you should get an OK result, meaning you successfully connected.
    If you don't see this, make sure you entered the ID and password correctly.
    
    You're now ready to start using the other RPCs in PhoneIoT to communicate with the device!
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def add_button(self, device: str, x: float, y: float, width: float, height: float, text: Optional[str] = None, options: Optional[dict] = None) -> str:
        '''
        Adds a button to the display with the given position and size.
        If not specified, the default text for a button is empty, which can be used to just make a colored, unlabeled button.
        The text can be modified later via PhoneIoT.setText.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the button (percentage)
        
        :y: Y position of the top left corner of the button (percentage)
        
        :width: Width of the button (percentage)
        
        :height: Height of the button (percentage)
        
        :text: text to display on the button (default empty)
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message type to be sent each time the button is pressed. You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id.
        
          - :style: (str) The display style of the button on the screen. This can be rectangle (default), ellipse, square, or circle. If square or circle is used, the height of the control is ignored (height equals width).
        
          - :color: (int) The background color of the button.
        
          - :textColor: (int) The text color of the button.
        
          - :landscape: (bool) If set to true, rotates the button 90 degrees around its top left corner.
        
          - :fontSize: (float) The size of the font to use for text (default 1.0).
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addButton', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'height': height, 'text': text, 'options': options })
        return str(res)
    def add_image_display(self, device: str, x: float, y: float, width: float, height: float, options: Optional[dict] = None) -> str:
        '''
        Adds an image display with the given position and size.
        If not specified, an image display is by default readonly = true, meaning that the user cannot modify its content.
        If (explicitly) set to readonly = false, then the user can click on the image display to change the image to a new picture from the camera.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the image display (percentage).
        
        :y: Y position of the top left corner of the image display (percentage).
        
        :width: Width of the image display (percentage).
        
        :height: Height of the image display (percentage).
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message type to be sent each time the user updates the content (only possible if readonly = false). You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id.
        
          - :readonly: (bool) If set to true (default), the user will not be able to edit the content; however, you will still be able to do so programmatically via PhoneIoT.setImage. Defaults to true.
        
          - :landscape: (bool) If set to true, rotates the image display 90 degrees around its top left corner.
        
          - :fit: (str) The technique used to fit the image into the display, in case the image and the display have different aspect ratios. This can be fit (default), zoom, or stretch.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addImageDisplay', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'height': height, 'options': options })
        return str(res)
    def add_joystick(self, device: str, x: float, y: float, width: float, options: Optional[dict] = None) -> str:
        '''
        Adds a joystick control to the canvas at the given position and size.
        No height parameter is given because joysticks are always circular (similar to passing style = circle to PhoneIoT.addButton).
        
        The position of the joystick is given by a vector [x, y], which is normalized to a length of 1.
        If you would prefer to not have this normalization and want rectangular coordinates instead of circular, consider using PhoneIoT.addTouchpad instead.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the joystick (percentage).
        
        :y: Y position of the top left corner of the joystick (percentage).
        
        :width: Width of the joystick (percentage).
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message type to be sent each time the user moves the joystick. The messages also include a tag field which functions identically to the one in PhoneIoT.addTouchpad. You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id, x, y, tag.
        
          - :color: (int) The color of the joystick.
        
          - :landscape: (bool) If set to true, the x and y values of the joystick are altered so that it acts correctly when in landscape mode. Unlike other controls, this option does not affect where the control is displayed on the screen (no rotation).
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addJoystick', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'options': options })
        return str(res)
    def add_label(self, device: str, x: float, y: float, text: Optional[str] = None, options: Optional[dict] = None) -> str:
        '''
        Adds a label control to the canvas at the given position.
        If text is not specified, it default to empty, which can be used to hide the label when nothing needs to be displayed.
        The text can be modified later via PhoneIoT.setText.
        
        Labels do not have a size, so they also don't do text wrapping.
        Because of this, you should keep label text relatively short.
        If you need a large amount of text written, consider using PhoneIoT.addTextField with readonly = true.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the label (percentage).
        
        :y: Y position of the top left corner of the label (percentage).
        
        :text: The text to display on the label (defaults to empty)
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :textColor: (int) The text color of the label.
        
          - :align: (str) The text alignment to use. If set to left, the text starts at the label position. If set to right, the text ends at the label position. If set to center, the text is centered on the label position.
        
          - :fontSize: (float) The size of the font to use for text (default 1.0).
        
          - :landscape: (bool) If set to true, rotates the label 90 degrees around the label position so the text appears upright when viewed in landscape.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addLabel', **{ 'device': device, 'x': x, 'y': y, 'text': text, 'options': options })
        return str(res)
    def add_radio_button(self, device: str, x: float, y: float, text: Optional[str] = None, options: Optional[dict] = None) -> str:
        '''
        Adds a radio button to the canvas.
        Radio buttons are like toggles (checkboxes), except that they are organized into groups
        and the user can check at most one radio button from any given group.
        These can be used to accept multiple-choice input from the user.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the radio button (percentage).
        
        :y: Y position of the top left corner of the radio button (percentage).
        
        :text: The text to display next to the checkbox (defaults to empty)
        
        :options: Additional options
        
          - :group: (str) The name of the group to associate this radio button with. You do not need this value to access the control later. If not specified, defaults to main.
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of an event to send every time the user clicks the radio button. Note that clicking a radio button always checks it, unlike toggles. You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id.
        
          - :checked: (bool) Defaults to false. If set to true, the radio button will be initially checked. Note that, while the user cannot check multiple radio buttons, you are free to do so programmatically.
        
          - :color: (int) The color of the radio button itself.
        
          - :textColor: (int) The text color of the radio button.
        
          - :fontSize: (float) The size of the font to use for text (default 1.0). Note that this will also scale up the size of the radio button itself (not just the text).
        
          - :landscape: (bool) If set to true, rotates the radio button 90 degrees around its top left corner.
        
          - :readonly: (bool) If set to true, the user will not be able to change the state by clicking; however, you will still be free to do so from code. Defaults to false.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addRadioButton', **{ 'device': device, 'x': x, 'y': y, 'text': text, 'options': options })
        return str(res)
    def add_slider(self, device: str, x: float, y: float, width: float, options: Optional[dict] = None) -> str:
        '''
        Adds a slider control to the display.
        Sliders can be moved around to input or display any value in the range [0, 1].
        If you need values outside of this range, you can do a little math to map them to [0, 1] or vice versa.
        
        You can read and write the value of a slider with PhoneIoT.getLevel and PhoneIoT.setLevel.
        Note that if the control is set to readonly = true, the user cannot change the value, but you can still do so from code.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the slider (percentage).
        
        :y: Y position of the top left corner of the slider (percentage).
        
        :width: Width (length) of the slider (percentage).
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message type to be sent each time the user touches, slides, or lets go of the slider. The messages also include a tag field which functions identically to the one in PhoneIoT.addTouchpad. You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id, level, tag.
        
          - :color: (int) The color of the slider.
        
          - :value: (float) The initial value of the slider (default 0.0).
        
          - :style: (str) Controls the appearance of the slider. Allowed values are slider (default) or progress.
        
          - :landscape: (bool) true to rotate the control 90 degrees into landscape mode.
        
          - :readonly: (bool) If set to true, the user will not be able to change the value by sliding; however, you are still able to change the value from code. This is especially useful for displaying progress bars such as for a long-running application. Defaults to false.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addSlider', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'options': options })
        return str(res)
    def add_text_field(self, device: str, x: float, y: float, width: float, height: float, options: Optional[dict] = None) -> str:
        '''
        Adds a text field to the canvas.
        These are typically used to display large blocks of text, or to accept input text from the user.
        Unless set to readonly = true, the user can click on the text field to change its content.
        
        If you have a small amount of text you need to show and would otherwise make this control readonly = true, consider using PhoneIoT.addLabel instead.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the text field (percentage).
        
        :y: Y position of the top left corner of the text field (percentage).
        
        :width: Width of the text field (percentage).
        
        :height: Height of the text field (percentage).
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of an event to send every time the user changes the text content (only possible if readonly = false). Note that this event is only sent once the user clicks accept on the new content (you do not get an event for every key press). You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id, text.
        
          - :text: (str) This can be used to set the initial text of the text field once created. Defaults to empty if not specified.
        
          - :color: (int) The color of the text field border.
        
          - :textColor: (int) The text color of the text field.
        
          - :readonly: (bool) If set to true, the user will not be able to edit the content; however, you will still be free to do so programmatically. Defaults to false.
        
          - :fontSize: (float) The size of the font to use for text (default 1.0).
        
          - :align: (str) The text alignment to use. This can be left (default), right, or center.
        
          - :landscape: (bool) If set to true, rotates the text field 90 degrees around its top left corner.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addTextField', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'height': height, 'options': options })
        return str(res)
    def add_toggle(self, device: str, x: float, y: float, text: Optional[str] = None, options: Optional[dict] = None) -> str:
        '''
        Adds a toggle control to the canvas at the given location.
        The text parameter can be used to set the initial text shown for the toggle (defaults to empty),
        but this can be changed later with PhoneIoT.setText.
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the toggle (percentage).
        
        :y: Y position of the top left corner of the toggle (percentage).
        
        :text: The text to display next to the toggle (defaults to empty)
        
        :options: Additional options
        
          - :style: (str) The visual style of the toggle control. This can be switch (default) for a mobile-style toggle, or checkbox for a desktop-style toggle.
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message to be sent every time the checkbox is toggled by the user. You must call PhoneIoT.listenToGUI to actually receive these messages. Message fields: device, id, state.
        
          - :checked: (bool) Defaults to false. If set to true, the toggle will be initially checked.
        
          - :color: (int) The color of the toggle itself.
        
          - :textColor: (int) The text color of the toggle.
        
          - :fontSize: (float) The size of the font to use for text (default 1.0). Note that this will also scale up the size of the toggle itself (not just the text).
        
          - :landscape: (bool) If set to true, rotates the toggle 90 degrees around its top left corner.
        
          - :readonly: (bool) If set to true, the user will not be able to change the state by clicking; however, you will still be free to do so from code. Defaults to false.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addToggle', **{ 'device': device, 'x': x, 'y': y, 'text': text, 'options': options })
        return str(res)
    def add_touchpad(self, device: str, x: float, y: float, width: float, height: float, options: Optional[dict] = None) -> str:
        '''
        Adds a touchpad control to the canvas at the given position and size.
        This control is similar to the joystick control, except that it is rectangular,
        the vector is not normalized to a distance of 1,
        the "stick" does not move back to (0, 0) upon letting go,
        and there is an additional "tag" value denoting if each event was a touch down, move, or up.
        
        Although the vector value is not normalized to a length of 1,
        each component (x and y individually) is in [-1, 1].
        
        Adding a widget/control to the device will automatically call PhoneIoT.listenToGUI, which is needed to receive events from user interaction.
        If you have a scenario where one project sets up the GUI but another project also needs to listen for GUI events,
        the other project can directly call PhoneIoT.listenToGUI to receive the events without needing to actually add a widget.
        
        :device: id of the device
        
        :x: X position of the top left corner of the touchpad (percentage).
        
        :y: Y position of the top left corner of the touchpad (percentage).
        
        :width: Width of the touchpad (percentage).
        
        :height: Height of the touchpad (percentage).
        
        :options: Additional options
        
          - :id: (str) The id to use for the control. If not specified, a new one will be automatically generated.
        
          - :event: (str) The name of a message type to be sent each time the user touches, slides, or lets go of the touchpad. A message field called tag is included to differentiate the different types of interactions; it is one of down (touch started), up (touch ended), or move (during continued/held touch). You must call PhoneIoT.listenToGUI to actually receive these messages. If not specified, no event is sent. Message fields: device, id, x, y, tag.
        
          - :color: (int) The color of the touchpad.
        
          - :style: (str) Controls the appearance of the touchpad. These are the same as for PhoneIoT.addButton except that only rectangle and square are allowed.
        
          - :landscape: (bool) true to rotate the control 90 degrees into landscape mode.
        
        :returns: id of the created control
        '''
        res = self._client.call('PhoneIoT', 'addTouchpad', **{ 'device': device, 'x': x, 'y': y, 'width': width, 'height': height, 'options': options })
        return str(res)
    def authenticate(self, device: str):
        '''
        This RPC simply checks that the connection to the device is still good.
        In particular, you can use this to check if the password is still valid.
        
        :device: id of the device
        '''
        return self._client.call('PhoneIoT', 'authenticate', **{ 'device': device })
    def clear_controls(self, device: str):
        '''
        Removes all controls from the device's canvas.
        If you would instead like to remove a specific control, see PhoneIoT.removeControl.
        
        :device: id of the device
        '''
        return self._client.call('PhoneIoT', 'clearControls', **{ 'device': device })
    def get_accelerometer(self, device: str) -> list:
        '''
        Gets the current output of the accelerometer sensor, if the device supports it.
        This is a vector representing the acceleration along the x, y, and z axes, relative to the device.
        When at rest, you can expect to measure the acceleration due to gravity.
        
        Sensor name: accelerometer
        
        Message fields: x, y, z, facingDir, device
        
        :device: id of the device
        
        :returns: current acceleration vector
        '''
        return self._client.call('PhoneIoT', 'getAccelerometer', **{ 'device': device })
    def get_altitude(self, device: str) -> float:
        '''
        Returns the current altitude of the device, expressed in meters above sea level.
        This is provided by the location service on the device, so you must have location turned on and give the app permission.
        
        Sensor name: location
        
        Message fields: latitude, longitude, heading, altitude, device
        
        :device: id of the device
        
        :returns: current altitude in meters
        '''
        res = self._client.call('PhoneIoT', 'getAltitude', **{ 'device': device })
        return float(res)
    @deprecated()
    def _get_bearing(self, device: str) -> float:
        '''
        :device: id of the device
        
        :returns: current heading (in degrees)
        '''
        res = self._client.call('PhoneIoT', 'getBearing', **{ 'device': device })
        return float(res)
    def get_color(self, red: int, green: int, blue: int, alpha: Optional[int] = None) -> int:
        '''
        Many of the Display RPCs take one or more optional parameters for controlling display color, which is specified as an integer.
        This RPC is a convenience function for constructing a color code from red, green, blue, and alpha values (each is 0-255).
        
        The alpha value controls transparency, with 0 being invisible and 255 being opaque.
        If not specified, alpha will default to 255.
        
        :red: red level (0-255)
        
        :green: green level (0-255)
        
        :blue: blue level (0-255)
        
        :alpha: alpha level (0-255)
        
        :returns: Constructed color code (an integer)
        '''
        res = self._client.call('PhoneIoT', 'getColor', **{ 'red': red, 'green': green, 'blue': blue, 'alpha': alpha })
        return int(res)
    def get_compass_cardinal_direction(self, device: str) -> str:
        '''
        Equivalent to PhoneIoT.getCompassDirection, except that it only returns N, E, S, or W.
        
        If you are getting inconsistent values, try moving and rotating your device around in a figure-8 to recalibrate it.
        
        Sensor name: orientation
        
        Message fields: x, y, z, heading, dir, cardinalDir, device
        
        :device: id of the device
        
        :returns: the compass cardinal direction name
        '''
        res = self._client.call('PhoneIoT', 'getCompassCardinalDirection', **{ 'device': device })
        return str(res)
    def get_compass_direction(self, device: str) -> str:
        '''
        Returns the current compass direction of the device, which is one of N, NE, E, SE, S, SW, W, or NW.
        This is provided by the magnetic field sensor, so using this RPC on devices without a magnetometer will result in an error.
        The output of this RPC assumes the device is face-up.
        
        If you are getting inconsistent values, try moving and rotating your device around in a figure-8 to recalibrate it.
        
        Sensor name: orientation
        
        Message fields: x, y, z, heading, dir, cardinalDir, device
        
        :device: id of the device
        
        :returns: the current compass direction name
        '''
        res = self._client.call('PhoneIoT', 'getCompassDirection', **{ 'device': device })
        return str(res)
    def get_compass_heading(self, device: str) -> float:
        '''
        Gets the current compass heading from the device.
        This is similar to PhoneIoT.getGPSHeading, except that it returns the angle from magnetic north, rather than the direction of travel.
        This is provided by the magnetic field sensor, so using this RPC on devices without a magnetometer will result in an error.
        The output of this RPC assumes the device is face-up.
        
        If you are getting inconsistent values, try moving and rotating your device around in a figure-8 to recalibrate it.
        
        Sensor name: orientation
        
        Message fields: x, y, z, heading, dir, cardinalDir, device
        
        :device: id of the device
        
        :returns: the compass heading (in degrees)
        '''
        res = self._client.call('PhoneIoT', 'getCompassHeading', **{ 'device': device })
        return float(res)
    def get_facing_direction(self, device: str) -> str:
        '''
        Attempts to determine the general orientation of the device based on the accelerometer output.
        This represents which direction the face of the device's screen is pointing.
        The possible values are:
        
        - up - the device is face up
        - down - the device is face down
        - vertical - the device is upright
        - upside down - the device is vertical, but upside down
        - left - the device is horizontal, lying on its left side (when facing the screen)
        - right - the device is horizontal, lying on its right side (when facing the screen)
        
        Sensor name: accelerometer
        
        Message fields: x, y, z, facingDir, device
        
        :device: id of the device
        
        :returns: name of the facing direction
        '''
        res = self._client.call('PhoneIoT', 'getFacingDirection', **{ 'device': device })
        return str(res)
    @deprecated()
    def _get_game_rotation(self, device: str) -> list:
        '''
        Equivalent to the PhoneIoT.getOrientation RPC except that it gets the orientation relative to a fixed reference frame, thus making it good for use in games.
        
        Sensor name: gameRotation
        
        Message fields: x, y, z, device
        
        :device: id of the device
        
        :returns: 3D rotational vector
        '''
        return self._client.call('PhoneIoT', 'getGameRotation', **{ 'device': device })
    def get_gps_heading(self, device: str) -> float:
        '''
        Returns the current heading (direction of travel) from the device.
        This is provided by the location sensor, so you must have location turned on and give the app permission.
        The heading is expressed as the angle (in degrees) from North, going clockwise.
        Thus, you can directly use this value in a point in direction block to point a sprite in the direction of travel (assuming North is up).
        
        Note that headings based on location work by approximating your direction of travel, rather than which way you are facing.
        Thus, this will not work while standing still.
        In these cases, consider using PhoneIoT.getCompassHeading instead.
        
        Sensor name: location
        
        Message fields: latitude, longitude, heading, altitude, device
        
        :device: id of the device
        
        :returns: current heading (in degrees)
        '''
        res = self._client.call('PhoneIoT', 'getGPSHeading', **{ 'device': device })
        return float(res)
    def get_gravity(self, device: str) -> list:
        '''
        Attempts to get the gravity acceleration angle, divorced from any linear acceleration the device might be experiencing.
        For example, even if you start running, this vector should always have roughly the same value.
        This is provided by a hybrid sensor, and is not available on all devices.
        
        The counterpart to this RPC is PhoneIoT.getLinearAcceleration.
        
        Sensor name: gravity
        
        Message fields: x, y, z, device
        
        :device: id of the device
        
        :returns: gravitational acceleration vector
        '''
        return self._client.call('PhoneIoT', 'getGravity', **{ 'device': device })
    def get_gyroscope(self, device: str) -> list:
        '''
        Gets the current output of the gyroscope sensor, which measures angular velocity (in degrees/s) along the three axes of the device.
        
        Sensor name: gyroscope
        
        Message fields: x, y, z, device
        
        :device: id of the device
        
        :returns: rotational acceleration vector
        '''
        return self._client.call('PhoneIoT', 'getGyroscope', **{ 'device': device })
    def get_image(self, device: str, id: str) -> Image.Image:
        '''
        Gets the displayed image of an image-like control with the given ID.
        This can be used on any control that displays images, which is currently only image displays.
        
        This can be used to retrieve images from the mobile device's camera by having the user store an image in an image display that was set to readonly = false.
        See the readonly optional parameter of PhoneIoT.addImageDisplay.
        
        :device: id of the device
        
        :id: id of the image display
        
        :returns: the displayed image
        '''
        return self._client.call('PhoneIoT', 'getImage', **{ 'device': device, 'id': id })
    @deprecated()
    def _get_joystick_vector(self, device: str, id: str) -> list:
        '''
        :device: 
        
        :id: 
        
        :returns: 
        '''
        return self._client.call('PhoneIoT', 'getJoystickVector', **{ 'device': device, 'id': id })
    def get_level(self, device: str, id: str) -> float:
        '''
        Get the current value (a single number) of a value-like control.
        Currently, the only supported control is a slider, which returns a value in [0, 1].
        
        Instead of calling this in a loop, it is likely better to use the event optional parameter of PhoneIoT.addSlider.
        
        If you want to get the cursor position of a joystick or touchpad, use PhoneIoT.getPosition instead.
        
        :device: id of the device
        
        :id: id of the control to read
        
        :returns: current value
        '''
        res = self._client.call('PhoneIoT', 'getLevel', **{ 'device': device, 'id': id })
        return float(res)
    def get_light_level(self, device: str) -> float:
        '''
        Gets the current light level from the device.
        This is represented as a number with higher values being brighter.
        
        Sensor name: lightLevel
        
        Message fields: level, device
        
        :device: id of the device
        
        :returns: current light level
        '''
        res = self._client.call('PhoneIoT', 'getLightLevel', **{ 'device': device })
        return float(res)
    def get_linear_acceleration(self, device: str) -> list:
        '''
        This RPC attempts to get the linear acceleration vector, divorced from the constant gravitational acceleration.
        Theoretically, if the device is at rest this RPC would report a nearly-zero vector (nothing is ever perfectly still).
        This is provided by a hybrid sensor, and is not available on all devices.
        
        The counterpart to this RPC is PhoneIoT.getGravity.
        
        Sensor name: linearAcceleration
        
        Message fields: x, y, z, device
        
        :device: id of the device
        
        :returns: current linear acceleration vector
        '''
        return self._client.call('PhoneIoT', 'getLinearAcceleration', **{ 'device': device })
    def get_location(self, device: str) -> list:
        '''
        Gets the current location of the device, specified as latitude and longitude coordinates (in degrees).
        This is provided by the location service on the device, so you must have location turned on and give the app permission.
        
        Sensor name: location
        
        Message fields: latitude, longitude, heading, altitude, device
        
        :device: id of the device
        
        :returns: a list containing the latitude and longitude
        '''
        return self._client.call('PhoneIoT', 'getLocation', **{ 'device': device })
    def get_magnetic_field(self, device: str) -> list:
        '''
        Gets the current output of the magnetic field sensor, measured in μT (micro Tesla) along each axis of the device.
        This is provided by the magnetic field sensor, so using this RPC on devices without a magnetometer will result in an error.
        
        Notably, this RPC can be used as a compass (measuring Earth's magnetic field).
        
        Sensor name: magneticField
        
        Message fields: x, y, z, device
        
        :device: id of the device
        
        :returns: magnetic field vector
        '''
        return self._client.call('PhoneIoT', 'getMagneticField', **{ 'device': device })
    def get_microphone_level(self, device: str) -> list:
        '''
        Gets the current level (volume) of the microphone on the device.
        This is specified as a number where 0.0 denotes silence and 1.0 is the maximum volume the microphone can record.
        
        Sensor name: microphoneLevel
        
        Message fields: volume, device
        
        :device: id of the device
        
        :returns: the current volume level
        '''
        return self._client.call('PhoneIoT', 'getMicrophoneLevel', **{ 'device': device })
    def get_orientation(self, device: str) -> list:
        '''
        Gets the current output of the orientation sensor, relative to Earth's magnetic reference frame.
        This is given as a vector (list) with three angular components (in degrees):
        
        - azimuth (effectively the compass heading) [-180, 180]
        - pitch (vertical tilt) [-90, 90]
        - roll [-180, 180]
        
        If you are getting inconsistent values for the first (azimuth) angle,
        try moving and rotating your device around in a figure-8 to recalibrate it.
        
        Sensor name: orientation
        
        Message fields: x, y, z, heading, dir, cardinalDir, device
        
        :device: id of the device
        
        :returns: the current orientation vector
        '''
        return self._client.call('PhoneIoT', 'getOrientation', **{ 'device': device })
    def get_position(self, device: str, id: str) -> list:
        '''
        Gets the current x and y values for the current position of a positional control.
        This does *not* give the location of the control on the screen.
        Positional controls are controls whose primary interaction is through position.
        For instance, this is used for both joystick and touchpad controls.
        
        For a joystick, this always returns a vector normalized to a length of 1.0.
        If the user is not touching the joystick, it will automatically go back to the center, [0, 0].
        
        For a touchpad, this will either give you the current location of the touch (a list of [x, y])
        or an error if the user is not touching the screen.
        
        If you want to get the value of a slider, use PhoneIoT.getLevel instead.
        
        Instead of calling this in a loop, it is likely better to use the event optional parameter of
        PhoneIoT.addJoystick or PhoneIoT.addTouchpad.
        
        :device: id of the device
        
        :id: id of the control to read
        
        :returns: a list of [x, y] for the current position, or a string explaining that there is no current position
        '''
        return self._client.call('PhoneIoT', 'getPosition', **{ 'device': device, 'id': id })
    def get_pressure(self, device: str) -> float:
        '''
        Gets the current atmospheric pressure around the device in kPa (kilopascals).
        For reference, 1 atmosphere of pressure is 101.325 kPa.
        
        Sensor name: pressure
        
        Message fields: pressure, device
        
        :device: id of the device
        
        :returns: current pressure level
        '''
        res = self._client.call('PhoneIoT', 'getPressure', **{ 'device': device })
        return float(res)
    def get_proximity(self, device: str) -> float:
        '''
        Gets the current output of the proximity (distance) sensor, measured in cm.
        Phones typically have this sensor for turning off the display when you put it to your ear, but tablets typically do not.
        In any case, the distances are not typically very long, and some devices only have binary (near/far) sensors.
        
        Sensor name: proximity
        
        Message fields: distance, device
        
        :device: id of the device
        
        :returns: current proximity sensor output
        '''
        res = self._client.call('PhoneIoT', 'getProximity', **{ 'device': device })
        return float(res)
    def get_relative_humidity(self, device: str) -> float:
        '''
        Gets the relative humidity as a percent.
        
        Sensor name: humidity
        
        Message fields: humidity, device
        
        :device: id of the device
        
        :returns: current relative humidity
        '''
        res = self._client.call('PhoneIoT', 'getRelativeHumidity', **{ 'device': device })
        return float(res)
    @deprecated()
    def _get_rotation(self, device: str) -> list:
        '''
        Gets the current output of the rotation sensor.
        This is a 4D rotation vector, given as rotation along 3 axes, plus a scalar component.
        This is provided in case it is needed, but in practice, it's typically easier to use 3D quantities, as provided by PhoneIoT.getOrientation.
        
        Sensor name: rotation
        
        Message fields: x, y, z, w, device
        
        :device: id of the device
        
        :returns: 4D rotational vector
        '''
        return self._client.call('PhoneIoT', 'getRotation', **{ 'device': device })
    def get_sensors(self) -> list:
        '''
        This RPC returns a list containing the name of every sensor supported by PhoneIoT.
        Note that your specific device might not support all of these sensors, depending on the model.
        
        See Sensors for more information.
        
        :returns: A list of sensor names
        '''
        return self._client.call('PhoneIoT', 'getSensors', **{  })
    def get_step_count(self, device: str) -> float:
        '''
        Gets the current step count from the device's step counter sensor.
        Not all devices have a step counter sensor, but you can manually emulate one by using the accelerometer.
        
        Sensor name: stepCount
        
        Message fields: count, device
        
        :device: id of the device
        
        :returns: current step count
        '''
        res = self._client.call('PhoneIoT', 'getStepCount', **{ 'device': device })
        return float(res)
    def get_temperature(self, device: str) -> float:
        '''
        Gets the current ambient temperature around the device in Celsius.
        
        Sensor name: temperature
        
        Message fields: temp, device
        
        :device: id of the device
        
        :returns: current temperature
        '''
        res = self._client.call('PhoneIoT', 'getTemperature', **{ 'device': device })
        return float(res)
    def get_text(self, device: str, id: str) -> str:
        '''
        Gets the current text content of the text-like control with the given ID.
        This can be used on any control that has text, such as a button, label, or text field.
        
        :device: id of the device
        
        :id: id of the control to read
        
        :returns: currently displayed text
        '''
        res = self._client.call('PhoneIoT', 'getText', **{ 'device': device, 'id': id })
        return str(res)
    def get_toggle_state(self, device: str, id: str) -> bool:
        '''
        Gets the toggle state of a toggleable control.
        This can be used on any toggleable control, such as toggles and radio buttons.
        
        :device: id of the device
        
        :id: id of the control to read
        
        :returns: true for checked, otherwise false
        '''
        res = self._client.call('PhoneIoT', 'getToggleState', **{ 'device': device, 'id': id })
        return bool(res)
    def is_pressed(self, device: str, id: str) -> bool:
        '''
        Checks if the pressable control with the given ID is currently pressed.
        This can be used on any pressable control, which currently includes buttons, joysticks, and touchpads.
        
        By calling this RPC in a loop, you could perform some action every second while a button is held down.
        If you would instead like to receive click events, see the event optional parameter of PhoneIoT.addButton.
        
        :device: id of the device
        
        :id: id of the control to read
        
        :returns: true for pressed, otherwise false
        '''
        res = self._client.call('PhoneIoT', 'isPressed', **{ 'device': device, 'id': id })
        return bool(res)
    def listen_to_gui(self, device: str):
        '''
        This RPC requests that you receive any events from the *Graphical User Interface* (GUI) on the phone's display.
        This is needed to receive any type of GUI event, including button clicks, joystick movements, and textbox update events.
        You only need to call this RPC once, which you can do at the start of your program (but after calling PhoneIoT.setCredentials).
        
        Adding a widget/control to the device will automatically register that project to listen for GUI updates,
        so it is not typically required to call this RPC directly.
        However, this is still available in the case that a project needs to listen to events without actually creating any widgets itself
        (e.g., if another project sets up the GUI and this project only needs to listen to events).
        
        See the Display section for more information.
        
        :device: id of the device
        '''
        return self._client.call('PhoneIoT', 'listenToGUI', **{ 'device': device })
    def listen_to_sensors(self, device: str, sensors: Optional[dict] = None):
        '''
        This RPC requests that you receive periodic sensor update events from the device.
        The sensors input is a list of pairs (lists of length 2), where each pair is a sensor name and an update period in milliseconds.
        You can have different update periods for different sensors.
        You will receive a message of the same name as the sensor at most once per whatever update period you specified.
        
        Any call to this RPC will invalidate all previous calls - thus, calling it with an empty list will stop all updates.
        Alternatively, the dedicated PhoneIoT.stopSensors RPC will likewise stop all updates.
        
        This method of accessing sensor data is often easier, as it doesn't require loops or error-checking code.
        If a networking error occurs, you simply miss that single message.
        
        The PhoneIoT.getSensors RPC can be used to get a list of the valid sensor names.
        See the Sensors section for more information, esp. the required fields for each message type.
        
        :device: id of the device
        
        :sensors: structured data representing the minimum time in milliseconds between updates for each sensor type to listen for
        
          - :gravity: (float) gravity period
        
          - :gyroscope: (float) gyroscope period
        
          - :orientation: (float) orientation period
        
          - :accelerometer: (float) accelerometer period
        
          - :magneticField: (float) magneticField period
        
          - :rotation: (float) rotation period
        
          - :linearAcceleration: (float) linearAcceleration period
        
          - :gameRotation: (float) gameRotation sensor period
        
          - :lightLevel: (float) lightLevel period
        
          - :microphoneLevel: (float) microphoneLevel period
        
          - :proximity: (float) proximity period
        
          - :stepCount: (float) stepCount period
        
          - :location: (float) location period
        
          - :pressure: (float) pressure period
        
          - :temperature: (float) temperature period
        
          - :humidity: (float) humidity period
        '''
        return self._client.call('PhoneIoT', 'listenToSensors', **{ 'device': device, 'sensors': sensors })
    @deprecated()
    def _magnitude(self, vec: List[float]) -> float:
        '''
        Given a list of numbers representing a vector, this RPC returns the magnitude (length) of the vector.
        This can be used to get the total acceleration from the accelerometer (which gives a vector).
        
        :vec: the vector value
        
        :returns: magnitude of the vector (a non-negative number)
        '''
        res = self._client.call('PhoneIoT', 'magnitude', **{ 'vec': vec })
        return float(res)
    @deprecated()
    def _normalize(self, vec: List[float]) -> List[float]:
        '''
        Given a list of numbers representing a vector, returns the normalized vector (same direction but with a magnitude of 1.0).
        This is identical to dividing each component by the magnitude.
        
        :vec: the vector value
        
        :returns: the normalized vector
        '''
        res = self._client.call('PhoneIoT', 'normalize', **{ 'vec': vec })
        return _common.vectorize(float)(res)
    def remove_control(self, device: str, id: str):
        '''
        Removes a control with the given ID if it exists.
        If the control does not exist, does nothing (but still counts as success).
        If you would instead like to remove all controls, see PhoneIoT.clearControls.
        
        :device: id of the device
        
        :id: id of the control to remove
        '''
        return self._client.call('PhoneIoT', 'removeControl', **{ 'device': device, 'id': id })
    def set_credentials(self, device: str, password: str):
        '''
        This is the first RPC you should *always* call when working with PhoneIoT.
        It sets the login credentials (password) to use for all future interactions with the device.
        
        :device: id of the device
        
        :password: the password to use for accessing the device
        '''
        return self._client.call('PhoneIoT', 'setCredentials', **{ 'device': device, 'password': password })
    def set_image(self, device: str, id: str, img: Image.Image):
        '''
        Sets the displayed image of an image-like control with the given ID.
        This can be used on any control that displays images, which is currently only image displays.
        
        :device: id of the device
        
        :id: the id of the control to modify
        
        :img: the new image to display
        '''
        return self._client.call('PhoneIoT', 'setImage', **{ 'device': device, 'id': id, 'img': img })
    def set_level(self, device: str, id: str, value: float) -> float:
        '''
        Set the current value (a single number) of a value-like control.
        Currently, the only supported control is a slider, which sets the displayed value.
        
        Note that you can use this RPC even if the control was set to readonly = true (readonly is only a restriction for the user).
        
        :device: id of the device
        
        :id: id of the control to read
        
        :value: new value to set
        
        :returns: current value
        '''
        res = self._client.call('PhoneIoT', 'setLevel', **{ 'device': device, 'id': id, 'value': value })
        return float(res)
    def set_text(self, device: str, id: str, text: Optional[str] = None):
        '''
        Sets the text content of the text-like control with the given ID.
        This can be used on any control that has text, such as a button, label, or text field.
        
        :device: id of the device
        
        :id: id of the control to modify
        
        :text: The new text to display (defaults to empty)
        '''
        return self._client.call('PhoneIoT', 'setText', **{ 'device': device, 'id': id, 'text': text })
    def set_toggle_state(self, device: str, id: str, state: bool):
        '''
        Sets the toggle state of a toggleable control with the given ID.
        This can be used on any toggleable control, such as toggles and radio buttons.
        If state is true, the toggleable becomes checked, otherwise it is unchecked.
        
        If used on a radio button, it sets the state independent of the control's group.
        That is, although the user can't select multiple radio buttons in the same group, you can do so programmatically through this RPC.
        
        :device: id of the device
        
        :id: id of the control to modify
        
        :state: new value for the toggle state
        '''
        return self._client.call('PhoneIoT', 'setToggleState', **{ 'device': device, 'id': id, 'state': state })
    def stop_sensors(self, device: str):
        '''
        Stops outgoing sensor updates that were previously requested by PhoneIoT.listenToSensors.
        This is equivalent to calling PhoneIoT.listenToSensors with an empty sensors list,
        but is provided as a separate RPC for convenience and discoverability.
        
        :device: id of the device
        '''
        return self._client.call('PhoneIoT', 'stopSensors', **{ 'device': device })
    def vibrate(self, device: str, durations: Any, strength: Optional[float] = None):
        '''
        Causes the phone to vibrate with a specified duration (in seconds) and strength.
        durations can either be a single number representing a continuous vibration for that amount of time (in seconds), or it can be a list of durations.
        For instance, [1, 0.5, 2] would mean: vibrate for 1 second, stop for 0.5 seconds, then vibrate for 2 seconds.
        
        Some older devices lack support for customizable vibration patterns/durations,
        in which case PhoneIoT may have to resort to an approximation of the desired pattern using longer vibrations.
        
        :device: id of the device
        
        :durations: the duration of a vibration or a pattern of on/off times
        
        :strength: the strength of vibration (default 100)
        '''
        return self._client.call('PhoneIoT', 'vibrate', **{ 'device': device, 'durations': durations, 'strength': strength })
class Pixabay:
    '''
    The Pixabay Service provides access to free images released under Creative Commons CC0.
    For more information, check out https://pixabay.com
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_image(self, url: str) -> Image.Image:
        '''
        Retrieve an image from Pixabay from the URL
        
        :url: URL of the image to retrieve
        
        :returns: the requested image
        '''
        return self._client.call('Pixabay', 'getImage', **{ 'url': url })
    def search_all(self, keywords: str, max_height: Optional[float] = None, min_height: Optional[float] = None) -> List[dict]:
        '''
        Search Pixabay for an image matching the keywords.
        The returned data is a list of structeud data objects containing information about each matching image.
        Notably, the image_url field of each match can be passed to Pixabay.getImage.
        
        :keywords: Search query
        
        :max_height: Restrict query to images smaller than maxHeight
        
        :min_height: Restrict query to images larger than minHeight
        
        :returns: list of matching images
        '''
        res = self._client.call('Pixabay', 'searchAll', **{ 'keywords': keywords, 'maxHeight': max_height, 'minHeight': min_height })
        return _common.vectorize(dict)(res)
    def search_illustration(self, keywords: str, max_height: Optional[float] = None, min_height: Optional[float] = None) -> List[dict]:
        '''
        Search Pixabay for an illustration matching the keywords.
        This is identical to Pixabay.searchAll except that only illustrations are returned.
        
        :keywords: Search query
        
        :max_height: Restrict query to images smaller than maxHeight
        
        :min_height: Restrict query to images larger than minHeight
        
        :returns: list of matching images
        '''
        res = self._client.call('Pixabay', 'searchIllustration', **{ 'keywords': keywords, 'maxHeight': max_height, 'minHeight': min_height })
        return _common.vectorize(dict)(res)
    def search_photo(self, keywords: str, max_height: Optional[float] = None, min_height: Optional[float] = None) -> List[dict]:
        '''
        Search Pixabay for a photo matching the keywords.
        This is identical to Pixabay.searchAll except that only photos are returned.
        
        :keywords: Search query
        
        :max_height: Restrict query to images smaller than maxHeight
        
        :min_height: Restrict query to images larger than minHeight
        
        :returns: list of matching images
        '''
        res = self._client.call('Pixabay', 'searchPhoto', **{ 'keywords': keywords, 'maxHeight': max_height, 'minHeight': min_height })
        return _common.vectorize(dict)(res)
class ProjectGutenberg:
    '''
    The Project Gutenberg service provides access to public domain books. For more information, check out https://project-gutenberg.org/.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_info(self, id: str) -> list:
        '''
        Get information about a given book including title and author.
        
        :id: Book ID
        
        :returns: 
        '''
        return self._client.call('ProjectGutenberg', 'getInfo', **{ 'ID': id })
    def get_text(self, id: str) -> str:
        '''
        Get the URL for the full text of a given book.
        
        :id: Book ID
        
        :returns: 
        '''
        res = self._client.call('ProjectGutenberg', 'getText', **{ 'ID': id })
        return str(res)
    def search(self, field: str, text: str) -> List[str]:
        '''
        Search for a book given title text and optional advanced options. Returns a list of up to 100 book IDs.
        
        :field: 
        
        :text: 
        
        :returns: 
        '''
        res = self._client.call('ProjectGutenberg', 'search', **{ 'field': field, 'text': text })
        return _common.vectorize(str)(res)
class PublicRoles:
    '''
    The PublicRoles Service provides access to the user's public role
    ID programmatically. This enables communication between projects.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_public_role_id(self) -> str:
        '''
        Get the public role ID for the current role.
        
        :returns: the public role ID
        '''
        res = self._client.call('PublicRoles', 'getPublicRoleId', **{  })
        return str(res)
    @deprecated()
    def _request_public_role_id(self):
        '''
        Get the public role ID for the current role.
        '''
        return self._client.call('PublicRoles', 'requestPublicRoleId', **{  })
class RainViewer:
    '''
    This service provides access to the RainViewer (https://www.rainviewer.com/api.html) aggregated database.
    RainViewer provides access to recent and forecasted weather radar maps all around the world.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_color_schemes(self) -> List[str]:
        '''
        Get the list of valid color schemes for the RainViewer.getOverlay RPC.
        
        :returns: The list of valid color schemes.
        '''
        res = self._client.call('RainViewer', 'getColorSchemes', **{  })
        return _common.vectorize(str)(res)
    def get_overlay(self, latitude: float, longitude: float, width: int, height: int, zoom: int, time_offset: Optional[str] = None, options: Optional[dict] = None) -> Image.Image:
        '''
        Gets a transparent overlay that can be placed directly on to of a map provided by GoogleMaps.getMap
        to display recent or forecasted weather radar data.
        
        :latitude: Latitude of the returned map (centered).
        
        :longitude: Longitude of the returned map (centered).
        
        :width: Width (in pixels) of the returned map.
        
        :height: Height (in pixels) of the returned map.
        
        :zoom: The zoom level of the returned image (see the /services/GoogleMaps/index service).
        
        :time_offset: The time offset of the desired forecast (defaults to now, which represents current weather).
        
        :options: Additional drawing options.
        
          - :smooth: (bool) If set to true, smooths the radar overlay in the returned image to be more aesthetically pleasing (default true).
        
          - :showSnow: (bool) If set to true, renders snow as a separate color from normal precipitation (default false).
        
          - :colorScheme: (str) An integer denoting the color scheme to use in the returned image (default 4).
        
        :returns: The rendered radar data overlay.
        '''
        return self._client.call('RainViewer', 'getOverlay', **{ 'latitude': latitude, 'longitude': longitude, 'width': width, 'height': height, 'zoom': zoom, 'timeOffset': time_offset, 'options': options })
    def get_time_offsets(self) -> List[str]:
        '''
        Get the list of valid radar time offsets for the RainViewer.getOverlay RPC.
        The returned time offsets are in chronological order.
        
        :returns: The list of valid time offsets in chronological order.
        '''
        res = self._client.call('RainViewer', 'getTimeOffsets', **{  })
        return _common.vectorize(str)(res)
class RoboScape:
    
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    @deprecated()
    def _eavesdrop(self, robots: Any):
        '''
        Registers for receiving messages from the given robots.
        
        :robots: one or a list of robots
        '''
        return self._client.call('RoboScape', 'eavesdrop', **{ 'robots': robots })
    def get_robots(self) -> List[str]:
        '''
        Returns the MAC addresses of all authorized robots.
        
        :returns: 
        '''
        res = self._client.call('RoboScape', 'getRobots', **{  })
        return _common.vectorize(str)(res)
    def listen(self, robots: Any):
        '''
        Registers for receiving messages from the given robots.
        
        :robots: one or a list of robots
        '''
        return self._client.call('RoboScape', 'listen', **{ 'robots': robots })
    def send(self, robot: str, command: str) -> str:
        '''
        Sends a textual command to the robot
        
        :robot: name of the robot (matches at the end)
        
        :command: textual command
        
        :returns: textual response
        '''
        res = self._client.call('RoboScape', 'send', **{ 'robot': robot, 'command': command })
        return str(res)
class ServiceCreation:
    '''
    The ServiceCreation Service enables users to create custom services. Custom
    Services can be found under the "Community" section using the call <RPC>
    block.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def create_service_from_table(self, name: str, data: list, options: Optional[dict] = None):
        '''
        Create a service using a given dataset.
        
        :name: Service name
        
        :data: 2D list of data
        
        :options: Options (for details, check out ServiceCreation.getCreateFromTableOptions)
        '''
        return self._client.call('ServiceCreation', 'createServiceFromTable', **{ 'name': name, 'data': data, 'options': options })
    def delete_service(self, name: str):
        '''
        Delete an existing service.
        
        :name: Service name
        '''
        return self._client.call('ServiceCreation', 'deleteService', **{ 'name': name })
    def get_create_from_table_options(self, data: list):
        '''
        Get the default settings for a given dataset.
        
        :data: 2D list of data
        '''
        return self._client.call('ServiceCreation', 'getCreateFromTableOptions', **{ 'data': data })
class SharedCanvas:
    '''
    SharedCanvas is a service that lets all NetsBlox users view and edit a shared canvas (image).
    Users can view the canvas, or edit it pixel by pixel.
    However, there is a cooldown between canvas edits, meaning one user cannot dominate the entire canvas.
    
    SharedCanvas was inspired by Place (https://en.wikipedia.org/wiki/R/place), which was
    a social experiment started on Reddit that functioned in much the same way. Place came to capture
    Reddit's online culture through the combined efforts of many users striving to control the canvas
    and display their own images.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_cooldown(self) -> float:
        '''
        Gets the edit cooldown time (in seconds) that is imposed after each edit.
        
        :returns: Edit cooldown (in seconds).
        '''
        res = self._client.call('SharedCanvas', 'getCooldown', **{  })
        return float(res)
    def get_cooldown_remaining(self) -> float:
        '''
        Gets the amount of cooldown time remaining (in seconds) before the next edit can be made on this account.
        If this is 0, then the cooldown has expired and you can make your next edit.
        
        :returns: Remaining cooldown time (in seconds), or 0 if no cooldown remaining.
        '''
        res = self._client.call('SharedCanvas', 'getCooldownRemaining', **{  })
        return float(res)
    def get_edit_count(self) -> int:
        '''
        Gets the total number of edits that have been made (successfully) on this account.
        
        :returns: Total number of edits that have been made on this account.
        '''
        res = self._client.call('SharedCanvas', 'getEditCount', **{  })
        return int(res)
    def get_height(self) -> int:
        '''
        Gets the current canvas height.
        
        :returns: The canvas height.
        '''
        res = self._client.call('SharedCanvas', 'getHeight', **{  })
        return int(res)
    def get_image(self, x: Optional[int] = None, y: Optional[int] = None, width: Optional[int] = None, height: Optional[int] = None, scale: Optional[int] = None) -> Image.Image:
        '''
        Gets a snapshot of the current canvas as an image.
        The arguments to this function can be used to retrieve a specific region of the canvas,
        or they can all be omitted to grab a snapshot of the entire canvas.
        
        :x: X position of the top left corner to grab (default 0).
        
        :y: Y position of the top left corner to grab (default 0).
        
        :width: Width of the returned image to grab (default goes all the way to the right).
        
        :height: Height of the returned image to grab (default goes all the way to the bottom).
        
        :scale: Zoom scale of the returned image (final size cannot be larger than the full canvas) (default 1).
        
        :returns: The requested slice of the current canvas as an image.
        '''
        return self._client.call('SharedCanvas', 'getImage', **{ 'x': x, 'y': y, 'width': width, 'height': height, 'scale': scale })
    def get_pixel(self, x: int, y: int) -> list:
        '''
        Gets the color of the specified pixel in the image.
        
        :x: X coordinate of the pixel to read.
        
        :y: Y coordinate of the pixel to read.
        
        :returns: The pixel color at the given location.
        '''
        return self._client.call('SharedCanvas', 'getPixel', **{ 'x': x, 'y': y })
    def get_size(self) -> list:
        '''
        Gets the current canvas size.
        
        :returns: The width and height of the canvas, as a list.
        '''
        return self._client.call('SharedCanvas', 'getSize', **{  })
    def get_width(self) -> int:
        '''
        Gets the current canvas width.
        
        :returns: The canvas width.
        '''
        res = self._client.call('SharedCanvas', 'getWidth', **{  })
        return int(res)
    def set_pixel(self, x: int, y: int, color: list) -> bool:
        '''
        Sets the color of the specified pixel in the image.
        
        After making an edit, your account is placed in a cooldown mode where no other edits can be made for a short period.
        If you are not signed in, you will be counted as a special guest account, which all share the same cooldown timer.
        Because of this, it is advised to sign in before using this service, esp. if you want to make many edits.
        
        :x: X coordinate of the pixel to read.
        
        :y: Y coordinate of the pixel to read.
        
        :color: The new color to set at the given location.
        
        :returns: true if the edit was successful, otherwise false (attempt to edit during cooldown).
        '''
        res = self._client.call('SharedCanvas', 'setPixel', **{ 'x': x, 'y': y, 'color': color })
        return bool(res)
class SimpleHangman:
    '''
    The SimpleHangman Service provides RPCs for playing single player hangman.
    The service will choose a word for the player to guess using the given RPCs.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_currently_known_word(self) -> str:
        '''
        Get the current word with where unknown letters are replaced with "_".
        
        :returns: current word with blanks
        '''
        res = self._client.call('SimpleHangman', 'getCurrentlyKnownWord', **{  })
        return str(res)
    def get_wrong_count(self) -> int:
        '''
        Get the current number of incorrect guesses.
        
        :returns: number of wrong guesses
        '''
        res = self._client.call('SimpleHangman', 'getWrongCount', **{  })
        return int(res)
    def guess(self, letter: str):
        '''
        Guess a letter in the current word.
        
        :letter: 
        '''
        return self._client.call('SimpleHangman', 'guess', **{ 'letter': letter })
    def is_word_guessed(self) -> bool:
        '''
        Check if the current word has been guessed correctly.
        
        :returns: true if word was guessed correctly
        '''
        res = self._client.call('SimpleHangman', 'isWordGuessed', **{  })
        return bool(res)
    def restart(self, word: Optional[str] = None) -> bool:
        '''
        Restart the current game.
        
        :word: New word to guess
        
        :returns: true on successful restart
        '''
        res = self._client.call('SimpleHangman', 'restart', **{ 'word': word })
        return bool(res)
class SoundClips:
    '''
    This service allows users to play songs.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_drum_loop_names(self, pack_name: Optional[str] = None, bpm: Optional[str] = None) -> str:
        '''
        Get drum loops based on query.
        
        :pack_name: 
        
        :bpm: 
        
        :returns: 
        '''
        res = self._client.call('SoundClips', 'getDrumLoopNames', **{ 'packName': pack_name, 'bpm': bpm })
        return str(res)
    def get_drum_one_shot_names(self, pack_name: Optional[str] = None, drum_type: Optional[str] = None) -> str:
        '''
        Get sounds based on query.
        
        :pack_name: 
        
        :drum_type: 
        
        :returns: 
        '''
        res = self._client.call('SoundClips', 'getDrumOneShotNames', **{ 'packName': pack_name, 'drumType': drum_type })
        return str(res)
    def get_fx_sound_names(self) -> list:
        '''
        Get fx sounds
        
        :returns: 
        '''
        return self._client.call('SoundClips', 'getFXSoundNames', **{  })
    def get_sound_names(self, chords: Optional[str] = None, key: Optional[str] = None, bpm: Optional[str] = None, instrument_name: Optional[str] = None) -> list:
        '''
        Get sounds based on query.
        
        :chords: 
        
        :key: 
        
        :bpm: 
        
        :instrument_name: 
        
        :returns: 
        '''
        return self._client.call('SoundClips', 'getSoundNames', **{ 'chords': chords, 'key': key, 'bpm': bpm, 'instrumentName': instrument_name })
    def get_sound_names_by_instrument(self, instrument_family: Optional[str] = None, key: Optional[str] = None, bpm: Optional[str] = None) -> list:
        '''
        Get sounds based on query.
        
        :instrument_family: synth, guitar, brass, etc.
        
        :key: C, D, Eb, etc.
        
        :bpm: e.g., 90BPM
        
        :returns: 
        '''
        return self._client.call('SoundClips', 'getSoundNamesByInstrument', **{ 'instrumentFamily': instrument_family, 'key': key, 'bpm': bpm })
    def name_to_sound(self, name_of_sound: Optional[str] = None):
        '''
        Get sound by name.
        
        :name_of_sound: 
        '''
        return self._client.call('SoundClips', 'nameToSound', **{ 'nameOfSound': name_of_sound })
class StarMap:
    '''
    The StarMap Service provides access to astronomy data using Sloan Digital Sky Survey.
    For more information, check out http://skyserver.sdss.org/dr14/en/home.aspx
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def arc_hour_min_sec_to_deg(self, arc_hour: float, arc_min: float, arc_sec: float):
        '''
        Convert arc to degree.
        
        :arc_hour: 
        
        :arc_min: 
        
        :arc_sec: 
        '''
        return self._client.call('StarMap', 'arcHourMinSecToDeg', **{ 'arcHour': arc_hour, 'arcMin': arc_min, 'arcSec': arc_sec })
    def find_object(self, name: str):
        '''
        Search for significant object in the sky.
        
        :name: 
        '''
        return self._client.call('StarMap', 'findObject', **{ 'name': name })
    def get_image(self, right_ascension: float, declination: float, arcseconds_per_pixel: float, options: str, width: Optional[float] = None, height: Optional[float] = None):
        '''
        Get an image of the sky at the given coordinates.
        
        :right_ascension: 
        
        :declination: 
        
        :arcseconds_per_pixel: 
        
        :options: 
        
        :width: 
        
        :height: 
        '''
        return self._client.call('StarMap', 'getImage', **{ 'right_ascension': right_ascension, 'declination': declination, 'arcseconds_per_pixel': arcseconds_per_pixel, 'options': options, 'width': width, 'height': height })
class Thingspeak:
    '''
    The ThingSpeak Service provides access to the ThingSpeak IoT analytics platform.
    For more information, check out https://thingspeak.com/.
    
    Terms of use: https://thingspeak.com/pages/terms
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def channel_details(self, id: float) -> dict:
        '''
        Get various details about the channel, including location, fields, tags and name.
        
        :id: channel ID
        
        :returns: Channel details.
        '''
        res = self._client.call('Thingspeak', 'channelDetails', **{ 'id': id })
        return dict(res)
    def channel_feed(self, id: str, num_result: float):
        '''
        Get channel feed.
        
        :id: 
        
        :num_result: 
        '''
        return self._client.call('Thingspeak', 'channelFeed', **{ 'id': id, 'numResult': num_result })
    def private_channel_feed(self, id: str, num_result: float, api_key: str):
        '''
        Request data from a private channel
        
        :id: ID of the private channel feed
        
        :num_result: Number of results to fetch
        
        :api_key: Thingspeak API key
        '''
        return self._client.call('Thingspeak', 'privateChannelFeed', **{ 'id': id, 'numResult': num_result, 'apiKey': api_key })
    def search_by_location(self, latitude: float, longitude: float, distance: Optional[float] = None, limit: Optional[float] = None, updated_since: Optional[str] = None) -> List[dict]:
        '''
        Search for channels by location.
        
        :latitude: latitude to search near
        
        :longitude: longitude to search near
        
        :distance: max distance from location in meters (default 100000 = 100Km)
        
        :limit: max number of results to return (default 15)
        
        :updated_since: only include results which have (some) new data since this date (default no time-based filtering)
        
        :returns: search results
        '''
        res = self._client.call('Thingspeak', 'searchByLocation', **{ 'latitude': latitude, 'longitude': longitude, 'distance': distance, 'limit': limit, 'updatedSince': updated_since })
        return _common.vectorize(dict)(res)
    def search_by_tag(self, tag: str, limit: Optional[float] = None, updated_since: Optional[str] = None) -> List[dict]:
        '''
        Search for ThingSpeak channels by tag.
        
        :tag: tag to search for
        
        :limit: max number of results to return (default 15)
        
        :updated_since: only include results which have (some) new data since this date (default no time-based filtering)
        
        :returns: search results
        '''
        res = self._client.call('Thingspeak', 'searchByTag', **{ 'tag': tag, 'limit': limit, 'updatedSince': updated_since })
        return _common.vectorize(dict)(res)
    def search_by_tag_and_location(self, tag: str, latitude: float, longitude: float, distance: Optional[float] = None, limit: Optional[float] = None, updated_since: Optional[str] = None) -> List[dict]:
        '''
        Search for channels by tag and location.
        
        :tag: tag to search for
        
        :latitude: latitude to search near
        
        :longitude: longitude to search near
        
        :distance: max distance from location in meters (default 100000 = 100Km)
        
        :limit: max number of results to return (default 15)
        
        :updated_since: only include results which have (some) new data since this date (default no time-based filtering)
        
        :returns: search results
        '''
        res = self._client.call('Thingspeak', 'searchByTagAndLocation', **{ 'tag': tag, 'latitude': latitude, 'longitude': longitude, 'distance': distance, 'limit': limit, 'updatedSince': updated_since })
        return _common.vectorize(dict)(res)
class ThisXDoesNotExist:
    '''
    This service uses Artificial Intelligence (AI) to make random, realistic images.
    For a list of example websites, see https://thisxdoesnotexist.com/.
    These are typically made by a Generative Adversarial neural Network (GAN).
    Put simply, this involves two AIs: one to make images and another to guess if they're real or fake, and making them compete to mutually improve.
    For more information, see https://en.wikipedia.org/wiki/Generative_adversarial_network.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    @deprecated()
    def _get_artwork(self) -> Image.Image:
        '''
        Gets an image of an artwork that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getArtwork', **{  })
    @deprecated()
    def _get_cat(self) -> Image.Image:
        '''
        Gets an image of a cat that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getCat', **{  })
    def get_congress_person(self) -> Image.Image:
        '''
        Gets an image of a congress person that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getCongressPerson', **{  })
    def get_fursona(self) -> Image.Image:
        '''
        Gets an image of a fursona that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getFursona', **{  })
    @deprecated()
    def _get_home_interior(self) -> Image.Image:
        '''
        Gets an image of a home interior that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getHomeInterior', **{  })
    @deprecated()
    def _get_horse(self) -> Image.Image:
        '''
        Gets an image of a horse that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getHorse', **{  })
    @deprecated()
    def _get_person(self) -> Image.Image:
        '''
        Gets an image of a person that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getPerson', **{  })
    def get_pony(self) -> Image.Image:
        '''
        Gets an image of a pony that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getPony', **{  })
    def get_waifu(self) -> Image.Image:
        '''
        Gets an image of a waifu that does not exist
        
        :returns: a random image of the given type
        '''
        return self._client.call('ThisXDoesNotExist', 'getWaifu', **{  })
class TimeSync:
    '''
    TimeSync is a tool for measuring the latency and clock offset between your NetsBlox client and the NetsBlox server.
    This can be used to have more precise timings for message passing and other time-based synchronization tasks.
    
    To use this service, you first call TimeSync.prepare, followed by performing several (e.g., 100) calls
    to TimeSync.step, and then finishing with TimeSync.complete to get the computed timing metrics.
    
    Note that the calls to TimeSync.step are intended to be back-to-back.
    You should perform this in a loop that does nothing else.
    In particular, you should not sleep/wait inside the loop; if you need this,
    you may provide a sleepTime to TimeSync.prepare and it will do the sleeping/waiting for you (do not also sleep yourself).
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def complete(self) -> dict:
        '''
        Completes a timing operation started by TimeSync.prepare and returns the summarized timing metrics.
        
        :returns: Information about the computed timing metrics.
        '''
        res = self._client.call('TimeSync', 'complete', **{  })
        return dict(res)
    def prepare(self, sleep_time: Optional[float] = None) -> dict:
        '''
        Prepares to receive a new sequence of time steps.
        The return value of this RPC includes the minimum and maximum number of times
        TimeSync.step must be called before calling TimeSync.complete.
        
        :sleep_time: Amount of time (in seconds) to automatically wait between steps (default 0.1).
        
        :returns: Information about the min and max number of steps that can be performed.
        '''
        res = self._client.call('TimeSync', 'prepare', **{ 'sleepTime': sleep_time })
        return dict(res)
    def step(self):
        '''
        Adds a time step to the data pool.
        You must call TimeSync.prepare before calling this RPC.
        '''
        return self._client.call('TimeSync', 'step', **{  })
class Translation:
    '''
    Uses Microsoft's Azure Cognitive Services API to translate text.
    For more information, check out https://azure.microsoft.com/en-us/pricing/details/cognitive-services/translator-text-api/.
    
    Terms of use: https://www.microsoft.com/en-us/servicesagreement
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def detect_language(self, text: str) -> str:
        '''
        Attempt to detect language of input text
        
        :text: Text in an unknown language
        
        :returns: Abbreviation for name of language detected in text
        '''
        res = self._client.call('Translation', 'detectLanguage', **{ 'text': text })
        return str(res)
    def get_supported_languages(self) -> list:
        '''
        Attempt to detect language of input text
        
        :returns: List of languages supported by the translator
        '''
        return self._client.call('Translation', 'getSupportedLanguages', **{  })
    def to_english(self, text: str) -> str:
        '''
        Translate text to English
        
        :text: Text in another language
        
        :returns: Text translated to English
        '''
        res = self._client.call('Translation', 'toEnglish', **{ 'text': text })
        return str(res)
    def translate(self, text: str, to: str, _from: Optional[str] = None) -> str:
        '''
        Translate text between languages
        
        :text: Text in another language
        
        :to: Language to translate to
        
        :_from: Language to translate from (auto-detects if not specified)
        
        :returns: Text translated to requested language
        '''
        res = self._client.call('Translation', 'translate', **{ 'text': text, 'to': to, 'from': _from })
        return str(res)
class Trivia:
    '''
    The Trivia Service provides access to trivia questions using the jservice API.
    For more information, check out https://jservice.io.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_random_question(self) -> dict:
        '''
        Get a random trivia question.
        This includes the question, answer, and additional information.
        
        :returns: structured data representing the trivia question
        '''
        res = self._client.call('Trivia', 'getRandomQuestion', **{  })
        return dict(res)
    @deprecated()
    def _random(self) -> str:
        '''
        Get random trivia question.
        
        :returns: 
        '''
        res = self._client.call('Trivia', 'random', **{  })
        return str(res)
class TwentyQuestions:
    '''
    The TwentyQuestions Service aids in the creation of a multiplayer
    game of twenty questions.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def answer(self, answer: str):
        '''
        Answer a yes or no question about the secret word or phrase.
        
        :answer: yes or no response to previous question
        '''
        return self._client.call('TwentyQuestions', 'answer', **{ 'answer': answer })
    def game_started(self) -> bool:
        '''
        Check if the game has been started.
        
        :returns: true if the game has started
        '''
        res = self._client.call('TwentyQuestions', 'gameStarted', **{  })
        return bool(res)
    def guess(self, guess: str) -> bool:
        '''
        Guess the word or phrase.
        
        :guess: word or phrase to guess
        
        :returns: true if the guess was correct, otherwise false
        '''
        res = self._client.call('TwentyQuestions', 'guess', **{ 'guess': guess })
        return bool(res)
    def restart(self):
        '''
        Restart the game.
        '''
        return self._client.call('TwentyQuestions', 'restart', **{  })
    def start(self, answer: str) -> bool:
        '''
        Start a new game of twenty questions.
        
        :answer: The word or phrase to guess
        
        :returns: true on successful start
        '''
        res = self._client.call('TwentyQuestions', 'start', **{ 'answer': answer })
        return bool(res)
class WaterWatch:
    '''
    The WaterWatch Service provides access to real-time water data.
    For more information, check out https://waterservices.usgs.gov/
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def gage_height(self, min_latitude: float, max_latitude: float, min_longitude: float, max_longitude: float):
        '''
        Get the water data for sites within a bounding box.
        For help interpreting this data, see https://help.waterdata.usgs.gov/tutorials/surface-water-data/how-do-i-interpret-gage-height-and-streamflow-values
        
        :min_latitude: Minimum latitude of bounding box
        
        :max_latitude: Maximum latitude of bounding box
        
        :min_longitude: Minimum longitude of bounding box
        
        :max_longitude: Maximum longitude of bounding box
        '''
        return self._client.call('WaterWatch', 'gageHeight', **{ 'minLatitude': min_latitude, 'maxLatitude': max_latitude, 'minLongitude': min_longitude, 'maxLongitude': max_longitude })
    def stop(self) -> int:
        '''
        Stop sending messages from this service.
        
        :returns: Number of messages stopped.
        '''
        res = self._client.call('WaterWatch', 'stop', **{  })
        return int(res)
    def stream_flow(self, min_latitude: float, max_latitude: float, min_longitude: float, max_longitude: float):
        '''
        Get stream flow data for sites within a bounding box.
        For help interpreting this data, see https://help.waterdata.usgs.gov/tutorials/surface-water-data/how-do-i-interpret-gage-height-and-streamflow-values
        
        :min_latitude: Minimum latitude of bounding box
        
        :max_latitude: Maximum latitude of bounding box
        
        :min_longitude: Minimum longitude of bounding box
        
        :max_longitude: Maximum longitude of bounding box
        '''
        return self._client.call('WaterWatch', 'streamFlow', **{ 'minLatitude': min_latitude, 'maxLatitude': max_latitude, 'minLongitude': min_longitude, 'maxLongitude': max_longitude })
    def water_temp(self, min_latitude: float, max_latitude: float, min_longitude: float, max_longitude: float):
        '''
        Get the water temperature data for sites within a bounding box.
        
        :min_latitude: Minimum latitude of bounding box
        
        :max_latitude: Maximum latitude of bounding box
        
        :min_longitude: Minimum longitude of bounding box
        
        :max_longitude: Maximum longitude of bounding box
        '''
        return self._client.call('WaterWatch', 'waterTemp', **{ 'minLatitude': min_latitude, 'maxLatitude': max_latitude, 'minLongitude': min_longitude, 'maxLongitude': max_longitude })
class Weather:
    '''
    The Weather Service provides access to real-time weather data using OpenWeatherMap.
    For more information, check out https://openweathermap.org/.
    
    Terms of Service: https://openweathermap.org/terms
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def description(self, latitude: float, longitude: float):
        '''
        Get a short description of the current weather for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'description', **{ 'latitude': latitude, 'longitude': longitude })
    def humidity(self, latitude: float, longitude: float):
        '''
        Get the current humidity for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'humidity', **{ 'latitude': latitude, 'longitude': longitude })
    def icon(self, latitude: float, longitude: float):
        '''
        Get a small icon of the current weather for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'icon', **{ 'latitude': latitude, 'longitude': longitude })
    @deprecated()
    def _temp(self, latitude: float, longitude: float):
        '''
        Get the current temperature for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'temp', **{ 'latitude': latitude, 'longitude': longitude })
    def temperature(self, latitude: float, longitude: float):
        '''
        Get the current temperature for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'temperature', **{ 'latitude': latitude, 'longitude': longitude })
    def wind_angle(self, latitude: float, longitude: float):
        '''
        Get the current wind direction for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'windAngle', **{ 'latitude': latitude, 'longitude': longitude })
    def wind_speed(self, latitude: float, longitude: float):
        '''
        Get the current wind speed for a given location.
        
        :latitude: 
        
        :longitude: 
        '''
        return self._client.call('Weather', 'windSpeed', **{ 'latitude': latitude, 'longitude': longitude })
class Wildcam:
    '''
    Wildcam provides access to wildlife images from around the world.
    
    Current data sources:
    
    - Zooniverse (https://classroom.zooniverse.org/#/wildcam-gorongosa-lab/explorers/map/)
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_cameras(self, latitude: Optional[float] = None, longitude: Optional[float] = None, radius: Optional[float] = None) -> List[dict]:
        '''
        Returns all the cameras that are stored in the database, optionally filtering by proximity to a central location.
        
        :latitude: Filters results to only cameras within a given distance from a central location. Requires longitude and radius also be set.
        
        :longitude: Filters results to only cameras within a given distance from a central location. Requires latitude and radius also be set.
        
        :radius: Filters results to only cameras within a given distance (in meters) from a central location. Requires latitude and longitude also be set.
        
        :returns: All found cameras
        '''
        res = self._client.call('Wildcam', 'getCameras', **{ 'latitude': latitude, 'longitude': longitude, 'radius': radius })
        return _common.vectorize(dict)(res)
    def get_image(self, entry: dict) -> Image.Image:
        '''
        Gets the image associated with a given entry.
        The provided entry should be exactly the format that was returned by one of the various search RPCs in this service.
        
        :entry: The search entry to get an image of
        
        :returns: The snapshot associated with the given entry
        '''
        return self._client.call('Wildcam', 'getImage', **{ 'entry': entry })
    def get_species_list(self) -> List[str]:
        '''
        Returns all the valid species that can be used by Wildcam.search.
        
        :returns: All valid species in alphabetical order.
        '''
        res = self._client.call('Wildcam', 'getSpeciesList', **{  })
        return _common.vectorize(str)(res)
    def search(self, start_date: Optional[str] = None, stop_date: Optional[str] = None, species: Optional[str] = None, latitude: Optional[float] = None, longitude: Optional[float] = None, radius: Optional[float] = None) -> List[dict]:
        '''
        Searches the database for wildlife camera entries.
        Each return value includes information about the contents of its associated image.
        You can pass an entry to Wildcam.getImage to get the actual image being described.
        
        :start_date: The earliest date to include in the results. If omitted, no starting cutoff is used for filtering.
        
        :stop_date: The latest date to include in the results. If omitted, no stopping cutoff is used for filtering.
        
        :species: Filters results to only entries which contained the requested species. If omitted, no species filtering is performed.
        
        :latitude: Filters results to only entries within a given distance from a central location. Requires longitude and radius also be set.
        
        :longitude: Filters results to only entries within a given distance from a central location. Requires latitude and radius also be set.
        
        :radius: Filters results to only entries within a given distance (in meters) from a central location. Requires latitude and longitude also be set.
        
        :returns: All data entries matching the search, in chronological order
        '''
        res = self._client.call('Wildcam', 'search', **{ 'startDate': start_date, 'stopDate': stop_date, 'species': species, 'latitude': latitude, 'longitude': longitude, 'radius': radius })
        return _common.vectorize(dict)(res)
    def search_by_camera(self, start_date: Optional[str] = None, stop_date: Optional[str] = None, species: Optional[str] = None, camera: Optional[dict] = None) -> List[dict]:
        '''
        Equivalent to Wildcam.search, but can filter to only images taken by a specific camera.
        
        :start_date: The earliest date to include in the results. If omitted, no starting cutoff is used for filtering.
        
        :stop_date: The latest date to include in the results. If omitted, no stopping cutoff is used for filtering.
        
        :species: Filters results to only entries which contained the requested species. If omitted, no species filtering is performed.
        
        :camera: Filters results to only entries taken by a specific camera. If omitted, no camera-based filtering is performed.
        
        :returns: All data entries matching the search, in chronological order
        '''
        res = self._client.call('Wildcam', 'searchByCamera', **{ 'startDate': start_date, 'stopDate': stop_date, 'species': species, 'camera': camera })
        return _common.vectorize(dict)(res)
class WordGuess:
    '''
    A simple Wordle-like word guessing game.
    '''
    def __init__(self, client):
        self._client = client
    def __getattr__(self, attr):
        if isinstance(attr, str) and not attr.startswith('_'):
            res = getattr(self, f'_{attr}', None)
            if res is not None: return res
        raise AttributeError(f'No attribute {attr}')
    def get_word_list(self, length: int) -> List[str]:
        '''
        Get a list of all the possible words given a word length
        
        :length: Length of word
        
        :returns: word list
        '''
        res = self._client.call('WordGuess', 'getWordList', **{ 'length': length })
        return _common.vectorize(str)(res)
    def give_up(self):
        '''
        Give up on the current game and learn the target word
        '''
        return self._client.call('WordGuess', 'giveUp', **{  })
    def guess(self, word: str):
        '''
        Guess the word. Returns a list where each item is the feedback for
        the corresponding character. Feedback is a "3" if the character is
        correct, "2" if it is correct but in the wrong place, and "1" if the
        letter is not present in the word.
        
        :word: Guess for this round
        '''
        return self._client.call('WordGuess', 'guess', **{ 'word': word })
    def start(self, length: Optional[int] = None):
        '''
        Start the guessing game by having the computer choose a random word
        with the given length.
        
        :length: Length of word to search for (default 5)
        '''
        return self._client.call('WordGuess', 'start', **{ 'length': length })