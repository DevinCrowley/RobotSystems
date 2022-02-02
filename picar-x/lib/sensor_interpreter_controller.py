from adc import ADC

from message_bus import MessageBus
import time
import cv2

class Sensor:
    
    def __init__(self):
        self.channel_0 = ADC("A0")
        self.channel_1 = ADC("A1")
        self.channel_2 = ADC("A2")
        self.go = True

    def read_channels(self):
        return [self.channel_0.read(), self.channel_1.read(), self.channel_2.read()]
    
    def read_channels_loop(self, sensor_message_bus):
        while self.go:
            sensor_message_bus.write(self.read_channels())
            time.sleep(0.05)


class Interpreter:

    def __init__(self, threshold=500, polarity='dark_target'):
        self.threshold = threshold
        assert polarity in ['dark_target', 'light_target']
        self.polarity = polarity
        self.go = True

    def on_target(self, channel):
        if self.polarity == 'dark_target':
            return channel <= self.threshold
        elif self.polarity == 'light_target':
            return channel >= self.threshold
        else:
            return RuntimeError(f"Self.polarity is invalid: {self.polarity}")

    def channels_to_car_offset(self, channels):
        channels_on_target = [self.on_target(channel) for channel in channels]
        if not any(channels_on_target):
            return None
        
        # If no target to the left, robot is to the left.
        if not channels_on_target[0]:
            if channels_on_target[1]:
                return -1
            else:
                return -0.5
        # If no target to the right, robot is to the right.
        elif not channels_on_target[1]:
            if channels_on_target[1]:
                return 1
            else:
                return 0.5
        # If target is seen everywhere, we're right on target.
        else:
            return 0

    def channels_to_car_offset_loop(self, sensor_message_bus, interpreter_message_bus):
        while self.go:
            channels_from_sensor = sensor_message_bus.read()
            output_offset = self.channels_to_car_offset(channels_from_sensor)
            interpreter_message_bus.write(output_offset)
            time.sleep(0.1)


class Controller:

    def __init__(self, picarx, offset_to_steering_angle=12):
        self.picarx = picarx
        self.offset_to_steering_angle = offset_to_steering_angle
        self.go = True

    def follow_line_control(self, car_offset):
        angle = car_offset * self.offset_to_steering_angle
        self.picarx.set_dir_servo_angle(angle)
        return angle
    
    def follow_line_control_loop(self, interpreter_message_bus):
        while self.go:
            self.follow_line_control(interpreter_message_bus.read())
            time.sleep(0.1)

# Using the 3-pixel downward facing sensor on the front:
def follow_line_grayscale(picarx):
    sensor = Sensor()
    interpreter = Interpreter(threshold=500, polarity='dark_target')
    controller = Controller(picarx, offset_to_steering_angle=12)

    while True:
        channels = sensor.read_channels()
        car_offset = interpreter.channels_to_car_offset(channels)
        # Terminate when the target is not detected whatsoever.
        if car_offset is None:
            break
        controller.follow_line_control(car_offset)
    # Stop when done.
    picarx.stop()


import concurrent.futures
def follow_line_grayscale_multithread(picarx):
    sensor_message_bus = MessageBus()
    interpreter_message_bus = MessageBus()

    sensor = Sensor()
    interpreter = Interpreter(threshold=500, polarity='dark_target')
    controller = Controller(picarx, offset_to_steering_angle=12)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(sensor.read_channels_loop, sensor_message_bus)
        eInterpreter = executor.submit(interpreter.channels_to_car_offset_loop, sensor_message_bus, interpreter_message_bus)
        eController = executor.submit(controller.follow_line_control_loop, interpreter_message_bus)
    eSensor.result()
    eInterpreter.result()
    eController.result()
    
    while True:
        k = cv2.waitKey(1) & 0xFF
        # 27 is the ESC key, which means that if you press the ESC key to exit
        if k == 27:
            sensor.go = False
            interpreter.go = False
            controller.go = False
            break
        time.sleep(0.5)



from rossros import Bus, ConsumerProducer, Consumer, Producer, Timer, runConcurrently
def follow_line_rossros(picarx):

    sensor = Sensor()
    interpreter = Interpreter(threshold=500, polarity='dark_target')
    controller = Controller(picarx, offset_to_steering_angle=12)

    sensor_bus = Bus(name='sensor_bus')
    interpreter_bus = Bus(name='interpreter_bus')
    termination_bus = Bus(False, name='termination_bus')

    sensor_producer = Producer(
        producer_function=sensor.read_channels,
        output_busses=sensor_bus,
        delay=0.05,
        termination_busses=termination_bus,
        name='sensor_producer',
    )

    interpreter_consumer_producer = ConsumerProducer(
        consumer_producer_function=interpreter.channels_to_car_offset,
        input_busses=sensor_bus,
        output_busses=interpreter_bus,
        delay=0.1,
        termination_busses=termination_bus,
        name='interpreter_consumer_producer',
    )

    controller_consumer = Consumer(
        consumer_function=controller.follow_line_control,
        input_busses=interpreter_bus,
        delay=0.1,
        termination_busses=termination_bus,
        name='controller_consumer',
    )

    termination_timer = Timer(
        timer_busses=termination_bus,
        duration=5,
        delay=0.5,
        # termination_busses=DEFAULT, termination_timer has no termination_bus of its own.
        name='termination_timer',
    )

    runConcurrently([sensor_producer, interpreter_consumer_producer, controller_consumer, termination_timer])

