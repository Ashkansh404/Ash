# -*- coding: utf-8 -*-
"""
ربات ستاره داوود - ربات اصلی سیستم اسرائیل
Star of David Bot - Main Israel RP System Bot
"""

import discord
from discord.ext import commands, tasks
import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# اضافه کردن مسیر اصلی پروژه
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from database import DatabaseManager, User, Economy, Military, Government, Event
from utils import GeminiAI, EmbedBuilder, TimeManager, EconomyCalculator, TextProcessor

class StarOfDavidBot(commands.Bot):
    """ربات اصلی ستاره داوود"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        # تنظیمات اصلی
        self.token = DISCORD_TOKENS["star_of_david"]
        self.guild_id = SERVER_CONFIG["guild_id"]
        self.owner_id = SERVER_CONFIG["owner_id"]
        
        # کلاس‌های کمکی
        self.db = DatabaseManager(DATABASE_CONFIG)
        self.gemini = GeminiAI(GEMINI_API_KEY)
        self.time_manager = TimeManager()
        self.embed_builder = EmbedBuilder()
        
        # متغیرهای وضعیت
        self.is_initialized = False
        self.current_defcon = 5
        self.public_satisfaction = 0.7
        self.active_crises = []
        self.scheduled_events = {}
        
        # ثبت رویدادها
        self.add_listeners()
        
    async def setup_hook(self):
        """تنظیم اولیه ربات"""
        print("🚀 راه‌اندازی ربات ستاره داوود...")
        
        # اتصال به پایگاه داده
        await self.db.connect()
        
        # بارگذاری کماندها
        await self.load_extension("cogs.government")
        await self.load_extension("cogs.military")
        await self.load_extension("cogs.economy")
        await self.load_extension("cogs.civilian")
        await self.load_extension("cogs.intelligence")
        
        print("✅ ربات ستاره داوود آماده است!")
    
    def add_listeners(self):
        """اضافه کردن گوش‌دهندگان رویدادها"""
        
        @self.event
        async def on_ready():
            """رویداد آماده شدن ربات"""
            print(f"✅ {self.user} آماده است!")
            print(f"🆔 شناسه ربات: {self.user.id}")
            print(f"🏛️ سرور: {self.guild.name}")
            
            # شروع وظایف زمان‌بندی شده
            self.daily_tasks.start()
            self.random_events.start()
            self.day_night_cycle.start()
            self.weather_cycle.start()
            
            # تنظیم وضعیت ربات
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="سرزمین مقدس اسرائیل ✡️"
                )
            )
        
        @self.event
        async def on_member_join(member):
            """رویداد پیوستن عضو جدید"""
            await self.handle_new_member(member)
        
        @self.event
        async def on_member_remove(member):
            """رویداد خروج عضو"""
            await self.handle_member_leave(member)
        
        @self.event
        async def on_message(message):
            """رویداد دریافت پیام"""
            if message.author.bot:
                return
            
            # پردازش کماندها
            await self.process_commands(message)
            
            # بررسی اسپم
            await self.check_spam(message)
    
    async def handle_new_member(self, member):
        """مدیریت عضو جدید"""
        try:
            # ایجاد کاربر در پایگاه داده
            user = await self.db.create_user(
                member.id,
                member.name,
                member.display_name
            )
            
            # اعطای نقش گردشگر
            tourist_role = discord.utils.get(member.guild.roles, name=SYSTEM_ROLES["tourist"])
            if tourist_role:
                await member.add_roles(tourist_role)
            
            # ارسال پیام خوشامدگویی
            welcome_message = random.choice(WELCOME_MESSAGES)
            embed = self.embed_builder.info_embed(
                "خوش آمدید!",
                f"{welcome_message}\n\nبرای شروع، لطفاً به کانال #immigration-office بروید و از دستور `!apply_citizenship` استفاده کنید."
            )
            
            try:
                await member.send(embed=embed)
            except:
                # اگر DM بسته باشد، در کانال عمومی ارسال کن
                general_channel = discord.utils.get(member.guild.channels, name="عمومی")
                if general_channel:
                    await general_channel.send(f"{member.mention} {welcome_message}")
            
            # لاگ
            await self.db.log_event("INFO", "star_of_david", f"عضو جدید {member.display_name} پیوست", member.id)
            
        except Exception as e:
            print(f"خطا در مدیریت عضو جدید: {e}")
    
    async def handle_member_leave(self, member):
        """مدیریت خروج عضو"""
        try:
            goodbye_message = random.choice(GOODBYE_MESSAGES)
            
            # ارسال پیام خداحافظی در کانال عمومی
            general_channel = discord.utils.get(member.guild.channels, name="عمومی")
            if general_channel:
                embed = self.embed_builder.info_embed(
                    "خداحافظ!",
                    f"{member.display_name} {goodbye_message}"
                )
                await general_channel.send(embed=embed)
            
            # لاگ
            await self.db.log_event("INFO", "star_of_david", f"عضو {member.display_name} خارج شد", member.id)
            
        except Exception as e:
            print(f"خطا در مدیریت خروج عضو: {e}")
    
    async def check_spam(self, message):
        """بررسی اسپم"""
        # اینجا می‌توانید منطق بررسی اسپم را اضافه کنید
        pass
    
    @tasks.loop(hours=24)
    async def daily_tasks(self):
        """وظایف روزانه"""
        try:
            print("🔄 اجرای وظایف روزانه...")
            
            # پرداخت حقوق روزانه
            await self.pay_daily_salaries()
            
            # به‌روزرسانی اقتصاد
            await self.update_economy()
            
            # بررسی رویدادهای ملی
            await self.check_national_events()
            
            # به‌روزرسانی رضایت عمومی
            await self.update_public_satisfaction()
            
            print("✅ وظایف روزانه تکمیل شد")
            
        except Exception as e:
            print(f"خطا در وظایف روزانه: {e}")
    
    @tasks.loop(minutes=30)
    async def random_events(self):
        """رویدادهای تصادفی"""
        try:
            if random.random() < 0.3:  # 30% احتمال
                await self.generate_random_event()
        except Exception as e:
            print(f"خطا در رویدادهای تصادفی: {e}")
    
    @tasks.loop(minutes=30)
    async def day_night_cycle(self):
        """چرخه روز و شب"""
        try:
            is_day = self.time_manager.is_day()
            status = "روز ☀️" if is_day else "شب 🌙"
            
            # ارسال اعلان در کانال عمومی
            general_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="عمومی")
            if general_channel:
                embed = self.embed_builder.info_embed(
                    "چرخه روز و شب",
                    f"حالا {status} است در سرزمین مقدس اسرائیل."
                )
                await general_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در چرخه روز و شب: {e}")
    
    @tasks.loop(minutes=15)
    async def weather_cycle(self):
        """چرخه آب و هوا"""
        try:
            weather = self.time_manager.get_weather_condition()
            season = self.time_manager.get_season()
            
            # ارسال اعلان در کانال عمومی
            general_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="عمومی")
            if general_channel:
                embed = self.embed_builder.info_embed(
                    "وضعیت آب و هوا",
                    f"وضعیت: {weather}\nفصل: {season}"
                )
                await general_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در چرخه آب و هوا: {e}")
    
    async def pay_daily_salaries(self):
        """پرداخت حقوق روزانه"""
        try:
            # دریافت همه کاربران
            async with self.db.pool.acquire() as conn:
                users = await conn.fetch("SELECT * FROM users WHERE job IS NOT NULL")
            
            for user_data in users:
                user = await self.db.get_user(user_data['user_id'])
                if user and user.job:
                    job_config = JOBS.get(user.job, {})
                    salary = job_config.get('salary', 0)
                    
                    # پرداخت حقوق
                    user.balance += salary
                    await self.db.update_user(user)
                    
                    # ثبت تراکنش
                    await self.db.create_transaction(
                        None, user.user_id, salary, "salary", f"حقوق روزانه {job_config.get('name', '')}"
                    )
            
            print(f"✅ حقوق روزانه برای {len(users)} کاربر پرداخت شد")
            
        except Exception as e:
            print(f"خطا در پرداخت حقوق: {e}")
    
    async def update_economy(self):
        """به‌روزرسانی اقتصاد"""
        try:
            economy = await self.db.get_economy()
            
            # محاسبه تغییرات اقتصادی
            inflation_effect = economy.gdp * economy.inflation_rate
            economy.gdp += inflation_effect
            
            # به‌روزرسانی در پایگاه داده
            await self.db.update_economy(economy)
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی اقتصاد: {e}")
    
    async def check_national_events(self):
        """بررسی رویدادهای ملی"""
        try:
            current_date = self.time_manager.get_current_time()
            current_month_day = current_date.strftime("%m-%d")
            
            for event_id, event_data in NATIONAL_EVENTS.items():
                if event_data["date"] == current_month_day:
                    await self.celebrate_national_event(event_id, event_data)
                    
        except Exception as e:
            print(f"خطا در بررسی رویدادهای ملی: {e}")
    
    async def celebrate_national_event(self, event_id: str, event_data: Dict):
        """جشن رویداد ملی"""
        try:
            # ارسال اعلان در کانال اخبار ملی
            news_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="اخبار ملی")
            if news_channel:
                embed = self.embed_builder.government_embed(
                    f"🎉 {event_data['name']}",
                    f"{event_data['description']}\n\nامروز {event_data['name']} را جشن می‌گیریم!"
                )
                await news_channel.send(embed=embed)
                
                # اعطای پاداش به همه کاربران
                bonus_multiplier = event_data.get('bonus', 1.0)
                await self.grant_event_bonus(bonus_multiplier)
                
        except Exception as e:
            print(f"خطا در جشن رویداد ملی: {e}")
    
    async def grant_event_bonus(self, multiplier: float):
        """اعطای پاداش رویداد"""
        try:
            async with self.db.pool.acquire() as conn:
                users = await conn.fetch("SELECT user_id FROM users WHERE citizenship_status = 'citizen'")
            
            base_bonus = 50
            bonus_amount = int(base_bonus * multiplier)
            
            for user_data in users:
                user = await self.db.get_user(user_data['user_id'])
                if user:
                    user.balance += bonus_amount
                    await self.db.update_user(user)
                    
                    await self.db.create_transaction(
                        None, user.user_id, bonus_amount, "event_bonus", "پاداش رویداد ملی"
                    )
            
            print(f"✅ پاداش رویداد ملی برای {len(users)} شهروند اعطا شد")
            
        except Exception as e:
            print(f"خطا در اعطای پاداش رویداد: {e}")
    
    async def update_public_satisfaction(self):
        """به‌روزرسانی رضایت عمومی"""
        try:
            government = await self.db.get_government()
            
            # محاسبه رضایت بر اساس عوامل مختلف
            satisfaction_change = 0.0
            
            # اثر بحران‌های فعال
            for crisis in self.active_crises:
                if crisis.get('effects', {}).get('satisfaction'):
                    satisfaction_change += crisis['effects']['satisfaction']
            
            # اثر وضعیت اقتصادی
            economy = await self.db.get_economy()
            if economy.unemployment_rate > 0.1:
                satisfaction_change -= 0.1
            elif economy.unemployment_rate < 0.05:
                satisfaction_change += 0.05
            
            # به‌روزرسانی رضایت
            government.public_satisfaction = max(0.0, min(1.0, government.public_satisfaction + satisfaction_change))
            await self.db.update_government(government)
            
            self.public_satisfaction = government.public_satisfaction
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی رضایت عمومی: {e}")
    
    async def generate_random_event(self):
        """تولید رویداد تصادفی"""
        try:
            event_types = ["natural_disaster", "political_scandal", "economic_crisis", "security_threat", "positive_event"]
            event_type = random.choice(event_types)
            
            # تولید رویداد با جیمینی
            event_data = await self.gemini.generate_event(event_type)
            
            # ایجاد رویداد در پایگاه داده
            event = Event(
                event_id=TextProcessor.generate_id(),
                event_type=event_type,
                title=event_data["title"],
                description=event_data["description"],
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2),
                participants=[],
                rewards=event_data["effects"],
                status="active",
                created_by=self.user.id
            )
            
            await self.db.create_event(event)
            
            # ارسال اعلان
            news_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="اخبار ملی")
            if news_channel:
                embed = self.embed_builder.warning_embed(
                    "🚨 رویداد مهم",
                    f"**{event_data['title']}**\n\n{event_data['description']}"
                )
                await news_channel.send(embed=embed)
            
            # اعمال اثرات
            await self.apply_event_effects(event_data["effects"])
            
        except Exception as e:
            print(f"خطا در تولید رویداد تصادفی: {e}")
    
    async def apply_event_effects(self, effects: Dict[str, float]):
        """اعمال اثرات رویداد"""
        try:
            for effect_type, value in effects.items():
                if effect_type == "economy":
                    economy = await self.db.get_economy()
                    economy.gdp *= (1 + value)
                    await self.db.update_economy(economy)
                    
                elif effect_type == "satisfaction":
                    self.public_satisfaction = max(0.0, min(1.0, self.public_satisfaction + value))
                    
                elif effect_type == "defense_budget":
                    military = await self.db.get_military()
                    military.defense_budget *= (1 + value)
                    await self.db.update_military(military)
            
        except Exception as e:
            print(f"خطا در اعمال اثرات رویداد: {e}")
    
    async def close(self):
        """بستن ربات"""
        print("🔄 بستن ربات ستاره داوود...")
        
        # توقف وظایف
        self.daily_tasks.cancel()
        self.random_events.cancel()
        self.day_night_cycle.cancel()
        self.weather_cycle.cancel()
        
        # بستن پایگاه داده
        await self.db.close()
        
        await super().close()
        print("✅ ربات ستاره داوود بسته شد")

# کماندهای اصلی
class MainCommands(commands.Cog):
    """کماندهای اصلی ربات"""
    
    def __init__(self, bot: StarOfDavidBot):
        self.bot = bot
    
    @commands.command(name="initialize_israel")
    @commands.has_permissions(administrator=True)
    async def initialize_israel(self, ctx):
        """راه‌اندازی اولیه سرور اسرائیل"""
        try:
            embed = self.bot.embed_builder.info_embed(
                "🏗️ راه‌اندازی اسرائیل",
                "در حال راه‌اندازی سرور اسرائیل... لطفاً صبر کنید."
            )
            message = await ctx.send(embed=embed)
            
            # ایجاد نقش‌ها
            await self.create_roles(ctx.guild)
            
            # ایجاد دسته‌بندی‌ها
            await self.create_categories(ctx.guild)
            
            # ایجاد کانال‌ها
            await self.create_channels(ctx.guild)
            
            # تنظیم مجوزها
            await self.setup_permissions(ctx.guild)
            
            # علامت‌گذاری به عنوان راه‌اندازی شده
            self.bot.is_initialized = True
            
            embed = self.bot.embed_builder.success_embed(
                "✅ راه‌اندازی کامل",
                "سرور اسرائیل با موفقیت راه‌اندازی شد!\n\nحالا کاربران می‌توانند از دستور `!apply_citizenship` استفاده کنند."
            )
            await message.edit(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا در راه‌اندازی",
                f"خطا در راه‌اندازی سرور: {str(e)}"
            )
            await message.edit(embed=embed)
    
    async def create_roles(self, guild):
        """ایجاد نقش‌های سیستم"""
        for role_key, role_name in SYSTEM_ROLES.items():
            if not discord.utils.get(guild.roles, name=role_name):
                await guild.create_role(
                    name=role_name,
                    color=discord.Color.random(),
                    reason="راه‌اندازی سیستم اسرائیل"
                )
                print(f"✅ نقش {role_name} ایجاد شد")
    
    async def create_categories(self, guild):
        """ایجاد دسته‌بندی‌ها"""
        for category_key, category_name in CHANNEL_CATEGORIES.items():
            if not discord.utils.get(guild.categories, name=category_name):
                await guild.create_category(
                    name=category_name,
                    reason="راه‌اندازی سیستم اسرائیل"
                )
                print(f"✅ دسته‌بندی {category_name} ایجاد شد")
    
    async def create_channels(self, guild):
        """ایجاد کانال‌ها"""
        # کانال‌های متنی
        for channel_key, channel_name in TEXT_CHANNELS.items():
            if not discord.utils.get(guild.channels, name=channel_name):
                category = discord.utils.get(guild.categories, name="عمومی")
                await guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    reason="راه‌اندازی سیستم اسرائیل"
                )
                print(f"✅ کانال متنی {channel_name} ایجاد شد")
        
        # کانال‌های صوتی
        for channel_key, channel_name in VOICE_CHANNELS.items():
            if not discord.utils.get(guild.channels, name=channel_name):
                category = discord.utils.get(guild.categories, name="عمومی")
                await guild.create_voice_channel(
                    name=channel_name,
                    category=category,
                    reason="راه‌اندازی سیستم اسرائیل"
                )
                print(f"✅ کانال صوتی {channel_name} ایجاد شد")
    
    async def setup_permissions(self, guild):
        """تنظیم مجوزها"""
        # اینجا می‌توانید منطق تنظیم مجوزها را اضافه کنید
        pass
    
    @commands.command(name="control_panel")
    @commands.has_permissions(administrator=True)
    async def control_panel(self, ctx):
        """پنل کنترل مرکزی"""
        try:
            # دریافت آمار
            stats = await self.bot.db.get_statistics()
            
            # دریافت وضعیت‌ها
            economy = await self.bot.db.get_economy()
            military = await self.bot.db.get_military()
            government = await self.bot.db.get_government()
            
            embed = self.bot.embed_builder.government_embed(
                "🏛️ پنل کنترل مرکزی",
                "وضعیت کلی سیستم اسرائیل"
            )
            
            embed.add_field(
                name="👥 جمعیت",
                value=f"کل کاربران: {stats['total_users']}\nشهروندان: {stats['citizens']}\nسربازان: {stats['soldiers']}",
                inline=True
            )
            
            embed.add_field(
                name="💰 اقتصاد",
                value=f"بودجه ملی: {EconomyCalculator.format_currency(economy.national_budget)}\nGDP: {EconomyCalculator.format_currency(economy.gdp)}\nکل ثروت: {EconomyCalculator.format_currency(stats['total_wealth'])}",
                inline=True
            )
            
            embed.add_field(
                name="⚔️ نظامی",
                value=f"سطح DEFCON: {military.defcon_level}\nپرسنل فعال: {military.active_personnel}\nبودجه دفاعی: {EconomyCalculator.format_currency(military.defense_budget)}",
                inline=True
            )
            
            embed.add_field(
                name="🏛️ دولت",
                value=f"رضایت عمومی: {government.public_satisfaction:.1%}\nنخست‌وزیر: {'تعیین شده' if government.prime_minister_id else 'تعیین نشده'}\nعضو کنست: {len(government.knesset_members)}",
                inline=True
            )
            
            embed.add_field(
                name="🌍 محیط",
                value=f"وضعیت: {self.bot.time_manager.get_weather_condition()}\nفصل: {self.bot.time_manager.get_season()}\nبحران‌های فعال: {len(self.bot.active_crises)}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش پنل کنترل: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="apply_citizenship")
    async def apply_citizenship(self, ctx):
        """درخواست شهروندی"""
        try:
            user = await self.bot.db.get_user(ctx.author.id)
            if not user:
                embed = self.bot.embed_builder.error_embed(
                    "❌ خطا",
                    "کاربر در سیستم ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            if user.citizenship_status == "citizen":
                embed = self.bot.embed_builder.warning_embed(
                    "⚠️ قبلاً شهروند",
                    "شما قبلاً شهروند اسرائیل هستید."
                )
                await ctx.send(embed=embed)
                return
            
            # تولید سوالات با جیمینی
            questions = await self.bot.gemini.generate_content(
                "5 سوال کوتاه برای درخواست شهروندی اسرائیل تولید کن. سوالات باید ساده و مناسب باشند."
            )
            
            embed = self.bot.embed_builder.info_embed(
                "📝 درخواست شهروندی",
                f"برای دریافت شهروندی اسرائیل، لطفاً به سوالات زیر پاسخ دهید:\n\n{questions}\n\nپاسخ خود را در پیام بعدی ارسال کنید."
            )
            await ctx.send(embed=embed)
            
            # انتظار برای پاسخ
            try:
                response = await self.bot.wait_for(
                    'message',
                    timeout=300.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
                
                # بررسی پاسخ (در اینجا می‌توانید منطق پیچیده‌تری اضافه کنید)
                if len(response.content) > 50:  # پاسخ کافی
                    # اعطای شهروندی
                    user.citizenship_status = "citizen"
                    await self.bot.db.add_user_role(ctx.author.id, "citizen")
                    await self.bot.db.update_user(user)
                    
                    # اعطای نقش
                    citizen_role = discord.utils.get(ctx.guild.roles, name=SYSTEM_ROLES["citizen"])
                    if citizen_role:
                        await ctx.author.add_roles(citizen_role)
                    
                    embed = self.bot.embed_builder.success_embed(
                        "✅ شهروندی اعطا شد",
                        "تبریک! شما اکنون شهروند اسرائیل هستید.\n\nشما می‌توانید از تمام امکانات سرور استفاده کنید."
                    )
                    await ctx.send(embed=embed)
                    
                else:
                    embed = self.bot.embed_builder.error_embed(
                        "❌ پاسخ ناکافی",
                        "پاسخ شما کافی نبود. لطفاً دوباره تلاش کنید."
                    )
                    await ctx.send(embed=embed)
                    
            except asyncio.TimeoutError:
                embed = self.bot.embed_builder.error_embed(
                    "⏰ زمان تمام شد",
                    "زمان پاسخ‌دهی تمام شد. لطفاً دوباره تلاش کنید."
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در درخواست شهروندی: {str(e)}"
            )
            await ctx.send(embed=embed)

async def main():
    """تابع اصلی"""
    bot = StarOfDavidBot()
    
    # اضافه کردن کماندها
    await bot.add_cog(MainCommands(bot))
    
    try:
        await bot.start(bot.token)
    except KeyboardInterrupt:
        print("\n🛑 دریافت سیگنال توقف...")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())