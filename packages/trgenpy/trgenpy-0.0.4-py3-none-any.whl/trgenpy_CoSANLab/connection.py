from .trigger import Trigger
from .trigger_pin import TriggerPin
from .instruction import active_for_us, unactive_for_us, repeat, end, not_admissible
import socket
import time

# Command encoding/decoding (as per gui_trigger.c)
CMD_PACKET_PROGRAM = 0x01
CMD_PACKET_START   = 0x02
CMD_SET_GPIO       = 0x03
CMD_REQ_IMPL       = 0x04
CMD_REQ_STATUS     = 0x05
CMD_SET_LEVEL      = 0x06
CMD_REQ_GPIO       = 0x07
CMD_REQ_LEVEL      = 0x08
CMD_STOP_TRGEN     = 0x09

class InvalidAckError(Exception):
    def __init__(self, expected, received):
        super().__init__(f"Expected ACK{expected}, got '{received}'")

class AckFormatError(Exception):
    def __init__(self, ack_str):
        super().__init__(f"Malformed ACK string: '{ack_str}'")

class TriggerClient:
    """
    Client per la comunicazione con dispositivi TrGen tramite socket TCP/IP.
    """

    def __init__(self, ip='192.168.123.1', port=4242, timeout=2.0):
        """
        Inizializza il client per la TriggerBox.

        Args:
            ip (str): Indirizzo IP del dispositivo.
            port (int): Porta di comunicazione.
            timeout (float): Timeout per la connessione in secondi.
        """
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self._impl = None
        self._memory_length = 32
    
    def create_trigger(self, trigger_id):
        #if self._impl is None:
        #    raise RuntimeError("Call connect() before creating triggers")
        return Trigger(trigger_id, self._memory_length)

    # Connect to Trgen Device and get the Trgen Implementation
    def connect(self):
        """
        Connette il client al dispositivo TrGen e recupera la configurazione.

        Raises:
            InvalidAckError: Se la risposta ACK non è valida.
            AckFormatError: Se la risposta ACK è malformata.
            TimeoutError: Se la connessione va in timeout.
        """
        try:
            self._impl = self.get_implementation()
            self._memory_length = self._impl.memory_length
            #self._memory_length = 5**(self._impl.memory_length)
        except InvalidAckError as e:
            print(f"⚠️ ACK sbagliato: {e}")
        except AckFormatError as e:
            print(f"⚠️ ACK malformato: {e}")
        except TimeoutError as e:
            print(f"⏱️ Timeout: {e}")

    # Get Device Availability
    def is_available(self):
        """
        Verifica se il dispositivo TrGen è raggiungibile.

        Returns:
            bool: True se il dispositivo risponde, False altrimenti.
        """
        try:
            with socket.create_connection((self.ip, self.port), timeout=self.timeout) as sock:
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def disable_trigger(self, trigger):
        packet_id = CMD_PACKET_PROGRAM | (trigger.id << 24)


    # Start all triggers activities
    def start(self):
        """
        Avvia l'esecuzione dei trigger programmati sul dispositivo.
        """
        # Invia CMD_START (0x03) senza payload
        return self.__send_packet(CMD_PACKET_START)

    # Stop   all triggers activities
    def stop(self):
        """
        Ferma l'esecuzione dei trigger sul dispositivo.
        """
        # Invia CMD_STOP (0x09) senza payload
        return self.__send_packet(CMD_STOP_TRGEN)

    # Send program command for single trigger
    def send_trigger_memory(self, trigger):
        """
        Invia la memoria di un trigger programmato al dispositivo.

        Args:
            trigger (Trigger): Oggetto trigger da inviare.
        """
        packet_id = CMD_PACKET_PROGRAM | (trigger.id << 24)
        return self.__send_packet(packet_id, trigger.memory)

    # Set the Polarity Level for single Trigger
    def set_level(self, level_mask):
        """
        Set the trigger polarity (bitmask: 1 = active high, 0 = active low)
        """
        packet_id = CMD_SET_LEVEL
        payload = [level_mask]
        return self.__send_packet(packet_id, payload)

    def get_level(self):
        """
        Get the trigger active polarity
        """
        ack = self.__send_packet(CMD_REQ_LEVEL)
        return self.__parse_ack_value(ack, expected_id=CMD_REQ_LEVEL)
    
    # Get TriggerBox status
    def get_status(self):
        """
        Get current State for all triggers
        """
        ack = self.__send_packet(CMD_REQ_STATUS)
        return self.__parse_ack_value(ack, expected_id=CMD_REQ_STATUS)

    # Set GPIO Direction
    # esempio:
    #   client.set_gpio(0b00001111)  # GPIO0-3 ON, GPIO4-7 OFF
    def set_gpio(self, gpio_mask):
        """
        Set the direction (bitmask da 0 a 7) for GPIO
        """
        packet_id = CMD_SET_GPIO
        payload = [gpio_mask]
        return self.__send_packet(packet_id, payload)
    
    def get_gpio(self):
        """
        Get current direction for GPIO
        """
        ack = self.__send_packet(CMD_REQ_GPIO)
        return self.__parse_ack_value(ack, expected_id=CMD_REQ_GPIO)
    
    # Get the current Trgen Implementation
    def get_implementation(self):
        # Invia CMD_REQ_IMPL (0x04) senza payload
        ack = self.__send_packet(CMD_REQ_IMPL)  # 
        value = self.__parse_ack_value(ack, expected_id=0x04)

        from .implementation import TrgenImplementation
        impl = TrgenImplementation.from_packed_value(value)
        print(f"[TRGEN] Config: ns={impl.ns_num}, sa={impl.sa_num}, "
            f"tmso={impl.tmso_num}, tmsi={impl.tmsi_num}, "
            f"gpio={impl.gpio_num}, mtml={impl.mtml} → memory_length={impl.memory_length}")
        return impl

    def __send_packet(self, packet_id, payload=None):
        try:
            if payload is None:
                payload_bytes = b''
            else:
                from struct import pack
                payload_bytes = b''.join(pack('<I', w) for w in payload)

            from struct import pack
            from .crc import compute_crc32

            header = pack('<I', packet_id)
            raw = header + payload_bytes
            crc = pack('<I', compute_crc32(raw))
            packet = raw + crc

            with socket.create_connection((self.ip, self.port), timeout=self.timeout) as sock:
                sock.sendall(packet)
                try:
                    response = sock.recv(64)
                    return response.decode(errors='ignore')
                except socket.timeout:
                    raise TimeoutError(f"No ACK received for packet 0x{packet_id:02X}")
        except socket.timeout:
            raise TimeoutError(f"⏱️ Connessione timeout verso TriggerBox [{self.ip}:{self.port}]")
        except OSError as e:
            raise ConnectionError(f"🔌 Connessione fallita verso TriggerBox [{self.ip}:{self.port}] – {e.strerror or str(e)}")

    def __parse_ack_value(self, ack_str, expected_id):
        if not ack_str.startswith(f"ACK{expected_id}"):
            raise InvalidAckError(f"Unexpected ACK: '{ack_str}'")
        parts = ack_str.strip().split(".")
        if len(parts) != 2:
            raise AckFormatError(f"ACK format invalid: '{ack_str}'")
        return int(parts[1])
    
    def __reset_trigger(self,trigger):
        trigger.set_instruction(0, end())
        for i in range(1, 31):
            trigger.set_instruction(i,not_admissible())
        self.send_trigger_memory(trigger)


    def __reset_all_gpio(self):
        gpioPinoutMap = [
            TriggerPin.GPIO0,
            TriggerPin.GPIO1,
            TriggerPin.GPIO2,
            TriggerPin.GPIO3,
            TriggerPin.GPIO4,
            TriggerPin.GPIO5,
            TriggerPin.GPIO6,
            TriggerPin.GPIO7
        ]
        for id in gpioPinoutMap:
            gpio = self.create_trigger(id)
            gpio.set_instruction(0, end())
            for i in range(1, 31):
                gpio.set_instruction(i,not_admissible())
            self.send_trigger_memory(gpio)

    def __reset_all_sa(self):
        synampsPinoutMap = [
            TriggerPin.SA0,
            TriggerPin.SA1,
            TriggerPin.SA2,
            TriggerPin.SA3,
            TriggerPin.SA4,
            TriggerPin.SA5,
            TriggerPin.SA6,
            TriggerPin.SA7
        ]
        for id in synampsPinoutMap:
            sa = self.create_trigger(id)
            sa.set_instruction(0, end())
            for i in range(1, 31):
                sa.set_instruction(i,not_admissible())
            self.send_trigger_memory(sa)

    def __reset_all_ns(self):
        neuroscanPinoutMap = [
            TriggerPin.NS0,
            TriggerPin.NS1,
            TriggerPin.NS2,
            TriggerPin.NS3,
            TriggerPin.NS4,
            TriggerPin.NS5,
            TriggerPin.NS6,
            TriggerPin.NS7
        ]
        for id in neuroscanPinoutMap:
            ns = self.create_trigger(id)
            ns.set_instruction(0, end())
            for i in range(1, 31):
                ns.set_instruction(i,not_admissible())
            self.send_trigger_memory(ns)
    
    def __reset_all_tmso(self):
        tmsoPinoutMap = [
            TriggerPin.TMSO,
        ]
        for id in tmsoPinoutMap:
            tmso = self.create_trigger(id)
            tmso.set_instruction(0, end())
            for i in range(1, 31):
                tmso.set_instruction(i,not_admissible())
            self.send_trigger_memory(tmso)

    # Prende in input un oggetto Trigger e lo programma
    # con un impulso di default di durata 20µs
    def program_default_trigger(self,trigger,us=20):
        """
        Programma un trigger con un impulso di default.

        Args:
            trigger (Trigger): Oggetto trigger da programmare.
            us (int): Durata dell'impulso in microsecondi (default 20).
        """
        # TODO check if not Only Input (TMSI or GPIO Inputs)
        trigger.set_instruction(0, active_for_us(us))
        trigger.set_instruction(1, unactive_for_us(3))
        trigger.set_instruction(2, end())
        for i in range(3, 31):
            trigger.set_instruction(i,not_admissible())
        # Invio del trigger
        self.send_trigger_memory(trigger)

    # decode and send out a marker to all ports
    # You can also choose to send individually to:
    # - NeuroScan 25Pin Serial connector
    # - Synamps 15Pin Serial connector
    # - GPIO 8Pin DIN connector
    #
    # 
    def sendMarker(self, markerNS=None, markerSA=None, markerGPIO=None, LSB=False):
        """
        Invia un marker ai connettori NS, SA e/o GPIO.

        Args:
            markerNS (int, optional): Marker per NeuroScan.
            markerSA (int, optional): Marker per Synamps.
            markerGPIO (int, optional): Marker per GPIO.
            LSB (bool, optional): Se True, usa il bit meno significativo come primo.
        """
        
        if markerNS and markerSA and markerGPIO == None:
            return
        
        neuroscanMap = [
            TriggerPin.NS0,
            TriggerPin.NS1,
            TriggerPin.NS2,
            TriggerPin.NS3,
            TriggerPin.NS4,
            TriggerPin.NS4,
            TriggerPin.NS5,
            TriggerPin.NS6,
            TriggerPin.NS7
        ]

        synampsMap = [
            TriggerPin.SA0,
            TriggerPin.SA1,
            TriggerPin.SA2,
            TriggerPin.SA3,
            TriggerPin.SA4,
            TriggerPin.SA5,
            TriggerPin.SA6,
            TriggerPin.SA7
        ]

        gpioMap = [
            TriggerPin.GPIO0,
            TriggerPin.GPIO1,
            TriggerPin.GPIO2,
            TriggerPin.GPIO3,
            TriggerPin.GPIO4,
            TriggerPin.GPIO5,
            TriggerPin.GPIO6,
            TriggerPin.GPIO7,
        ]

        self.__reset_all_ns()
        self.__reset_all_sa()
        self.__reset_all_gpio()
        self.__reset_all_tmso()

        maskNS = list(format(markerNS, 'b').zfill(8))
        maskSA = list(format(markerSA, 'b').zfill(8))
        maskGPIO = list(format(markerGPIO, 'b').zfill(8))

        if LSB == False:
            maskNS = maskNS[::-1]
            maskSA = maskSA[::-1]
            maskGPIO = maskGPIO[::-1]

        for idx, i in enumerate(maskNS):
            if maskNS[idx] == '1':
                if(markerNS != None):
                    nsx = self.create_trigger(neuroscanMap[idx])
                    self.program_default_trigger(nsx)
        
        for idx, i in enumerate(maskGPIO):
            if maskGPIO[idx] == '1':
                if(markerGPIO != None):
                    sax = self.create_trigger(gpioMap[idx])
                    self.program_default_trigger(sax)
                
        for idx, i in enumerate(maskSA):
            if maskSA[idx] == '1':
                if(markerSA != None):
                    sax = self.create_trigger(synampsMap[idx])
                    self.program_default_trigger(sax)

        # Avvio sequenza
        self.start()

    # Send Trigger signal out of the BNC (TMSO)
    def sendTrigger(self):
        
        # create trigger
        tr = self.create_trigger(TriggerPin.TMSO)
        
        # reset all triggers
        self.__reset_all_gpio()
        self.__reset_all_sa()
        self.__reset_all_ns()
        self.__reset_all_tmso()

        self.program_default_trigger(tr)
        
        # start
        self.start()


    def sendCustomTrigger(self,triggerList):
        
        # reset all triggers
        self.__reset_all_gpio()
        self.__reset_all_sa()
        self.__reset_all_ns()
        self.__reset_all_tmso()

        for tid in triggerList:
            # create trigger
            tr = self.create_trigger(tid)
            # set default program for each one
            self.program_default_trigger(tr)
        
        # start
        self.start()

