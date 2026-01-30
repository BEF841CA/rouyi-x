# -*- coding: utf-8 -*-
# @Time : 2021/05/25
# @Author : ricky
# @File : alterparam.py
# @Software: vscode
"""
修改参数实体类
"""


class AlterParam(object):
    def __init__(self):
        pass

    @property
    def context(self):
        """上下文对象"""
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def targetdir(self):
        """目标路径"""
        return self._targetdir

    @targetdir.setter
    def targetdir(self, value):
        self._targetdir = value

    @property
    def sitename(self):
        """新站点名称"""
        return self._sitename

    @sitename.setter
    def sitename(self, value):
        self._sitename = value

    @property
    def projectdirname(self):
        """新目录名称"""
        return self._projectdirname

    @projectdirname.setter
    def projectdirname(self, value):
        self._projectdirname = value

    @property
    def packagename(self):
        """新包名"""
        return self._packagename

    @packagename.setter
    def packagename(self, value):
        self._packagename = value

    @property
    def projectname(self):
        """新项目名"""
        return self._projectname

    @projectname.setter
    def projectname(self, value):
        self._projectname = value

    @property
    def artifactid(self):
        """新artifactId"""
        return self._artifactid

    @artifactid.setter
    def artifactid(self, value):
        self._artifactid = value

    @property
    def groupid(self):
        """新groupId"""
        return self._groupid

    @groupid.setter
    def groupid(self, value):
        self._groupid = value
