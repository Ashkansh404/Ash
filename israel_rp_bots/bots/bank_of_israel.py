# -*- coding: utf-8 -*-
"""
ربات بانک اسرائیل - سیستم اقتصادی اسرائیل
Bank of Israel Bot - Israel's Economic System
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
from database import DatabaseManager, User, Economy
from utils import EmbedBuilder, EconomyCalculator, TextProcessor, TimeManager

class BankOfIsraelBot(commands.Bot):
    """ربات بانک اسرائیل"""
    
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        # تنظیمات اصلی
        self.token = DISCORD_TOKENS["bank_of_israel"]
        self.guild_id = SERVER_CONFIG["guild_id"]
        
        # کلاس‌های کمکی
        self.db = DatabaseManager(DATABASE_CONFIG)
        self.embed_builder = EmbedBuilder()
        self.time_manager = TimeManager()
        
        # متغیرهای اقتصادی
        self.interest_rate = 0.05  # نرخ سود
        self.inflation_rate = 0.02  # نرخ تورم
        self.exchange_rates = {
            "USD": 3.5,  # دلار آمریکا
            "EUR": 3.8,  # یورو
            "GBP": 4.2,  # پوند انگلیس
            "JPY": 0.025  # ین ژاپن
        }
        
        # ثبت رویدادها
        self.add_listeners()
        
    async def setup_hook(self):
        """تنظیم اولیه ربات"""
        print("🏦 راه‌اندازی ربات بانک اسرائیل...")
        
        # اتصال به پایگاه داده
        await self.db.connect()
        
        print("✅ ربات بانک اسرائیل آماده است!")
    
    def add_listeners(self):
        """اضافه کردن گوش‌دهندگان رویدادها"""
        
        @self.event
        async def on_ready():
            """رویداد آماده شدن ربات"""
            print(f"✅ {self.user} آماده است!")
            print(f"🆔 شناسه ربات: {self.user.id}")
            print(f"🏦 نرخ سود: {self.interest_rate:.2%}")
            
            # شروع وظایف زمان‌بندی شده
            self.daily_interest.start()
            self.market_update.start()
            self.economic_report.start()
            
            # تنظیم وضعیت ربات
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="اقتصاد اسرائیل 💰"
                )
            )
        
        @self.event
        async def on_message(message):
            """رویداد دریافت پیام"""
            if message.author.bot:
                return
            
            # پردازش کماندها
            await self.process_commands(message)
    
    @tasks.loop(hours=24)
    async def daily_interest(self):
        """پرداخت سود روزانه"""
        try:
            print("💰 پرداخت سود روزانه...")
            
            # دریافت همه کاربران
            async with self.db.pool.acquire() as conn:
                users = await conn.fetch("SELECT * FROM users WHERE balance > 0")
            
            total_interest_paid = 0
            
            for user_data in users:
                user = await self.db.get_user(user_data['user_id'])
                if user and user.balance > 0:
                    # محاسبه سود
                    daily_interest = user.balance * (self.interest_rate / 365)
                    user.balance += daily_interest
                    total_interest_paid += daily_interest
                    
                    # به‌روزرسانی کاربر
                    await self.db.update_user(user)
                    
                    # ثبت تراکنش
                    await self.db.create_transaction(
                        None, user.user_id, daily_interest, "interest", "سود روزانه"
                    )
            
            print(f"✅ سود روزانه پرداخت شد: {EconomyCalculator.format_currency(total_interest_paid)}")
            
            # اعلان در کانال بانک
            bank_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="عملیات بانکی")
            if bank_channel:
                embed = self.embed_builder.economy_embed(
                    "💰 سود روزانه پرداخت شد",
                    f"**سود روزانه برای {len(users)} کاربر پرداخت شد!**\n\n"
                    f"💰 کل سود پرداختی: {EconomyCalculator.format_currency(total_interest_paid)}\n"
                    f"📊 نرخ سود سالانه: {self.interest_rate:.2%}\n"
                    f"📅 تاریخ: {self.time_manager.get_current_time().strftime('%Y-%m-%d')}"
                )
                await bank_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در پرداخت سود روزانه: {e}")
    
    @tasks.loop(hours=6)
    async def market_update(self):
        """به‌روزرسانی بازار"""
        try:
            # تغییر نرخ ارز
            for currency in self.exchange_rates:
                change = random.uniform(-0.05, 0.05)  # تغییر 5%-
                self.exchange_rates[currency] *= (1 + change)
                self.exchange_rates[currency] = max(0.01, self.exchange_rates[currency])
            
            # تغییر نرخ تورم
            inflation_change = random.uniform(-0.001, 0.001)
            self.inflation_rate = max(0.0, min(0.1, self.inflation_rate + inflation_change))
            
            # تغییر نرخ سود
            interest_change = random.uniform(-0.001, 0.001)
            self.interest_rate = max(0.01, min(0.15, self.interest_rate + interest_change))
            
            print(f"📊 بازار به‌روزرسانی شد - تورم: {self.inflation_rate:.3%}, سود: {self.interest_rate:.3%}")
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی بازار: {e}")
    
    @tasks.loop(hours=12)
    async def economic_report(self):
        """گزارش اقتصادی"""
        try:
            # دریافت آمار اقتصادی
            stats = await self.db.get_statistics()
            economy = await self.db.get_economy()
            
            embed = self.embed_builder.economy_embed(
                "📊 گزارش اقتصادی",
                f"**وضعیت اقتصادی اسرائیل:**\n\n"
                f"💰 GDP: {EconomyCalculator.format_currency(economy.gdp)}\n"
                f"🏦 بودجه ملی: {EconomyCalculator.format_currency(economy.national_budget)}\n"
                f"💸 کل ثروت: {EconomyCalculator.format_currency(stats['total_wealth'])}\n"
                f"📈 نرخ تورم: {self.inflation_rate:.2%}\n"
                f"💵 نرخ سود: {self.interest_rate:.2%}\n"
                f"👥 تعداد شهروندان: {stats['citizens']}"
            )
            
            # اضافه کردن نرخ ارز
            exchange_info = "\n**💱 نرخ ارز:**\n"
            for currency, rate in self.exchange_rates.items():
                exchange_info += f"{currency}: {rate:.3f} شکل\n"
            
            embed.description += exchange_info
            
            # ارسال به کانال اخبار
            news_channel = discord.utils.get(self.get_guild(self.guild_id).channels, name="اخبار ملی")
            if news_channel:
                await news_channel.send(embed=embed)
                
        except Exception as e:
            print(f"خطا در گزارش اقتصادی: {e}")
    
    async def close(self):
        """بستن ربات"""
        print("🔄 بستن ربات بانک اسرائیل...")
        
        # توقف وظایف
        self.daily_interest.cancel()
        self.market_update.cancel()
        self.economic_report.cancel()
        
        # بستن پایگاه داده
        await self.db.close()
        
        await super().close()
        print("✅ ربات بانک اسرائیل بسته شد")

# کماندهای بانک اسرائیل
class BankCommands(commands.Cog):
    """کماندهای ربات بانک اسرائیل"""
    
    def __init__(self, bot: BankOfIsraelBot):
        self.bot = bot
    
    @commands.command(name="balance")
    async def balance(self, ctx, member: discord.Member = None):
        """نمایش موجودی حساب"""
        try:
            target_member = member or ctx.author
            user = await self.bot.db.get_user(target_member.id)
            
            if not user:
                embed = self.bot.embed_builder.error_embed(
                    "❌ کاربر یافت نشد",
                    "این کاربر در سیستم بانکی ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            embed = self.bot.embed_builder.economy_embed(
                "💰 موجودی حساب",
                f"**حساب {target_member.display_name}:**\n\n"
                f"💰 موجودی: {EconomyCalculator.format_currency(user.balance)}\n"
                f"📅 تاریخ عضویت: {user.join_date.strftime('%Y-%m-%d')}\n"
                f"👤 وضعیت: {user.citizenship_status}\n"
                f"💼 شغل: {user.job or 'بیکار'}"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش موجودی: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="transfer")
    async def transfer(self, ctx, member: discord.Member, amount: float):
        """انتقال پول"""
        try:
            if amount <= 0:
                embed = self.bot.embed_builder.error_embed(
                    "❌ مقدار نامعتبر",
                    "مقدار انتقال باید مثبت باشد."
                )
                await ctx.send(embed=embed)
                return
            
            sender = await self.bot.db.get_user(ctx.author.id)
            receiver = await self.bot.db.get_user(member.id)
            
            if not sender or not receiver:
                embed = self.bot.embed_builder.error_embed(
                    "❌ کاربر یافت نشد",
                    "یکی از کاربران در سیستم بانکی ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            if sender.balance < amount:
                embed = self.bot.embed_builder.error_embed(
                    "❌ موجودی ناکافی",
                    f"موجودی شما کافی نیست. موجودی فعلی: {EconomyCalculator.format_currency(sender.balance)}"
                )
                await ctx.send(embed=embed)
                return
            
            # انجام انتقال
            sender.balance -= amount
            receiver.balance += amount
            
            # به‌روزرسانی کاربران
            await self.bot.db.update_user(sender)
            await self.bot.db.update_user(receiver)
            
            # ثبت تراکنش
            await self.bot.db.create_transaction(
                sender.user_id, receiver.user_id, amount, "transfer", f"انتقال به {member.display_name}"
            )
            
            embed = self.bot.embed_builder.success_embed(
                "✅ انتقال موفق",
                f"**انتقال با موفقیت انجام شد!**\n\n"
                f"💰 مبلغ: {EconomyCalculator.format_currency(amount)}\n"
                f"👤 گیرنده: {member.display_name}\n"
                f"💳 موجودی جدید: {EconomyCalculator.format_currency(sender.balance)}"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در انتقال: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="deposit")
    async def deposit(self, ctx, amount: float):
        """واریز پول (فقط برای ادمین)"""
        try:
            if not ctx.author.guild_permissions.administrator:
                embed = self.bot.embed_builder.error_embed(
                    "❌ دسترسی محدود",
                    "فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
                )
                await ctx.send(embed=embed)
                return
            
            if amount <= 0:
                embed = self.bot.embed_builder.error_embed(
                    "❌ مقدار نامعتبر",
                    "مقدار واریز باید مثبت باشد."
                )
                await ctx.send(embed=embed)
                return
            
            user = await self.bot.db.get_user(ctx.author.id)
            if not user:
                embed = self.bot.embed_builder.error_embed(
                    "❌ کاربر یافت نشد",
                    "کاربر در سیستم بانکی ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            # واریز
            old_balance = user.balance
            user.balance += amount
            await self.bot.db.update_user(user)
            
            # ثبت تراکنش
            await self.bot.db.create_transaction(
                None, user.user_id, amount, "deposit", "واریز ادمین"
            )
            
            embed = self.bot.embed_builder.success_embed(
                "✅ واریز موفق",
                f"**واریز با موفقیت انجام شد!**\n\n"
                f"💰 مبلغ: {EconomyCalculator.format_currency(amount)}\n"
                f"💳 موجودی قبلی: {EconomyCalculator.format_currency(old_balance)}\n"
                f"💳 موجودی جدید: {EconomyCalculator.format_currency(user.balance)}"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در واریز: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: float):
        """برداشت پول (فقط برای ادمین)"""
        try:
            if not ctx.author.guild_permissions.administrator:
                embed = self.bot.embed_builder.error_embed(
                    "❌ دسترسی محدود",
                    "فقط ادمین‌ها می‌توانند از این دستور استفاده کنند."
                )
                await ctx.send(embed=embed)
                return
            
            if amount <= 0:
                embed = self.bot.embed_builder.error_embed(
                    "❌ مقدار نامعتبر",
                    "مقدار برداشت باید مثبت باشد."
                )
                await ctx.send(embed=embed)
                return
            
            user = await self.bot.db.get_user(ctx.author.id)
            if not user:
                embed = self.bot.embed_builder.error_embed(
                    "❌ کاربر یافت نشد",
                    "کاربر در سیستم بانکی ثبت نشده است."
                )
                await ctx.send(embed=embed)
                return
            
            if user.balance < amount:
                embed = self.bot.embed_builder.error_embed(
                    "❌ موجودی ناکافی",
                    f"موجودی کافی نیست. موجودی فعلی: {EconomyCalculator.format_currency(user.balance)}"
                )
                await ctx.send(embed=embed)
                return
            
            # برداشت
            old_balance = user.balance
            user.balance -= amount
            await self.bot.db.update_user(user)
            
            # ثبت تراکنش
            await self.bot.db.create_transaction(
                user.user_id, None, amount, "withdraw", "برداشت ادمین"
            )
            
            embed = self.bot.embed_builder.success_embed(
                "✅ برداشت موفق",
                f"**برداشت با موفقیت انجام شد!**\n\n"
                f"💰 مبلغ: {EconomyCalculator.format_currency(amount)}\n"
                f"💳 موجودی قبلی: {EconomyCalculator.format_currency(old_balance)}\n"
                f"💳 موجودی جدید: {EconomyCalculator.format_currency(user.balance)}"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در برداشت: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="transactions")
    async def transactions(self, ctx, limit: int = 10):
        """نمایش تراکنش‌های اخیر"""
        try:
            if limit > 20:
                limit = 20
            
            transactions = await self.bot.db.get_user_transactions(ctx.author.id, limit)
            
            if not transactions:
                embed = self.bot.embed_builder.info_embed(
                    "📋 تراکنش‌ها",
                    "هیچ تراکنشی یافت نشد."
                )
                await ctx.send(embed=embed)
                return
            
            embed = self.bot.embed_builder.economy_embed(
                "📋 تراکنش‌های اخیر",
                f"**آخرین {len(transactions)} تراکنش شما:**\n\n"
            )
            
            for i, trans in enumerate(transactions[:10], 1):
                amount = float(trans['amount'])
                amount_str = EconomyCalculator.format_currency(amount)
                
                if trans['from_user_id'] == ctx.author.id:
                    # برداشت
                    embed.add_field(
                        name=f"❌ {i}. برداشت",
                        value=f"مبلغ: {amount_str}\nنوع: {trans['transaction_type']}\nتاریخ: {trans['timestamp'].strftime('%Y-%m-%d %H:%M')}",
                        inline=True
                    )
                else:
                    # واریز
                    embed.add_field(
                        name=f"✅ {i}. واریز",
                        value=f"مبلغ: {amount_str}\nنوع: {trans['transaction_type']}\nتاریخ: {trans['timestamp'].strftime('%Y-%m-%d %H:%M')}",
                        inline=True
                    )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش تراکنش‌ها: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="exchange_rates")
    async def exchange_rates(self, ctx):
        """نمایش نرخ ارز"""
        try:
            embed = self.bot.embed_builder.economy_embed(
                "💱 نرخ ارز",
                "**نرخ ارز فعلی اسرائیل:**\n\n"
            )
            
            for currency, rate in self.bot.exchange_rates.items():
                embed.add_field(
                    name=f"💵 {currency}",
                    value=f"{rate:.3f} شکل",
                    inline=True
                )
            
            embed.add_field(
                name="📊 اطلاعات اقتصادی",
                value=f"نرخ تورم: {self.bot.inflation_rate:.2%}\nنرخ سود: {self.bot.interest_rate:.2%}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش نرخ ارز: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="bank_status")
    @commands.has_permissions(administrator=True)
    async def bank_status(self, ctx):
        """وضعیت بانک (فقط ادمین)"""
        try:
            stats = await self.bot.db.get_statistics()
            economy = await self.bot.db.get_economy()
            
            embed = self.bot.embed_builder.economy_embed(
                "🏦 وضعیت بانک اسرائیل",
                f"**وضعیت کامل سیستم بانکی:**\n\n"
                f"💰 کل ثروت: {EconomyCalculator.format_currency(stats['total_wealth'])}\n"
                f"👥 تعداد حساب‌ها: {stats['total_users']}\n"
                f"📈 GDP: {EconomyCalculator.format_currency(economy.gdp)}\n"
                f"🏦 بودجه ملی: {EconomyCalculator.format_currency(economy.national_budget)}\n"
                f"📊 نرخ تورم: {self.bot.inflation_rate:.2%}\n"
                f"💵 نرخ سود: {self.bot.interest_rate:.2%}\n"
                f"🔄 به‌روزرسانی بازار: هر 6 ساعت\n"
                f"💰 پرداخت سود: روزانه"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = self.bot.embed_builder.error_embed(
                "❌ خطا",
                f"خطا در نمایش وضعیت بانک: {str(e)}"
            )
            await ctx.send(embed=embed)

async def main():
    """تابع اصلی"""
    bot = BankOfIsraelBot()
    
    # اضافه کردن کماندها
    await bot.add_cog(BankCommands(bot))
    
    try:
        await bot.start(bot.token)
    except KeyboardInterrupt:
        print("\n🛑 دریافت سیگنال توقف...")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())