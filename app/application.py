import os
import time
import zipfile
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel

from app.enums.project_enum import ProjectEnum
from app.repo.alterparam import AlterParam
from app.repo.ruoyi import RuoYi
from app.repo.ruoyicloud import RuoYiCloud
from app.repo.ruoyifast import RuoYiFast
from app.repo.ruoyivue import RuoYiVue
from app.repo.templates import get_flat_template_dict

load_dotenv()

application = FastAPI()
application.mount("/static", StaticFiles(directory="static"), name="static")


class DownloadRequest(BaseModel):
    id: int
    version: str
    version_type: str
    project_name: str
    package_name: str
    artifact_id: str
    group_id: str
    site_name: str


@application.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")


@application.get("/api/projects")
async def get_projects():
    return ProjectEnum.get_all_projects()


@application.get("/api/tags")
async def get_tags(project_id: int = Query(...)):
    project = ProjectEnum.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    url = f"https://api.github.com/repos/{project.repo}/tags"
    logger.info(f"开始获取{project.repo}的Tag,url {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        tags = response.json()
        # 只返回前30个tag
        return tags[:30]
    except Exception as e:
        logger.error(f"获取tags失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取tags失败: {str(e)}")


@application.get("/api/branches")
async def get_branches(project_id: int = Query(...)):
    project = ProjectEnum.get_project_by_id(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    url = f"https://api.github.com/repos/{project.repo}/branches"
    logger.info(f"开始获取{project.repo}的Branches,url {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        branches = response.json()
        # 只返回前30个分支
        return branches[:30]
    except Exception as e:
        logger.error(f"获取branches失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取branches失败: {str(e)}")


@application.post("/api/download")
async def download_and_process(request: DownloadRequest):
    logger.info(f"开始处理下载请求: {request}")
    project = ProjectEnum.get_project_by_id(request.id)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    source_dir = download_code(project.repo, request.version_type, request.version)

    param = AlterParam()

    param.context = ''
    param.targetdir = str(source_dir)
    param.sitename = request.site_name
    param.packagename = request.package_name
    param.projectdirname = ''
    param.projectname = request.project_name
    param.artifactid = request.artifact_id
    param.groupid = request.group_id

    config = {
        'config.enable': 'False',  # 关闭配置修改
    }

    # 使用统一的模板配置系统
    template = get_flat_template_dict(request.id)  # 传入项目ID以获取特定配置

    logger.info(f"加载模板配置 {template}")

    logger.info("开始创建修改创建实例...")
    if project == ProjectEnum.RUOYI:
        processor = RuoYi(param, config, template, message_callback)
    elif project == ProjectEnum.RUOYI_VUE:
        processor = RuoYiVue(param, config, template, message_callback)
    elif project == ProjectEnum.RUOYI_FAST:
        processor = RuoYiFast(param, config, template, message_callback)
    elif project == ProjectEnum.RUOYI_CLOUD:
        processor = RuoYiCloud(param, config, template, message_callback)
    else:
        raise HTTPException(status_code=400, detail="不支持的项目")

    logger.info("执行修改...")
    processor.start()

    # 打包修改后的目录
    zip_path = create_zip_package(str(source_dir), request.project_name)

    # 直接返回文件下载响应
    filename = os.path.basename(zip_path)
    logger.info(f"提供文件下载: {zip_path}")
    return FileResponse(
        path=zip_path,
        filename=filename,
        media_type='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


def message_callback(message: str):
    """消息回调函数"""
    logger.info(f"[处理进度] {message}")


def download_code(repo, version_type, version, output_dir="/tmp"):
    if version_type == "tag":
        download_api_url = f"{os.environ.get("PROXY_URL")}/{repo}/archive/refs/tags/{version}.zip"
        logger.info(f"开始构建tag下载链接{download_api_url}")
    elif version_type == "branch":
        download_api_url = f"{os.environ.get("PROXY_URL")}/{repo}/archive/refs/heads/{version}.zip"
        logger.info(f"开始构建分支下载链接: {download_api_url}")
    else:
        raise HTTPException(status_code=400, detail="不支持的版本类型")

    name = time.time()

    download_path = os.path.join(output_dir, f"{name}.zip")
    logger.info("开始下载")
    zip_response = requests.get(download_api_url, stream=True)
    zip_response.raise_for_status()

    os.makedirs(output_dir, exist_ok=True)
    with open(download_path, "wb") as f:
        for chunk in zip_response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"下载完成: {download_path}")

    extract_to = os.path.join(output_dir, f"{name}")
    logger.info(f"正在解压到: {extract_to}")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"解压完成！源码路径: {extract_to}")

    # 找到唯一子目录（即 {repo}-{tag}）
    extracted_dirs = [d for d in Path(extract_to).iterdir() if d.is_dir()]
    if len(extracted_dirs) != 1:
        raise RuntimeError("解压后目录结构异常，无法展平")

    source_dir = extracted_dirs[0]

    logger.info(f"项目路径: {source_dir}")

    return source_dir


def create_zip_package(source_dir: str, project_name: str) -> str:
    """创建ZIP压缩包"""
    timestamp = int(time.time())
    zip_filename = f"{project_name}_{timestamp}.zip"
    zip_path = os.path.join("/tmp", zip_filename)

    logger.info(f"开始打包目录: {source_dir} -> {zip_path}")

    # 确保临时目录存在
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    # 创建ZIP文件
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径作为ZIP内的路径
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    logger.info(f"打包完成: {zip_path}")
    return zip_path
