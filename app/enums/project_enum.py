from enum import Enum


class ProjectEnum(Enum):
    RUOYI = (1, "RuoYi", "yangzongzhuan/RuoYi", "基于SpringBoot开发的轻量级Java快速开发框架")
    RUOYI_VUE = (2, "RuoYi-Vue", "yangzongzhuan/RuoYi-Vue", "基于SpringBoot+Vue前后端分离的Java快速开发框架")
    RUOYI_FAST = (3, "RuoYi-fast", "yangzongzhuan/RuoYi-fast", "基于SpringBoot开发的轻量级Java快速开发框架")
    RUOYI_CLOUD = (4, "RuoYi-Cloud", "yangzongzhuan/RuoYi-Cloud",
                   "基于 Vue/Element UI 和 Spring Boot/Spring Cloud & Alibaba 前后端分离的分布式微服务架构")

    def __init__(self, project_id, project_name, repo, description):
        self._project_id = project_id
        self._project_name = project_name
        self._repo = repo
        self._description = description

    @property
    def project_id(self):
        return self._project_id

    @property
    def project_name(self):
        return self._project_name

    @property
    def repo(self):
        return self._repo

    @property
    def description(self):
        return self._description

    @property
    def to_dict(self):
        return {
            "id": self.project_id,
            "name": self.project_name,
            "repo": self.repo,
            "description": self.description
        }

    @classmethod
    def get_all_projects(cls):
        return [project.to_dict for project in cls]

    @classmethod
    def get_project_by_id(cls, project_id):
        for project in cls:
            if project.project_id == project_id:
                return project
        return None