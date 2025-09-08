#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @Time    : 2025-08-31 22:33
# @Author  : crawl-coder
# @Desc    : 命令行入口：crawlo list，用于列出所有已注册的爬虫
"""
import sys
import configparser
from pathlib import Path
from importlib import import_module

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from crawlo.crawler import CrawlerProcess
from crawlo.utils.log import get_logger

logger = get_logger(__name__)
console = Console()


def get_project_root():
    """
    自动检测项目根目录：从当前目录向上查找 crawlo.cfg
    找到后返回该目录路径（字符串），最多向上查找10层。
    """
    current = Path.cwd()
    for _ in range(10):
        cfg = current / "crawlo.cfg"
        if cfg.exists():
            return str(current)
        if current == current.parent:
            break
        current = current.parent
    return None  # 未找到


def main(args):
    """
    主函数：列出所有可用爬虫
    用法: crawlo list
    """
    if args:
        console.print("[bold red]❌ Error:[/bold red] Usage: [blue]crawlo list[/blue]")
        return 1

    try:
        # 1. 查找项目根目录
        project_root = get_project_root()
        if not project_root:
            console.print(Panel(
                Text.from_markup(
                    ":cross_mark: [bold red]Cannot find 'crawlo.cfg'[/bold red]\n"
                    "💡 Run this command inside your project directory.\n"
                    "🚀 Or create a new project with:\n"
                    "   [blue]crawlo startproject myproject[/blue]"
                ),
                title="❌ Not in a Crawlo Project",
                border_style="red",
                padding=(1, 2)
            ))
            return 1

        project_root_path = Path(project_root)
        project_root_str = str(project_root_path)

        # 2. 将项目根加入 Python 路径
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)

        # 3. 读取 crawlo.cfg 获取 settings 模块
        cfg_file = project_root_path / "crawlo.cfg"
        config = configparser.ConfigParser()
        config.read(cfg_file, encoding="utf-8")

        if not config.has_section("settings") or not config.has_option("settings", "default"):
            console.print(Panel(
                ":cross_mark: [bold red]Invalid crawlo.cfg[/bold red]\n"
                "Missing [settings] section or 'default' option.",
                title="❌ Config Error",
                border_style="red"
            ))
            return 1

        settings_module = config.get("settings", "default")
        project_package = settings_module.split(".")[0]

        # 4. 确保项目包可导入
        try:
            import_module(project_package)
        except ImportError as e:
            console.print(Panel(
                f":cross_mark: Failed to import project package '[cyan]{project_package}[/cyan]':\n{e}",
                title="❌ Import Error",
                border_style="red"
            ))
            return 1

        # 5. 初始化 CrawlerProcess 并加载爬虫模块
        spider_modules = [f"{project_package}.spiders"]
        process = CrawlerProcess(spider_modules=spider_modules)

        # 6. 获取所有爬虫名称
        spider_names = process.get_spider_names()
        if not spider_names:
            console.print(Panel(
                Text.from_markup(
                    ":envelope_with_arrow: [bold]No spiders found[/bold] in '[cyan]spiders/[/cyan]' directory.\n\n"
                    "[bold]💡 Make sure:[/bold]\n"
                    "  • Spider classes inherit from [blue]`crawlo.spider.Spider`[/blue]\n"
                    "  • Each spider has a [green]`name`[/green] attribute\n"
                    "  • Spiders are imported in [cyan]`spiders/__init__.py`[/cyan] (if using package)"
                ),
                title="📭 No Spiders Found",
                border_style="yellow",
                padding=(1, 2)
            ))
            return 1

        # 7. 输出爬虫列表 —— 使用表格
        table = Table(
            title=f"📋 Found {len(spider_names)} spider(s)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            title_style="bold green"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Class", style="green")
        table.add_column("Module", style="dim")

        for name in sorted(spider_names):
            spider_cls = process.get_spider_class(name)
            module_name = spider_cls.__module__.replace(f"{project_package}.", "")
            table.add_row(name, spider_cls.__name__, module_name)

        console.print(table)
        return 0

    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        logger.exception("Exception during 'crawlo list'")
        return 1
