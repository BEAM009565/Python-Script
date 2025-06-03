"""
คำนวณวันเกิดแฟนและวันครบรอบ
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime

# ฟังก์ชันสำหรับแปลงเดือนเป็นภาษาไทย
def get_thai_month(month):
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    return thai_months[month - 1]

class คํานวณอายุ(toga.App):
    def startup(self):
        # กำหนดชื่อแอปพลิเคชัน
        self.name = "คำนวณวันเกิดแฟนและวันครบรอบ"

        # สร้างกล่องหลัก
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # ปุ่มคำนวณวันเกิดแฟน (ผู้ชาย)
        birthday_button_male = toga.Button(
            "🎂 คำนวณวันเกิดแฟน (ชาย)",
            on_press=self.calculate_birthday_male,
            style=Pack(margin=5)
        )
        main_box.add(birthday_button_male)

        # ปุ่มคำนวณวันเกิดแฟน (หญิง)
        birthday_button = toga.Button(
            "🎂 คำนวณวันเกิดแฟน (หญิง)",
            on_press=self.calculate_birthday,
            style=Pack(margin=5)
        )
        main_box.add(birthday_button)

        # ปุ่มคำนวณวันครบรอบ
        anniversary_button = toga.Button(
            "💘 คำนวณวันครบรอบ",
            on_press=self.calculate_anniversary,
            style=Pack(margin=5)
        )
        main_box.add(anniversary_button)

        # ป้ายแสดงผลลัพธ์
        self.result_label = toga.Label("ผลลัพธ์จะแสดงที่นี่", style=Pack(margin=5))
        main_box.add(self.result_label)

        # ตั้งค่าหน้าต่างหลัก
        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = main_box
        self.main_window.show()

    def calculate_birthday_male(self, widget):
        try:
            # วันเกิดแฟน (ผู้ชาย)
            birthday = datetime.strptime("2004-10-28", "%Y-%m-%d")  # เปลี่ยนวันเกิดเป็น 28 ตุลาคม 2004
            today = datetime.today()
            delta = today - birthday
            years = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            months = (today.year - birthday.year) * 12 + today.month - birthday.month - (today.day < birthday.day)
            days = delta.days
            minutes = delta.total_seconds() // 60

            # คำนวณวันเกิดครั้งถัดไป
            next_birthday = datetime(today.year, birthday.month, birthday.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birthday.month, birthday.day)
            remaining_delta = next_birthday - today
            remaining_months = remaining_delta.days // 30
            remaining_days = remaining_delta.days % 30

            # คำนวณวันครบรอบปีถัดไป
            next_anniversary = datetime(today.year, birthday.month, birthday.day)
            if today > next_anniversary:
                next_anniversary = datetime(today.year + 1, birthday.month, birthday.day)
            next_anniversary_years = next_anniversary.year - birthday.year

            self.result_label.text = (
                f"🎂 วันเกิดแฟน (ผู้ชาย): 28 ตุลาคม 2004\n"
                f"👦 อายุแฟน: {years} ปี\n"
                f"📆 ประมาณ: {months} เดือน\n"
                f"🕰 รวมทั้งหมด: {days} วัน\n"
                f"⏱ รวมทั้งหมด: {int(minutes):,} นาที\n\n"
                f"🎉 เหลืออีก: {remaining_months} เดือน {remaining_days} วัน\n"
                f"✨ จนถึงวันเกิดครั้งถัดไป ({next_birthday.strftime('%d')} {get_thai_month(next_birthday.month)} {next_birthday.year})"
            )
            self.result_label.text += f"\n🎊 จะครบรอบ {next_anniversary_years} ปี"
            print(f"Today: {today}, Birthday: {birthday}, Next Birthday: {next_birthday}")
        except Exception as e:
            self.result_label.text = f"เกิดข้อผิดพลาด: {e}"


    def calculate_birthday(self, widget):
        try:
            # วันเกิดแฟน
            birthday = datetime.strptime("2007-12-12", "%Y-%m-%d")  # เปลี่ยนวันเกิดเป็น 12 ธันวาคม 2007
            today = datetime.today()
            delta = today - birthday
            years = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            months = (today.year - birthday.year) * 12 + today.month - birthday.month - (today.day < birthday.day)
            days = delta.days
            minutes = delta.total_seconds() // 60

            # คำนวณวันเกิดครั้งถัดไป
            next_birthday = datetime(today.year, birthday.month, birthday.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, birthday.month, birthday.day)
            remaining_delta = next_birthday - today
            remaining_months = remaining_delta.days // 30
            remaining_days = remaining_delta.days % 30

            # คำนวณวันครบรอบปีถัดไป
            next_anniversary = datetime(today.year, birthday.month, birthday.day)
            if today > next_anniversary:
                next_anniversary = datetime(today.year + 1, birthday.month, birthday.day)
            next_anniversary_years = next_anniversary.year - birthday.year

            self.result_label.text = (
                f"🎂 วันเกิดแฟน: 12 ธันวาคม 2007\n"
                f"👧 อายุแฟน: {years} ปี\n"
                f"📆 ประมาณ: {months} เดือน\n"
                f"🕰 รวมทั้งหมด: {days} วัน\n"
                f"⏱ รวมทั้งหมด: {int(minutes):,} นาที\n\n"
                f"🎉 เหลืออีก: {remaining_months} เดือน {remaining_days} วัน\n"
                f"✨ จนถึงวันเกิดครั้งถัดไป ({next_birthday.strftime('%d')} {get_thai_month(next_birthday.month)} {next_birthday.year})"
            )
            self.result_label.text += f"\n🎊 จะครบรอบ {next_anniversary_years} ปี"
            print(f"Today: {today}, Birthday: {birthday}, Next Birthday: {next_birthday}")
        except Exception as e:
            self.result_label.text = f"เกิดข้อผิดพลาด: {e}"

    def calculate_anniversary(self, widget):
        try:
            # วันครบรอบ
            anniversary = datetime.strptime("2023-01-07", "%Y-%m-%d")
            today = datetime.today()
            delta = today - anniversary

            # คำนวณปี เดือน และวัน
            years = today.year - anniversary.year
            months = today.month - anniversary.month
            days = today.day - anniversary.day
            if days < 0:
                months -= 1
                days += (datetime(today.year, today.month, 1) - datetime(today.year, today.month - 1, 1)).days
            if months < 0:
                years -= 1
                months += 12

            total_months = years * 12 + months  # รวมเดือนทั้งหมด
            total_days = delta.days
            total_minutes = delta.total_seconds() // 60

            # คำนวณวันครบรอบปีถัดไป
            next_anniversary = datetime(today.year, anniversary.month, anniversary.day)
            if today > next_anniversary:
                next_anniversary = datetime(today.year + 1, anniversary.month, anniversary.day)
            remaining_delta = next_anniversary - today
            remaining_months = remaining_delta.days // 30
            remaining_days = remaining_delta.days % 30

            # คำนวณจำนวนปีที่จะครบรอบในปีถัดไป
            next_anniversary_years = next_anniversary.year - anniversary.year

            self.result_label.text = (
                f"💘 วันครบรอบ: 7 {get_thai_month(1)} 2023\n"
                f"👫 คบกันมาแล้ว: {years} ปี {months} เดือน {days} วัน\n"
                f"📆 รวมทั้งหมด: {total_days} วัน\n"
                f"📅 รวมทั้งหมด: {total_months} เดือน\n"
                f"⏱ รวมทั้งหมด: {int(total_minutes):,} นาที\n\n"
                f"🎉 เหลืออีก: {remaining_months} เดือน {remaining_days} วัน\n"
                f"✨ จนถึงวันครบรอบปีถัดไป ({next_anniversary.strftime('%d')} {get_thai_month(next_anniversary.month)} {next_anniversary.year})\n"
                f"🎊 จะครบรอบ {next_anniversary_years} ปี"
            )
        except Exception as e:
            self.result_label.text = f"เกิดข้อผิดพลาด: {e}"


def main():
    return คํานวณอายุ("คำนวณวันเกิดแฟนและวันครบรอบ")
