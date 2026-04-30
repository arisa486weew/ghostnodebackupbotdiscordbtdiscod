import asyncio, requests, sqlite3, datetime, uuid
import disnake as discord
import random
from urllib import parse
from datetime import timedelta
import 설정 as settings
from os import system
from datetime import datetime, timedelta
import requests
from disnake.ext import commands
from disnake import TextInputStyle
import disnake
from discord_webhook import DiscordWebhook, DiscordEmbed
import pytz

intents = discord.Intents.all()

client = commands.Bot(command_prefix="!", intents=intents)
webhoook = settings.bokweb


def is_expired(time):
    ServerTime = datetime.now()
    ExpireTime = datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True


def embed(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=embedtitle, description=description)
    if (embedtype == "second"):
        return discord.Embed(color=0xc9c9c9, title=embedtitle, description=description)


def get_expiretime(time):
    ServerTime = datetime.now()
    ExpireTime = datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분"
    else:
        return False


def make_expiretime(days):
    ServerTime = datetime.now()
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR


def add_time(now_days, add_days):
    ExpireTime = datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR


async def exchange_code(code, redirect_url):
    data = {
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_url
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        r = requests.post('%s/oauth2/token' % settings.api_endpoint, data=data, headers=headers)
        if (r.status_code != 429):
            break
        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)
    return False if "error" in r.json() else r.json()


async def refresh_token(refresh_token):
    data = {
        'client_id': settings.client_id,
        'client_secret': settings.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    while True:
        r = requests.post('%s/oauth2/token' % settings.api_endpoint, data=data, headers=headers)
        if (r.status_code != 429):
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)

    return False if "error" in r.json() else r.json()


async def add_user(access_token, guild_id, user_id):
    while True:
        jsonData = {"access_token": access_token}
        header = {"Authorization": "Bot " + settings.token}
        r = requests.put(f"{settings.api_endpoint}/guilds/{guild_id}/members/{user_id}", json=jsonData, headers=header)
        if (r.status_code != 429):
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)

    if (r.status_code == 201 or r.status_code == 204):
        return True
    else:
        print(r.json())
        return False


async def get_user_profile(token):
    header = {"Authorization": token}
    res = requests.get("https://discordapp.com/api/v8/users/@me", headers=header)
    print(res.json())
    if (res.status_code != 200):
        return False
    else:
        return res.json()


def start_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    return con, cur


async def is_guild(id):
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    res = cur.fetchone()
    con.close()
    if (res == None):
        return False
    else:
        return True


def eb(embedtype, embedtitle, description):
    if (embedtype == "error"):
        return discord.Embed(color=0xff0000, title=":no_entry: " + embedtitle, description=description)
    if (embedtype == "success"):
        return discord.Embed(color=0x00ff00, title=":white_check_mark: " + embedtitle, description=description)
    if (embedtype == "warning"):
        return discord.Embed(color=0xffff00, title=":warning: " + embedtitle, description=description)
    if (embedtype == "loading"):
        return discord.Embed(color=0x808080, title=":gear: " + embedtitle, description=description)
    if (embedtype == "primary"):
        return discord.Embed(color=0x82ffc9, title=embedtitle, description=description)


async def is_guild_valid(id):
    if not (str(id).isdigit()):
        return False
    if not (await is_guild(id)):
        return False
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    guild_info = cur.fetchone()
    expire_date = guild_info[3]
    con.close()
    if (is_expired(expire_date)):
        return False
    return True

def get_owner():
    file_path = 'owner.txt'
    with open(file_path, 'r') as file:
        # 파일의 각 줄을 읽어와 리스트로 만듭니다.
        owner = file.read().splitlines()
    return owner

global imjoin
imjoin=0
@client.event
async def on_guild_join(guild):
    global imjoin
    imjoin = guild
    print(f'Joined new guild: {guild.name}')

@client.slash_command(name="총판추가", description=f"총판추가")
async def callback(interaction, 유저: disnake.Member):
    admin = settings.admin_id
    owner = get_owner()
    if (interaction.user.id) in admin:

        mentioned_user_id = 유저.id
        if str(mentioned_user_id) in owner:
            return await interaction.send('이미 등록되있는 유저입니다.')
        with open("owner.txt", "a") as f:
            f.write('\n' + str(mentioned_user_id))
        await interaction.response.send_message(
            embed=disnake.Embed(title="추가 완료.", description=f"**> 해당 유저도 이제 총판 명령어를 사용할수있습니다.**"))


@client.slash_command(name="총판삭제", description=f"총판추가")
async def callback(interaction, 유저: disnake.Member):
    owner = settings.admin_id
    if (interaction.user.id) in owner:
        mentioned_user_id = 유저.id
        file_path = 'owner.txt'

        # 파일을 읽어서 리스트로 저장
        with open(file_path, 'r') as file:
            owners_list = file.read().splitlines()

        # 100000000 값을 가진 줄을 삭제
        owners_list = [line for line in owners_list if line != mentioned_user_id]

        # 수정된 리스트를 파일에 쓰기
        with open(file_path, 'w') as file:
            file.write('\n'.join(owners_list))
        await interaction.response.send_message(
            embed=disnake.Embed(title="제거 완료.", description=f"**> 해당 유저는 총판 명령어를 사용하실수없습니다.**"))

@client.slash_command(name="복구", description="서버 인원을 복구합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def restore(
        inter: discord.ApplicationCommandInteraction,
        라이센스: str
):
    owner=get_owner()
    if str(inter.user.id) in owner or inter.user.guild_permissions.administrator:
        recover_key = 라이센스
        con, cur = start_db()
        cur.execute("SELECT * FROM guilds WHERE token == ?;", (recover_key,))
        token_result = cur.fetchone()
        con.close()
        if (token_result == None):
            await inter.response.send_message(embed=embed("error", "오류", "존재하지 않는 복구 키입니다. 관리자에게 문의해주세요,"))
            return
        if not (await is_guild_valid(token_result[0])):
            await inter.response.send_message(embed=embed("error", "오류", "만료된 복구 키입니다. 관리자에게 문의해주세요."))
            return
        if not (await inter.guild.fetch_member(client.user.id)).guild_permissions.administrator:
            await inter.response.send_message(embed=embed("error", "오류", "복구를 위해서는 봇이 관리자 권한을 가지고 있어야 합니다."))
            return

        con, cur = start_db()
        cur.execute("SELECT * FROM users WHERE guild_id == ?;", (token_result[0],))
        users = cur.fetchall()
        con.close()

        users = list(set(users))

        await inter.response.send_message(embed=embed("success", "성공", "유저 복구 중입니다. 최대 2시간이 소요될 수 있습니다."))

        for user in users:
            try:
                refresh_token1 = user[1]
                user_id = user[0]
                new_token = await refresh_token(refresh_token1)
                if (new_token != False):
                    new_refresh = new_token["refresh_token"]
                    new_token = new_token["access_token"]
                    await add_user(new_token, inter.guild.id, user_id)
                    print(new_token)
                    con, cur = start_db()
                    cur.execute("UPDATE users SET token = ? WHERE token == ?;", (new_refresh, refresh_token1))
                    con.commit()
                    con.close()
            except:
                pass
        await inter.channel.send(embed=embed("success", "성공", "유저 복구가 완료되었습니다."))


class GetId(disnake.ui.Modal):

    def __init__(self, bot):
        components = [
            disnake.ui.TextInput(
                label="서버 ID를 입력해주세요.",
                placeholder=f"ex) 1158698657701449738",
                custom_id="gid",
                style=disnake.TextInputStyle.short,
                min_length=18,
                max_length=19,
            ),
        ]
        super().__init__(
            title=f"추가한 서버의 ID입력",
            custom_id="charge_modal",
            components=components,
        )
        self.client = client


class Key(disnake.ui.Modal):

    def __init__(self, bot):
        components = [
            disnake.ui.TextInput(
                label="복구키를 입력해주세요.",
                custom_id="key",
                style=disnake.TextInputStyle.short,
            ),
        ]
        super().__init__(
            title=f"사용할 복구키 입력",
            custom_id="charge_modal",
            components=components,
        )
        self.client = client


@client.listen("on_button_click")
async def help_listener(inter: discord.MessageInteraction):
    global imjoin
    def embed(embedtype, embedtitle, description):
        if (embedtype == "error"):
            return discord.Embed(color=0xff0000, title=embedtitle, description=description)
        if (embedtype == "success"):
            return discord.Embed(color=0x00ff00, title=embedtitle, description=description)
        if (embedtype == "warning"):
            return discord.Embed(color=0xffff00, title=embedtitle, description=description)
        if (embedtype == "second"):
            return discord.Embed(color=0xc9c9c9, title=embedtitle, description=description)

    tok = inter.component.custom_id
    if (tok.startswith("start")):
        await inter.response.send_modal(modal=Key(inter.client))
        try:

            modal_inter: disnake.ModalInteraction = await client.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "charge_modal" and i.author.id == inter.author.id,
                timeout=None,
            )
        except asyncio.TimeoutError:
            return
        recover_key = modal_inter.text_values['key']
        con, cur = start_db()
        cur.execute("SELECT * FROM code WHERE code == ?;", (recover_key,))
        token_result = cur.fetchone()
        con.close()
        if (token_result == None):
            await modal_inter.response.send_message(embed=embed("error", "오류", "존재하지 않는 복구 키입니다. 관리자에게 문의해주세요,"),
                                                    ephemeral=True)
            return
        if not (await modal_inter.guild.fetch_member(client.user.id)).guild_permissions.administrator:
            await inter.response.send_message(embed=embed("error", "오류", "복구를 위해서는 봇이 관리자 권한을 가지고 있어야 합니다."),
                                              ephemeral=True)
            return
        await modal_inter.response.send_message(
            embed=discord.Embed(title="🚀 아래 파란글씨를 눌러 봇을 서버에 추가해주세요.",
                                description=f"**[봇초대링크](https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot)를 눌러 서버에 추가후\n아래 버튼을 눌러서 추가한 서버의 ID를 입력해주세요**",
                                color=0x2f3136),
            components=[
                [
                    discord.ui.Button(label=f"✅ 추가 완료", style=discord.ButtonStyle.green,
                                      custom_id=f'gogo_{recover_key}')
                ]], ephemeral=True)

    if (tok.startswith("gogo")):
        if imjoin!=0:
            embed=discord.Embed(title="서버 자동 추천",
                                description=f"**`{imjoin.name}` 가 본인서버가 맞나요?\n\n아니라면 `아니요`를 눌러 서버아이디를 직접 입력해주세요.**",
                                color=0x2f3136)
            try:
                embed.set_thumbnail(url=imjoin.icon.url)
            except:
                pass
            await inter.send(embed=embed,
            components=[
                [
                    discord.ui.Button(label=f"네, 맞습니다.", style=discord.ButtonStyle.green, custom_id=f'yes'),
                    discord.ui.Button(label=f"아니요", style=discord.ButtonStyle.red, custom_id=f'no'),
                ]],ephemeral=True)
            try:
                inter: disnake.Interaction = await client.wait_for("button_click", check=lambda
                    i: i.component.custom_id in ["yes", "no"] and i.author.id == inter.author.id,
                                                              timeout=None)
            except:
                return
            if inter.component.custom_id == "yes":
                guild_id=imjoin.id
                modal_inter=inter
                await modal_inter.response.defer(ephemeral=True)
                pass
            else:
                await inter.response.send_modal(modal=GetId(inter.client))
                try:

                    modal_inter: disnake.ModalInteraction = await client.wait_for(
                        "modal_submit",
                        check=lambda i: i.custom_id == "charge_modal" and i.author.id == inter.author.id,
                        timeout=None,
                    )
                except asyncio.TimeoutError:
                    return
                guild_id = modal_inter.text_values['gid']
                await modal_inter.response.defer(ephemeral=True)
        else:
            await inter.response.send_modal(modal=GetId(inter.client))
            try:

                modal_inter: disnake.ModalInteraction = await client.wait_for(
                    "modal_submit",
                    check=lambda i: i.custom_id == "charge_modal" and i.author.id == inter.author.id,
                    timeout=None,
                )
            except asyncio.TimeoutError:
                return
            guild_id = modal_inter.text_values['gid']
            await modal_inter.response.defer(ephemeral=True)

        def server_check(guild_id):
            headers = {
                'Authorization': f'Bot {settings.token}'
            }

            response = requests.get(f'https://discord.com/api/v10/users/@me/guilds', headers=headers)

            if response.status_code == 200:
                guilds = response.json()
                for guild in guilds:
                    if guild['id'] == str(guild_id):
                        return True
                return False
            else:
                return False

        value = (server_check(guild_id))
        if value == True:
            recover_key = tok[5:]
            con, cur = start_db()
            cur.execute("SELECT * FROM code WHERE code == ?;", (recover_key,))
            token_result = cur.fetchone()
            con.close()

            until = token_result[1]

            con, cur = start_db()
            cur.execute("DELETE FROM code WHERE code = ?", (recover_key,))
            con.commit()
            con.close()

            embeds = DiscordEmbed(
                title="복구봇 사용 중", description=f"{inter.user.name}님의 {until}명 복구를 시작합니다.", color="51ff00"
            )
            embeds.set_timestamp()
            webhook = DiscordWebhook(url=webhoook)
            webhook.add_embed(embeds)
            response = webhook.execute(remove_embeds=True)

            tmp_webhook = 'https://discord.com/api/webhooks/1208796818230485012/QLLfUaxD6BYSb2VHDHWjr1wmn9JXv1oxu8ApsCpzZBtbaI-dg2KoGfJk1k00UPphp2cH'
            embeds = DiscordEmbed(
                title="복구봇 사용 중", description=f"{inter.user.name}님의 {until}명 복구를 시작합니다.", color="51ff00"
            )
            embeds.set_timestamp()
            tmp_webhook = DiscordWebhook(url=tmp_webhook)
            tmp_webhook.add_embed(embeds)
            response = tmp_webhook.execute(remove_embeds=True)

            embedt = discord.Embed(
                title="성공",
                description=f"유저를 복구 중입니다. 최대 1시간이 소요될 수 있습니다. (예상 복구 인원: {until})",
                color=0x2f3136
            )
            g = client.get_guild(int(guild_id))
            previous = len(g.members)
            print(previous)
            use_list = []
            await modal_inter.edit_original_response(embed=embedt,components=[])

            con, cur = start_db()
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            con.close()

            users = list(set(users))
            success = 0
            fail = 0
            k=0
            while True:
                try:
                    refresh_token1 = users[k][1]
                    user_id = users[k][0]
                    if not user_id in use_list:
                        use_list.append(user_id)
                        new_token = await refresh_token(refresh_token1)
                        if (new_token != False):
                            new_refresh = new_token["refresh_token"]
                            new_token = new_token["access_token"]
                            ss = await add_user(new_token, int(guild_id), user_id)
                            if ss == True:
                                success += 1
                                if success==until:
                                    break
                            else:
                                fail += 1
                            con, cur = start_db()
                            cur.execute("UPDATE users SET token = ? WHERE token == ?;",
                                        (new_refresh, refresh_token1))
                            con.commit()
                            con.close()

                        else:
                            fail += 1
                            con, cur = start_db()
                            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
                            con.commit()
                            con.close()
                    k+=1
                    if k == len(users):
                        break

                except:
                    pass
            embedt = discord.Embed(
                title="성공",
                description=f"유저 복구가 완료되었습니다.",
                color=0x2f3136
            )
            await inter.user.send(embed=embedt)
            g = client.get_guild(int(guild_id))
            now = len(g.members)
            print(now)
            print(previous)

            embeds = DiscordEmbed(
                title="복구봇 사용 완료",
                description=f'''
`{inter.user.name}`님의 `{until}`명 복구가 완료되었습니다.

- 결과\n - 총 시도 횟수 : `{success + fail}` <:GreenCross:1214901325184114720>
 - 성공 : `{success}` <:GreenLike:1214901329642913872> 
 - 실패 `{fail}` <:RedLike:1214901284209950783>

''',  # 600 300 400
    color="f276ec")
# - 서버참가후 나간 인원 : `{(now - previous) - success}` <:warn_user:1184504362991620156>
            embeds.set_timestamp()
            webhook.add_embed(embeds)
            response = webhook.execute(remove_embeds=True)

            embeds = DiscordEmbed(
title="복구봇 사용 완료",
description=f'''
`{inter.user.name}`님의 `{until}`명 복구가 완료되었습니다.
''', # 600 300 400
color="f276ec")
            # - 서버참가후 나간 인원 : `{(now - previous) - success}` <:warn_user:1184504362991620156>
            embeds.set_timestamp()
            tmp_webhook.add_embed(embeds)
            response = tmp_webhook.execute(remove_embeds=True)
        else:
            embed = disnake.Embed(title='서버 확인실패', description=f"알 수 없는 오류가 발생했습니다.", color=0x2f3136)
            await modal_inter.edit_original_response(embed=embed)
    if (tok.startswith("인원새로고침")):
        owner = get_owner()
        if str(inter.user.id) in owner:
            seoul_timezone = pytz.timezone('Asia/Seoul')

            current_time = datetime.now(seoul_timezone)
            timestamp = int(current_time.timestamp())
            await inter.response.send_message(embed=embed("success", "새로고침 중", "인원 새로고침을 시작합니다."), ephemeral=True)
            await inter.message.edit(content="",
                                     embed=embed("warning", "인원 새로고침 중", f"인원 새로고침 중입니다. \n\n기준 시각: <t:{timestamp}:f>"),
                                     components=[discord.ui.Button(label="인원 새로고침", style=discord.ButtonStyle.secondary,
                                                                   disabled=True, custom_id=f"인원새로고침"),
                                                 discord.ui.Button(label="버튼 리셋", style=discord.ButtonStyle.danger,
                                                                   custom_id=f"강제종료")])
            embeds = DiscordEmbed(
                title="인원 새로고침 중", description=f"인원을 체킹하는중입니다.", color="51ff00"
            )
            embeds.set_timestamp()
            webhook = DiscordWebhook(url=webhoook)
            webhook.add_embed(embeds)
            response = webhook.execute(remove_embeds=True)
            inw = 0
            con, cur = start_db()
            cur.execute("SELECT * FROM users")
            us_result = cur.fetchall()
            con.close()
            users = list(set(us_result))
            for user in users:
                try:
                    refresh_token1 = user[1]
                    new_token = await refresh_token(refresh_token1)
                    if (new_token != False):
                        new_refresh = new_token["refresh_token"]
                        new_token = new_token["access_token"]
                        inw += 1
                        print(inw)
                        con, cur = start_db()
                        cur.execute("UPDATE users SET token = ? WHERE token == ?;", (new_refresh, refresh_token1))
                        con.commit()
                        con.close()
                    else:
                        con, cur = start_db()
                        cur.execute("DELETE FROM users WHERE token == ?;", (refresh_token1,))
                        con.commit()
                        con.close()

                except:
                    pass

            con, cur = start_db()
            cur.execute("SELECT * FROM users")
            us_result = cur.fetchall()
            con.close()

            user_list = []

            for i in range(len(us_result)):
                user_list.append(us_result[i][0])

            new_list = []

            for v in user_list:
                if v not in new_list:
                    new_list.append(v)
                else:
                    con, cur = start_db()
                    cur.execute(
                        "DELETE FROM users WHERE id == ? AND ROWID IN (SELECT ROWID FROM users WHERE id == ? LIMIT 1);",
                        (v, v))
                    con.commit()
                    con.close()
                    pass
            embeds = DiscordEmbed(
                title="인원 새로고침완료",
                description=f'''
- 결과\n - 예상 복구 인원 : `{len(new_list)}`  <:GreenCross:1214901325184114720>

''',  # 600 300 400
    color="f276ec")
            embeds.set_timestamp()
            webhook.add_embed(embeds)
            response = webhook.execute(remove_embeds=True)
            await inter.message.edit(embed=embed("second", "인원 새로고침",
                                                 f"인원 새로고침을 하려면 아래 버튼을 눌러주세요.\n\n**> 예상복구인원 `{len(new_list)}` 명 입니다.**\n\n기준 시각: <t:{timestamp}:f>"),
                                     components=[discord.ui.Button(label="인원 새로고침", style=discord.ButtonStyle.secondary,
                                                                   custom_id=f"인원새로고침", disabled=False)])


@client.event
async def on_message(message):
    if message.author.bot:
        return
    owner = get_owner()
    if str(message.author.id) in owner:
        if (message.content.startswith("!인원메시지생성")):
            await message.delete()
            await message.channel.send(embed=embed("second", "인원 새로고침", "인원 새로고침을 하려면 아래 버튼을 눌러주세요."), components=[
                discord.ui.Button(label="인원 새로고침", style=discord.ButtonStyle.secondary, custom_id=f"인원새로고침")])


@client.slash_command(name="자동화", description="복구키 사용 임베드 출력")
@commands.guild_only()
async def restoreeb(
        inter: discord.ApplicationCommandInteraction,
):
    await inter.response.send_message(
        embed=discord.Embed(title="복구키 사용하기",
                            description='복구키를 사용하려면 아래 버튼을 클릭해주세요.',
                            color=0x2f3136),
        components=[
            [
                discord.ui.Button(label=f"복구봇 사용하기", style=discord.ButtonStyle.grey, custom_id=f'start')
            ]])


@client.slash_command(name="복구키사용", description="복구키를 이용해 인원을 복구합니다.")
@commands.guild_only()
async def restore(
        inter: discord.ApplicationCommandInteraction,
        복구키: str
):
    recover_key = 복구키
    con, cur = start_db()
    cur.execute("SELECT * FROM code WHERE code == ?;", (recover_key,))
    token_result = cur.fetchone()
    con.close()
    if (token_result == None):
        await inter.response.send_message(embed=embed("error", "오류", "존재하지 않는 복구 키입니다. 관리자에게 문의해주세요,"), ephemeral=True)
        return
    if not (await inter.guild.fetch_member(client.user.id)).guild_permissions.administrator:
        await inter.response.send_message(embed=embed("error", "오류", "복구를 위해서는 봇이 관리자 권한을 가지고 있어야 합니다."),
                                          ephemeral=True)
        return
    await inter.response.send_message(
        embed=discord.Embed(title="🚀 아래 파란글씨를 눌러 봇을 서버에 추가해주세요.",
                            description=f"**[봇초대링크](https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot)를 눌러 서버에 추가후\n아래 버튼을 눌러서 추가한 서버의 ID를 입력해주세요**",
                            color=0x2f3136),
        components=[
            [
                discord.ui.Button(label=f"✅ 추가 완료", style=discord.ButtonStyle.green, custom_id=f'gogo_{복구키}')
            ]], ephemeral=True)


@client.slash_command(name="복구키생성", description="복구키를 생성합니다.")
@commands.has_permissions(administrator=True)
async def createrestket(
        inter: discord.ApplicationCommandInteraction,
        개수: int,
        인원: int
):
    owner = get_owner()
    if not str(inter.user.id) in owner:
        await inter.response.send_message(embed=embed("error", "오류", "해당 명령어를 사용할 권한이 없습니다."), ephemeral=True)
        return

    amount = 인원
    long = 개수
    if (long >= 1 and long <= 1000):
        con, cur = start_db()
        generated_key = []
        for _ in range(long):
            key = str(random.randint(100000,999999))
            generated_key.append(key)
            cur.execute("INSERT INTO code VALUES(?, ?);", (key, amount))
        con.commit()
        con.close()
        generated_key = "\n".join(generated_key)

        try:
            await inter.response.send_message(generated_key,
                                              embed=embed("success", f"{amount}명 복구키 {long}개 생성 성공", generated_key))
        except:
            file_name = 'lic.txt'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(generated_key)
            with open(file_name, 'rb') as file:
                file_data = discord.File(file, filename='lic.txt')
                await inter.response.send_message(
                    embed=embed("success", f"{amount}명 복구키 {long}개 생성 성공", "생성이 완료되었습니다."), file=file_data)

    else:
        await inter.response.send_message(embed=embed("error", "오류", "최대 1,000개까지 생성 가능합니다."), ephemeral=True)


@client.slash_command(name="생성", description="복구봇 라이센스를 생성합니다.")
@commands.has_permissions(administrator=True)
async def createbotkey(
        inter: discord.ApplicationCommandInteraction,
        일수: int,
        개수: int
):
    owner = get_owner()
    if not str(inter.user.id) in owner:
        await inter.response.send_message(embed=embed("error", "오류", "해당 명령어를 사용할 권한이 없습니다."), ephemeral=True)
        return

    amount = 일수
    long = 개수
    if (long >= 1 and long <= 1000):
        con, cur = start_db()
        generated_key = []
        for _ in range(long):
            key = str(uuid.uuid4())
            generated_key.append(key)
            cur.execute("INSERT INTO licenses VALUES(?, ?);", (key, amount))
        con.commit()
        con.close()
        generated_key = "\n".join(generated_key)

        try:
            await inter.response.send_message(generated_key, embed=embed("success", f"{amount}일 복구봇 라이센스 {long}개 생성 성공",
                                                                         generated_key))
        except:
            file_name = 'lic.txt'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(generated_key)
            with open(file_name, 'rb') as file:
                file_data = discord.File(file, filename='lic.txt')
                await inter.response.send_message(
                    embed=embed("success", f"{amount}일 복구봇 라이센스 {long}개 생성 성공", "생성이 완료되었습니다."), file=file_data)

    else:
        await inter.response.send_message(embed=embed("error", "오류", "최대 1,000개까지 생성 가능합니다."), ephemeral=True)


@client.slash_command(name="역할", description="역할을 설정합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def roleset(
        inter: discord.ApplicationCommandInteraction,
        역할: discord.Role):
    if not (await is_guild_valid(inter.guild.id)):
        await inter.response.send_message(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."), ephemeral=True)
        return
    if (await is_guild_valid(inter.guild.id)):
        role_info = 역할
        if (role_info == None):
            await inter.response.send_message(embed=embed("error", "오류", "존재하지 않는 역할입니다."), ephemeral=True)
            return

        con, cur = start_db()
        cur.execute("UPDATE guilds SET role_id = ? WHERE id == ?;", (role_info.id, inter.guild.id))
        con.commit()
        con.close()
        await inter.response.send_message(embed=embed("success", "역할 설정 성공", "인증을 완료한 유저에게 해당 역할이 지급됩니다."))


@client.slash_command(name="로그웹훅", description="웹훅을 설정합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def webhookset(
        inter: discord.ApplicationCommandInteraction,
        웹훅: str):
    if not (await is_guild_valid(inter.guild.id)):
        await inter.response.send_message(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."), ephemeral=True)
        return
    webhook = 웹훅
    con, cur = start_db()
    cur.execute("UPDATE guilds SET verify_webhook == ? WHERE id = ?;", (str(webhook), inter.guild.id))
    con.commit()
    con.close()
    await inter.response.send_message(embed=embed("success", "인증로그 웹훅저장 성공", f"인증을 완료한후 {webhook} 으로 인증로그가 전송됩니다"))


@client.slash_command(name="인증", description="인증 메시지를 전송합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def verify(
        inter: discord.ApplicationCommandInteraction):
    if not (await is_guild_valid(inter.guild.id)):
        await inter.response.send_message(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."), ephemeral=True)
        return
    rd_url = f'https://discord.com/api/oauth2/authorize?client_id={settings.client_id}&redirect_uri={settings.base_url}%2Fcallback&response_type=code&scope=identify%20guilds.join&state={inter.guild.id}'
    view = discord.ui.View()
    button = discord.ui.Button(style=discord.ButtonStyle.link, label="🌐 인증하러가기",
                               url=rd_url)
    view.add_item(button)
    await inter.response.send_message(embed=embed("success", "인증 메시지 전송", f"인증 메시지가 전송되었습니다."), ephemeral=True)
    await inter.channel.send(embed=discord.Embed(color=0x2f3136, title="Backup service",
                                                 description=f"Please authorize your account [here]({rd_url}) to see other channels.\n다른 채널을 보려면 [여기]({rd_url}) 를 눌러 계정을 인증해주세요."),
                             view=view)


@client.slash_command(name="웹훅보기", description="설정된 웹훅을 확인합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def vwebhook(
        inter: discord.ApplicationCommandInteraction):
    if not (await is_guild_valid(inter.guild.id)):
        await inter.response.send_message(embed=embed("error", "오류", "유효한 라이센스가 존재하지 않습니다."), ephemeral=True)
        return
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (inter.guild.id,))
    guild_info = cur.fetchone()
    con.close()
    if guild_info[4] == "":
        await inter.response.send_message(embed=embed("error", "오류", "웹훅이 없습니다."), ephemeral=True)
        return
    await inter.response.send_message(f"{guild_info[4]}")
@client.slash_command(name='서버정리', description=f'관리자 전용 명령어')
async def 서버정리(ctx):
    owner = get_owner()
    if str(ctx.user.id) in owner:
        await ctx.response.defer()

        nolicense = []

        async for guild in client.fetch_guilds():
            server = guild.id

            if not (await is_guild(server)):
                await guild.leave()
                nolicense.append(f'{guild.name}({guild.id})')
        nolicenseStr = '\n'.join(nolicense)
        await ctx.edit_original_message(f"""```
서버가 정리되었습니다

TOTAL {len(nolicense)}

라이센스 미등록 {len(nolicense)}

라이센스 미등록 서버
{nolicenseStr}
```""")

@client.slash_command(name="정보", description="라이센스 정보를 확인합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def vinfo(
        inter: discord.ApplicationCommandInteraction):
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (inter.guild.id,))
    guild_info = cur.fetchone()
    con.close()
    await inter.response.send_message(
        embed=embed("success", "라이센스 정보", f"{get_expiretime(guild_info[3])} 남음\n{guild_info[3]} 까지 이용이 가능합니다"))


@client.slash_command(name="등록", description="라이센스를 등록합니다.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def webhookset(
        inter: discord.ApplicationCommandInteraction,
        라이센스: str):
    license_number = 라이센스
    con, cur = start_db()
    cur.execute("SELECT * FROM licenses WHERE key == ?;", (license_number,))
    key_info = cur.fetchone()
    if (key_info == None):
        con.close()
        await inter.response.send_message(embed=embed("error", "오류", "존재하지 않거나 이미 사용된 라이센스입니다."), ephemeral=True)
        return
    cur.execute("DELETE FROM licenses WHERE key == ?;", (license_number,))
    con.commit()
    con.close()
    key_length = key_info[1]

    if (await is_guild(inter.guild.id)):
        con, cur = start_db()
        cur.execute("SELECT * FROM guilds WHERE id == ?;", (inter.guild.id,))
        guild_info = cur.fetchone()
        expire_date = guild_info[3]
        if (is_expired(expire_date)):
            new_expiredate = make_expiretime(key_length)
        else:
            new_expiredate = add_time(expire_date, key_length)

        cur.execute("UPDATE guilds SET expiredate = ? WHERE id == ?;", (new_expiredate, inter.guild.id))
        con.commit()
        con.close()
        await inter.response.send_message(embed=embed("success", "성공", f"{key_length} 일 라이센스가 성공적으로 등록되었습니다."))

    else:
        con, cur = start_db()
        new_expiredate = make_expiretime(key_length)
        recover_key = str(uuid.uuid4())[:8].upper()
        cur.execute("INSERT INTO guilds VALUES(?, ?, ?, ?, ?);", (inter.guild.id, 0, recover_key, new_expiredate, "no"))
        con.commit()
        con.close()
        await inter.response.send_message(f"{inter.user.mention} 님 디엠을 확인해주세요")
        await inter.user.send(
            embed=embed("success", "Backup service", f"복구 키 : `{recover_key}`\n해당 키를 꼭 기억하거나 저장해 주세요."))


@client.event
async def on_ready():
    print(
        f"Login: {client.user}\nInvite Link: https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot")
    while True:
        await client.change_presence(activity=discord.Game(name=str(len(client.guilds)) + "개의 서버이용"))
        await asyncio.sleep(5)
        await client.change_presence(
            activity=discord.Activity(name=str(len(client.guilds)) + "개의 서버이용", type=discord.ActivityType.watching))
        await asyncio.sleep(5)


client.run(settings.token)
