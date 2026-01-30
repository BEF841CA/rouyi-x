# -*- coding: utf-8 -*-
# @Time : 2021/05/17/
# @Author : ricky
# @File : base.py
# @Software: vscode
"""
关键字修改类基类
"""
import os
import shutil

import chardet
from loguru import logger

# 禁止修改的目录
FORBID_ALTER_DIR_TUPLE = ('target', 'node_modules')


class BaseCore:
    """
    初始化参数:
        param (AlterParam): 修改参数
        configdict (dict): 配置字典
        callback (function): 回调方法

    """

    def __init__(self, param, configdict, templatedict, callback):

        self.context = param.context
        self.targetdir = param.targetdir
        self.sitename = param.sitename
        self.packagename = param.packagename
        self.projectdirname = param.projectdirname
        self.projectname = param.projectname
        self.artifactid = param.artifactid
        self.groupid = param.groupid
        self.configdict = configdict
        self.templatedict = templatedict
        self.callback = callback
        self.exceptions = []

    def start(self):
        """开始方法"""
        pass

    def messagehandle(self, message):
        """
        消息处理

        参数:
            message (str): 消息
        """
        if hasattr(self.callback, '__call__'):
            self.callback(message)

    def exceptionhandle(self, message):
        """
        异常处理

        参数:
            message (str): 消息
        """
        self.exceptions.append(str(len(self.exceptions) + 1) + "." + message)
        logger.error(message)

    def move_dir(self, old_dir, new_dir):
        """
        移动目录（移动完成后删除旧目录）

        参数:
            old_dir (str): 旧目录
            new_dir (str): 新目录
        """
        for temp_path in os.listdir(old_dir):
            filepath = new_dir + os.path.sep + temp_path
            oldpath = old_dir + os.path.sep + temp_path
            if os.path.isdir(oldpath):
                os.mkdir(filepath)
                self.move_dir(oldpath, filepath)
            if os.path.isfile(oldpath):
                shutil.move(oldpath, filepath)
        # 移动完之后删除旧目录
        shutil.rmtree(old_dir)

    def find_root_dir(self, prev_path, prev_dir_name=''):
        """
        递归查找项目根目录

        参数:
            prev_path (str): 上一层目录路径
            prev_dir_name (str): 上一层目录名称
        """
        if len(prev_path) == 0:
            prev_path = self.targetdir
        files = os.listdir(prev_path)
        if len(files) != 1:
            return prev_path, prev_dir_name
        filename = files[0]
        return self.find_root_dir(os.path.join(prev_path, filename), filename)

    def is_allowed_alter(self, dir_name):
        """
        检查目录以及目录以下的文件是否允许修改

        参数:
            dir_name (str): 目录名称
        """
        if dir_name in FORBID_ALTER_DIR_TUPLE:
            return False
        return True

    def get_encoding(self, file: str):
        """
        返回文件编码

        参数:
            file (str): 文件名路径
        """
        with open(file, "rb") as fp:
            return chardet.detect(fp.read(1024 * 1024))["encoding"]
