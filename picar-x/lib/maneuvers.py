from picarx_improved import Picarx
import time

def go(picarx, angle=None, speed=None):
    if speed is None and angle is None:
        # Stop and straighten on empty command.
        speed = 0
        angle = 0
    if angle is not None: picarx.set_dir_servo_angle(angle)
    if speed is not None: picarx.forward(speed)

def ppark(picarx, to_left=True):
    pos_if_to_left = 1 if to_left else -1

    go(picarx, angle=0, speed=30)
    time.sleep(0.5)
    go(picarx, angle=30 * pos_if_to_left, speed=-30)
    time.sleep(0.75)
    go(picarx, angle=-30 * pos_if_to_left, speed=-30)
    time.sleep(0.75)
    go(picarx, angle=0, speed=0)

def kturn(picarx, to_left=True):
    pos_if_to_left = 1 if to_left else -1

    go(picarx, angle = 45 * pos_if_to_left, speed = 60)
    time.sleep(1)
    go(picarx, angle = -45 * pos_if_to_left, speed = -60)
    time.sleep(1)
    go(picarx, angle = 30 * pos_if_to_left, speed = 60)
    time.sleep(1)
    go(picarx)


if __name__ == "__main__":    
    from utils import reset_mcu
    reset_mcu()

    picarx = Picarx

    while True:
        command = input(
            f"\nWhat do?\n"
            f"go: g\n"
            f"ppark: p\n"
            f"kturn: k\n"
            f"quit: q\n"
        )
        valid_commands = ['g', 'p', 'k', 'q']
        if command not in valid_commands:
            print(f"command {command} not in valid_commands {valid_commands}. Try again.")
            continue
        if command == 'g':
            print(f"Executing 'go' command. No inputs will stop and straighten.")
            angle_cmd = input(f"Enter the angle in degrees, or nothing for current angle: ")
            if angle_cmd == '':
                angle_cmd = None
            else:
                angle_cmd = float(angle_cmd)
            speed_cmd = input(f"Enter the speed, or nothing for current speed: ")
            if speed_cmd == '':
                speed_cmd = None
            else:
                speed_cmd = float(speed_cmd)
            go(picarx, angle=angle_cmd, speed=speed_cmd)
        elif command == 'p':
            print(f"Executing 'ppark' command.")
            to_left_cmd = bool(input(f"Enter 1 to ppark to_left or 0 to ppark to right: "))
            ppark(picarx, to_left=to_left_cmd)
        elif command == 'k':
            print(f"Executing 'kturn' command.")
            to_left_cmd = bool(input(f"Enter 1 to kturn to_left or 0 to kturn to right: "))
            kturn(picarx, to_left=to_left_cmd)
        elif command == 'q':
            print("Goodbye!")
            break
        else:
            raise RuntimeError(f"Dead code entered.")
        
