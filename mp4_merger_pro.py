import subprocess
import sys
import importlib.util
import pkg_resources
import os
import zipfile
import requests
import time
import threading
import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

# === ฟังก์ชันติดตั้งตัวเสริม ===
def is_package_installed(pkg_name: str) -> bool:
    spec = importlib.util.find_spec(pkg_name)
    return spec is not None

def get_installed_version(pkg_name: str) -> str:
    try:
        version = pkg_resources.get_distribution(pkg_name).version
        return version
    except pkg_resources.DistributionNotFound:
        return None

def install_package(pkg_name: str, version: str = None):
    package = pkg_name if version is None else f"{pkg_name}=={version}"
    print(f"⏳ กำลังติดตั้งแพ็กเกจ: {package} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade", "--no-cache-dir"])
    print(f"✅ ติดตั้ง {package} สำเร็จ")

def install_melt_from_drive():
    try:
        base_dir = r"C:\app Gu"
        shotcut_dir = os.path.join(base_dir, "Shotcut")
        melt_exe_path = os.path.join(shotcut_dir, "melt.exe")
        shotcut_zip_path = os.path.join(base_dir, "Shotcut.zip")

        # เช็คว่ามีโฟลเดอร์ Shotcut และ melt.exe อยู่แล้ว ไม่ต้องติดตั้งซ้ำ
        if os.path.isdir(shotcut_dir) and os.path.isfile(melt_exe_path):
            print(f"✅ พบโฟลเดอร์และ melt.exe ที่ {shotcut_dir} แล้ว ไม่ต้องติดตั้งซ้ำ")
            return

        # ถ้าไม่มีโฟลเดอร์ Shotcut ให้ดาวน์โหลดและแตกไฟล์
        if not os.path.isdir(shotcut_dir):
            print(f"📁 ไม่พบโฟลเดอร์ {shotcut_dir} กำลังดาวน์โหลดและติดตั้ง...")

            download_url = "https://drive.usercontent.google.com/download?id=1c5-_1aXDIwki0KjVkDD-Hyw7v1DJTRlT&export=download&authuser=0&confirm=t&uuid=b443227e-8c2f-494a-8098-c80bfd2189ec&at=ALoNOgnQNqJaorrkotwaJNfFPwph%3A1747340742231"

            # ดาวน์โหลด Shotcut.zip ลง C:\app Gu
            print(f"⬇️ กำลังดาวน์โหลด Shotcut.zip ไปที่ {shotcut_zip_path} ...")
            response = requests.get(download_url, stream=True)
            total = int(response.headers.get('content-length', 0))
            chunk_size = 32768
            with open(shotcut_zip_path, "wb") as f:
                downloaded = 0
                start = time.time()
                for chunk in response.iter_content(chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        done = int(50 * downloaded / total) if total else 0
                        speed = downloaded / (time.time() - start + 0.01) / 1024
                        print(f"\r[{'█' * done}{'.' * (50 - done)}] {downloaded / 1024 / 1024:.2f} MB, {speed:.1f} KB/s", end='')
            print("\n✅ ดาวน์โหลด Shotcut.zip เสร็จเรียบร้อย")

            # แตกไฟล์ zip ลงใน C:\app Gu
            print(f"🗜️ กำลังแตกไฟล์ Shotcut.zip ...")
            with zipfile.ZipFile(shotcut_zip_path, 'r') as zip_ref:
                zip_ref.extractall(base_dir)
            print("✅ แตกไฟล์เสร็จเรียบร้อย")

            # ลบไฟล์ Shotcut.zip ทิ้ง
            try:
                os.remove(shotcut_zip_path)
                print("🗑️ ลบไฟล์ Shotcut.zip ออกเรียบร้อย")
            except Exception as e:
                print(f"⚠️ ไม่สามารถลบไฟล์ Shotcut.zip ได้: {e}")

        else:
            print(f"📁 พบโฟลเดอร์ {shotcut_dir} แต่ไม่พบ melt.exe - กรุณาตรวจสอบ")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการติดตั้ง melt.exe: {e}")

def ensure_packages():
    required_pkgs = {
        "tkinterdnd2": None,
        "requests": None,
    }
    moviepy_required_version = "1.0.3"
    moviepy_installed_version = get_installed_version("moviepy")

    if moviepy_installed_version != moviepy_required_version:
        print(f"⚠️ พบ moviepy เวอร์ชัน {moviepy_installed_version}, จะติดตั้งเวอร์ชัน {moviepy_required_version} เท่านั้น")
        install_package("moviepy", moviepy_required_version)
    else:
        print(f"✅ พบ moviepy เวอร์ชัน {moviepy_required_version} แล้ว")

    for pkg_name, version in required_pkgs.items():
        if not is_package_installed(pkg_name):
            install_package(pkg_name, version)
        else:
            print(f"✅ พบแพ็กเกจ {pkg_name} แล้ว")

MELT_PATH = r"C:\app Gu\Shotcut\melt.exe"

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("รวมวิดีโอด้วย Shotcut (melt CLI) พร้อมใช้ GPU Encoder")
        self.geometry("720x740")
        self.configure(bg="#222222")  # สีพื้นหลังเข้ม

        self.selected_files = []
        self.video_durations = []
        self.process = None  # เก็บ subprocess
        self.is_processing = False  # สถานะกำลังทำงาน

        self.ask_before_delete = True
        self.delete_all_on_confirm = None

        self.create_widgets()
        self.setup_drag_and_drop()
        self.create_context_menu()

        self.set_style()

    def set_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure("Treeview",
                        background="#333333",
                        foreground="white",
                        fieldbackground="#333333",
                        bordercolor="#555555",
                        borderwidth=1)
        style.map("Treeview", background=[('selected', '#555555')], foreground=[('selected', 'white')])

        style.configure("Vertical.TScrollbar", background="#444444", troughcolor="#222222", bordercolor="#222222", arrowcolor="white")

        style.configure("TProgressbar", troughcolor="#222222", background="#4CAF50", bordercolor="#222222")

        style.configure("TButton",
                        background="#333333",
                        foreground="white",
                        bordercolor="#555555",
                        focusthickness=3,
                        focuscolor='none')
        style.map("TButton",
                  background=[('active', '#555555'), ('!disabled', '#444444')],
                  foreground=[('active', 'white'), ('!disabled', 'white')])

    def create_widgets(self):
        label_fg = "white"
        btn_font = ("Kanit", 12)

        self.label_title = tk.Label(self, text="🔷 รวมไฟล์วิดีโอด้วย Shotcut (melt CLI) พร้อมใช้ GPU Encoder",
                                    font=("Kanit", 16), bg="#222222", fg=label_fg)
        self.label_title.pack(pady=10)

        self.btn_copy_times = tk.Button(self, text="คัดลอกเวลาเริ่มต้น", font=btn_font,
                                        bg="#2196F3", fg="white", width=20, command=self.copy_times_summary)
        self.btn_copy_times.pack(pady=5)

        self.btn_remove = tk.Button(self, text="ลบไฟล์ที่เลือก", font=btn_font,
                                    bg="#f44336", fg="white", width=20, command=self.remove_selected_files)
        self.btn_remove.pack(pady=5)

        self.frame_list = tk.Frame(self, bg="#333333", relief="sunken", bd=1)
        self.frame_list.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("#1", "#2", "#3")
        self.tree = ttk.Treeview(self.frame_list, columns=columns, show='headings', height=12)
        self.tree.heading("#1", text="ลำดับ")
        self.tree.heading("#2", text="ชื่อไฟล์")
        self.tree.heading("#3", text="ความยาว (HH:MM:SS)")

        self.tree.column("#1", width=60, anchor='center')
        self.tree.column("#2", width=480, anchor='w')
        self.tree.column("#3", width=120, anchor='center')
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<Button-3>", self.show_context_menu)

        scrollbar = ttk.Scrollbar(self.frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.btn_select = tk.Button(self, text="เลือกไฟล์วิดีโอ", font=btn_font,
                                    bg="#4CAF50", fg="white", width=20, command=self.select_videos)
        self.btn_select.pack(pady=5)

        # Frame สำหรับตั้งค่า ความละเอียด, FPS, โหมดประมวลผล
        self.frame_settings = tk.Frame(self, bg="#222222")
        self.frame_settings.pack(pady=10, padx=10, fill="x")

        # ความละเอียด (เพิ่มรายการเยอะขึ้น)
        tk.Label(self.frame_settings, text="ความละเอียด:", bg="#222222", fg="white", font=("Kanit", 12)).grid(row=0, column=0, sticky="w")
        resolutions = [
            "3840x2160",  # 4K UHD
            "2560x1440",  # 2K QHD
            "1920x1080",  # Full HD
            "1280x720",   # HD
            "1024x576",   # WSVGA
            "854x480",    # FWVGA
            "640x360",    # nHD
            "426x240",    # QCIF
            "256x144"     # Low Quality
        ]
        self.combo_resolution = ttk.Combobox(self.frame_settings, values=resolutions, font=("Kanit", 12), width=12)
        self.combo_resolution.current(2)  # ค่าเริ่มต้น 1080p
        self.combo_resolution.grid(row=0, column=1, padx=5, pady=2)

        # FPS (เพิ่มรายการเยอะขึ้น)
        tk.Label(self.frame_settings, text="FPS:", bg="#222222", fg="white", font=("Kanit", 12)).grid(row=0, column=2, sticky="w", padx=(20,0))
        fps_values = ["15", "24", "30", "48", "50", "60", "72", "90", "120", "144", "240"]
        self.combo_fps = ttk.Combobox(self.frame_settings, values=fps_values, font=("Kanit", 12), width=5)
        self.combo_fps.current(5)  # ค่าเริ่มต้น 60 FPS
        self.combo_fps.grid(row=0, column=3, padx=5, pady=2)

        # โหมดประมวลผล
        tk.Label(self.frame_settings, text="โหมดประมวลผล:", bg="#222222", fg="white", font=("Kanit", 12)).grid(row=1, column=0, sticky="w", pady=(5,0))
        self.process_mode_var = tk.StringVar(value="GPU+CPU")
        process_modes = ["CPU", "GPU", "GPU+CPU"]
        self.combo_process_mode = ttk.Combobox(self.frame_settings, values=process_modes, font=("Kanit", 12), width=10, textvariable=self.process_mode_var)
        self.combo_process_mode.grid(row=1, column=1, padx=5, pady=5)

        # ปุ่มรวมและหยุด
        self.btn_merge_stop = tk.Button(self, text="เอ็กซ์พอร์ตวิดีโอ", font=btn_font,
                                       bg="#2196F3", fg="white", width=25, command=self.merge_or_stop)
        self.btn_merge_stop.pack(pady=10)

        self.label_progress = tk.Label(self, text="", font=("Kanit", 10), bg="#222222", fg="white")
        self.label_progress.pack()

        self.progress_bar = ttk.Progressbar(self, length=600, mode='determinate')
        self.progress_bar.pack(pady=5)

        # ปุ่มเปิดโปรแกรม Shotcut มุมขวาล่าง
        self.btn_open_shotcut = tk.Button(self, text="เปิด Shotcut", font=("Kanit", 9),
                                          bg="#555555", fg="white", width=15, command=self.open_shotcut_program)
        self.btn_open_shotcut.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-30)

    def open_shotcut_program(self):
        path = r"C:\app Gu\Shotcut\shotcut.exe"
        if os.path.isfile(path):
            try:
                subprocess.Popen([path])
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเปิดโปรแกรมได้:\n{e}")
        else:
            messagebox.showerror("ไม่พบไฟล์", f"ไม่พบไฟล์ {path}")

    def setup_drag_and_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)

        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.drop_event)

    def drop_event(self, event):
        dropped = self.tk.splitlist(event.data)
        added = 0
        for path in dropped:
            if os.path.isfile(path) and path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
                if path not in self.selected_files:
                    self.selected_files.append(path)
                    added += 1
        if added:
            self.update_file_list()

    def select_videos(self):
        files = filedialog.askopenfilenames(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        if files:
            added = 0
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
                    added += 1
            if added:
                self.update_file_list()

    def update_file_list(self):
        import moviepy.editor as mp

        self.video_durations.clear()
        self.tree.delete(*self.tree.get_children())

        for idx, f in enumerate(self.selected_files, start=1):
            try:
                clip = mp.VideoFileClip(f)
                duration = clip.duration
                clip.close()
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถโหลดไฟล์ {os.path.basename(f)} ได้\n{e}")
                duration = 0
            self.video_durations.append(duration)
            dur_str = self.seconds_to_hhmmss(duration)
            self.tree.insert("", "end", values=(idx, os.path.basename(f), dur_str))

    def remove_selected_files(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("ไม่มีการเลือก", "กรุณาเลือกไฟล์ที่ต้องการลบก่อน")
            return

        if self.ask_before_delete:
            self.show_confirm_delete_dialog(selected_items)
        else:
            if self.delete_all_on_confirm:
                self._do_delete_all()
            else:
                self._do_delete((selected_items[0],))

    def show_confirm_delete_dialog(self, selected_items):
        # 🟩 ซ่อนหน้าต่างหลักชั่วคราว
        self.withdraw()

        # 🟩 ผูกหน้าต่างใหม่กับ root
        dialog = tk.Toplevel(self)
        dialog.title("ยืนยันการลบ")
        dialog.geometry("320x160")

        # 🟩 ให้อยู่ตำแหน่งเดียวกับ root
        x = self.winfo_x()
        y = self.winfo_y()
        w = self.winfo_width()
        h = self.winfo_height()
        dialog.geometry(f"+{x + w//2 - 160}+{y + h//2 - 80}")

        # 🔒 ล็อกหน้าต่างไม่ให้ขยาย
        dialog.resizable(False, False)
        dialog.configure(bg="#222222")

        # 🟩 คืนค่าหน้าต่างหลักเมื่อปิด
        def on_close():
            self.deiconify()  # คืนค่าหน้าต่างหลัก
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)

        dialog.grab_set()

        label = ttk.Label(dialog, text=f"คุณต้องการลบไฟล์ที่เลือกทั้งหมดหรือไม่? จำนวน {len(selected_items)} ไฟล์")
        label.pack(pady=10, padx=10)

        var_no_ask = tk.BooleanVar(value=False)
        check = ttk.Checkbutton(dialog, text="ไม่ต้องถามอีก", variable=var_no_ask)
        check.pack()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        def on_yes():
            if var_no_ask.get():
                self.ask_before_delete = False
                self.delete_all_on_confirm = True
            self.deiconify()  # คืนค่าหน้าต่างหลัก
            dialog.destroy()
            self._do_delete_all()

        def on_no():
            if var_no_ask.get():
                self.ask_before_delete = False
                self.delete_all_on_confirm = False
            self.deiconify()  # คืนค่าหน้าต่างหลัก
            dialog.destroy()
            self._do_delete((selected_items[0],))

        btn_yes = ttk.Button(btn_frame, text="ใช่", width=10, command=on_yes)
        btn_yes.pack(side="left", padx=10)
        btn_no = ttk.Button(btn_frame, text="ไม่", width=10, command=on_no)
        btn_no.pack(side="left")

    def _do_delete(self, selected_items):
        indices_to_remove = sorted(
            [self.tree.index(item) for item in selected_items],
            reverse=True
        )
        for index in indices_to_remove:
            if 0 <= index < len(self.selected_files):
                self.selected_files.pop(index)
                self.video_durations.pop(index)
        self.update_file_list()

    def _do_delete_all(self):
        self.selected_files.clear()
        self.video_durations.clear()
        self.update_file_list()

    def seconds_to_hhmmss(self, seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def merge_or_stop(self):
        if self.is_processing:
            self.stop_merge()
        else:
            self.merge_and_convert()

    def merge_and_convert(self):
        if not self.selected_files:
            messagebox.showwarning("ยังไม่ได้เลือกไฟล์", "กรุณาเลือกไฟล์วิดีโอก่อน")
            return

        output_file = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                   filetypes=[("MP4 files", "*.mp4")])
        if not output_file:
            return

        if not os.path.isfile(MELT_PATH):
            messagebox.showerror("ไม่พบ melt.exe", f"ไม่พบ melt.exe ที่\n{MELT_PATH}")
            return

        self.is_processing = True
        self.btn_merge_stop.config(text="หยุดการเอ็กซ์พอร์ต", bg="#f44336")
        threading.Thread(target=self.merge_and_convert_thread, args=(output_file,), daemon=True).start()

    def stop_merge(self):
        if self.process and self.is_processing:
            self.process.terminate()
            self.process = None
            self.is_processing = False
            self.label_progress.config(text="หยุดการเอ็กซ์พอร์ตแล้ว")
            self.progress_bar['value'] = 0
            self.btn_merge_stop.config(text="เอ็กซ์พอร์ตวิดีโอ", bg="#2196F3")
            self.btn_select.config(state=tk.NORMAL)

    def merge_and_convert_thread(self, output_file):
        try:
            self.btn_select.config(state=tk.DISABLED)

            # กำหนดความละเอียดและ FPS จาก UI
            resolution = self.combo_resolution.get() or "1920x1080"
            fps = self.combo_fps.get() or "60"

            width, height = resolution.split("x")

            # กำหนดโหมดประมวลผล
            mode = self.process_mode_var.get()

            # เตรียมคำสั่งสำหรับ melt ตามโหมดที่เลือก
            cmd = [MELT_PATH] + self.selected_files + ["-consumer", f"avformat:{output_file}"]

            # เพิ่ม filter scale ความละเอียด
            cmd += [f"vfilters=scale={width}:{height}"]

            # เพิ่ม frame rate
            cmd += [f"r={fps}"]

            # เพิ่ม codec และ option ตามโหมด
            if mode == "GPU+CPU":
                # ใช้ทั้ง GPU encoder และ multi-thread CPU 100%
                cpu_count = multiprocessing.cpu_count()
                threads_to_use = max(1, int(cpu_count * 1.0))
                cmd += ["vcodec=h264_nvenc", "acodec=aac", "-threads", str(threads_to_use)]
            elif mode == "GPU":
                cmd += ["vcodec=h264_nvenc", "acodec=aac", "-threads", "1"]  # ใช้ GPU encoder แต่ CPU น้อย
            else:  # CPU
                cpu_count = multiprocessing.cpu_count()
                threads_to_use = max(1, int(cpu_count * 0.8))
                cmd += ["vcodec=libx264", "acodec=aac", "-threads", str(threads_to_use)]

            print("Running melt command:")
            print(" ".join(cmd))

            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

            last_pos = 0
            last_update_time = 0
            max_pos = 50000

            for line in self.process.stderr:
                line = line.strip()
                if not self.is_processing:  # ถ้าไม่ประมวลผลแล้ว ให้หยุด loop
                    self.process.terminate()
                    break

                if "Current Position:" in line:
                    try:
                        pos = int(line.split(":")[1].strip())
                    except:
                        pos = last_pos

                    now = time.time()
                    if now - last_update_time > 0.5:
                        percent = min(100, pos / max_pos * 100)
                        self.label_progress.config(text=f"กำลังเอ็กซ์พอร์ตวิดีโอ ({percent:.1f}%)")
                        self.progress_bar['value'] = percent
                        self.update_idletasks()
                        print(f"Progress: {percent:.1f}%   ", end='\r', flush=True)
                        last_update_time = now
                        last_pos = pos

            if self.process:
                self.process.wait()
                retcode = self.process.returncode
            else:
                retcode = -1

            self.process = None
            self.is_processing = False

            print(' ' * 40, end='\r')

            if retcode == 0 and os.path.isfile(output_file) and os.path.getsize(output_file) > 0:
                self.label_progress.config(text="เอ็กซ์พอร์ตวิดีโอเสร็จสิ้น (100%)")
                self.progress_bar['value'] = 100
                messagebox.showinfo("สำเร็จ", f"เอ็กซ์พอร์ตวิดีโอเรียบร้อยแล้ว:\n{output_file}")
            else:
                self.label_progress.config(text="เอ็กซ์พอร์ตวิดีโอล้มเหลว")
                messagebox.showerror("ล้มเหลว", "เอ็กซ์พอร์ตวิดีโอไม่สำเร็จ")

        except Exception as e:
            if self.is_processing:  # ตรวจสอบว่าไม่ใช่การยกเลิกเอง
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด:\n{e}")
                self.label_progress.config(text="เกิดข้อผิดพลาดระหว่างเอ็กซ์พอร์ตวิดีโอ")
        finally:
            self.btn_select.config(state=tk.NORMAL)
            self.btn_merge_stop.config(text="เอ็กซ์พอร์ตวิดีโอ", bg="#2196F3")
            self.is_processing = False
            self.process = None

    # ==== ฟังก์ชันคัดลอกเวลาเริ่มต้น ====
    def copy_times_summary(self):
        if not self.selected_files:
            messagebox.showinfo("ไม่มีข้อมูล", "ยังไม่มีไฟล์ในรายการ")
            return

        def format_time(seconds):
            seconds = int(seconds)
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if h > 0:
                return f"{h}:{m:02d}:{s:02d}"
            else:
                return f"{m}:{s:02d}"

        lines = []
        current_time = 0.0
        for idx, dur in enumerate(self.video_durations, start=1):
            start_str = format_time(current_time)
            lines.append(f"{start_str} ตอนที่ {idx}")
            current_time += dur

        lines.append("")
        last_start_str = format_time(current_time - self.video_durations[-1])
        last_idx = len(self.video_durations)
        lines.append(f"{last_start_str} ตอนใหม่ล่าสุด {last_idx}")

        summary = "\n".join(lines)

        self.clipboard_clear()
        self.clipboard_append(summary)
        messagebox.showinfo("คัดลอกแล้ว", "คัดลอกเวลาคลิปเริ่มต้นไปยังคลิปบอร์ดเรียบร้อย")

    # ==== เมนูคลิกขวา Copy Duration ====
    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0, bg="#222222", fg="white")
        self.context_menu.add_command(label="Copy Duration", command=self.copy_duration)

    def show_context_menu(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            if row_id:
                self.tree.selection_set(row_id)
                self.context_menu.post(event.x_root, event.y_root)

    def copy_duration(self):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            duration = self.tree.item(item, "values")[2]
            self.clipboard_clear()
            self.clipboard_append(duration)
            messagebox.showinfo("คัดลอกแล้ว", f"คัดลอกความยาว {duration} ไปยังคลิปบอร์ดเรียบร้อย")

if __name__ == "__main__":
    ensure_packages()
    install_melt_from_drive()
    app = App()
    app.mainloop()
