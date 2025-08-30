# -*- coding: utf-8 -*-
"""
ربات گنبد آهنین - سیستم دفاعی اسرائیل
Iron Dome Bot - Israel's Defense System
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
from database import DatabaseManager
from utils import EmbedBuilder, SecurityManager, TextProcessor

class IronDomeBot(commands.Bot):
    """ربات گنبد آهنین"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        # تنظیمات اصلی
        self.token = DISCORD_TOKENS["iron_dome"]
        self.guild_id = SERVER_CONFIG["guild_id"]
        
        # کلاس‌های کمکی
        self.db = DatabaseManager(DATABASE_CONFIG)
        self.embed_builder = EmbedBuilder()
        self.security_manager = SecurityManager()
        
        # متغیرهای دفاعی
        self.missile_inventory = 100  # موجودی موشک
        self.interception_count = 0
        self.last_interception = None
        self.defense_mode = "active"
        self.threat_level = "low"
        
        # ثبت رویدادها
        self.add_listeners()
        
    async def setup_hook(self):
        """تنظیم اولیه ربات"""
        print("🛡️ راه‌اندازی ربات گنبد آهنین...")
        
        # اتصال به پایگاه داده
        await self.db.connect()
        
        print("✅ ربات گنبد آهنین آماده است!")
    
    def add_listeners(self):
        """اضافه کردن گوش‌دهندگان رویدادها"""
        
        @self.event
        async def on_ready():
            """رویداد آماده شدن ربات"""
            print(f"✅ {self.user} آماده است!")
            print(f"🆔 شناسه ربات: {self.user.id}")
            print(f"🛡️ وضعیت دفاعی: {self.defense_mode}")
            
            # شروع وظایف زمان‌بندی شده
            self.missile_replenishment.start()
            self.threat_assessment.start()
            self.defense_status_report.start()
            
            # تنظیم وضعیت ربات
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="تهدیدات امنیتی 🛡️"
                )
            )
        
        @self.event
        async def on_message(message):
            """رویداد دریافت پیام"""
            if message.author.bot:
                return
            
            # بررسی اسپم
            await self.check_spam(message)
            
            # پردازش کماندها
            await self.process_commands(message)
        
        @self.event
        async def on_message_delete(message):
            """رویداد حذف پیام"""
            await self.handle_message_deletion(message)
        
        @self.event
        async def on_member_ban(guild, user):
            """رویداد بن شدن کاربر"""
            await self.handle_member_ban(guild, user)
        
        @self.event
        async def on_member_unban(guild, user):
            """رویداد آنبن شدن کاربر"""
            await self.handle_member_unban(guild, user)
    
    async def check_spam(self, message):
        """بررسی اسپم"""
        try:
            user_id = message.author.id
            
            # بررسی اسپم با SecurityManager
            if self.security_manager.check_spam(user_id):
                await self.intercept_spam(message)
                return
            
            # بررسی منشن‌های بیش از حد
            mention_count = len(message.mentions)
            if mention_count > SECURITY_CONFIG["max_mentions_per_message"]:
                await self.intercept_mention_spam(message, mention_count)
                return
            
            # بررسی پیام‌های تکراری
            await self.check_repeated_messages(message)
            
        except Exception as e:
            print(f"خطا در بررسی اسپم: {e}")
    
    async def intercept_spam(self, message):
        """رابطه اسپم"""
        try:
            # کاهش موجودی موشک
            if self.missile_inventory > 0:
                self.missile_inventory -= 1
                self.interception_count += 1
                self.last_interception = datetime.now()
                
                # ایجاد انیمیشن رابط
                embed = self.embed_builder.military_embed(
                    "🛡️ گنبد آهنین فعال شد",
                    f"**رابط اسپم انجام شد!**\n\nتهدید شناسایی و خنثی شد.\nموجودی موشک: {self.missile_inventory}"
                )
                
                # اضافه کردن انیمیشن
                embed.set_thumbnail(url="https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif")
                
                await message.channel.send(embed=embed)
                
                # حذف پیام اسپم
                await message.delete()
                
                # لاگ
                await self.db.log_event("WARNING", "iron_dome", f"اسپم از {message.author.display_name} رفع شد", message.author.id)
                
                # اخطار به کاربر
                warning_embed = self.embed_builder.warning_embed(
                    "⚠️ اخطار امنیتی",
                    "پیام شما به عنوان اسپم شناسایی و حذف شد. لطفاً از ارسال پیام‌های مکرر خودداری کنید."
                )
                
                try:
                    await message.author.send(embed=warning_embed)
                except:
                    pass
                
            else:
                # موجودی موشک تمام شده
                embed = self.embed_builder.error_embed(
                    "❌ موجودی موشک تمام شد",
                    "موجودی موشک‌های گنبد آهنین تمام شده است. لطفاً منتظر تامین مجدد باشید."
                )
                await message.channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در رابط اسپم: {e}")
    
    async def intercept_mention_spam(self, message, mention_count):
        """رابط منشن اسپم"""
        try:
            if self.missile_inventory > 0:
                self.missile_inventory -= 1
                self.interception_count += 1
                
                embed = self.embed_builder.military_embed(
                    "🛡️ رابط منشن اسپم",
                    f"**رابط منشن اسپم انجام شد!**\n\nتعداد منشن‌های مشکوک: {mention_count}\nموجودی موشک: {self.missile_inventory}"
                )
                
                await message.channel.send(embed=embed)
                await message.delete()
                
                # اخطار به کاربر
                warning_embed = self.embed_builder.warning_embed(
                    "⚠️ اخطار منشن",
                    f"شما {mention_count} منشن در یک پیام ارسال کردید که بیش از حد مجاز است."
                )
                
                try:
                    await message.author.send(embed=warning_embed)
                except:
                    pass
                
        except Exception as e:
            print(f"خطا در رابط منشن اسپم: {e}")
    
    async def check_repeated_messages(self, message):
        """بررسی پیام‌های تکراری"""
        try:
            # اینجا می‌توانید منطق بررسی پیام‌های تکراری را اضافه کنید
            pass
        except Exception as e:
            print(f"خطا در بررسی پیام‌های تکراری: {e}")
    
    async def handle_message_deletion(self, message):
        """مدیریت حذف پیام"""
        try:
            # بررسی حذف مشکوک
            if message.author and not message.author.bot:
                embed = self.embed_builder.warning_embed(
                    "⚠️ حذف پیام",
                    f"پیام از {message.author.display_name} حذف شد.\nمحتوای پیام: {message.content[:100]}..."
                )
                
                # ارسال به کانال لاگ
                log_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="war_room")
                if log_channel:
                    await log_channel.send(embed=embed)
                    
        except Exception as e:
            print(f"خطا در مدیریت حذف پیام: {e}")
    
    async def handle_member_ban(self, guild, user):
        """مدیریت بن شدن کاربر"""
        try:
            embed = self.embed_builder.military_embed(
                "🚫 کاربر بن شد",
                f"کاربر {user.display_name} از سرور بن شد.\n\nاین عملیات توسط سیستم دفاعی انجام شد."
            )
            
            # ارسال به کانال لاگ
            log_channel = discord.utils.get(guild.channels, name="war_room")
            if log_channel:
                await log_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در مدیریت بن کاربر: {e}")
    
    async def handle_member_unban(self, guild, user):
        """مدیریت آنبن شدن کاربر"""
        try:
            embed = self.embed_builder.success_embed(
                "✅ کاربر آنبن شد",
                f"کاربر {user.display_name} از سرور آنبن شد."
            )
            
            # ارسال به کانال لاگ
            log_channel = discord.utils.get(guild.channels, name="war_room")
            if log_channel:
                await log_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در مدیریت آنبن کاربر: {e}")
    
    @tasks.loop(hours=1)
    async def missile_replenishment(self):
        """تامین مجدد موشک‌ها"""
        try:
            if self.missile_inventory < 100:
                replenishment = min(10, 100 - self.missile_inventory)
                self.missile_inventory += replenishment
                
                print(f"🛡️ {replenishment} موشک تامین شد. موجودی: {self.missile_inventory}")
                
                # اعلان در کانال نظامی
                military_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="فرماندهی نظامی")
                if military_channel:
                    embed = self.embed_builder.military_embed(
                        "🛡️ تامین مجدد موشک",
                        f"**{replenishment} موشک جدید تامین شد!**\n\nموجودی کل: {self.missile_inventory}"
                    )
                    await military_channel.send(embed=embed)
                    
        except Exception as e:
            print(f"خطا در تامین مجدد موشک: {e}")
    
    @tasks.loop(minutes=5)
    async def threat_assessment(self):
        """ارزیابی تهدیدات"""
        try:
            # بررسی سطح تهدید بر اساس فعالیت‌های اخیر
            if self.interception_count > 10:
                self.threat_level = "high"
            elif self.interception_count > 5:
                self.threat_level = "medium"
            else:
                self.threat_level = "low"
            
            # تنظیم حالت دفاعی
            if self.threat_level == "high":
                self.defense_mode = "maximum"
            elif self.threat_level == "medium":
                self.defense_mode = "active"
            else:
                self.defense_mode = "normal"
                
        except Exception as e:
            print(f"خطا در ارزیابی تهدیدات: {e}")
    
    @tasks.loop(hours=6)
    async def defense_status_report(self):
        """گزارش وضعیت دفاعی"""
        try:
            embed = self.embed_builder.military_embed(
                "🛡️ گزارش وضعیت گنبد آهنین",
                f"**وضعیت فعلی سیستم دفاعی:**\n\n"
                f"🛡️ حالت دفاعی: {self.defense_mode}\n"
                f"⚠️ سطح تهدید: {self.threat_level}\n"
                f"🚀 موجودی موشک: {self.missile_inventory}\n"
                f"🎯 تعداد رابط‌ها: {self.interception_count}\n"
                f"⏰ آخرین رابط: {self.last_interception.strftime('%H:%M') if self.last_interception else 'هیچ'}"
            )
            
            # ارسال به کانال نظامی
            military_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="فرماندهی نظامی")
            if military_channel:
                await military_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در گزارش وضعیت دفاعی: {e}")
    
    async def close(self):
        """بستن ربات"""
        print("🔄 بستن ربات گنبد آهنین...")
        
        # توقف وظایف
        self.missile_replenishment.cancel()
        self.threat_assessment.cancel()
        self.defense_status_report.cancel()
        
        # بستن پایگاه داده
        await self.db.close()
        
        await super().close()
        print("✅ ربات گنبد آهنین بسته شد")

# کماندهای گنبد آهنین
class IronDomeCommands(commands.Cog):
    """کماندهای ربات گنبد آهنین"""
    
    def __init__(self, bot: IronDomeBot):
        self.bot = bot
    
    @commands.command(name="defense_status")
    @commands.has_permissions(administrator=True)
    async def defense_status(self, ctx):
        """نمایش وضعیت دفاعی"""
        try:
            embed = self.bot.embed_builder.military_embed(
                "🛡️ وضعیت گنبد آهنین",
                f"**وضعیت کامل سیستم دفاعی:**\n\n"
                f"🛡️ حالت دفاعی: {self.bot.defense_mode}\n"
                f"⚠️ سطح تهدید: {self.bot.threat_level}\n"
                f"🚀 موجودی موشک: {self.bot.missile_inventory}\n"
                f"🎯 تعداد رابط‌ها: {self.bot.interception_count}\n"
                f"⏰ آخرین رابط: {self.bot.last_interception.strftime('%Y-%m-%d %H:%M') if self.bot.last_interception else 'هیچ'}\n"
                f"🔄 تامین مجدد: هر ساعت\n"
                f"📊 ارزیابی تهدید: هر 5 دقیقه"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش وضعیت دفاعی: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="replenish_missiles")
    @commands.has_permissions(administrator=True)
    async def replenish_missiles(self, ctx, amount: int = 50):
        """تامین مجدد موشک‌ها"""
        try:
            if amount <= 0:
                embed = self.bot.embed_builder.error_embed(
                    "❌ مقدار نامعتبر",
                    "مقدار موشک باید مثبت باشد."
                )
                await ctx.send(embed=embed)
                return
            
            old_inventory = self.bot.missile_inventory
            self.bot.missile_inventory = min(200, self.bot.missile_inventory + amount)
            added = self.bot.missile_inventory - old_inventory
            
            embed = self.bot.embed_builder.success_embed(
                "✅ تامین مجدد انجام شد",
                f"**{added} موشک جدید اضافه شد!**\n\n"
                f"موجودی قبلی: {old_inventory}\n"
                f"موجودی جدید: {self.bot.missile_inventory}"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در تامین مجدد موشک: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="set_defense_mode")
    @commands.has_permissions(administrator=True)
    async def set_defense_mode(self, ctx, mode: str):
        """تنظیم حالت دفاعی"""
        try:
            valid_modes = ["normal", "active", "maximum", "disabled"]
            
            if mode.lower() not in valid_modes:
                embed = self.bot.embed_builder.error_embed(
                    "❌ حالت نامعتبر",
                    f"حالت‌های معتبر: {', '.join(valid_modes)}"
                )
                await ctx.send(embed=embed)
                return
            
            old_mode = self.bot.defense_mode
            self.bot.defense_mode = mode.lower()
            
            embed = self.bot.embed_builder.success_embed(
                "✅ حالت دفاعی تغییر کرد",
                f"**حالت دفاعی از {old_mode} به {self.bot.defense_mode} تغییر کرد.**"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در تنظیم حالت دفاعی: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="reset_interceptions")
    @commands.has_permissions(administrator=True)
    async def reset_interceptions(self, ctx):
        """ریست کردن آمار رابط‌ها"""
        try:
            old_count = self.bot.interception_count
            self.bot.interception_count = 0
            self.bot.last_interception = None
            
            embed = self.bot.embed_builder.success_embed(
                "✅ آمار ریست شد",
                f"**آمار رابط‌ها ریست شد!**\n\n"
                f"تعداد قبلی: {old_count}\n"
                f"تعداد جدید: 0"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در ریست آمار: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="emergency_defense")
    @commands.has_permissions(administrator=True)
    async def emergency_defense(self, ctx):
        """فعال‌سازی حالت دفاع اضطراری"""
        try:
            self.bot.defense_mode = "maximum"
            self.bot.threat_level = "critical"
            
            # تامین مجدد فوری
            self.bot.missile_inventory = 200
            
            embed = self.bot.embed_builder.military_embed(
                "🚨 حالت دفاع اضطراری فعال شد",
                "**سیستم گنبد آهنین در حالت دفاع اضطراری قرار گرفت!**\n\n"
                "🛡️ حالت: حداکثر\n"
                "⚠️ سطح تهدید: بحرانی\n"
                "🚀 موجودی موشک: 200\n"
                "🔄 تمام سیستم‌های دفاعی فعال شدند!"
            )
            
            await ctx.send(embed=embed)
            
            # اعلان در کانال‌های مختلف
            channels_to_notify = ["عمومی", "فرماندهی نظامی", "اتاق جنگ"]
            for channel_name in channels_to_notify:
                channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                if channel:
                    await channel.send("🚨 **حالت دفاع اضطراری فعال شد!**")
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در فعال‌سازی حالت دفاع اضطراری: {str(e)}"
            )
            await ctx.send(embed=embed)

async def main():
    """تابع اصلی"""
    bot = IronDomeBot()
    
    # اضافه کردن کماندها
    await bot.add_cog(IronDomeCommands(bot))
    
    try:
        await bot.start(bot.token)
    except KeyboardInterrupt:
        print("\n🛑 دریافت سیگنال توقف...")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())