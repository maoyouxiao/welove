#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import hmac
import base64
import requests
from urllib import parse
from hashlib import sha1
from config import config

app_key = "ac5f34563a4344c4"
baseURL = "http://api.welove520.com"
hmacKey = b"8b5b6eca8a9d1d1f"
headers = {
        "Welove-UA": "[Device:RedmiNote3][OSV:6.0.1][CV:Android3.3.7][WWAN:0][zh_CN][platform:xiaomi][WSP:2]",
        "Accept-Language": "zh_CN",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi Note 3 MIUI/7.9.7)",
}

def buildSig(url, contents, method="POST"):
    data = ""
    keys = sorted(contents.keys())
    for key in keys:
        data += "%s=%s&" % (key, parse.quote_plus(str(contents[key])))
    msg = "%s&%s&%s" % (method.upper(), parse.quote_plus(url), parse.quote_plus(data[:-1]))
    sig = hmac.new(hmacKey, msg.encode("utf-8"), sha1).digest()
    sig = base64.b64encode(sig).decode("utf-8")
    return sig

class Home(object):

    def __init__(self, token):
        self.token = token
        self.space = self.get_space_id()
        self.name = {1:'回家', 4:'吃饭', 5:'睡觉', 6:'洗澡', 7:'休息', 8:'拜访', 11:'互动', 12:'互动', 13:'互动'} 

    def get_space_id(self):
        url = baseURL + "/v5/useremotion/getone"
        data = {}
        data["access_token"] = self.token
        data["app_key"] = app_key
        data["user_id"] = 0
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        return results['love_space_id']

    def get_tasks(self):
        url = baseURL + "/v1/game/house/task/list"
        data = {}
        data["access_token"] = self.token
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        task_list = []
        try:
            tasks = results['messages'][0]['tasks']
            for task in tasks:
                if task['remain_time'] == 0:
                    if task['task_type'] == 8 and task['count'] == 10:
                        continue
                    if task['task_type'] == 14:
                        continue
                    task_list.append(task['task_type'])
            return task_list
        except KeyError:
            return None

    def get_house(self):
        url = baseURL + "/v1/game/house/info"
        data = {}
        data["access_token"] = self.token
        data["love_space_id"] = "random"
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers) 
        results = response.json()
        try:
            return results["messages"][0]["house"]["love_space_id"]
        except KeyError:
            return None

    def visit(self):
        url = baseURL + "/v1/game/house/task"
        data = {}
        data["access_token"] = self.token
        data["task_type"] = 8
        data["house_num"] = 0
        count = 0
        print("正在完成拜访任务...")
        for x in range(20):
            data["love_space_id"] = self.get_house()
            if data["love_space_id"]:
                data["sig"] = buildSig(url, data)
                requests.post(url, data, headers=headers)
                data.pop("love_space_id")
                data.pop("sig")
                count += 1
                if count == 10:
                    break
        if count == 10:
            print("拜访任务已完成~~~")
        else:
            print("拜访任务未完成!!!")

    def fuck(self):
        url = baseURL + "/v1/game/house/task"
        data = {}
        data["access_token"] = self.token
        data["love_space_id"] = self.space
        task_list = self.get_tasks()
        if 8 in task_list:
            self.visit()
            task_list.remove(8)
        if task_list:
            print("正在完成回家任务...")
            for task in task_list:
                data["task_type"] = task
                data["sig"] = buildSig(url, data)
                requests.post(url, data, headers=headers)
                data.pop("sig")
            task_list = self.get_tasks()
            task_list = [self.name[x] for x in task_list if x in self.name.keys()]
            if task_list:
                print(task_list, "尚未完成!!!")
            else:
                print("回家任务已完成~~~")
        else:
            print("回家任务已完成~~~")


class Pet(object):

    def __init__(self, token):
        self.token = token
        self.pet_id, _ = self.get_tasks()
        self.name = {1:"吃饭", 2:"喝水", 3:"洗澡", 4:"抚摸"}

    def get_tasks(self):
        url = baseURL + "/v1/game/house/pet/task/list"
        data = {}
        data["access_token"] = self.token
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        try:
            pets = results['messages'][0]['pets'][0]
            pet_id = pets['pet_id']
            task_list = []
            for task in pets['pet_tasks']:
                if task['remain_time'] == 0:
                    task_list.append(task['task_type'])
            return pet_id, task_list
        except KeyError:
            return None

    def do_tasks(self):
        url = baseURL + "/v1/game/house/pet/task/do"
        data = {}
        data["access_token"] = self.token
        data["pet_id"] = self.pet_id
        _, task_list = self.get_tasks()
        if task_list:
            print("正在完成宠物任务...")
            for task in task_list:
                data["task_type"] = task
                data["sig"] = buildSig(url, data)
                requests.post(url, data, headers=headers)
                data.pop("task_type")
                data.pop("sig")
            _, task_list = self.get_tasks()
            task_list = [self.name[x] for x in task_list if x in self.name.keys()]
            if task_list:
                print(task_list, "尚未完成!!!")
            else:
                print("宠物任务已完成~~~")
        else:
            print("宠物任务已完成~~~")

    def get_info(self):
        url = baseURL + "/v1/game/house/pet/union"
        data = {}
        data["access_token"] = self.token
        data["pet_id"] = self.pet_id
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        for info in results['messages']:
            if 'goods' in info.keys():
                need_to_buy = [good['goods_id'] for good in info['goods'][:3] if good['count'] == 0]
            if 'tasks' in info.keys():
                day_tasks = [task['task_id'] for task in info['tasks'] if task['status'] == 1] 
            if 'stamina' in info.keys():
                stamina = info['stamina']
        return need_to_buy, day_tasks, stamina
    
    def buy(self, need_to_buy):
        url = baseURL + "/v1/game/house/pet/goods/buy"
        data = {}
        data["access_token"] = self.token
        data["count"] = 10
        print("正在购买宠物用品...")
        for good in need_to_buy:
            data["goods_id"] = good
            data["sig"] = buildSig(url, data)
            requests.post(url, data, headers=headers)
            data.pop("goods_id")
            data.pop("sig")
        need_to_buy, _, _ = self.get_info()
        if need_to_buy:
            print(need_to_buy, "未购买成功!!!")
        else:
            print("已购买宠物用品~~~")

    def do_day_tasks(self, day_tasks):
        url = baseURL + "/v1/game/house/pet/dayTask/reward"
        data = {}
        data["access_token"] = self.token
        data["pet_id"] = self.pet_id
        print("正在获取每日奖励...")
        for task in day_tasks:
            data["task_id"] = task
            data["sig"] = buildSig(url, data)
            requests.post(url, data, headers=headers)
            data.pop("task_id")
            data.pop("sig")
        _, day_tasks, _ = self.get_info()
        if day_tasks:
            print(day_tasks, "未获取成功!!!")
        else:
            print("已获取日常奖励~~~")

    def chest_info(self):
        url = baseURL + "/v1/game/house/pet/chest/info"
        data = {}
        data["access_token"] = self.token
        data["chest_ids"] = "301,302"
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        free_chest = [chest['chest_id'] for chest in results['messages'][0]['chests'] if chest['free_chest_time_left'] == 0]
        return free_chest

    def get_chest(self, free_chest):
        url = baseURL + "/v1/game/house/pet/chest/open"
        data = {}
        data["access_token"] = self.token
        data["count"] = 1
        data["pet_id"] = self.pet_id
        print("正在进行宠物抽奖...")
        for chest in free_chest:
            data["chest_id"] = chest
            data["sig"] = buildSig(url, data)
            requests.post(url, data, headers=headers)
            data.pop("chest_id")
            data.pop("sig")
        free_chest = self.chest_info() 
        if free_chest:
            print(free_chest, "抽奖未成功!!!")
        else:
            print("抽奖已完成~~~")

    def walk(self):
        url = baseURL + "/v1/game/house/pet/walk"
        data = {}
        data["access_token"] = self.token
        data["pet_id"] = self.pet_id
        print("正在进行遛狗任务...")
        for scene in [30002, 30004, 30005, 30006]:
            data["scene_id"] = scene
            data["sig"] = buildSig(url, data)
            response = requests.post(url, data)
            data.pop("scene_id")
            data.pop("sig")
        print("遛狗任务已完成~~~")

    def fuck(self):
        need_to_buy, day_tasks, stamina = self.get_info()
        if need_to_buy:
            self.buy(need_to_buy)
        self.do_tasks()
        free_chest = self.chest_info()
        if free_chest:
            self.get_chest(free_chest)
        need_to_buy, day_tasks, stamina = self.get_info()
        if need_to_buy:
            self.buy(need_to_buy)
        if day_tasks:
            self.do_day_tasks(day_tasks)
        if stamina >= 68:
            self.walk()


class Tree(object):

    def __init__(self, token):
        self.token = token

    def info(self):
        url = baseURL + "/v1/game/tree/getInfo"
        data = {}
        data["access_token"] = self.token
        data["app_key"] = app_key
        data["screen_type"] = 102
        data["tree_version"] = 32
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        return results

    def records(self):
        url = baseURL + "/v1/game/tree/records"
        data = {}
        data["access_token"] = self.token
        data["app_key"] = app_key
        data["sig"] = buildSig(url, data)
        response = requests.post(url, data, headers=headers)
        results = response.json()
        return results
    
    def fuck(self):
        url = baseURL + "/v1/game/tree/op"
        data = {}
        data["access_token"] = self.token
        data["app_key"] = app_key
        print("正在完成爱情树任务...")
        for op in [1,2]:
            data["op"] = op
            data["sig"] = buildSig(url, data)
            requests.post(url, data, headers=headers)
            data.pop("op")
            data.pop("sig")
        self.records()
        print("爱情树任务已完成~~~")


class Welove(object):

    def __init__(self, token):
        self.home = Home(token)
        self.tree = Tree(token)
        self.pet = Pet(token)

    def fuck(self):
        self.home.fuck()
        self.pet.fuck()
        self.tree.fuck()


if __name__ == "__main__":
    for name, key in config.items():
        print(time.asctime())
        print("开始%s的表演..." % name)
        welove = Welove(key)
        welove.fuck()
        print("谢谢%s的表演~~~\n" % name)
        time.sleep(5)
