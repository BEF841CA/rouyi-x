# -*- coding: utf-8 -*-
# @Time : 2021/05/18
# @Author : ricky
# @File : ruoyicloud.py
# @Software: vscode
"""
核心修改类 RuoYi-Cloud版本
"""
import os

from app.repo.base import BaseCore


class RuoYiCloud(BaseCore):
    def start(self):
        self.series = 'RuoYi-Cloud'
        # 查找项目根目录
        self.rootpath, self.rootname = self.find_root_dir(
            self.targetdir)
        # 1.修改站点名称
        self.messagehandle('正在修改标题和修站点名称...')
        self.__alter_site_name_and_title()
        self.messagehandle('站点名称和标题修改完成!')
        # 2.修改包名和项目名
        self.messagehandle('正在修改包名和项目名...')
        self.__alter_package_name_and_project_name(self.rootpath)
        self.messagehandle('包名和项目名修改完成!')
        # 3.修改项目配置和日志配置
        self.messagehandle('正在修改项目配置和日志配置...')
        self.__alter_bootstrapyml_and_logbackxml(self.rootpath)
        self.messagehandle('项目配置和日志配置修改完成!')
        # 4.修改Nacos配置
        self.messagehandle('正在修改Nacos配置...')
        self.__alter_nacos_config(os.path.join(self.rootpath, 'sql'))
        self.messagehandle('Nacos配置修改完成!')
        # 5.修改pom.xml文件
        self.messagehandle('正在修改pom.xml...')
        self.__alter_pom_xml(self.rootpath)
        self.messagehandle('pom.xml修改完成!')
        # 6.修改目录结构
        self.messagehandle('正在修改代码目录结构...')
        self.__alter_code_project_dir()
        self.messagehandle('正在修改项目目录结构...')
        self.__alter_project_dir()
        self.messagehandle('目录结构修改完成!')

        if len(self.exceptions) > 0:
            self.messagehandle('\r发现有异常信息')
            self.messagehandle('-------------------\n\r')
            for e in self.exceptions:
                self.messagehandle(e)
            self.messagehandle('\r----------------------')

    def __alter_site_name_and_title(self):
        """修改站点名称和网站标题"""
        ntuple = tuple(
            eval(self.templatedict[self.series + '.site_resources_path_tuple']))
        default_site_name = self.templatedict[self.series +
                                              '.default_site_name']
        for item in ntuple:
            filepath = os.path.join(self.rootpath,
                                    item.replace('#', os.path.sep))
            if not os.path.exists(filepath):
                continue
            try:
                encoding = self.get_encoding(filepath)
                with open(filepath, 'r',
                          encoding=encoding) as srcfile, open(
                    '%s.bak' % filepath,
                    'w',
                    encoding=encoding) as desfile:
                    for line in srcfile:
                        if default_site_name in line:
                            line = line.replace(
                                default_site_name, self.sitename)
                        if '若依管理系统' in line:
                            line = line.replace('若依管理系统', self.sitename)
                        if '若依后台管理系统' in line:
                            line = line.replace('若依后台管理系统', self.sitename)
                        desfile.write(line)
                # 移除旧文件
                os.remove(filepath)
                # 重命名备份文件为新文件
                os.rename('%s.bak' % filepath, filepath)
            except Exception as err:
                self.exceptionhandle('修改站点名称和网站标题异常\n修改文件：{}\n异常信息：{}'.format(
                    filepath, err))

    def __alter_package_name_and_project_name(self, rootpath):
        """修改包名和项目名称"""
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
                        '.yml'
                ) or filename.endswith('Mapper.xml') or filename.endswith(
                    'logback.xml') or filename.endswith(
                    '.factories') or filename.endswith(
                    '.vm') or filename.endswith(
                    '.bat') or filename.endswith('.sh') or filename.endswith('.imports') or filename == 'dockerfile':
                    try:
                        encoding = self.get_encoding(filepath)
                        with open(filepath, 'r',
                                  encoding=encoding) as srcfile, open(
                            '%s.bak' % filepath,
                            'w',
                            encoding=encoding) as desfile:
                            self.messagehandle('正在修改：' + filename)
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
                                        line = self.__check_yml_or_sql_config(
                                            line, filename)
                                desfile.write(line)
                        # 移除旧文件
                        os.remove(filepath)
                        # 重命名备份文件为新文件
                        os.rename('%s.bak' % filepath, filepath)
                    except Exception as err:
                        self.exceptionhandle(
                            '修改包名和项目名称异常\n修改文件：{}\n异常信息：{}'.format(
                                filepath, err))

    def __alter_bootstrapyml_and_logbackxml(self, rootpath):
        """
        修改项目bootstrap.yml和logback.xml中的模块名

        参数:
            rootpath (str): 根路径
        """
        # 循环修改指定后缀名的文件内容
        files = os.listdir(rootpath)
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        for filename in files:
            filepath = os.path.join(rootpath, filename)
            # 如果是目录继续递归
            if os.path.isdir(filepath):
                self.__alter_bootstrapyml_and_logbackxml(filepath)
            else:
                try:
                    # 如果是文件才进行修改
                    if filename.endswith('.yml') or filename.endswith(
                            'logback.xml'):
                        encoding = self.get_encoding(filepath)
                        with open(
                                filepath, 'r', encoding=encoding
                        ) as srcfile, open(
                            '%s.bak' % filepath,
                            'w',
                            encoding=encoding) as desfile:
                            self.messagehandle('正在修改：' + filename)
                            for line in srcfile:
                                if default_project_name in line:
                                    line = line.replace(
                                        default_project_name,
                                        self.projectname)
                                desfile.write(line)
                        # 移除旧文件
                        os.remove(filepath)
                        # 重命名备份文件为新文件
                        os.rename('%s.bak' % filepath, filepath)
                except Exception as err:
                    self.exceptionhandle(
                        '修改项目bootstrap.yml和logback.xml中的模块名异常\n修改文件：{}\n异常信息：{}'
                        .format(filepath, err))

    def __alter_nacos_config(self, sqldir):
        """
        修改项目Nacos配置

        参数:
            sqldir (str): sql目录
        """
        files = os.listdir(sqldir)
        default_nacos_config_sql_prefix = self.templatedict[
            self.series + '.default_nacos_config_sql_prefix']
        default_package_name = self.templatedict[self.series +
                                                 '.default_package_name']
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        for filename in files:
            filepath = os.path.join(sqldir, filename)
            # 如果是目录继续递归
            if os.path.isdir(filepath):
                self.__alter_nacos_config(filepath)
            else:
                try:
                    # 如果是文件才进行修改
                    if filename.startswith(
                            default_nacos_config_sql_prefix):
                        encoding = self.get_encoding(filepath)
                        with open(
                                filepath, 'r', encoding=encoding
                        ) as srcfile, open(
                            '%s.bak' % filepath,
                            'w',
                            encoding=encoding) as desfile:
                            self.messagehandle('正在修改：' + filename)
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
                                    line = self.__check_yml_or_sql_config(
                                        line, filename)
                                desfile.write(line)
                        # 移除旧文件
                        os.remove(filepath)
                        # 重命名备份文件为新文件
                        os.rename('%s.bak' % filepath, filepath)
                except Exception as err:
                    self.exceptionhandle(
                        '修改项目Nacos配置异常\n修改文件：{}\n异常信息：{}'.format(
                            filepath, err))

    def __check_yml_or_sql_config(self, line, filename):
        """
        检测yml配置文件

        参数:
            line (str): 行
            filename (str): 文件名
        """
        if 'localhost:3306/ry-cloud' in line and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'mysql_ip_port_name')
        if 'username: root' in line and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'mysql_username')
        if 'password: password' in line and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'mysql_password')
        if 'host: localhost' in line and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'redis_host')
        if 'port: 6379' in line and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'redis_port')
        if ('password: \\r\\n' in line or 'password: \\n' in line) and filename.endswith('.sql'):
            line = self.__alert_yml_or_sql_config(line, 'redis_password')

        return line

    def __alert_yml_or_sql_config(self, line, type_):
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
            return line.replace('localhost:3306/ry-cloud',
                                mysql_ip + ':' + mysql_port + '/' + mysql_name)
        if type_ == 'mysql_username':
            mysql_username = self.configdict['database.username']
            return line.replace('username: root',
                                'username: ' + mysql_username)
        if type_ == 'mysql_password':
            mysql_password = self.configdict['database.password']
            return line.replace('password: password',
                                'password: ' + mysql_password)
        if type_ == 'redis_host':
            redis_ip = self.configdict['redis.ip']
            return line.replace('host: localhost', 'host: ' + redis_ip)
        if type_ == 'redis_port':
            redis_port = self.configdict['redis.port']
            return line.replace('port: 6379', 'port: ' + redis_port)
        if type_ == 'redis_password':
            redis_password = self.configdict['redis.password']
            return line.replace('password: \\r\\n',
                                'password: ' + redis_password + '\\r\\n').replace('password: \\n',
                                                                                  'password: ' + redis_password + '\\n')
        return line

    def __alter_pom_xml(self, rootpath):
        """
        修改项目pom.xml文件

        参数：
            rootpath (str): 根目录
        """
        default_artifactid_prefix = self.templatedict[self.series +
                                                      '.default_artifactid_prefix']
        default_group_id = self.templatedict[self.series + '.default_group_id']
        default_site_name = self.templatedict[self.series +
                                              '.default_site_name']
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        files = os.listdir(rootpath)
        for filename in files:
            filepath = os.path.join(rootpath, filename)
            # 如果是目录继续递归
            if os.path.isdir(filepath):
                self.__alter_pom_xml(filepath)
            else:
                try:
                    # 如果是文件才进行修改
                    if filename.endswith('pom.xml'):
                        encoding = self.get_encoding(filepath)
                        with open(
                                filepath, 'r', encoding=encoding
                        ) as srcfile, open(
                            '%s.bak' % filepath,
                            'w',
                            encoding=encoding) as desfile:
                            self.messagehandle('正在修改：' + filename)
                            for line in srcfile:
                                if default_group_id in line and '<groupId>' in line:
                                    line = line.replace(
                                        default_group_id,
                                        self.groupid)
                                if default_artifactid_prefix in line and '<artifactId>' in line:
                                    line = line.replace(
                                        default_artifactid_prefix,
                                        self.artifactid)
                                if '<name>' in line or '<module>' in line:
                                    line = line.replace(
                                        default_project_name,
                                        self.projectname)
                                if 'version>' in line:
                                    line = line.replace(
                                        default_artifactid_prefix,
                                        self.artifactid)
                                if default_site_name in line:
                                    line = line.replace(
                                        default_site_name,
                                        self.sitename)
                                line = line.replace(
                                    default_artifactid_prefix,
                                    self.projectname)
                                desfile.write(line)
                        # 移除旧文件
                        os.remove(filepath)
                        # 重命名备份文件为新文件
                        os.rename('%s.bak' % filepath, filepath)
                except Exception as err:
                    self.exceptionhandle(
                        '修改项目pom.xml文件异常\n修改文件：{}\n异常信息：{}'.format(
                            filepath, err))

    def __alter_code_project_dir(self):
        """修改代码目录名"""
        default_package_name = self.templatedict[self.series +
                                                 '.default_package_name']
        default_module_name_tuple = tuple(
            eval(self.templatedict[self.series + '.default_module_name_tuple']))
        for module_name in default_module_name_tuple:
            replace_module_name = module_name.replace('#', os.path.sep)
            if not os.path.exists(
                    os.path.join(self.rootpath, replace_module_name)):
                continue
            src_dir = os.path.join(self.rootpath,
                                   replace_module_name,
                                   'src/main/java')
            self.__alter_src_dir(src_dir, replace_module_name,
                                 default_package_name, 'main')
            src_dir = os.path.join(self.rootpath,
                                   replace_module_name,
                                   'src/test-integration/java')
            self.__alter_src_dir(src_dir, replace_module_name,
                                 default_package_name, 'test-integration')
            src_dir = os.path.join(self.rootpath,
                                   replace_module_name,
                                   'src/test/java')
            self.__alter_src_dir(src_dir, replace_module_name,
                                 default_package_name, 'test')

    def __alter_src_dir(self, src_dir, replace_module_name, default_package_name, src_type):
        """修改src目录名"""
        # 如果src目录不存在，返回
        if not os.path.exists(src_dir):
            return
        source_dir = os.path.join(
            src_dir,
            self.packagename.replace('.', os.path.sep))
        old_dir = os.path.join(
            src_dir, default_package_name.replace('.', os.path.sep))
        # 如果旧目录不存在，返回
        if not os.path.exists(old_dir):
            return
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        # 移动目录及文件
        self.move_dir(old_dir,
                      source_dir)

        # 删除空目录
        a = default_package_name.split('.')
        for i in range(0, len(a)):
            n = a[:(i + 1) * -1]
            if len(n) == 0:
                break
            dpath = os.path.join(src_dir, os.path.sep.join(n))
            if not os.listdir(dpath):
                os.rmdir(dpath)
        self.messagehandle('正在修改：' + replace_module_name +
                           ' [' + src_type + ']')

    def __alter_project_dir(self):
        """修改目录名"""
        default_project_name = self.templatedict[self.series +
                                                 '.default_project_name']
        default_module_name_tuple = tuple(
            eval(self.templatedict[self.series + '.default_module_name_tuple']))
        for module_name in default_module_name_tuple:
            replace_module_name = module_name.replace('#', os.path.sep)
            if not os.path.exists(
                    os.path.join(self.rootpath, replace_module_name)):
                continue
            if module_name.find('#') == -1:
                os.rename(
                    os.path.join(self.rootpath, module_name),
                    os.path.join(
                        self.rootpath, module_name.replace(
                            default_project_name, self.projectname)
                    ))
            else:
                tarpath = os.path.join(
                    self.rootpath,
                    module_name.split('#')[0],
                    module_name.split('#')[1].replace(
                        default_project_name, self.projectname)
                )
                os.rename(os.path.join(self.rootpath, replace_module_name),
                          tarpath)
            self.messagehandle('正在修改：' + replace_module_name)
        if (len(self.rootname) > 0):
            os.rename(self.rootpath,
                      os.path.join(self.targetdir, self.projectdirname))
            self.messagehandle('正在修改：' + self.rootname)
