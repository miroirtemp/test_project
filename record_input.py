from pynput import keyboard, mouse
import time
import json


class InputRecord(object):
    def __init__(self, at, kn, action_time, px, py):
        self.action_type = at
        self.key_name = kn
        self.action_time = action_time
        self.pos_x = px
        self.pox_y = py

    def __str__(self):
        if self.action_type == "move":
            return "move to (%s, %s) at %s" % (self.pox_x, self.pos_y, self.action_time)
        else:
            return "%s %s at %s" % (self.key_name, self.action_type, self.action_time)

    def to_dict(self):
        ret = {
            "action": self.action_type,
            "key": str(self.key_name),
            "time": self.action_time,
        }
        return ret
    action_type = ""
    key_name = ""
    action_time = 0
    pos_x = -1
    pos_y = -1


class InputRecordMgr(object):
    record_list = []
    start_record_time = 0
    keyboard_listener = None
    mouse_listener = None

    def _add_input_record(self, action_type, key_name, pos_x=-1, pos_y=-1):
        if self.start_record_time == 0:
            return
        # print("add record action: %s, key: %s" % (action_type, key_name))
        record = InputRecord(action_type, key_name, time.time() - self.start_record_time, pos_x, pos_y)
        self.record_list.append(record)

    def on_press(self, key):
        self._add_input_record("down", key)

    def run(self):
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, refresh_rate=5)

        self.keyboard_listener.start()
        self.mouse_listener.start()

        self.keyboard_listener.join()
        self.mouse_listener.join()

    def stop_listening(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

    def save_records(self):
        # 转化成json格式保存
        print("START SAVE")
        datas = []
        for r in self.record_list:
            datas.append(r.to_dict())
        print("LZJ_TEST %s" % datas)
        save_str = json.dumps(datas)
        print(save_str)

    def on_release(self, key):
        if self.start_record_time == 0 and str(key) == "'q'":
            self.start_record_time = time.time()
            print("START RECORDING")
            return
        self._add_input_record("up", key)
        if key == keyboard.Key.esc:
            self.stop_listening()
            self.save_records()
            # TODO Save Records
            # for r in self.record_list:
            #     print(r)
            return False

    def on_move(self, x, y):
        self._add_input_record("move", "mouse", x, y)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self._add_input_record("down", button, x, y)
        else:
            self._add_input_record("up", button, x, y)


# Collect events until released
record_mgr = InputRecordMgr()
record_mgr.run()
