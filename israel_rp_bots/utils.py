# -*- coding: utf-8 -*-
"""
ابزارهای کمکی سیستم ربات‌های دیسکورد اسرائیل
Israel Discord Bots Ecosystem Utilities
"""

import asyncio
import json
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import discord
from discord import Embed, Color
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io
import aiohttp
import pytz

# تنظیمات جیمینی
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel('gemini-pro')

class GeminiAI:
    """کلاس هوش مصنوعی جیمینی"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])
    
    async def generate_content(self, prompt: str, context: str = "") -> str:
        """تولید محتوا با جیمینی"""
        try:
            full_prompt = f"""
            شما یک دستیار هوش مصنوعی برای سرور نقش‌آفرینی اسرائیل هستید.
            لطفاً به زبان فارسی پاسخ دهید و محتوای خلاقانه و جذاب تولید کنید.
            
            زمینه: {context}
            درخواست: {prompt}
            
            لطفاً پاسخ خود را به صورت متن ساده و بدون کد ارائه دهید.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, full_prompt
            )
            return response.text
        except Exception as e:
            return f"خطا در تولید محتوا: {str(e)}"
    
    async def generate_event(self, event_type: str) -> Dict[str, Any]:
        """تولید رویداد تصادفی"""
        prompts = {
            "natural_disaster": "یک بلای طبیعی در اسرائیل رخ داده است. جزئیات کامل رویداد را توصیف کنید.",
            "political_scandal": "یک رسوایی سیاسی در دولت اسرائیل افشا شده است. جزئیات کامل را توصیف کنید.",
            "economic_crisis": "یک بحران اقتصادی در اسرائیل رخ داده است. جزئیات کامل را توصیف کنید.",
            "security_threat": "یک تهدید امنیتی علیه اسرائیل شناسایی شده است. جزئیات کامل را توصیف کنید.",
            "positive_event": "یک رویداد مثبت و امیدبخش در اسرائیل رخ داده است. جزئیات کامل را توصیف کنید."
        }
        
        prompt = prompts.get(event_type, "یک رویداد تصادفی در اسرائیل رخ داده است. جزئیات کامل را توصیف کنید.")
        
        response = await self.generate_content(prompt, "تولید رویداد تصادفی")
        
        return {
            "title": f"رویداد {event_type}",
            "description": response,
            "type": event_type,
            "effects": self._generate_effects(event_type)
        }
    
    def _generate_effects(self, event_type: str) -> Dict[str, float]:
        """تولید اثرات رویداد"""
        effects = {
            "natural_disaster": {"economy": -0.3, "satisfaction": -0.4},
            "political_scandal": {"satisfaction": -0.6, "government_approval": -0.5},
            "economic_crisis": {"economy": -0.5, "satisfaction": -0.3},
            "security_threat": {"satisfaction": -0.4, "defense_budget": 0.3},
            "positive_event": {"economy": 0.2, "satisfaction": 0.3}
        }
        return effects.get(event_type, {})
    
    async def generate_news(self, news_type: str) -> str:
        """تولید اخبار"""
        prompts = {
            "politics": "یک خبر سیاسی مهم از اسرائیل بنویسید.",
            "economy": "یک خبر اقتصادی مهم از اسرائیل بنویسید.",
            "military": "یک خبر نظامی مهم از اسرائیل بنویسید.",
            "society": "یک خبر اجتماعی مهم از اسرائیل بنویسید.",
            "technology": "یک خبر تکنولوژی مهم از اسرائیل بنویسید."
        }
        
        prompt = prompts.get(news_type, "یک خبر مهم از اسرائیل بنویسید.")
        return await self.generate_content(prompt, "تولید اخبار")
    
    async def generate_dialogue(self, character_type: str, context: str) -> str:
        """تولید دیالوگ شخصیت"""
        character_prompts = {
            "prime_minister": "نخست‌وزیر اسرائیل",
            "general": "ژنرال ارتش اسرائیل",
            "banker": "مدیر بانک اسرائیل",
            "scientist": "دانشمند اسرائیلی",
            "journalist": "روزنامه‌نگار اسرائیلی",
            "judge": "قاضی اسرائیلی"
        }
        
        character = character_prompts.get(character_type, "شخصیت اسرائیلی")
        prompt = f"دیالوگ {character} در مورد {context} را بنویسید."
        
        return await self.generate_content(prompt, "تولید دیالوگ")

class EmbedBuilder:
    """سازنده امبدهای زیبا"""
    
    @staticmethod
    def create_embed(title: str, description: str, color: Color = Color.blue(), 
                    thumbnail: str = None, fields: List[Dict] = None, 
                    footer: str = None, timestamp: datetime = None) -> Embed:
        """ایجاد امبد زیبا"""
        embed = Embed(
            title=title,
            description=description,
            color=color,
            timestamp=timestamp or datetime.now()
        )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get("name", ""),
                    value=field.get("value", ""),
                    inline=field.get("inline", True)
                )
        
        if footer:
            embed.set_footer(text=footer)
        
        return embed
    
    @staticmethod
    def success_embed(title: str, description: str) -> Embed:
        """امبد موفقیت"""
        return EmbedBuilder.create_embed(
            title=f"✅ {title}",
            description=description,
            color=Color.green()
        )
    
    @staticmethod
    def error_embed(title: str, description: str) -> Embed:
        """امبد خطا"""
        return EmbedBuilder.create_embed(
            title=f"❌ {title}",
            description=description,
            color=Color.red()
        )
    
    @staticmethod
    def warning_embed(title: str, description: str) -> Embed:
        """امبد هشدار"""
        return EmbedBuilder.create_embed(
            title=f"⚠️ {title}",
            description=description,
            color=Color.yellow()
        )
    
    @staticmethod
    def info_embed(title: str, description: str) -> Embed:
        """امبد اطلاعات"""
        return EmbedBuilder.create_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=Color.blue()
        )
    
    @staticmethod
    def government_embed(title: str, description: str) -> Embed:
        """امبد دولت"""
        return EmbedBuilder.create_embed(
            title=f"🏛️ {title}",
            description=description,
            color=Color.from_rgb(0, 102, 204)
        )
    
    @staticmethod
    def military_embed(title: str, description: str) -> Embed:
        """امبد نظامی"""
        return EmbedBuilder.create_embed(
            title=f"⚔️ {title}",
            description=description,
            color=Color.from_rgb(139, 0, 0)
        )
    
    @staticmethod
    def economy_embed(title: str, description: str) -> Embed:
        """امبد اقتصاد"""
        return EmbedBuilder.create_embed(
            title=f"💰 {title}",
            description=description,
            color=Color.from_rgb(255, 215, 0)
        )
    
    @staticmethod
    def intelligence_embed(title: str, description: str) -> Embed:
        """امبد اطلاعات"""
        return EmbedBuilder.create_embed(
            title=f"🕵️ {title}",
            description=description,
            color=Color.from_rgb(128, 0, 128)
        )

class TimeManager:
    """مدیر زمان"""
    
    def __init__(self, timezone: str = "Asia/Jerusalem"):
        self.timezone = pytz.timezone(timezone)
    
    def get_current_time(self) -> datetime:
        """دریافت زمان فعلی"""
        return datetime.now(self.timezone)
    
    def format_time(self, dt: datetime) -> str:
        """فرمت‌بندی زمان"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def is_day(self) -> bool:
        """آیا روز است؟"""
        current_hour = self.get_current_time().hour
        return 6 <= current_hour <= 18
    
    def get_weather_condition(self) -> str:
        """دریافت وضعیت آب و هوا"""
        conditions = [
            "آفتابی ☀️",
            "ابری ⛅",
            "بارانی 🌧️",
            "طوفانی ⚡",
            "مه‌آلود 🌫️",
            "گرم و خشک 🔥",
            "خنک و مطبوع 🌤️"
        ]
        return random.choice(conditions)
    
    def get_season(self) -> str:
        """دریافت فصل"""
        month = self.get_current_time().month
        if month in [12, 1, 2]:
            return "زمستان ❄️"
        elif month in [3, 4, 5]:
            return "بهار 🌸"
        elif month in [6, 7, 8]:
            return "تابستان ☀️"
        else:
            return "پاییز 🍂"

class EconomyCalculator:
    """محاسبه‌گر اقتصادی"""
    
    @staticmethod
    def calculate_tax(amount: float, tax_rate: float) -> float:
        """محاسبه مالیات"""
        return amount * tax_rate
    
    @staticmethod
    def calculate_inflation_adjusted_amount(amount: float, inflation_rate: float, months: int) -> float:
        """محاسبه مبلغ با در نظر گرفتن تورم"""
        return amount * (1 + inflation_rate) ** months
    
    @staticmethod
    def calculate_interest(principal: float, rate: float, time: int) -> float:
        """محاسبه سود"""
        return principal * rate * time
    
    @staticmethod
    def format_currency(amount: float, currency: str = "₪") -> str:
        """فرمت‌بندی ارز"""
        if amount >= 1_000_000_000:
            return f"{amount / 1_000_000_000:.2f} میلیارد {currency}"
        elif amount >= 1_000_000:
            return f"{amount / 1_000_000:.2f} میلیون {currency}"
        elif amount >= 1_000:
            return f"{amount / 1_000:.2f} هزار {currency}"
        else:
            return f"{amount:.2f} {currency}"

class MilitaryCalculator:
    """محاسبه‌گر نظامی"""
    
    @staticmethod
    def calculate_combat_power(equipment: Dict[str, int], personnel: int) -> int:
        """محاسبه قدرت رزمی"""
        power = personnel * 10
        
        for eq_type, count in equipment.items():
            multipliers = {
                "tanks": 50,
                "fighters": 100,
                "missiles": 25,
                "ships": 75,
                "drones": 30
            }
            power += count * multipliers.get(eq_type, 10)
        
        return power
    
    @staticmethod
    def calculate_defense_bonus(defcon_level: int) -> float:
        """محاسبه پاداش دفاعی"""
        return 1.0 + (5 - defcon_level) * 0.2
    
    @staticmethod
    def calculate_mission_success_rate(combat_power: int, difficulty: int) -> float:
        """محاسبه نرخ موفقیت ماموریت"""
        base_rate = 0.5
        power_bonus = min(combat_power / 1000, 0.4)
        difficulty_penalty = min(difficulty / 100, 0.3)
        
        return min(base_rate + power_bonus - difficulty_penalty, 0.95)

class TextProcessor:
    """پردازش متن"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """پاک‌سازی متن"""
        # حذف کاراکترهای غیرمجاز
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', text)
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1024) -> str:
        """کوتاه کردن متن"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_number(number: Union[int, float]) -> str:
        """فرمت‌بندی اعداد"""
        if isinstance(number, float):
            return f"{number:,.2f}"
        return f"{number:,}"
    
    @staticmethod
    def generate_id() -> str:
        """تولید شناسه منحصر به فرد"""
        timestamp = int(time.time() * 1000)
        random_part = random.randint(1000, 9999)
        return f"{timestamp}{random_part}"

class ImageGenerator:
    """تولید تصاویر"""
    
    @staticmethod
    def create_flag_image(width: int = 800, height: int = 600) -> io.BytesIO:
        """ایجاد تصویر پرچم اسرائیل"""
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # رسم ستاره داوود
        center_x, center_y = width // 2, height // 2
        size = min(width, height) // 4
        
        # رسم مثلث‌های ستاره داوود
        points1 = [
            (center_x, center_y - size),
            (center_x - size//2, center_y + size//2),
            (center_x + size//2, center_y + size//2)
        ]
        points2 = [
            (center_x, center_y + size),
            (center_x - size//2, center_y - size//2),
            (center_x + size//2, center_y - size//2)
        ]
        
        draw.polygon(points1, fill='blue')
        draw.polygon(points2, fill='blue')
        
        # ذخیره در بافر
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_chart_image(data: Dict[str, int], title: str) -> io.BytesIO:
        """ایجاد نمودار"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # رسم عنوان
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((400, 30), title, fill='black', anchor='mm', font=font)
        
        # رسم نمودار
        if data:
            max_value = max(data.values())
            bar_width = 700 // len(data)
            start_x = 50
            
            for i, (label, value) in enumerate(data.items()):
                bar_height = int((value / max_value) * 400)
                x1 = start_x + i * bar_width
                y1 = 550 - bar_height
                x2 = x1 + bar_width - 10
                y2 = 550
                
                draw.rectangle([x1, y1, x2, y2], fill='blue')
                draw.text((x1 + bar_width//2, 570), str(label), fill='black', anchor='mm', font=font)
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

class SecurityManager:
    """مدیر امنیت"""
    
    def __init__(self):
        self.spam_detection = {}
        self.mention_tracking = {}
        self.suspicious_users = set()
    
    def check_spam(self, user_id: int, message_count: int = 1) -> bool:
        """بررسی اسپم"""
        current_time = time.time()
        
        if user_id not in self.spam_detection:
            self.spam_detection[user_id] = {"count": 0, "last_reset": current_time}
        
        # ریست شمارنده هر دقیقه
        if current_time - self.spam_detection[user_id]["last_reset"] > 60:
            self.spam_detection[user_id] = {"count": 0, "last_reset": current_time}
        
        self.spam_detection[user_id]["count"] += message_count
        
        # بیش از 10 پیام در دقیقه = اسپم
        return self.spam_detection[user_id]["count"] > 10
    
    def check_mentions(self, user_id: int, mention_count: int) -> bool:
        """بررسی منشن‌های بیش از حد"""
        current_time = time.time()
        
        if user_id not in self.mention_tracking:
            self.mention_tracking[user_id] = {"count": 0, "last_reset": current_time}
        
        # ریست شمارنده هر 5 دقیقه
        if current_time - self.mention_tracking[user_id]["last_reset"] > 300:
            self.mention_tracking[user_id] = {"count": 0, "last_reset": current_time}
        
        self.mention_tracking[user_id]["count"] += mention_count
        
        # بیش از 5 منشن در 5 دقیقه = مشکوک
        return self.mention_tracking[user_id]["count"] > 5
    
    def mark_suspicious(self, user_id: int):
        """علامت‌گذاری کاربر مشکوک"""
        self.suspicious_users.add(user_id)
    
    def is_suspicious(self, user_id: int) -> bool:
        """بررسی کاربر مشکوک"""
        return user_id in self.suspicious_users

class EventScheduler:
    """برنامه‌ریز رویدادها"""
    
    def __init__(self):
        self.scheduled_events = {}
        self.event_handlers = {}
    
    def schedule_event(self, event_id: str, delay: int, handler, *args, **kwargs):
        """برنامه‌ریزی رویداد"""
        self.scheduled_events[event_id] = {
            "delay": delay,
            "handler": handler,
            "args": args,
            "kwargs": kwargs,
            "scheduled_time": time.time() + delay
        }
    
    def cancel_event(self, event_id: str):
        """لغو رویداد"""
        if event_id in self.scheduled_events:
            del self.scheduled_events[event_id]
    
    async def process_events(self):
        """پردازش رویدادهای برنامه‌ریزی شده"""
        current_time = time.time()
        events_to_execute = []
        
        for event_id, event_data in self.scheduled_events.items():
            if current_time >= event_data["scheduled_time"]:
                events_to_execute.append(event_id)
        
        for event_id in events_to_execute:
            event_data = self.scheduled_events[event_id]
            try:
                if asyncio.iscoroutinefunction(event_data["handler"]):
                    await event_data["handler"](*event_data["args"], **event_data["kwargs"])
                else:
                    event_data["handler"](*event_data["args"], **event_data["kwargs"])
            except Exception as e:
                print(f"خطا در اجرای رویداد {event_id}: {e}")
            finally:
                del self.scheduled_events[event_id]

class NotificationManager:
    """مدیر اعلان‌ها"""
    
    def __init__(self):
        self.notifications = []
        self.subscribers = {}
    
    def add_notification(self, notification_type: str, message: str, priority: str = "normal"):
        """افزودن اعلان"""
        self.notifications.append({
            "type": notification_type,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now()
        })
    
    def subscribe(self, user_id: int, notification_types: List[str]):
        """اشتراک در اعلان‌ها"""
        self.subscribers[user_id] = notification_types
    
    def unsubscribe(self, user_id: int):
        """لغو اشتراک"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
    
    def get_notifications_for_user(self, user_id: int) -> List[Dict]:
        """دریافت اعلان‌های کاربر"""
        if user_id not in self.subscribers:
            return []
        
        user_types = self.subscribers[user_id]
        return [n for n in self.notifications if n["type"] in user_types]

# نمونه استفاده
async def main():
    """تابع اصلی برای تست"""
    # تست جیمینی
    gemini = GeminiAI("YOUR_API_KEY")
    content = await gemini.generate_content("یک خبر سیاسی از اسرائیل بنویسید")
    print(f"محتوای تولید شده: {content}")
    
    # تست امبد
    embed = EmbedBuilder.success_embed("موفقیت", "عملیات با موفقیت انجام شد")
    print(f"امبد ایجاد شد: {embed.title}")
    
    # تست زمان
    time_manager = TimeManager()
    current_time = time_manager.get_current_time()
    print(f"زمان فعلی: {time_manager.format_time(current_time)}")
    
    # تست اقتصاد
    tax = EconomyCalculator.calculate_tax(1000, 0.15)
    print(f"مالیات: {EconomyCalculator.format_currency(tax)}")
    
    # تست نظامی
    power = MilitaryCalculator.calculate_combat_power({"tanks": 10, "fighters": 5}, 1000)
    print(f"قدرت رزمی: {power}")

if __name__ == "__main__":
    asyncio.run(main())