#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @Time    : 2025-08-31 22:36
# @Author  : crawl-coder
# @Desc    : 命令行入口：crawlo startproject baidu，创建项目。
"""
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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


def _copytree_with_templates(src, dst, context):
    """
    递归复制目录，将 .tmpl 文件渲染后复制（去除 .tmpl 后缀），其他文件直接复制。
    """
    src_path = Path(src)
    dst_path = Path(dst)
    dst_path.mkdir(parents=True, exist_ok=True)

    for item in src_path.rglob('*'):
        rel_path = item.relative_to(src_path)
        dst_item = dst_path / rel_path

        if item.is_dir():
            dst_item.mkdir(parents=True, exist_ok=True)
        else:
            if item.suffix == '.tmpl':
                rendered_content = _render_template(item, context)
                final_dst = dst_item.with_suffix('')
                final_dst.parent.mkdir(parents=True, exist_ok=True)
                with open(final_dst, 'w', encoding='utf-8') as f:
                    f.write(rendered_content)
            else:
                shutil.copy2(item, dst_item)


def main(args):
    if len(args) != 1:
        console.print("[bold red]Error:[/bold red] Usage: crawlo startproject <project_name>")
        return 1

    project_name = args[0]
    project_dir = Path(project_name)

    if project_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '[cyan]{project_dir}[/cyan]' already exists.")
        return 1

    context = {'project_name': project_name}
    template_dir = TEMPLATES_DIR / 'project'

    try:
        # 1. 创建项目根目录
        project_dir.mkdir()

        # 2. 渲染 crawlo.cfg.tmpl
        cfg_template = TEMPLATES_DIR / 'crawlo.cfg.tmpl'
        if cfg_template.exists():
            cfg_content = _render_template(cfg_template, context)
            (project_dir / 'crawlo.cfg').write_text(cfg_content, encoding='utf-8')
            console.print(f":white_check_mark: Created [green]{project_dir / 'crawlo.cfg'}[/green]")
        else:
            console.print("[yellow]⚠ Warning:[/yellow] Template 'crawlo.cfg.tmpl' not found.")

        # 3. 复制并渲染项目包内容
        package_dir = project_dir / project_name
        _copytree_with_templates(template_dir, package_dir, context)
        console.print(f":white_check_mark: Created project package: [green]{package_dir}[/green]")

        # 4. 创建 logs 目录
        (project_dir / 'logs').mkdir(exist_ok=True)
        console.print(":white_check_mark: Created logs directory")

        # 成功面板
        success_text = Text.from_markup(f"Project '[bold cyan]{project_name}[/bold cyan]' created successfully!")
        console.print(Panel(success_text, title=":rocket: Success", border_style="green", padding=(1, 2)))

        # 下一步操作提示（对齐美观 + 语法高亮）
        next_steps = f"""
        [bold]Next steps:[/bold]
        [blue]cd[/blue] {project_name}
        [blue]crawlo genspider[/blue] example example.com
        [blue]crawlo run[/blue] example
        """.strip()
        console.print(next_steps)

        return 0

    except Exception as e:
        console.print(f"[bold red]Error creating project:[/bold red] {e}")
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
            console.print("[red]:cross_mark: Cleaned up partially created project.[/red]")
        return 1
