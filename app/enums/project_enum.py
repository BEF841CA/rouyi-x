from enum import Enum


# RuoYi 项目枚举
class ProjectEnum(Enum):
    RUOYI = ("RuoYi",
             "yangzongzhuan/RuoYi",
             "基于SpringBoot开发的轻量级Java快速开发框架")
    RUOYI_VUE = ("RuoYi-Vue",
                 "yangzongzhuan/RuoYi-Vue",
                 "基于SpringBoot+Vue前后端分离的Java快速开发框架")
    RUOYI_FAST = ("RuoYi-fast",
                  "yangzongzhuan/RuoYi-fast",
                  "基于SpringBoot开发的轻量级Java快速开发框架")
    RUOYI_CLOUD = ("RuoYi-Cloud",
                   "yangzongzhuan/RuoYi-Cloud",
                   "基于 Vue/Element UI 和 Spring Boot/Spring Cloud & Alibaba 前后端分离的分布式微服务架构")

    def __init__(self, project_name, repo, description):
        self._project_name = project_name
        self._repo = repo
        self._description = description

    @property
    def name(self):
        """项目显示名称"""
        return self._project_name

    @property
    def repo(self):
        """仓库路径"""
        return self._repo

    @property
    def description(self):
        """项目描述"""
        return self._description

    @property
    def to_dict(self):
        return {
            "name": self.name,
            "repo": self.repo,
            "description": self.description
        }

    @classmethod
    def get_all_projects(cls):
        return [project.to_dict for project in cls]

    @classmethod
    def get_project_by_repo(cls, repo):
        for project in cls:
            if project.repo == repo:
                return project
        return None
