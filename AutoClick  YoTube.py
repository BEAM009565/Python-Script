# 🔧 ตรวจสอบและติดตั้งไลบรารีอัตโนมัติ (พร้อมข้อความภาษาไทย)
import subprocess
import sys
import importlib

def install_and_check(package_name, import_name=None):
    try:
        importlib.import_module(import_name or package_name)
        print(f"✅ พบไลบรารี {package_name} แล้ว ไม่ต้องติดตั้งเพิ่ม")
    except ImportError:
        print(f"📦 กำลังติดตั้งไลบรารี {package_name} ... กรุณารอสักครู่")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"🎉 ติดตั้ง {package_name} เสร็จสมบูรณ์แล้ว!")

required_packages = [
    ("pyautogui", "pyautogui"),
    ("pynput", "pynput")
]

for pkg, imp in required_packages:
    install_and_check(pkg, imp)













import os
import time
import threading
import pyautogui
import tkinter as tk
from tkinter import messagebox, ttk
from pynput import keyboard, mouse
import json

LOG_DIR = r"C:\app Gu\ออโต้คลิก"
LOG_FILE = os.path.join(LOG_DIR, "log.txt")

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker ลำดับความสำคัญ F1,F2,F3")
        self.root.geometry("400x480")
        self.root.resizable(False, False)

        # จุด * (F1)
        self.star_point = None
        # จุดหลายจุด (F2)
        self.multi_points = []

        # Delay ระหว่างคลิก (วินาที)
        self.delay_var = tk.DoubleVar(value=0.3)
        # ความเร็ว F3
        self.speed_f3_var = tk.DoubleVar(value=1.0)
        # วนลูปหรือไม่
        self.is_loop_mode = tk.BooleanVar(value=False)

        # ฟังก์ชันที่เปิดใช้งาน
        self.enabled_funcs = []
        # ฟังก์ชันที่กำลังทำงาน
        self.active_funcs = []

        # สถานะการทำงานของ F1,F2
        self.running_f1f2 = False
        # สถานะการทำงานของ F3
        self.running_f3 = False
        self.f3_stop_flag = threading.Event()
        self.f3_thread = None
        self.is_recording = False

        # เก็บเหตุการณ์เมาส์ที่บันทึก
        self.mouse_events = []
        self.mouse_listener = None

        self.create_widgets()
        self.load_log()

        # เริ่มฟัง keyboard
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def create_widgets(self):
        pad = 10

        f1f2_frame = ttk.LabelFrame(self.root, text="(Auto Click)")
        f1f2_frame.pack(fill="x", padx=pad, pady=(pad, 5))

        self.star_label = ttk.Label(f1f2_frame, text="จุด * (F1): ยังไม่มาร์ค")
        self.star_label.pack(anchor="w", padx=pad, pady=(5, 2))

        self.multi_label = ttk.Label(f1f2_frame, text="จุดหลายจุด (F2): ยังไม่มีจุด")
        self.multi_label.pack(anchor="w", padx=pad, pady=(0, 5))

        ttk.Label(f1f2_frame, text="Delay ระหว่างคลิก (วินาที):").pack(anchor="w", padx=pad)
        self.delay_entry = ttk.Entry(f1f2_frame, textvariable=self.delay_var, width=10)
        self.delay_entry.pack(anchor="w", padx=pad, pady=(0, 5))

        self.loop_check = ttk.Checkbutton(f1f2_frame, text="วนลูป 🔄️", variable=self.is_loop_mode)
        self.loop_check.pack(anchor="w", padx=pad, pady=(0, 5))

        f3_frame = ttk.LabelFrame(self.root, text="ฟังก์ชัน F3 (บันทึกและเล่นพฤติกรรมเมาส์)")
        f3_frame.pack(fill="x", padx=pad, pady=5)

        ttk.Label(f3_frame, text="ความเร็ว F3 (ปรับระดับเพื่อเร็วขึ้นได้ 🔶ไม่ค่อยเห็นผลเท่าไหร่🔶):").pack(anchor="w", padx=pad)
        self.speed_f3_slider = ttk.Scale(f3_frame, variable=self.speed_f3_var, from_=0.1, to=5.0, orient=tk.HORIZONTAL)
        self.speed_f3_slider.pack(fill="x", padx=pad, pady=(0, 5))

        self.record_label = ttk.Label(f3_frame, text="ยังไม่บันทึกพฤติกรรมเมาส์")
        self.record_label.pack(anchor="w", padx=pad, pady=(0, 5))

        status_frame = ttk.LabelFrame(self.root, text="สถานะและคำสั่ง")
        status_frame.pack(fill="x", padx=pad, pady=5)

        self.status_label = ttk.Label(status_frame, text="สถานะ: รอคำสั่ง (กด Spacebar เพื่อเริ่ม/หยุด)", foreground="blue")
        self.status_label.pack(anchor="center", padx=pad, pady=10)

        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill="x", padx=pad, pady=(5, pad))

        tk.Label(info_frame,
                 text="กดปุ่มควบคุม: F1 = มาร์คจุด *, F2 = มาร์คจุดหลายจุด, F3 = เริ่ม/หยุดบันทึกเมาส์, Spacebar = เริ่ม/หยุดทำงาน, Alt = รีเซ็ต",
                 wraplength=380, justify="left").pack(anchor="w")

    def update_labels(self):
        if self.star_point:
            self.star_label.config(text=f"จุด * (F1): ({self.star_point[0]}, {self.star_point[1]})")
        else:
            self.star_label.config(text="จุด * (F1): ยังไม่มาร์ค")

        if self.multi_points:
            pts = ", ".join([f"({x},{y})" for x, y in self.multi_points])
            self.multi_label.config(text=f"จุดหลายจุด (F2): {pts}")
        else:
            self.multi_label.config(text="จุดหลายจุด (F2): ยังไม่มีจุด")

        if self.is_recording:
            self.record_label.config(text=f"กำลังบันทึกพฤติกรรมเมาส์... เหตุการณ์: {len(self.mouse_events)}")
        else:
            if len(self.mouse_events) > 0:
                self.record_label.config(text=f"พฤติกรรมเมาส์บันทึกไว้แล้ว เหตุการณ์: {len(self.mouse_events)}")
            else:
                self.record_label.config(text="ยังไม่บันทึกพฤติกรรมเมาส์")

    def save_log(self):
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"delay={self.delay_var.get()}\n")
                f.write(f"loop_mode={self.is_loop_mode.get()}\n")
                f.write(f"speed_f3={self.speed_f3_var.get()}\n")
                if self.star_point:
                    f.write(f"star={self.star_point[0]},{self.star_point[1]}\n")
                for x, y in self.multi_points:
                    f.write(f"multi={x},{y}\n")
                if self.mouse_events:
                    json_events = json.dumps(self.mouse_events, default=str)
                    f.write(f"mouse_events={json_events}\n")
        except Exception as e:
            messagebox.showerror("Error", f"บันทึกไฟล์ log ไม่ได้: {e}")

    def load_log(self):
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                self.star_point = None
                self.multi_points = []
                self.mouse_events = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("delay="):
                        try:
                            self.delay_var.set(float(line.split("=")[1]))
                        except:
                            pass
                    elif line.startswith("loop_mode="):
                        try:
                            self.is_loop_mode.set(line.split("=")[1] == "True")
                        except:
                            pass
                    elif line.startswith("speed_f3="):
                        try:
                            self.speed_f3_var.set(float(line.split("=")[1]))
                        except:
                            pass
                    elif line.startswith("star="):
                        parts = line.split("=")[1].split(",")
                        if len(parts) == 2:
                            try:
                                self.star_point = (int(parts[0]), int(parts[1]))
                            except:
                                pass
                    elif line.startswith("multi="):
                        parts = line.split("=")[1].split(",")
                        if len(parts) == 2:
                            try:
                                self.multi_points.append((int(parts[0]), int(parts[1])))
                            except:
                                pass
                    elif line.startswith("mouse_events="):
                        json_str = line[len("mouse_events="):]
                        try:
                            self.mouse_events = json.loads(json_str)
                            for i in range(len(self.mouse_events)):
                                event = self.mouse_events[i]
                                event_type, params, timestamp = event
                                try:
                                    timestamp = float(timestamp)
                                except:
                                    timestamp = 0.0
                                self.mouse_events[i] = (event_type, params, timestamp)
                        except Exception as e:
                            print("โหลด mouse_events ผิดพลาด:", e)
                self.update_labels()
                if self.star_point or self.multi_points:
                    if 'f1f2' not in self.enabled_funcs:
                        self.enabled_funcs.append('f1f2')
                if self.mouse_events:
                    if 'f3' not in self.enabled_funcs:
                        self.enabled_funcs.append('f3')
            except Exception as e:
                messagebox.showwarning("Warning", f"โหลดไฟล์ log ผิดพลาด: {e}")

    def reset_all(self):
        # หยุดการทำงานทั้งหมดก่อนรีเซ็ต
        if self.running_f1f2:
            self.running_f1f2 = False
            time.sleep(0.3)
        if self.running_f3:
            self.f3_stop_flag.set()
            self.running_f3 = False
            if self.f3_thread and self.f3_thread.is_alive():
                self.f3_thread.join()
            time.sleep(0.3)
        if self.is_recording:
            self.stop_mouse_record()

        # รีเซ็ตข้อมูลทั้งหมด
        self.star_point = None
        self.multi_points.clear()
        self.delay_var.set(0.3)
        self.speed_f3_var.set(1.0)
        self.is_loop_mode.set(False)

        self.mouse_events.clear()
        self.enabled_funcs.clear()
        self.active_funcs.clear()

        self.update_labels()
        self.status_label.config(text="สถานะ: รีเซ็ตข้อมูลเรียบร้อย (กด Spacebar เพื่อเริ่ม)")

        try:
            if os.path.exists(LOG_FILE):
                os.remove(LOG_FILE)
        except Exception as e:
            messagebox.showwarning("Warning", f"ลบไฟล์ log ผิดพลาด: {e}")

        print("รีเซ็ตค่าทั้งหมดเรียบร้อย")

    def on_key_press(self, key):
        try:
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.reset_all()
                return

            def add_enabled_func(name):
                if name not in self.enabled_funcs:
                    self.enabled_funcs.append(name)
                    print(f"เปิดใช้งานฟังก์ชัน {name} : {self.enabled_funcs}")

            if key == keyboard.Key.f1:
                x, y = pyautogui.position()
                self.star_point = (x, y)
                self.update_labels()
                self.save_log()
                add_enabled_func('f1f2')
                print(f"มาร์ค * (F1): ({x}, {y})")

            elif key == keyboard.Key.f2:
                x, y = pyautogui.position()
                self.multi_points.append((x, y))
                self.update_labels()
                self.save_log()
                add_enabled_func('f1f2')
                print(f"มาร์ค จุด F2 เพิ่มเติม: ({x}, {y})")

            elif key == keyboard.Key.f3:
                if not self.is_recording:
                    self.start_mouse_record()
                else:
                    self.stop_mouse_record()
                add_enabled_func('f3')

            elif key == keyboard.Key.space:
                # ถ้าเครื่องมือทำงานอยู่ ให้หยุดทั้งหมดก่อน
                if self.running_f1f2 or self.running_f3 or self.is_recording:
                    self.running_f1f2 = False
                    self.f3_stop_flag.set()
                    self.running_f3 = False
                    if self.f3_thread and self.f3_thread.is_alive():
                        self.f3_thread.join()
                    if self.is_recording:
                        self.stop_mouse_record()
                    self.status_label.config(text="สถานะ: หยุดแล้ว (กด Spacebar เพื่อเริ่ม)")
                    print("หยุดฟังก์ชันทั้งหมดแล้ว")
                    return

                if not self.enabled_funcs:
                    messagebox.showwarning("คำเตือน", "ต้องตั้งค่าฟังก์ชันก่อน F1,F2 หรือ F3")
                    return

                self.f3_stop_flag.clear()
                self.active_funcs = self.enabled_funcs.copy()
                threading.Thread(target=self.run_active_funcs, daemon=True).start()
                self.status_label.config(text="สถานะ: รันฟังก์ชันที่เลือกอยู่... (กด Spacebar เพื่อหยุด)")

        except AttributeError:
            pass

    def run_active_funcs(self):
        for func_name in self.active_funcs:
            if func_name == 'f3':
                # รอให้ f1f2 หยุดก่อนถ้าเปิดใช้งานพร้อมกัน
                for prev_func in self.active_funcs[:self.active_funcs.index(func_name)]:
                    if prev_func == 'f1f2' and self.running_f1f2:
                        while self.running_f1f2:
                            if self.f3_stop_flag.is_set():
                                print("หยุด f3 ระหว่างรอ f1f2")
                                return
                            time.sleep(0.1)

                if not self.mouse_events:
                    messagebox.showwarning("คำเตือน", "ยังไม่มีพฤติกรรมเมาส์ที่บันทึกไว้")
                    continue

                self.running_f3 = True
                self.f3_thread = threading.Thread(target=self.play_mouse_events)
                self.f3_thread.start()
                self.f3_thread.join()
                self.running_f3 = False

            elif func_name == 'f1f2':
                # รอให้ f3 หยุดก่อนถ้าเปิดใช้งานพร้อมกัน
                for prev_func in self.active_funcs[:self.active_funcs.index(func_name)]:
                    if prev_func == 'f3' and self.running_f3:
                        while self.running_f3:
                            if self.f3_stop_flag.is_set():
                                print("หยุด f1f2 ระหว่างรอ f3")
                                return
                            time.sleep(0.1)

                if not self.star_point or not self.multi_points:
                    messagebox.showwarning("คำเตือน", "ต้องตั้งจุด * (F1) และจุดหลายจุด (F2) ก่อน")
                    continue
                self.running_f1f2 = True
                self.run_auto_click_loop()
                self.running_f1f2 = False

        self.status_label.config(text="สถานะ: หยุดแล้ว (กด Spacebar เพื่อเริ่ม)")

    def run_auto_click_loop(self):
        delay = self.delay_var.get()
        loop_mode = self.is_loop_mode.get()
        idx = 0
        total_points = len(self.multi_points)
        print(f"เริ่ม Auto Click ด้วย delay {delay} วินาที, วนซ้ำ: {loop_mode}")

        if loop_mode:
            while self.running_f1f2:
                # คลิกซ้ายที่จุด *
                pyautogui.click(x=self.star_point[0], y=self.star_point[1], button='left', _pause=False)
                print(f"คลิก * ที่ ({self.star_point[0]}, {self.star_point[1]})")
                time.sleep(delay)

                # ดับเบิลคลิกที่จุด F2
                point = self.multi_points[idx % total_points]
                pyautogui.click(x=point[0], y=point[1], button='left', _pause=False)
                time.sleep(0.05)
                pyautogui.click(x=point[0], y=point[1], button='left', _pause=False)
                print(f"ดับเบิลคลิก จุด F2 ที่ ({point[0]}, {point[1]})")
                time.sleep(delay)

                idx += 1
        else:
            for idx in range(total_points):
                if not self.running_f1f2:
                    break

                # คลิกซ้ายที่จุด *
                pyautogui.click(x=self.star_point[0], y=self.star_point[1], button='left', _pause=False)
                print(f"คลิก * ที่ ({self.star_point[0]}, {self.star_point[1]})")
                time.sleep(delay)

                # ดับเบิลคลิกที่จุด F2
                point = self.multi_points[idx]
                pyautogui.click(x=point[0], y=point[1], button='left', _pause=False)
                time.sleep(0.05)
                pyautogui.click(x=point[0], y=point[1], button='left', _pause=False)
                print(f"ดับเบิลคลิก จุด F2 ที่ ({point[0]}, {point[1]})")
                time.sleep(delay)

    def start_mouse_record(self):
        self.is_recording = True
        self.mouse_events.clear()
        self.status_label.config(text="สถานะ: กำลังบันทึกพฤติกรรมเมาส์... (กด F3 อีกครั้งเพื่อหยุด)")
        self.update_labels()
        print("เริ่มบันทึกพฤติกรรมเมาส์")

        self.record_start_time = time.time()

        def on_move(x, y):
            if not self.is_recording:
                return False
            timestamp = time.time() - self.record_start_time
            self.mouse_events.append(('move', (x, y), timestamp))
            self.update_labels()

        def on_click(x, y, button, pressed):
            if not self.is_recording:
                return False
            timestamp = time.time() - self.record_start_time
            action = 'click_press' if pressed else 'click_release'
            self.mouse_events.append((action, (x, y, button.name), timestamp))
            self.update_labels()

        def on_scroll(x, y, dx, dy):
            if not self.is_recording:
                return False
            timestamp = time.time() - self.record_start_time
            self.mouse_events.append(('scroll', (x, y, dx, dy), timestamp))
            self.update_labels()

        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll)
        self.mouse_listener.start()

    def stop_mouse_record(self):
        self.is_recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        self.status_label.config(text="สถานะ: หยุดบันทึกพฤติกรรมเมาส์แล้ว")
        self.update_labels()
        print(f"หยุดบันทึกพฤติกรรมเมาส์, เหตุการณ์ {len(self.mouse_events)} รายการ")
        self.save_log()

    def play_mouse_events(self):
        print("เล่นพฤติกรรมเมาส์ที่บันทึกไว้")
        speed = self.speed_f3_var.get()
        if speed < 0.1:
            speed = 0.1
        loop_mode = self.is_loop_mode.get()

        self.f3_stop_flag.clear()

        while self.running_f3 and not self.f3_stop_flag.is_set():
            last_time = 0
            for event in self.mouse_events:
                if self.f3_stop_flag.is_set() or not self.running_f3:
                    print("หยุดเล่นพฤติกรรมเมาส์")
                    break
                event_type, params, timestamp = event

                wait_time = max(0, (timestamp - last_time)) / speed
                if wait_time > 0:
                    time.sleep(wait_time)
                last_time = timestamp

                if event_type == 'move':
                    x, y = params
                    pyautogui.moveTo(x, y, duration=0)
                elif event_type == 'click_press':
                    x, y, button_name = params
                    if button_name == 'left':
                        pyautogui.mouseDown(button='left')
                    elif button_name == 'right':
                        pyautogui.mouseDown(button='right')
                elif event_type == 'click_release':
                    x, y, button_name = params
                    if button_name == 'left':
                        pyautogui.mouseUp(button='left')
                    elif button_name == 'right':
                        pyautogui.mouseUp(button='right')
                elif event_type == 'scroll':
                    x, y, dx, dy = params
                    pyautogui.scroll(dy)

            if not loop_mode:
                break

        self.running_f3 = False
        self.status_label.config(text="สถานะ: หยุดแล้ว (กด Spacebar เพื่อเริ่ม)")
        print("เล่นพฤติกรรมเมาส์เสร็จ")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
