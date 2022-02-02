from ultrasonic import Ultrasonic

class Sensor:
    def __init__(self):
        self.ultrasonic = Ultrasonic()
    def sense(self):
        return self.ultrasonic.read()

class Interpreter:
    def __init__(self):
        pass
    def interpret(self, sensor_reading):
        obstacle_detected = sensor_reading > -1
        if obstacle_detected:
            return 'stop'
        else:
            return 'go'

class Controller:
    def __init__(self, picarx, speed):
        self.picarx = picarx
        self.speed = speed
    def control(self, command):
        if command == 'go':
            self.picarx.forward(speed=self.speed)
            return False # output goes to termination_bus
        elif command == 'stop':
            self.picarx.stop()
            return True # output goes to termination_bus
        else:
            raise ValueError("command not recognized.")


from rossros import Bus, ConsumerProducer, Consumer, Producer, Timer, runConcurrently
def go_until_obstacle_rossros(picarx):

    sensor = Sensor()
    interpreter = Interpreter()
    controller = Controller(picarx, speed=50)

    sensor_bus = Bus(name='sensor_bus')
    interpreter_bus = Bus(name='interpreter_bus')
    termination_bus = Bus(False, name='termination_bus')

    sensor_producer = Producer(
        producer_function=sensor.sense,
        output_busses=sensor_bus,
        delay=0.05,
        termination_busses=termination_bus,
        name='sensor_producer',
    )

    interpreter_consumer_producer = ConsumerProducer(
        consumer_producer_function=interpreter.interpret,
        input_busses=sensor_bus,
        output_busses=interpreter_bus,
        delay=0.1,
        termination_busses=termination_bus,
        name='interpreter_consumer_producer',
    )

    controller_consumer_producer = ConsumerProducer(
        consumer_producer_function=controller.control,
        input_busses=interpreter_bus,
        output_busses=termination_bus,
        delay=0.1,
        # termination_bus can be set to True by controller_consumer_producer or termination_timer.
        termination_busses=termination_bus,
        name='controller_consumer_producer',
    )

    termination_timer = Timer(
        timer_busses=termination_bus,
        duration=5,
        delay=0.5,
        # termination_busses=DEFAULT, termination_timer has no termination_bus of its own.
        name='termination_timer',
    )

    runConcurrently([sensor_producer, interpreter_consumer_producer, controller_consumer_producer, termination_timer])

