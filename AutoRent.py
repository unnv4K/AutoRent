# scope: hikka_only

"""
Модуль для авто-выдачи
"""

from hikkatl.types import Message
from hikkatl.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest, EditAdminRequest
from hikkatl.tl.types import ChatAdminRights

from .. import loader, utils
import asyncio
import re
import time

_version_ = (1, 0, 4)

@loader.tds
class AutoRent(loader.Module):
    """Авто-выдача"""
    strings = {"name": "AutoRent"}

    async def client_ready(self):
        self.client = self._client
        self.BOT_ID = 5522271758
        self.lock = asyncio.Lock()
        
        # ЭКИПИРОВКА
        self.equip_dict = {
            "🔪": ["тесак", "кт"],
            "🗡️": ["экскалибур", "меч", "вэ"],
            "🪓": ["топор", "секира", "бс"],
            "⛏": ["кирка", "кд", "кирка добытчика"],
            "5235447666468491170": ["бластер", "бласт", "пест", "тб"],  # 🔫
            "5235919511575634597": ["лук", "эл", "энерго-лук", "энерголук"],  # 🏹
            "🪖": ["бшлем", "брш"],
            "⛑️": ["мшлем", "мш"],
            "🥼": ["халат", "мхн"],
            "🦺": ["жилет", "брж"],
            "👖": ["мштаны", "бштаны", "шн"],
            "👞": ["туфли", "туф"],
            "🥾": ["берцы", "бер"],
            "🧢": ["кепка", "кеп"],
            "👕": ["футболка", "футб"],
            "🩳": ["шорты", "лшн"],
            "🩴": ["тапки", "шлепки"]
        }
        
        # ПРЕДМЕТЫ
        self.subject_dict = {
            "🤡": ["мк", "маска", "маску"],
            "5294403217956837190": ["иа", "искатель", "искатель артефактов"],  # 🔍 Искатель
            "🧺": ["к", "корза", "корзина", "корзину", "корзу"],
            "🧮": ["с", "счёты", "счеты", "счёт", "счет"],
            "🌠": ["з", "звезда", "звезду", "п", "пз"],
            "🍀": ["ч", "чк", "клевер"],
            "☘": ["ст", "сингулярный", "трилистник"],
            "🍹": ["тк", "коктейль"],
            "🔋": ["а", "акум", "аккумулятор"],
            "🗺": ["км", "карта", "карту"],
            "🌡": ["кск", "колба", "колбу"],
            "🎗": ["ле", "лента", "ленту", "ленточка", "ленточку"],
            "🪃": ["б", "бумер", "бумеранг"],
            "🎖": ["мч", "мд", "медаль", "медальку"],
            "🧲": ["м", "магнит"],
            "🧿": ["ам", "амул", "амуль", "амулет"],
            "📿": ["ож", "ожка", "ожку", "ожерелье"],
            "🧤": ["перчи", "перчатки", "перчатку"],
            "⏱": ["сек", "секундомер"],
            "🧨": ["в", "взрыв", "взрыву", "взрыва", "взрывка", "взрывку", "взрывчатка", "взрывчатку"],
            "🪄": ["вп", "палка", "палку", "палочка", "палочку"],
            "📗": ["ропк", "руководство"],
            "⏲": ["т", "тайм", "таймер"],
            "🌜": ["лк", "луна", "луну", "луный"],
            "🌞": ["ск", "солнечный", "солнце"],
            "💍": ["ксб", "кольцо"],
            "🔧": ["гк", "гаечный", "ключ"],
            "⚖": ["весы"],
            "🧩": ["ои", "игра", "игру", "осколок"]
        }
        
        self.level_to_emoji = {
            "т1": "⚪",
            "т2": "🟢",
            "т3": "🔵",
            "т4": "🟣",
            "т5": "🟡",
            "т6": "🟠",
            "т7": "🔴"
        }
        
        try:
            self.work_chat, _ = await utils.asset_channel(
                self.client, 
                'AutoRent', 
                'Чат для работы', 
                silent=True, 
                archive=True, 
                _folder='hikka'
            )
            try:
                await self.client(InviteToChannelRequest(self.work_chat, [self.BOT_ID]))
            except:
                pass
            try:
                await self.client(EditAdminRequest(
                    channel=self.work_chat,
                    user_id=self.BOT_ID,
                    admin_rights=ChatAdminRights(
                        post_messages=True, 
                        edit_messages=True, 
                        delete_messages=True
                    ),
                    rank="EVO"
                ))
            except:
                pass
        except Exception:
            self.work_chat = None

    def get_equip_emoji_by_name(self, name: str) -> str | None:
        name = name.lower().strip()
        for emoji, names in self.equip_dict.items():
            for n in names:
                if name == n.lower() or name in n.lower() or n.lower() in name:
                    return emoji
        return None

    def get_subject_emoji_by_name(self, name: str) -> str | None:
        name = name.lower().strip()
        for emoji, names in self.subject_dict.items():
            for n in names:
                if name == n.lower() or name in n.lower():
                    return emoji
        return None

    def validate_time_format(self, time_str: str) -> bool:
        return bool(re.match(r'^\d+[мчд]$', time_str))

    async def refresh_message(self, message: Message) -> Message:
        if not message:
            return None
        try:
            msgs = await self.client.get_messages(message.peer_id, ids=[message.id])
            return msgs[0] if msgs else message
        except Exception:
            return message

    async def try_click(self, msg, required_texts, exclude_handshake=False):
        msg = await self.refresh_message(msg)
        if not msg or not msg.buttons:
            return False
        
        tokens = list(required_texts) if isinstance(required_texts, (list, tuple, set)) else [required_texts]
        
        for row in msg.buttons:
            for btn in row:
                if not btn.text:
                    continue
                if exclude_handshake and ('🤝' in btn.text or '🖐' in btn.text):
                    continue
                
                btn_text = btn.text
                
                # Извлекаем все emoji-id из текста кнопки
                emoji_ids_in_button = re.findall(r'<tg-emoji emoji-id="(\d+)">', btn_text)
                
                match_count = 0
                for token in tokens:
                    # 1. Проверяем прямое вхождение текста
                    if token in btn_text:
                        match_count += 1
                        continue
                    
                    # 2. Если токен - число, проверяем есть ли такой emoji-id в кнопке
                    if token.isdigit():
                        if token in emoji_ids_in_button:
                            match_count += 1
                            continue
                    
                    # 3. Если токен - это HTML тег, извлекаем ID и проверяем
                    if '<tg-emoji' in token:
                        match = re.search(r'emoji-id="(\d+)"', token)
                        if match:
                            emoji_id = match.group(1)
                            if emoji_id in emoji_ids_in_button:
                                match_count += 1
                                continue
                
                if match_count == len(tokens):
                    try:
                        await asyncio.wait_for(btn.click(), timeout=1.0)
                        await asyncio.sleep(0.05)
                        return True
                    except:
                        pass
        return False

    async def process_equip_interaction(self, equip_emoji: str, nickname: str, time_str: str, lvl_emoji: str = None) -> float:
        """Возвращает время выполнения в секундах (от первого ответа бота)"""
        if not self.validate_time_format(time_str):
            raise ValueError('<b>⏱ Неправильное время</b>')

        if not self.work_chat:
            raise ValueError('<b>❌ Чат не создан</b>')

        await self.client.send_message(self.work_chat, 'экип')
        
        bot_message = None
        start_time = time.time()
        first_response_time = None
        
        while time.time() - start_time < 10:
            await asyncio.sleep(0.5)
            msgs = await self.client.get_messages(self.work_chat, limit=5)
            for m in msgs:
                if m and m.sender_id == self.BOT_ID and m.buttons:
                    if m.date.timestamp() > start_time - 3:
                        bot_message = m
                        first_response_time = time.time()
                        break
            if bot_message:
                break

        if not bot_message:
            raise ValueError('<b>⌛ Бот не отвечает</b>')

        # Выбираем экипировку
        found = False
        timeout = 10
        search_start = time.time()

        while time.time() - search_start < timeout:
            await asyncio.sleep(0.05)
            new_msg = await self.refresh_message(bot_message)
            if new_msg.buttons != bot_message.buttons:
                bot_message = new_msg

            required_tokens = [equip_emoji] if not lvl_emoji else [equip_emoji, lvl_emoji]

            if await self.try_click(bot_message, required_tokens, exclude_handshake=True):
                found = True
                break

            if not await self.try_click(bot_message, '»'):
                break

        if not found:
            if lvl_emoji:
                raise ValueError(f'<b>⛔️ Экипировки {equip_emoji}{lvl_emoji} нету</b>')
            raise ValueError(f'<b>⛔️ Экипировки {equip_emoji} нету</b>')

        # Нажимаем кнопку 🤝
        if not await self.try_click(bot_message, '🤝'):
            raise ValueError('<b>⛔️ Нет кнопки 🤝</b>')

        # Отправляем ник и время
        await self.client.send_message(self.work_chat, f'{nickname} {time_str}', reply_to=bot_message.id)

        # Ждём и нажимаем кнопку 💜 Доверить
        trust_button_found = False
        trust_wait_start = time.time()

        while time.time() - trust_wait_start < 10:
            await asyncio.sleep(0.1)
            new_msg = await self.refresh_message(bot_message)
            if new_msg.buttons != bot_message.buttons:
                bot_message = new_msg

            if await self.try_click(bot_message, '💜 Доверить'):
                trust_button_found = True
                break

        if not trust_button_found:
            raise ValueError('<b>⛔️ Нет кнопки Доверить</b>')

        duration = time.time() - first_response_time

        try:
            await self.client.delete_messages(self.work_chat, [bot_message.id])
        except:
            pass

        return duration

    async def process_subject_interaction(self, subject_emoji: str, nickname: str, time_str: str, lvl_emoji: str = None) -> float:
        """Возвращает время выполнения в секундах (от первого ответа бота)"""
        if not self.validate_time_format(time_str):
            raise ValueError('<b>⏱ Неправильное время</b>')

        if not self.work_chat:
            raise ValueError('<b>❌ Чат не создан</b>')

        await self.client.send_message(self.work_chat, 'предметы')
        
        bot_message = None
        start_time = time.time()
        first_response_time = None
        
        while time.time() - start_time < 10:
            await asyncio.sleep(0.5)
            msgs = await self.client.get_messages(self.work_chat, limit=5)
            for m in msgs:
                if m and m.sender_id == self.BOT_ID and m.buttons:
                    if m.date.timestamp() > start_time - 3:
                        bot_message = m
                        first_response_time = time.time()
                        break
            if bot_message:
                break

        if not bot_message:
            raise ValueError('<b>⌛ Бот не отвечает</b>')

        # Выбираем предмет
        found = False
        timeout = 10
        search_start = time.time()

        while time.time() - search_start < timeout:
            await asyncio.sleep(0.05)
            new_msg = await self.refresh_message(bot_message)
            if new_msg.buttons != bot_message.buttons:
                bot_message = new_msg

            required_tokens = [subject_emoji] if not lvl_emoji else [subject_emoji, lvl_emoji]

            if await self.try_click(bot_message, required_tokens, exclude_handshake=True):
                found = True
                break

            if not await self.try_click(bot_message, '»'):
                break

        if not found:
            if lvl_emoji:
                raise ValueError(f'<b>⛔️ Предмета {subject_emoji}{lvl_emoji} нету</b>')
            raise ValueError(f'<b>⛔️ Предмета {subject_emoji} нету</b>')

        # Нажимаем кнопку 🤝
        if not await self.try_click(bot_message, '🤝'):
            raise ValueError('<b>⛔️ Нет кнопки 🤝</b>')

        # Отправляем ник и время
        await self.client.send_message(self.work_chat, f'{nickname} {time_str}', reply_to=bot_message.id)

        # Ждём и нажимаем кнопку 💜 Доверить
        trust_button_found = False
        trust_wait_start = time.time()

        while time.time() - trust_wait_start < 10:
            await asyncio.sleep(0.1)
            new_msg = await self.refresh_message(bot_message)
            if new_msg.buttons != bot_message.buttons:
                bot_message = new_msg

            if await self.try_click(bot_message, '💜 Доверить'):
                trust_button_found = True
                break

        if not trust_button_found:
            raise ValueError('<b>⛔️ Нет кнопки Доверить</b>')

        duration = time.time() - first_response_time

        try:
            await self.client.delete_messages(self.work_chat, [bot_message.id])
        except:
            pass

        return duration

    @loader.command()
    async def экип(self, message: Message) -> None:
        """<экипировка> [т] <ник> <время>"""
        async with self.lock:
            args = utils.get_args(message)

            if not (3 <= len(args) <= 4):
                await utils.answer(message, '<b>📄 .экип <предмет> [т] <ник> <время>\nПример: .экип кирка т6 кирич 2ч</b>')
                return

            level_str = None
            lvl_emoji = None
            
            if len(args) == 4:
                equip_name, level_str, nickname, time_str = args
            else:
                equip_name, nickname, time_str = args

            equip_emoji = self.get_equip_emoji_by_name(equip_name)
            if not equip_emoji:
                await utils.answer(message, f'<b>❌ "{equip_name}" не найдена</b>')
                return

            if level_str:
                match = re.match(r'^[тТ]\s*([1-7])$', level_str)
                if match:
                    lvl = match.group(1)
                    lvl_emoji = self.level_to_emoji.get(f'т{lvl}')
                    if not lvl_emoji:
                        await utils.answer(message, f'<b>⛔️ Уровень {lvl} не настроен</b>')
                        return
                else:
                    await utils.answer(message, '<b>⛔️ Уровень: т1-т7</b>')
                    return

            # Отправляем сообщение о начале процесса
            status_msg = await utils.answer(message, "<b>⚙️ В процессе...</b>")
            
            try:
                duration = await self.process_equip_interaction(
                    equip_emoji=equip_emoji, 
                    nickname=nickname, 
                    time_str=time_str, 
                    lvl_emoji=lvl_emoji
                )
                
                equip_display = f"{equip_emoji}{lvl_emoji or ''}"
                
                success_text = (
                    f"<b>🧰 Экипировка выдана!</b>\n"
                    f"• Экипировка: <code>{equip_display}</code>\n"
                    f"• Получатель: <code>{nickname}</code>\n"
                    f"• Время аренды: <code>{time_str}</code>\n"
                    f"• ⏱ <code>{duration:.1f} сек</code>"
                )
                
                await status_msg.edit(success_text)
                
            except Exception as e:
                await status_msg.edit(f'{str(e)}')

    @loader.command()
    async def прд(self, message: Message) -> None:
        """<предмет> [т] <ник> <время>"""
        async with self.lock:
            args = utils.get_args(message)

            if not (3 <= len(args) <= 4):
                await utils.answer(message, '<b>📄 .прд <предмет> [т] <ник> <время>\nПример: .прд маска т6 кирич 2ч</b>')
                return

            level_str = None
            lvl_emoji = None
            
            if len(args) == 4:
                subject_name, level_str, nickname, time_str = args
            else:
                subject_name, nickname, time_str = args

            subject_emoji = self.get_subject_emoji_by_name(subject_name)
            if not subject_emoji:
                await utils.answer(message, f'<b>❌ "{subject_name}" не найден</b>')
                return

            if level_str:
                match = re.match(r'^[тТ]\s*([1-7])$', level_str)
                if match:
                    lvl = match.group(1)
                    lvl_emoji = self.level_to_emoji.get(f'т{lvl}')
                    if not lvl_emoji:
                        await utils.answer(message, f'<b>⛔️ Уровень {lvl} не настроен</b>')
                        return
                else:
                    await utils.answer(message, '<b>⛔️ Уровень: т1-т7</b>')
                    return

            # Отправляем сообщение о начале процесса
            status_msg = await utils.answer(message, "<b>⚙️ В процессе...</b>")
            
            try:
                duration = await self.process_subject_interaction(
                    subject_emoji=subject_emoji, 
                    nickname=nickname, 
                    time_str=time_str, 
                    lvl_emoji=lvl_emoji
                )
                
                subject_display = f"{subject_emoji}{lvl_emoji or ''}"
                
                success_text = (
                    f"<b>👜 Предмет выдан!</b>\n"
                    f"• Предмет: <code>{subject_display}</code>\n"
                    f"• Получатель: <code>{nickname}</code>\n"
                    f"• Время аренды: <code>{time_str}</code>\n"
                    f"• ⏱ <code>{duration:.1f} сек</code>"
                )
                
                await status_msg.edit(success_text)
                
            except Exception as e:
                await status_msg.edit(f'{str(e)}')