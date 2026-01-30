# -*- coding: utf-8 -*-
"""
RuoYi项目模板配置文件
定义各系列项目的默认配置变量
"""

# RuoYi标准版系列配置
RUOYI_CONFIG = {
    'series': 'RuoYi',
    'default_artifactid_prefix': 'ruoyi',
    'default_group_id': 'com.ruoyi',
    'default_package_name': 'com.ruoyi',
    'default_site_name': '若依管理系统',
    'default_project_name': 'ruoyi',
    'site_resources_path_tuple': (
        'ruoyi-admin#src#main#resources#templates#login.html',
        'ruoyi-admin#src#main#resources#templates#index.html',
        'ruoyi-admin#src#main#resources#templates#index-topnav.html',
        'ruoyi-admin#src#main#resources#templates#main_v1.html',
        'ruoyi-admin#src#main#resources#templates#register.html',
        'ruoyi-admin#src#main#resources#templates#error#404.html',
        'ruoyi-admin#src#main#resources#templates#error#500.html',
        'ruoyi-admin#src#main#resources#templates#error#business.html',
        'ruoyi-admin#src#main#resources#templates#error#unauth.html'
    ),
    'default_module_name_tuple': (
        'ruoyi-admin',
        'ruoyi-common',
        'ruoyi-framework',
        'ruoyi-generator',
        'ruoyi-quartz',
        'ruoyi-system'
    )
}

# RuoYi-fast系列配置
RUOYI_FAST_CONFIG = {
    'series': 'RuoYi-fast',
    'default_artifactid_prefix': 'ruoyi',
    'default_group_id': 'com.ruoyi',
    'default_package_name': 'com.ruoyi',
    'default_site_name': '若依管理系统',
    'default_project_name': 'ruoyi',
    'site_resources_path_tuple': (
        'src#main#resources#templates#login.html',
        'src#main#resources#templates#index.html',
        'src#main#resources#templates#index-topnav.html',
        'src#main#resources#templates#main_v1.html',
        'src#main#resources#templates#register.html',
        'src#main#resources#templates#error#404.html',
        'src#main#resources#templates#error#500.html',
        'src#main#resources#templates#error#business.html',
        'src#main#resources#templates#error#unauth.html'
    )
}

# RuoYi-Vue系列配置
RUOYI_VUE_CONFIG = {
    'series': 'RuoYi-Vue',
    'default_artifactid_prefix': 'ruoyi',
    'default_group_id': 'com.ruoyi',
    'default_package_name': 'com.ruoyi',
    'default_site_name': '若依管理系统',
    'default_project_name': 'ruoyi',
    'site_resources_path_tuple': (
        'ruoyi-ui#.env.development',
        'ruoyi-ui#.env.production',
        'ruoyi-ui#.env.staging',
        'ruoyi-ui#package.json',
        'ruoyi-ui#vue.config.js',
        'ruoyi-ui#src#settings.js',
        'ruoyi-ui#src#layout#components#Sidebar#Logo.vue',
        'ruoyi-ui#src#views#login.vue'
    ),
    'default_module_name_tuple': (
        'ruoyi-admin',
        'ruoyi-common',
        'ruoyi-framework',
        'ruoyi-generator',
        'ruoyi-quartz',
        'ruoyi-system',
        'ruoyi-ui'
    )
}

# RuoYi-Cloud系列配置
RUOYI_CLOUD_CONFIG = {
    'series': 'RuoYi-Cloud',
    'default_artifactid_prefix': 'ruoyi',
    'default_group_id': 'com.ruoyi',
    'default_package_name': 'com.ruoyi',
    'default_site_name': '若依微服务系统',
    'default_project_name': 'ruoyi',
    'default_nacos_config_sql_prefix': 'ry_config_',
    'site_resources_path_tuple': (
        'ruoyi-ui#.env.development',
        'ruoyi-ui#.env.production',
        'ruoyi-ui#.env.staging',
        'ruoyi-ui#package.json',
        'ruoyi-ui#vue.config.js',
        'ruoyi-ui#src#settings.js',
        'ruoyi-ui#src#layout#components#Sidebar#Logo.vue',
        'ruoyi-ui#src#views#login.vue'
    ),
    'default_module_name_tuple': (
        'ruoyi-api#ruoyi-api-system',
        'ruoyi-common#ruoyi-common-core',
        'ruoyi-common#ruoyi-common-datascope',
        'ruoyi-common#ruoyi-common-datasource',
        'ruoyi-common#ruoyi-common-log',
        'ruoyi-common#ruoyi-common-redis',
        'ruoyi-common#ruoyi-common-seata',
        'ruoyi-common#ruoyi-common-security',
        'ruoyi-common#ruoyi-common-swagger',
        'ruoyi-modules#ruoyi-file',
        'ruoyi-modules#ruoyi-gen',
        'ruoyi-modules#ruoyi-job',
        'ruoyi-modules#ruoyi-system',
        'ruoyi-visual#ruoyi-monitor',
        'ruoyi-api',
        'ruoyi-auth',
        'ruoyi-common',
        'ruoyi-gateway',
        'ruoyi-modules',
        'ruoyi-visual',
        'ruoyi-ui'
    )
}

# 所有配置的映射字典
PROJECT_TEMPLATES = {
    1: RUOYI_CONFIG,
    2: RUOYI_VUE_CONFIG,
    3: RUOYI_FAST_CONFIG,
    4: RUOYI_CLOUD_CONFIG
}


def get_flat_template_dict(project_id):
    """
    获取扁平化的模板字典，用于当前项目的使用方式
    将嵌套的配置转换为键值对形式

    Returns:
        dict: 扁平化的配置字典
    """
    flat_dict = {}
    series = ''
    data = PROJECT_TEMPLATES.get(project_id)
    for key, value in data.items():
        if key == 'series':
            series = value
        else:
            if isinstance(value, tuple):
                # 将元组转换为字符串表示
                flat_dict[f'{series}.{key}'] = str(value)
            else:
                flat_dict[f'{series}.{key}'] = value

    return flat_dict
