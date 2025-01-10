import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox
import requests
import time
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import json
import os
from telethon.tl.types import InputPeerUser
import uuid
import random
import socks
import threading
import pytz
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from opentele.tl import TelegramClient
from opentele.api import API, UseCurrentSession
from telethon import errors
from telethon import events, utils
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl import types, functions
from asgiref.sync import async_to_sync, sync_to_async
from telethon.tl.types import InputPeerChannel, InputPeerUser, InputUser, User
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import  InputChannel
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.messages import AddChatUserRequest


class Telegram_Thread(threading.Thread):
    def __init__(self,region,ipproxy_name):
        super().__init__()
        self.phone_path = "phone"
        self.IP = "49.51.189.167"
        self.port = 18889
        self.ipproxy_name = ipproxy_name
        self.region = region
        try:
            if os.path.exists(self.phone_path):
                print("文件夹存在")
            else:
                os.makedirs(self.phone_path)
                print(f"phone '{self.phone_path}' created successfully.")
        except FileExistsError:
            print(f"phone '{self.phone_path}' already exists.")

    def get_proxy(self,region, ipproxy_name):
        region = region.upper()

        # 添加延迟
        time.sleep(random.randint(0, 10000) / 10000)
        proxy = ()
        fail_count = 0
        while 1:
            try:
                timestamp_hex = hex(int(time.time() * 1000))[2:]
                # 生成带时间戳的UUID
                uuid_with_timestamp = uuid.uuid1()
                # 拼接时间戳和UUID，并截取其中的16位作为UDID
                udid = (timestamp_hex + str(uuid_with_timestamp).replace('-', ''))[5:16]
                ran_str = "1234567890qwertyuiopasdfghjklmnbvcxzZXCVBNMLKJHGFDSAQWERTYUIOP"
                random_str = ''
                for ii in range(0, random.randint(4, 5)):
                    random_str = f"{random_str}{ran_str[random.randint(0, len(ran_str) - 1)]}"

                ipproxy_name_list = ipproxy_name.split("|")
                if "国家大写" in ipproxy_name_list[0]:
                    ipproxy_name_list[0] = ipproxy_name_list[0].replace("国家大写", region.upper())
                elif "国家小写" in ipproxy_name_list[0]:
                    ipproxy_name_list[0] = ipproxy_name_list[0].replace("国家小写", region.lower())

                if "随机字符串" in ipproxy_name_list[0]:
                    ipproxy_name_list[0] = ipproxy_name_list[0].replace("随机字符串", f"{udid}{random_str}")

                if "随机数字" in ipproxy_name_list[0]:
                    ipproxy_name_list[0] = ipproxy_name_list[0].replace("随机数字", str(random.randint(1, 99999999)))

                proxy = (
                    socks.SOCKS5,
                    ipproxy_name_list[2],  # proxy host
                    int(ipproxy_name_list[3]),  # proxy port
                    True,  # flag indicating if the proxy requires authentication
                    ipproxy_name_list[0],  # proxy username
                    ipproxy_name_list[1]  # proxy password
                )
                print(proxy)
                rep = requests.get("https://ipinfo.io/json", proxies={
                    'http': f'socks5://{ipproxy_name_list[0]}:{ipproxy_name_list[1]}@{ipproxy_name_list[2]}:{ipproxy_name_list[3]}',
                    'https': f'socks5://{ipproxy_name_list[0]}:{ipproxy_name_list[1]}@{ipproxy_name_list[2]}:{ipproxy_name_list[3]}'
                }, timeout=10)
                if rep.status_code == 200 and rep.json().get("ip"):
                    ip_real = rep.json().get("ip")
                    country = rep.json().get("country")
                    print(f'选择的IP地址地区：{region}, 实际IP所在地区：{country}')
                    if country.lower() == region.lower():
                        print(f'使用代理IP: {ip_real}')
                        break

                else:
                    fail_count += 1

                time.sleep(1)
            except Exception as e:
                print(f"获取代理异常{e}")
                fail_count += 1
                time.sleep(5)
            finally:
                if fail_count > 3:
                    break
        return proxy
    #获取手机号的session文件
    def add_phone(self,phone):
        url = f'http://{self.IP}:{self.port}/creat_phone'
        data = {
            'phone': phone,
            'region': self.region,
            'password': 'dem99998',
            'ipproxy_name': self.ipproxy_name
        }
        res = requests.post(url, json=data)
        print(res.text)
        sleep(0.1)
    #给TG账号发送验证码
    def set_phone_code(self,phone, code):
        url = f'http://{self.IP}:{self.port}/set_phone_code'

        data = {
            'phone': phone,
            'code': code
        }
        res = requests.post(url, json=data)
        print(res.json())
        sleep(0.1)

    # 停止给TG账号发送验证码
    def del_phone(self,phone):
        url = f'http://{self.IP}:{self.port}/del_phone'

        data = {
            'phone': phone,
            'region': 'gb',
            'password': 'dem99998',
            'ipproxy_name': '5Hj9Ks2Cv9He-res-US-sid-20383242|3Gy5Ne4Ba1Ru4Jx6Fj|z1.ipmart.io|9595'
        }
        res = requests.post(url, json=data)
        print(res.json())
        sleep(0.1)
    #获取TG当前的状态
    def get_tg_status(self,):
        res = requests.get(f'http://{self.IP}:{self.port}/get_phone_status')
        res_json = json.loads(res.text)
        return res_json
    #下载TG session压缩文件
    def get_tg_file(self,phone):
        res = requests.get(f'http://{self.IP}:{self.port}/get_phone_file', params={"phone": phone})
        file_path  = os.path.join(self.phone_path, f'{phone}.zip')
        with open(file_path, 'wb') as f:
                 f.write(res.content)

    # 下载TG session文件
    def get_tg_session(self,phone):
        res = requests.get(f'http://{self.IP}:{self.port}/get_phone_session_file', params={"phone": phone})
        file_path  = os.path.join(self.phone_path,f'{phone}.session')
        with open(file_path, 'wb') as f:
                 f.write(res.content)

    async def tg_login(self,phone,platform):
        client = None
        session_path =  os.path.join(self.phone_path,f'{phone}.session')
        if platform == 0:  # PC
            # api = API.TelegramDesktop.Generate(unique_id=account.phone)
            client = TelegramClient(session_path, proxy=self.get_proxy(self.region,self.ipproxy_name))
        if platform == 1:  # iOS
            api = API.TelegramIOS.Generate(unique_id=phone)
            session_path = session_path.replace('.session', '-ios.session')
            client = TelegramClient(session_path, api=api, proxy=self.get_proxy(self.region,self.ipproxy_name))
        elif platform == 2:  # Android
            api = API.TelegramAndroid.Generate(unique_id=phone)
            session_path = session_path.replace('.session', '-android.session')
            print(phone)
            print(session_path)
            client = TelegramClient(session_path, api=api, proxy=self.get_proxy(self.region,self.ipproxy_name))
        # elif platform == 3:  # AndroidX
        #     api = API.TelegramAndroidX.Generate(unique_id=account.phone)
        #     session_path = session_path.replace('.session', '-androidx.session')
        #     client = TelegramClient(session_path, api=api, proxy=self.get_proxy(self.region,self.ipproxy_name))
        if client:
            try:
                await client.connect()
                print("授权状态：",await client.is_user_authorized())
                if  await client.is_user_authorized(): #已授权
                    print(f'{phone} 登录成功')
                else:
                    return None
            except (errors.AuthKeyUnregisteredError, errors.UserDeactivatedError, errors.UserDeactivatedBanError) as e:
                print(f'账号：{phone} 连接失败: {e}')
                return None
            except Exception as e:
                print(f'账号：{phone} 连接失败: {e}')
                return None

        return  client


    #用户登入(线程池)
    async def batch_login(self, phone_list, platform=0):
        task = []
        # 获取 CPU 核数
        cpu_count = os.cpu_count()
        # 根据 CPU 核数设置线程池大小
        max_workers = cpu_count * 2  # 这里可以根据需求调整乘数
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(len(phone_list)):
                temp_obj = await  self.tg_login(phone_list[i],platform)
                task.append(executor.submit(temp_obj))
            # 输出每个线程运行的结果
            for i in task:
                print('result = {}'.format(i.result))


    async def client_join_group(self,client, group_name,user_list):
        try:
            if "https://t.me/" in group_name:
                # 从邀请链接中提取Hash部分
                invite_hash = group_name.split('/')[-1].split('+')[-1]
                print(invite_hash)
                # 解析邀请链接并获取群组信息
                chat_invite = await client(CheckChatInviteRequest(invite_hash))
                #私密群组的ID
                if chat_invite.chat:
                    group_id = chat_invite.chat.id
                    print(f'Group ID: {group_id}')
                else:
                    print('Invalid or expired invite link')
                for  user in  user_list:
                    print(user)

                    # 添加陌生号为联系人
                    # contacts = [
                    #     InputPhoneContact(client_id=0, phone='+' + str(user), first_name=str(user), last_name=str(user) + '_fans'),
                    # ]
                    # 添加联系人
                    # result = await client(ImportContactsRequest(contacts))
                    # 获取群组实体
                    chat  = await client.get_entity(group_id)
                    # 获取联系人实体
                    contact = await client.get_entity(user)
                    try:
                        # 邀请联系人加入群组
                        invited_users = await client(
                            AddChatUserRequest(chat_id=chat.id, user_id=contact.id, fwd_limit=0))
                    except Exception as e:
                        print(e)
                        continue
                #显式断开连接
                client.disconnect()
                return True
            else:
                # 解析群组用户名
                result = await client(ResolveUsernameRequest(group_name))
                # 使用群组的 ID 加入群组
                await client(JoinChannelRequest(result.chats[0].id))
                print("成功加入群组")
                return True
        except Exception as e:
            print(f'client_join_group failed：{e}')
            return False

    # 用户入群(线程池)
    async def batch_join_group(self,  phone_list, group_name ,user_list,platform=0):
        for i in phone_list:
            phone_obj = await self.tg_login(i, platform)
            await self.client_join_group(phone_obj, group_name,user_list)

        # task = []
        # # 获取 CPU 核数
        # cpu_count = os.cpu_count()
        # # 根据 CPU 核数设置线程池大小
        # max_workers = cpu_count * 2  # 这里可以根据需求调整乘数
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     for i in phone_list:
        #         phone_obj = self.tg_login(i, platform)
        #         print("加群")
        #         task.append(executor.submit(self.client_join_group, phone_obj, group_name))
        #     # 输出每个线程运行的结果
        #     for i in task:
        #         print('result = {}'.format(i.result))
    async def clent_send_mes(self,  phone,other,message,platform=0,):
            phone_obj = await self.tg_login(phone, platform)
            await phone_obj.send_message(other, message) #发信息
            await phone_obj.disconnect() #退出
    #发送信息
    async def batch_send_mes(self,phone_list,other,message,platform=0,):
        task = []
        # 获取 CPU 核数
        cpu_count = os.cpu_count()
        # 根据 CPU 核数设置线程池大小
        max_workers = cpu_count * 2  # 这里可以根据需求调整乘数
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in phone_list:
                temp_mes = await self.clent_send_mes(i,other,message,platform)
                task.append(executor.submit(temp_mes))
            # 输出每个线程运行的结果
            for i in task:
                print('result = {}'.format(i.result))
    #判断user是否存在
    async def validate_user(self,client, user):
        try:
            user_entity = await client.get_entity(user)
            if not isinstance(user_entity, User):
                print(f'{user} is not a user')
                return None
            return user_entity
        except Exception as e:
            print(f'get_entity failed：{e}')
            return None

    def is_valid_phone_number(self,phone_number):
        # 定义一个匹配手机号的正则表达式
        phone_pattern = re.compile(r'^\+?\d{10,15}$')

        # 使用正则表达式进行匹配
        return phone_pattern.match(phone_number) is not None

    async def invite_users_to_channel(self,client, group_name, batch_users, me,map):
        count = 0
        is_continue = True
        invite_result = {}
        for usr in batch_users:
            if isinstance(usr, types.User):
                invite_result[usr.id] = {"account": me.phone, "invite_ok": False, 'missing': False, 'phone': usr.phone, 'username': usr.username, 'name': utils.get_display_name(usr)}
        try:
            if all(isinstance(user, types.User) for user in batch_users):
                batch_users = [types.InputUser(user_id=u.id, access_hash=u.access_hash) for u in batch_users]
            invited_users = await client(functions.channels.InviteToChannelRequest(channel=group_name,users=batch_users)) #批量拉用户入群

            # 获取所有的用户信息
            user_dict = {user.id: user for user in invited_users.updates.users}

            # 遍历 updates 列表，查找 UpdateNewChannelMessage
            for update in invited_users.updates.updates:
                if isinstance(update, types.UpdateNewChannelMessage):
                    if isinstance(update.message.action, types.MessageActionChatAddUser):
                        # 遍历被邀请的用户 ID
                        for user_id in update.message.action.users:
                            update_user = user_dict.get(user_id)
                            if update_user:
                                username = update_user.username or ''
                                phone = update_user.phone or ''
                                print(f'账号：{utils.get_display_name(me)}, 邀请用户: {utils.get_display_name(update_user)} ({username} {phone}) 成功')
                                count += 1
                                invite_result[user_id].update({"invite_ok": True})

            if len(invited_users.missing_invitees) > 0:
                missing_invitees_user_ids = [invitee.user_id for invitee in invited_users.missing_invitees]
                for missing_invitees_user_id in missing_invitees_user_ids:
                    user_info = map[missing_invitees_user_id]
                    if user_info:
                        try:
                            identifier = user_info.get('username') or user_info.get('phone') or user_info.get('user_id')
                            print(f'用户: {identifier}, 有设权限不让拉入群')
                            invite_result[missing_invitees_user_id].update({'missing': True})
                        except:
                            traceback.print_exc()
                            pass

        # except errors.UserAlreadyParticipantError:
        #     print(f"{user.username} 已经是群组 {group_name} 的成员")
        # except errors.UserAlreadyInvitedError:
        #     print(f"{user.username} 已经被你邀请进群组 {group_name}")
        # except errors.UserPrivacyRestrictedError:
        #     print(f"由于隐私设置，无法邀请 {user.username}")
        # except errors.UserNotMutualContactError:
        #     print(f"{user.username} 不是双向联系人，无法邀请")
        except errors.PeerFloodError:
            error = "发送过多请求，需要等待"
            print(f'账号：{utils.get_display_name(me)}, {error}')
            account = await sync_to_async(Account.objects.get)(phone=me.phone)
            account.last_error = error
            account.last_error_time = timezone.now()
            await sync_to_async(account.save)()
            is_continue = False
        except errors.FloodWaitError as e:
            error = f"请求频率过高，请等待 {e.seconds} 秒"
            print(f'账号：{utils.get_display_name(me)}, {error}')
            account = await sync_to_async(Account.objects.get)(phone=me.phone)
            account.last_error = error
            account.last_error_time = timezone.now()
            await sync_to_async(account.save)()
            is_continue = False
        # except errors.ChatAdminRequiredError:
        #     print(f"邀请 {user.username} 需要管理员权限")
        except errors.ChannelPrivateError:
            print(f"群组 {group_name} 是私有的，无法邀请")
            is_continue = False
        except errors.UserBannedInChannelError:
            print(f'账号：{utils.get_display_name(me)}, 已被封禁')
            account = await sync_to_async(Account.objects.get)(phone=me.phone)
            account.status = 3  # 封禁
            await sync_to_async(account.save)()
            is_continue = False
        except errors.ChatWriteForbiddenError:
            print(f'群组：{group_name} 权限设置无法拉人')
            is_continue = False
        except errors.RpcCallFailError as e:
            print(f"发生 RPC 错误: {e}")
        except Exception as e:
            traceback.print_exc()
            print(f'账号：{utils.get_display_name(me)}, 尝试邀请用户时发生未知错误：{e}')

        return count, is_continue, invite_result

    #校验群组名信息
    async def get_channel_entity(self,client, group_name):
        entity = None
        is_channel = None
        participants_count = 0
        if client:
            try:
                if await client.is_user_authorized():
                    try:
                        result = await client.get_entity(group_name)
                        if isinstance(result, types.Channel):
                            entity = result
                            is_channel = True

                            full_channel = await client(functions.channels.GetFullChannelRequest(
                                types.InputChannel(channel_id=entity.id, access_hash=entity.access_hash)))
                            channel_info = full_channel.full_chat

                            participants_count = channel_info.participants_count
                        else:
                            print(f'{group_name} is not a group')
                            is_channel = False

                    except Exception as e:
                        traceback.print_exc()
                        print(f'get_input_entity failed: {e}')
                else:
                    account.status = 3  # 封禁
                    await sync_to_async(account.save)()

            except errors.FloodWaitError:
                account.status = 3  # 封禁
                await sync_to_async(account.save)()
            except Exception as e:
                account.status = 4  # 未知
                await sync_to_async(account.save)()
            finally:
                await client.disconnect()

        return is_channel, entity, participants_count

    def do_invite_to_group(self,phone_obj, group_name, users, interval, invite_by,active_only):
        if invite_by == 0:
            invite_ok_count, invite_tried, invite_res = async_to_sync(self.invite_group)(phone_obj, group_name, users,
                                                                                         interval, active_only)
        elif invite_by == 1:
            invite_ok_count, invite_tried, invite_res = async_to_sync(self.invite_group_by_phone)(phone_obj, group_name,
                                                                                                  users, interval,
                                                                                                  active_only)
        elif invite_by == 2:
            invite_ok_count, invite_tried, invite_res = async_to_sync(self.invite_group_by_id)(phone_obj, group_name,
                                                                                               users, interval,
                                                                                               active_only)

        return invite_ok_count, invite_tried, invite_res
    #拉人入群
    async def batch_invite_group(self,  phone_list, group_name,users,invite_by=0, max_invitees_per_account=50, interval=30,active_only=True):
        group_name = group_name.strip()
        if not group_name:
            print("群名是空")
            return
        if phone_list:
            phone_obj = await self.tg_login(phone_list[0], 0)
            is_channel, channel_entity, participants_count_before = await self.get_channel_entity(phone_obj,group_name)
            if is_channel is False:
                    print(f'{group_name} 不是一个群组')
                    return
            elif is_channel is True:  # 判断群名是否正常
                    pass
            print(f'本任务需要拉入的群名为：{group_name}, 拉人前群组成员数：{participants_count_before}')
        else:
            print("没有操作用户")
            return

        # 平均分配 invitees
        chunk_size = (len(users) + len(phone_list) - 1) // len(phone_list)
        print(chunk_size)
        if chunk_size > max_invitees_per_account:
            chunk_size = max_invitees_per_account
        invitees_chunks = [users[i:i + chunk_size] for i in range(0, len(users), chunk_size)]
        print(invitees_chunks)

        invite_ok_total = 0
        tried_total = 0
        results_collection = []
        # 获取 CPU 核数
        cpu_count = os.cpu_count()
        # 根据 CPU 核数设置线程池大小
        max_workers = cpu_count * 2  # 这里可以根据需求调整乘数
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for account_id, users_list in zip(phone_list, invitees_chunks):
                print(account_id, users_list)
                phone_obj = await self.tg_login(account_id, 0)
                if phone_obj is None:
                    print(f"{account_id}用户登入失败")
                    continue
                futures[executor.submit(self.do_invite_to_group, phone_obj, group_name, users_list, interval,invite_by,active_only)] = account_id
            # for i in phone_list:
            #     phone_obj = await self.tg_login(i, 0)
            #     futures[executor.submit(self.do_invite_to_group, phone_obj, group_name, users, interval,active_only)]
            for future in as_completed(futures):
                account_id = futures[future]
                try:
                    print("55555555555555555555")
                    phone, result, tried  = future.result()
                    print(phone, result, tried)
                    print("5555555555555511111111")
                    # phone, result, tried, invite_result = future.result()
                    # print("3333333333333333")
                    # count = result
                    # print(f'账号: {phone} 共成功拉入人数: {count}')
                    # invite_ok_total += count
                    # tried_total += tried
                    # results_collection.append((phone, count, tried, invite_result))
                except Exception as exc:
                    print(f'Account {account_id} generated an exception: {exc}')

            print('------------------任务完成--------------------')
            table_data = []
            for phone, ok_count, tried, invite_result in results_collection:
                print(f'账号: {phone}, 成功拉人数: {ok_count}, 共尝试拉人次数: {tried}')
                if invite_result:
                    for key, res in invite_result.items():
                        table_data.append([phone, res.get('phone', ''), res.get('username', ''), res.get('name', ''), \
                                           f'https://t.me/{group_name}', channel_entity.title, \
                                           '是' if res.get('invite_ok', False) else '否',
                                           '是' if res.get('missing', False) else '否', \
                                           datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

            participants_count_after = participants_count_before
            # print(f'本次任务总共成功拉人数：{invite_ok_total}，共尝试拉人次数：{tried_total}，每次尝试拉3个人')
            print(
                f'群组：{group_name}, 拉人前成员数：{participants_count_before}， 拉人后成员数：{participants_count_after}')
            print(
                f'本次任务总共成功拉人数：{participants_count_after - participants_count_before}，共尝试拉人次数：{tried_total}，每次尝试拉3个人')

            if table_data:
                summary_data = [
                    [f'https://t.me/{group_name}', channel_entity.title, invite_ok_total]
                ]
                file_path = create_excel_file_invite(table_data, summary_data, channel_entity.title, group_name)
                task.temp_file_path = file_path
                print('请前往【任务记录】下载拉人结果明细')


    async def invite_group_by_id(self,client: 'TelegramClient', group_name, users, interval,active_only):
        invite_ok_count = 0
        invite_tried = 0
        try:
            me = await client.get_me()
            # print(f'本账号信息：\n{me.stringify()}')
            # if user is not a participant in this group, join first
            try:
                await client.get_permissions(group_name, me)
            except errors.UserNotParticipantError:
                # need to join this group first
                print(f'账号：{utils.get_display_name(me)} 不是群: {group_name} 的成员，开始加入...')
                try:
                    # 解析群组用户名
                    result = await client(ResolveUsernameRequest(group_name))
                    # 使用群组的 ID 加入群组
                    await client(JoinChannelRequest(result.chats[0].id))
                    print("成功加入群组")
                except Exception as e:
                    print(f'账号：{utils.get_display_name(me)} 加入群: {group_name} 失败，原因：{e}')
                    return False, invite_tried
                print(f'账号：{utils.get_display_name(me)} 成功加入群: {group_name}')

            print(
                f'账号：{utils.get_display_name(me)}, 开始尝试邀请用户数: {len(users)}')

            batch_users = []
            batch_users_map = {}

            for user in users:
                user = user.strip()
                try:
                    numbers = user.split(',')
                    user_id = int(numbers[0])
                    user_access_hash = int(numbers[1])
                    peer_user = InputPeerUser(user_id, user_access_hash)
                except:
                    continue

                batch_users.append(peer_user)
                batch_users_map[peer_user.user_id] = {'username': None, 'phone': None, 'user_id': peer_user.user_id,
                                                      'access_hash': peer_user.access_hash}

                if len(batch_users) == 3:
                    invite_tried += 1
                    result, is_continue, invite_result = await self.invite_users_to_channel(client, group_name, batch_users,me, batch_users_map)
                    batch_users = []
                    batch_users_map = {}
                    invite_ok_count += result
                    if is_continue is False:
                        break

                    await asyncio.sleep(interval)

            # Invite remaining users in batch_users if any
            if batch_users:
                invite_tried += 1
                result, is_continue, invite_result = await self.invite_users_to_channel(client, group_name, batch_users, me, batch_users_map)
                invite_ok_count += result

            print(f'账号：{utils.get_display_name(me)}, 成功邀请用户数: {invite_ok_count}, 共尝试邀请次数：{invite_tried}')

        except Exception as e:
            print(f'op_invite_group failed：{e}')

        return invite_ok_count, invite_tried, None

    async def invite_group_by_phone(self,client: 'TelegramClient', group_name, users, interval, active_only):
        invite_ok_count = 0
        invite_tried = 0
        invite_res = {}
        try:
            me = await client.get_me()
            # print(f'本账号信息：\n{me.stringify()}')
            # if user is not a participant in this group, join first
            try:
                await client.get_permissions(group_name, me)
            except errors.UserNotParticipantError:
                # need to join this group first
                print(f'账号：{utils.get_display_name(me)} 不是群: {group_name} 的成员，开始加入...')
                try:
                    # 解析群组用户名
                    result = await client(ResolveUsernameRequest(group_name))
                    # 使用群组的 ID 加入群组
                    await client(JoinChannelRequest(result.chats[0].id))
                    print("成功加入群组")
                except Exception as e:
                    print(f'账号：{utils.get_display_name(me)} 加入群: {group_name} 失败，原因：{e}')
                    return False, invite_tried
                print(f'账号：{utils.get_display_name(me)} 成功加入群: {group_name}')

            print(
                f'账号：{utils.get_display_name(me)}, 开始尝试邀请用户数: {len(users)}')

            batch_users = []
            batch_users_map = {}

            import_contact_failed = 0
            for user in users:
                # 判断是否为手机号
                if not self.is_valid_phone_number(user):
                    print(f'{user} 不是手机号格式')
                    continue
                # 先导入该用户
                contact = types.InputPhoneContact(client_id=0, phone=user, first_name=user, last_name='')
                try:
                    print(f'开始导入手机号: {user} 为联系人')
                    result = await client(functions.contacts.ImportContactsRequest([contact]))
                    if not result.users:
                        print(f'导入手机号: {user} 为联系人失败！！')
                        import_contact_failed += 1
                        if import_contact_failed > 9:
                            break
                        await asyncio.sleep(2)
                        continue

                    print(f'导入手机号: {user} 为联系人成功')
                    import_contact_failed = 0
                    await asyncio.sleep(2)

                    added_user = result.users[0]
                    days_ago = datetime.now(pytz.utc) - timedelta(days=7)
                    # Only invite active user
                    if active_only and isinstance(added_user.status,types.UserStatusOffline) and added_user.status.was_online < days_ago:
                        continue

                    # batch_users.append(result.imported[0].user_id)
                    # user_entity = InputPeerUser(added_user.id, added_user.access_hash)
                    batch_users.append(added_user)
                    batch_users_map[added_user.id] = {'username': added_user.username, 'phone': user,
                                                      'user_id': added_user.id,
                                                      'access_hash': added_user.access_hash}

                    if len(batch_users) == 3:
                        invite_tried += 1
                        result, is_continue, invite_result = await self.invite_users_to_channel(client,
                                                                                           group_name,
                                                                                           batch_users,
                                                                                           me,
                                                                                           batch_users_map)
                        batch_users = []
                        batch_users_map = {}
                        invite_ok_count += result
                        invite_res.update(invite_result)
                        if is_continue is False:
                            break

                        await asyncio.sleep(interval)

                except errors.PeerFloodError:
                    error = "发送过多请求，需要等待"
                    print(f'账号：{utils.get_display_name(me)}, {error}')
                    account = await sync_to_async(Account.objects.get)(phone=me.phone)
                    account.last_error = error
                    account.last_error_time = timezone.now()
                    await sync_to_async(account.save)()
                    break
                except errors.FloodWaitError as e:
                    error = f"请求频率过高，请等待 {e.seconds} 秒"
                    print(f'账号：{utils.get_display_name(me)}, {error}')
                    account = await sync_to_async(Account.objects.get)(phone=me.phone)
                    account.last_error = error
                    account.last_error_time = timezone.now()
                    await sync_to_async(account.save)()
                    break
                except errors.UserBannedInChannelError:
                    print(f'账号：{utils.get_display_name(me)}, 已被封禁')
                    account = await sync_to_async(Account.objects.get)(phone=me.phone)
                    account.status = 3  # 封禁
                    await sync_to_async(account.save)()
                    break
                except Exception as e:
                    traceback.print_exc()
                    print(f"Failed to add contacts: {e}")
                    break

                await asyncio.sleep(1)

            # Invite remaining users in batch_users if any
            if batch_users:
                invite_tried += 1
                result, is_continue, invite_result = await self.invite_users_to_channel(client, group_name, batch_users, me,
                                                                                   batch_users_map)
                invite_ok_count += result
                invite_res.update(invite_result)

            print(
                f'账号：{utils.get_display_name(me)}, 成功邀请用户数: {invite_ok_count}, 共尝试邀请次数：{invite_tried}')

        except Exception as e:
            print(f'invite_group_phone failed：{e}')

        return invite_ok_count, invite_tried, invite_res

    async def invite_group(self,client, group_name,users,interval,active_only):
        invite_ok_count = 0
        invite_tried = 0
        invite_res = {}
        try:
            me = await client.get_me()
            # print(f'本账号信息：\n{me.stringify()}')
            try:
                await client.get_permissions(group_name, me)
            except errors.UserNotParticipantError:
                # need to join this group first
                print(f'账号：{utils.get_display_name(me)} 不是群: {group_name} 的成员，开始加入...')
                try:
                    print("1111111111111111")
                    # 解析群组用户名
                    result = await client(ResolveUsernameRequest(group_name))
                    # 使用群组的 ID 加入群组
                    await client(JoinChannelRequest(result.chats[0].id))
                    print("成功加入群组")
                except Exception as e:
                    print(f'账号：{utils.get_display_name(me)} 加入群: {group_name} 失败，原因：{e}')
                    return False
                print(f'账号：{utils.get_display_name(me)} 成功加入群: {group_name}')

            print(f'账号：{utils.get_display_name(me)}, 开始尝试邀请用户数: {len(users)}')


            batch_users = []
            batch_users_map = {}

            for user in users:
                # 判断用户是否是真实用户
                user_entity = await self.validate_user(client, user)
                if not user_entity:
                    await asyncio.sleep(2)
                    continue

                days_ago = datetime.now(pytz.utc) - timedelta(days=7)
                # Only invite active user
                if active_only and isinstance(user_entity.status,types.UserStatusOffline) and user_entity.status.was_online < days_ago:
                    continue

                await asyncio.sleep(3)


                batch_users.append(user_entity)
                batch_users_map[user_entity.id] = {'username': user, 'phone': user_entity.phone,'user_id': user_entity.id, 'access_hash': user_entity.access_hash}

                if len(batch_users) == 3:
                    invite_tried += 1
                    result, is_continue, invite_result = await self.invite_users_to_channel(client, group_name, batch_users,me, batch_users_map)
                    batch_users = []
                    batch_users_map = {}
                    invite_ok_count += result
                    invite_res.update(invite_result)

                    if is_continue is False:
                        break

                    await asyncio.sleep(interval) #间隔时间

            # Invite remaining users in batch_users if any
            if batch_users:
                invite_tried += 1
                result, is_continue, invite_result = await self.invite_users_to_channel(client, group_name, batch_users, me,batch_users_map)
                invite_ok_count += result
                invite_res.update(invite_result)

            print(f'账号：{utils.get_display_name(me)}, 成功邀请用户数: {invite_ok_count}, 共尝试邀请次数：{invite_tried}')

        except Exception as e:
            print(f'invite_group failed：{e}')

        return invite_ok_count, invite_tried, invite_res

    #获取用户信息
    async def get_user_entity(self, phone_list, user, platform=0):
            from telethon.errors import  UsernameNotOccupiedError, UserNotMutualContactError
            from telethon.tl.functions.contacts import ResolveUsernameRequest
            from telethon.tl.functions.contacts import SearchRequest
            for i in phone_list:
                # client = await self.tg_login(i, platform)
                # result = await client(SearchRequest(
                #     q=user,
                #     limit=20  # 设置要返回结果的最大数量
                # ))
                client = await self.tg_login(i, platform)
                result = await client(ResolveUsernameRequest("sdsadad13"))
                print(f"用户信息: {result}")
            message = await event.get_message()
            print(message.text)

    async def get_group_members(self,phone_list, group_name):
        from telethon import TelegramClient
        from telethon.tl.functions.messages import GetFullChatRequest
        from telethon.tl.functions.channels import GetParticipantsRequest
        from telethon.tl.types import ChannelParticipantsSearch
        usernames = []
        offset = 0
        limit = 100  # 每次请求的成员数量
        client = await self.tg_login(phone_list[0], 0)
        try:
            # 从邀请链接中提取Hash部分
            invite_hash = group_name.split('/')[-1].split('+')[-1]
            print(invite_hash)
            # 解析邀请链接并获取群组信息
            chat_invite = await client(CheckChatInviteRequest(invite_hash))
            # 私密群组的ID
            if chat_invite.chat:
                group_id = chat_invite.chat.id
                print(f'Group ID: {group_id}')
            else:
                print('Invalid or expired invite link')

            # 获取群组实体
            entity = await client.get_entity(group_id)
            participants = await client.get_participants(entity)
            for part in participants:
                print(part)
                # 要写入的内容
                text_to_write = "{}|{}".format(part.username,part.phone)

                # 打开文件进行写入，如果文件不存在将会被创建
                with open('ceshi_users.txt', "a") as file:
                    file.write(text_to_write+ '\n') # 将文本写入文


        except Exception as e:
            print(f"An error occurred: {e}")
            return []

if __name__ == '__main__':
    import asyncio

    users = []
    with open("ceshi.txt",'r') as f:
        temp_user = f.readlines()
        f.close()
    for i in temp_user:
        users.append(i.replace('\n', ''))
    print(users)
    phone_list = ["14642454611"]
    region = 'us'
    ipproxy_name = '5Hj9Ks2Cv9He-res-US-sid-2545452|Xv2u76ZeYPia86V123a|z1.ipmart.io|9595'
    tg_obj = Telegram_Thread(region,ipproxy_name)
    # tg_obj.add_phone('14642454611') #新增session
    # tg_obj.add_phone('13346415788') #新增session
    # tg_obj.add_phone('14646668656') #新增session
    # tg_obj.add_phone('14642461434') #新增session
    # tg_obj.add_phone('19599017019') #新增session
    # tg_obj.add_phone('14642509611') #新增session
    # tg_obj.add_phone('15859903822') #新增session
    # tg_obj.add_phone('13348102882') #新增session
    # tg_obj.add_phone('18049077472') #新增session
    # tg_obj.set_phone_code('14642454611',"47268") #发送验证码
    # re_json = tg_obj.get_tg_status() #获取状态
    # print(re_json)
    # tg_obj.get_tg_file('12709473859') #获取Tdata,session文件的压缩包
    # tg_obj.get_tg_session('14642454611')  # 获取session文件
    # asyncio.run(tg_obj.batch_login(phone_list,0)) #登入账号
    # asyncio.run(tg_obj.batch_join_group(phone_list,"ceshihu66",0,users))  # 自动加入群组
    # asyncio.run(tg_obj.batch_join_group(phone_list, "https://t.me/+Cym6uSUA9dE4NGVl",users, 0))  # 自动加入群组

    # asyncio.run(tg_obj.batch_invite_group(phone_list, "@ceshihu",users,invite_by=0, max_invitees_per_account=50, interval=30,active_only=True))  # 拉人入群
    # asyncio.run(tg_obj.get_group_members(phone_list, "https://t.me/+Cym6uSUA9dE4NGVl"))  # 拉人入群
    # 运行异步函数
    asyncio.run(tg_obj.clent_send_mes(phone_list[0],'@leiya11',"wew sdsada333", 0)) #手机账户发信息给网友
    # asyncio.run(tg_obj.batch_send_mes(phone_list, '@tianleiya11', 'Hello to myself!', 0))  # 手机账户发信息给多个网友
    # asyncio.run(tg_obj.get_user_entity(["12709473859"],"14646668587",0))