import socket


class RobotControl:
    S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # LIFT_SPEED: int
    # LIFT_CTRL: int
    # LEFT_MOTOR_SPEED: int
    # RIGHT_MOTOR_SPEED: int
    # MOTOR_CTRL: int
    # DATA: int
    motor_ctrl_state = 0

    def __init__(self):
        self.lift_speed: int = 0  # 0 -> stop, 250 -> run
        self.lift_ctrl:int = 0  # 0 -> nothing, 1 -> down, 2 -> up
        self.left_motor_speed:int = 0  # 0
        self.right_motor_speed:int = 0  # 0
        self.motor_left_ctrl: int = 0  # 0 left cw, 1 = left ccw
        self.motor_right_ctrl: int = 0  # 0 right cw, 2 = right ccw


        self.data = [0x08, 0x00, 0x00, 0x00, 0x12, 0x00, self.lift_speed, self.lift_ctrl, 0x00,
                     abs(self.left_motor_speed) + 60, abs(self.right_motor_speed) + 60,
                     self.motor_left_ctrl + self.motor_right_ctrl * 2,
                     0x38]

    def connection(self):
        # Connection
        server = '192.168.0.7'
        port = 20001
        addr = (server, port)
        print("Connection...")
        self.S.connect(addr)
        print("Connection Done\n")

    def set_lift_speed(self, speed):
        self.data[6] = speed

    def set_lift_ctrl(self, ctrl):
        self.data[7] = ctrl

    def set_left_speed(self, speed):
        self.data[9] = speed

    def set_right_speed(self, speed):
        self.data[10] = speed

    def set_motor_ctrl(self, left_motor, right_motor):
        ###############
        # this part is to pass through the issue when we want to change the motor direction
        # left_motor and right_motor : -180 ~ 180, 0/180 =>  forward, -180/0 => backward
        ###############
        # comparing current command with new command
        if self.right_motor_speed >= 0 & right_motor < 0:
            motor_ctrl_state = 0

        if self.right_motor_speed <= 0 & right_motor > 0:
            motor_ctrl_state = 0

        if self.left_motor_speed >= 0 & left_motor < 0:
            motor_ctrl_state = 0

        if self.left_motor_speed <= 0 & left_motor > 0:
            motor_ctrl_state = 0

        # current command = new command
        self.right_motor_speed = right_motor
        self.left_motor_speed = right_motor

        match motor_ctrl_state:
            case 0:
                # stop the motors
                self.data[9] = 60
                self.data[10] = 60

            case 1:
                # reset direction
                self.data[11] = 0

            case 2:
                # change direction

                # matching data to control motor and speed data
                # between 0 and 180
                if self.left_motor_speed >= 0:
                    self.motor_left_ctrl = 0
                # between -180 and -0.1
                else:
                    self.motor_left_ctrl = 1

                if self.right_motor_speed >= 0:
                    self.motor_right_ctrl = 0
                else:
                    self.motor_right_ctrl = 2

                # implementing the data
                self.data[11] = self.motor_left_ctrl + self.motor_right_ctrl

            # default case (normal)
            case _:
                # we have to change direction 3 times to make it accurate
                if motor_ctrl_state > 4:
                    self.data[9] = abs(self.left_motor_speed) + 60
                    self.data[10] = abs(self.right_motor_speed) + 60
                print("a")

        if self.left_motor_speed == 0:
            self.data[9] = 0
        if self.right_motor_speed == 0:
            self.data[9] = 0
        # increase case
        if motor_ctrl_state < 10:
            motor_ctrl_state += 1

    def sending_data(self):
        self.S.send(bytes(self.data))
