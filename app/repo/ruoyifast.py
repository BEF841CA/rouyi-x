# -*- coding: utf-8 -*-
# @Time : 2021/05/18
# @Author : ricky
# @File : ruoyifast.py
# @Software: vscode
"""
核心修改类 RuoYi-fast版本
"""
import os

import base


class RuoYiFast(base.BaseCore):
    def start(self):
        self.series = 'RuoYi-fast'
        # 查找项目根目录
        self.rootpath, self.rootname = self.find_root_dir(
            self.targetdir)
        # 1.修改站点名称
        self.messagehandle("正在修改标题和修站点名称...")
        self.__alter_site_name_and_title()
        self.messagehandle("站点名称和标题修改完成!")
        # 2.修改包名和项目名
        self.messagehandle("正在修改包名和项目名...")
        self.__alter_package_name_and_project_name(self.rootpath)
        self.messagehandle("包名和项目名修改完成!")
        # 3.修改pom.xml文件
        self.messagehandle("正在修改pom.xml...")
        self.__alter_pom_xml()
        self.messagehandle("pom.xml修改完成!")
        # 4.修改目录结构
        self.messagehandle("正在修改目录结构...")
        self.__alter_project_dir()
        self.messagehandle("目录结构修改完成!")

        if len(self.exceptions) > 0:
            self.messagehandle("\r发现有异常信息")
            self.messagehandle("-------------------\n\r")
            for e in self.exceptions:
                self.messagehandle(e)
            self.messagehandle("\r----------------------")

    def __alter_site_name_and_title(self):
        """修改站点名称和网站标题"""
        ntuple = tuple(
            eval(self.templatedict[self.series + '.site_resources_path_tuple']))
        default_site_name = self.templatedict[self.series +
                                              '.default_site_name']
        for item in ntuple:
            filepath = os.path.join(self.rootpath,
                                    item.replace('#', os.path.sep))
            if os.path.exists(filepath):
                try:
                    encoding = self.get_encoding(filepath)
                    with open(filepath, "r",
                              encoding=encoding) as srcfile, open(
                        "%s.bak" % filepath,
                        "w",
                        encoding=encoding) as desfile:
                        for line in srcfile:
                            if default_site_name in line:
                                line = line.replace(
                                    default_site_name,
                                    self.sitename)
                            if '若依后台管理系统' in line:
                                line = line.replace('若依后台管理系统', self.sitename)
                            if '若依 后台管理系统' in line:
                                line = line.replace('若依 后台管理系统', self.sitename)
                            if '登录若依系统' in line:
                                line = line.replace('登录若依系统',
                                                    '登录' + self.sitename)
                            if '若依系统' in line:
                                line = line.replace('若依系统', self.sitename)
                            if '若依介绍' in line:
                                line = line.replace('若依介绍',
                                                    self.sitename + '介绍')
                            if 'RuoYi -' in line:
                                line = line.replace('RuoYi -', self.sitename)
                            desfile.write(line)
                    # 移除旧文件
                    os.remove(filepath)
                    # 重命名备份文件为新文件
                    os.rename("%s.bak" % filepath, filepath)
                except Exception as err:
                    self.exceptionhandle(
                        "修改站点名称和网站标题异常\n修改文件：{}\n异常信息：{}".format(
                            filepath, err))

    def __alter_package_name_and_project_name(self, rootpath):
        """
        修改包名和项目名称

        参数:
            rootpath (str): 文件路径
        """
        files = os.listdir(rootpath)
        default_package_name = self.templatedict[self.series +
                                                 '.default_package_name']
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        for filename in files:
            filepath = os.path.join(rootpath, filename)
            if os.path.isdir(filepath):
                self.__alter_package_name_and_project_name(filepath)
            else:
                if filename.endswith('.java') or filename.endswith(
                        '.yml') or filename.endswith(
                    'Mapper.xml') or filename.endswith(
                    'logback.xml') or filename.endswith(
                    '.vm') or filename.endswith(
                    '.bat') or filename.endswith('.sh'):
                    try:
                        encoding = self.get_encoding(filepath)
                        with open(filepath, "r",
                                  encoding=encoding) as srcfile, open(
                            "%s.bak" % filepath,
                            "w",
                            encoding=encoding) as desfile:
                            self.messagehandle("正在修改：" + filename)
                            for line in srcfile:
                                if default_package_name in line:
                                    line = line.replace(
                                        default_package_name,
                                        self.packagename)
                                if default_project_name + '-' in line:
                                    line = line.replace(
                                        default_project_name + '-',
                                        self.projectname + '-')
                                if self.configdict['config.enable'] == 'True':
                                    if filename.endswith('.yml'):
                                        line = self.__check_yml_config(
                                            line, filename)
                                desfile.write(line)
                        # 移除旧文件
                        os.remove(filepath)
                        # 重命名备份文件为新文件
                        os.rename("%s.bak" % filepath, filepath)
                    except Exception as err:
                        self.exceptionhandle(
                            "修改包名和项目名称异常\n修改文件：{}\n异常信息：{}".format(
                                filepath, err))

    def __check_yml_config(self, line, filename):
        """
        检测yml配置文件

        参数:
            line (str): 行
            filename (str): 文件名
        """
        if 'localhost:3306/ry' in line and filename == 'application-druid.yml':
            line = self.__alert_yml_config(line, 'mysql_ip_port_name')
        if 'username: root' in line and filename == 'application-druid.yml':
            line = self.__alert_yml_config(line, 'mysql_username')
        if 'password: password' in line and filename == 'application-druid.yml':
            line = self.__alert_yml_config(line, 'mysql_password')
        return line

    def __alert_yml_config(self, line, type_):
        """
        修改yml配置文件

        参数:
            line (str): 行
            type_ (str): 修改类型
        """
        if type_ == 'mysql_ip_port_name':
            mysql_ip = self.configdict['database.ip']
            mysql_port = self.configdict['database.port']
            mysql_name = self.configdict['database.name']
            return line.replace('localhost:3306/ry',
                                mysql_ip + ":" + mysql_port + "/" + mysql_name)
        if type_ == 'mysql_username':
            mysql_username = self.configdict['database.username']
            return line.replace('username: root',
                                'username: ' + mysql_username)
        if type_ == 'mysql_password':
            mysql_password = self.configdict['database.password']
            return line.replace('password: password',
                                'password: ' + mysql_password)
        return line

    def __alter_pom_xml(self):
        """修改项目pom.xml文件"""
        pom_xml_file = os.path.join(self.rootpath, 'pom.xml')
        default_artifactid_prefix = self.templatedict[self.series +
                                                      '.default_artifactid_prefix']
        default_group_id = self.templatedict[self.series + '.default_group_id']
        default_site_name = self.templatedict[self.series +
                                              '.default_site_name']
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        if not os.path.exists(pom_xml_file):
            return
        try:
            encoding = self.get_encoding(pom_xml_file)
            with open(pom_xml_file, "r",
                      encoding=encoding) as xml_file, open(
                "%s.bak" % pom_xml_file,
                "w",
                encoding=encoding) as target_file:
                self.messagehandle("正在修改：" + self.rootname +
                                   "/pom.xml")
                for line in xml_file:
                    if '<groupId>' in line:
                        line = line.replace(default_group_id,
                                            self.groupid)
                    if '<artifactId>' in line:
                        line = line.replace(
                            default_artifactid_prefix,
                            self.artifactid)
                    if '<name>' in line:
                        line = line.replace(default_project_name,
                                            self.projectname)
                    if '<description>' in line:
                        line = line.replace(default_site_name,
                                            self.sitename)
                    target_file.write(line)
            # 移除旧文件
            os.remove(pom_xml_file)
            # 重命名备份文件为新文件
            os.rename("%s.bak" % pom_xml_file, pom_xml_file)
        except Exception as err:
            self.exceptionhandle("修改项目pom.xml文件异常\n修改文件：{}\n异常信息：{}".format(
                pom_xml_file, err))

    def __alter_project_dir(self):
        """修改目录名"""
        default_package_name = self.templatedict[self.series +
                                                 '.default_package_name']
        src_main_java_dir = os.path.join(self.rootpath, 'src/main/java')
        if not os.path.exists(src_main_java_dir):
            return
        source_dir = os.path.join(src_main_java_dir,
                                  self.packagename.replace('.', os.path.sep))
        old_dir = os.path.join(
            src_main_java_dir, default_package_name.replace('.', os.path.sep))
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        # 移动目录及文件
        self.move_dir(old_dir, source_dir)
        # 删除空目录
        for dir in os.listdir(src_main_java_dir):
            dpath = os.path.join(src_main_java_dir, dir)
            if not os.listdir(dpath):
                os.rmdir(dpath)
        if (len(self.rootname) > 0):
            os.rename(self.rootpath,
                      os.path.join(self.targetdir, self.projectdirname))
            self.messagehandle("正在修改：" + self.rootname)
