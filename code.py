import board, digitalio, time, usb_hid, sys, supervisor

from adafruit_hid.keyboard import Keyboard

from adafruit_hid.keycode import Keycode

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kbd = Keyboard(usb_hid.devices)

layout = KeyboardLayoutUS(kbd)


# Настройка кнопок

pins = [board.D7, board.D9, board.D12, board.D10]

buttons = []

for p in pins:

    b = digitalio.DigitalInOut(p)

    b.direction = digitalio.Direction.INPUT

    b.pull = digitalio.Pull.UP

    buttons.append(b)


# База макросов (примеры)

MACROS = {
    "COPY": [Keycode.LEFT_CONTROL, Keycode.C],
    "PASTE": [Keycode.LEFT_CONTROL, Keycode.V],
    "HELLO": "Hello, World!\n",
    "TSKMNGR":[Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.ESCAPE],
    "EXPLORER":[Keycode.GUI, Keycode.E],
    "PRINTSCREEN":[Keycode.PRINT_SCREEN],
    "CLOSEWINDOWS":[Keycode.GUI, Keycode.D]
}


# Текущие настройки (будут грузиться из файла)

config = {
    "btn0": {"short": "TSKMNGR", "long": "COPY"},
    "btn1": {"short": "EXPLORER", "long": "PASTE"},
    "btn2": {"short": "CLOSEWINDOWS", "long": "HELLO"},
    "btn3": {"short": "PRINTSCREEN", "long": "ENTER"},
}


def execute_action(action):

    if action in MACROS:

        m = MACROS[action]

        if isinstance(m, str):

            layout.write(m)

        else:

            kbd.press(*m)

            kbd.release_all()

    elif hasattr(Keycode, action):

        kbd.send(getattr(Keycode, action))


while True:

    # Проверка Serial для Веб-интерфейса (SET:btn0:short:ENTER)

    if supervisor.runtime.serial_bytes_available:

        line = sys.stdin.readline().strip()

        # Ожидаем формат: CMD:BUTTON_ID:TYPE:VALUE

        # Пример: CMD:0:short:SPACE

        if line.startswith("CMD:"):

            _, btn_id, press_type, val = line.split(":")

            config[f"btn{btn_id}"][press_type] = val

            print("ACK")  # Подтверждение для браузера

    for i, btn in enumerate(buttons):

        if not btn.value:

            start_time = time.monotonic()

            while not btn.value:

                time.sleep(0.01)

            duration = time.monotonic() - start_time

            action_type = "long" if duration > 0.5 else "short"

            execute_action(config[f"btn{i}"][action_type])

    time.sleep(0.01)
