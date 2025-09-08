#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @Time    : 2025-08-31 22:36
# @Author  : crawl-coder
# @Desc    : 命令行入口：crawlo genspider baidu，创建爬虫。
"""
import sys
from pathlib import Path
import configparser
import importlib
from rich.console import Console

# 初始化 rich 控制台
console = Console()

TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'


def _render_template(tmpl_path, context):
    """读取模板文件，替换 {{key}} 为 context 中的值"""
    with open(tmpl_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for key, value in context.items():
        content = content.replace(f'{{{{{key}}}}}', str(value))
    return content


def main(args):
    if len(args) < 2:
        console.print("[bold red]Error:[/bold red] Usage: [blue]crawlo genspider[/blue] <spider_name> <domain>")
        return 1

    spider_name = args[0]
    domain = args[1]

    # 查找项目根目录
    project_root = None
    current = Path.cwd()
    while True:
        cfg_file = current / 'crawlo.cfg'
        if cfg_file.exists():
            project_root = current
            break
        parent = current.parent
        if parent == current:
            break
        current = parent

    if not project_root:
        console.print("[bold red]:cross_mark: Error:[/bold red] Not a crawlo project. [cyan]crawlo.cfg[/cyan] not found.")
        return 1

    # 将项目根目录加入 sys.path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 从 crawlo.cfg 读取 settings 模块，获取项目包名
    config = configparser.ConfigParser()
    try:
        config.read(cfg_file, encoding='utf-8')
        settings_module = config.get('settings', 'default')
        project_package = settings_module.split('.')[0]  # e.g., myproject.settings -> myproject
    except Exception as e:
        console.print(f"[bold red]:cross_mark: Error reading crawlo.cfg:[/bold red] {e}")
        return 1

    # 确定 items 模块的路径
    items_module_path = f"{project_package}.items"

    # 尝试导入 items 模块
    default_item_class = "ExampleItem"  # 默认回退
    try:
        items_module = importlib.import_module(items_module_path)
        # 获取模块中所有大写开头的类
        item_classes = [
            cls for cls in items_module.__dict__.values()
            if isinstance(cls, type) and cls.__name__[0].isupper()  # 首字母大写
        ]

        if item_classes:
            default_item_class = item_classes[0].__name__
        else:
            console.print("[yellow]:warning: Warning:[/yellow] No item class found in [cyan]items.py[/cyan], using [green]ExampleItem[/green].")

    except ImportError as e:
        console.print(f"[yellow]:warning: Warning:[/yellow] Failed to import [cyan]{items_module_path}[/cyan]: {e}")
        # 仍使用默认 ExampleItem，不中断流程

    # 创建爬虫文件
    spiders_dir = project_root / project_package / 'spiders'
    spiders_dir.mkdir(parents=True, exist_ok=True)

    spider_file = spiders_dir / f'{spider_name}.py'
    if spider_file.exists():
        console.print(f"[bold red]:cross_mark: Error:[/bold red] Spider '[cyan]{spider_name}[/cyan]' already exists at [green]{spider_file}[/green]")
        return 1

    # 模板路径
    tmpl_path = TEMPLATES_DIR / 'spider' / 'spider.py.tmpl'
    if not tmpl_path.exists():
        console.print(f"[bold red]:cross_mark: Error:[/bold red] Template file not found at [cyan]{tmpl_path}[/cyan]")
        return 1

    # 生成类名
    class_name = f"{spider_name.capitalize()}Spider"

    context = {
        'spider_name': spider_name,
        'domain': domain,
        'project_name': project_package,
        'item_class': default_item_class,
        'class_name': class_name
    }

    content = _render_template(tmpl_path, context)

    with open(spider_file, 'w', encoding='utf-8') as f:
        f.write(content)

    console.print(f":white_check_mark: [green]Spider '[bold]{spider_name}[/bold]' created successfully![/green]")
    console.print(f"  → Location: [cyan]{spider_file}[/cyan]")
    console.print("\n[bold]Next step:[/bold]")
    console.print(f"  [blue]crawlo run[/blue] {spider_name}")

    return 0