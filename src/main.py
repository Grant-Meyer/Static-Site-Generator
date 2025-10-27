import sys, os, re, shutil
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path
from textnode import TextType, TextNode
from src.markdown import extract_title
from src.markdown_to_html import markdown_to_html_node


def get_basepath():
    # If a CLI argument is provided, use it; otherwise default to "/"
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "/"


# Paths anchored to project root
ROOT = Path(__file__).resolve().parents[1]
SRC_STATIC = ROOT / "static"
DST_PUBLIC = ROOT / "docs"
CONTENT_DIR = ROOT / "content"
TEMPLATE_PATH = ROOT / "template.html"


def _prefix_basepath(html: str, basepath: str) -> str:
    """Safely rewrite absolute /href and /src with a basepath."""
    # Skip for local dev
    if not basepath or basepath == "/":
        return html

    # Normalize basepath (no trailing slash)
    if not basepath.startswith("/"):
        basepath = "/" + basepath
    basepath = basepath.rstrip("/")

    def repl_href(m):
        path = m.group(1)
        return f'href="{basepath}/{path}"'

    def repl_src(m):
        path = m.group(1)
        return f'src="{basepath}/{path}"'

    html = re.sub(r'href="/([^"]+)"', repl_href, html)
    html = re.sub(r'src="/([^"]+)"', repl_src, html)
    return html


def _clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def _copy_dir(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Source directory does not exist: {src}")
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        d_path = dst / item.name
        if item.is_dir():
            _copy_dir(item, d_path)
        else:
            shutil.copy2(item, d_path)
        print(f"copied {item} -> {d_path}")


def copy_static_to_public(static_dir: Path = SRC_STATIC, public_dir: Path = DST_PUBLIC) -> None:
    _clean_dir(public_dir)
    _copy_dir(static_dir, public_dir)


def generate_page(from_path: Path, template_path: Path, dest_path: Path, basepath="/") -> None:
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")

    markdown_content = from_path.read_text(encoding="utf-8")
    template_html = template_path.read_text(encoding="utf-8")

    html_node = markdown_to_html_node(markdown_content)
    content_html = html_node.to_html()
    title = extract_title(markdown_content)

    final_html = (
        template_html.replace("{{ Title }}", title)
                     .replace("{{ Content }}", content_html)
    )

    # Only rewrite links if basepath != "/"
    final_html = _prefix_basepath(final_html, basepath)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(final_html, encoding="utf-8")


def generate_pages_recursive(content_dir: Path, template_path: Path, dest_dir: Path, basepath="/") -> None:
    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory does not exist: {content_dir}")

    for item in content_dir.iterdir():
        rel = item.relative_to(content_dir)
        out_path = dest_dir / rel

        if item.is_dir():
            generate_pages_recursive(item, template_path, out_path, basepath)
        elif item.is_file() and item.suffix.lower() == ".md":
            dest_file = out_path.with_suffix(".html")
            generate_page(item, template_path, dest_file, basepath)


def main():
    basepath = get_basepath()
    copy_static_to_public()
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, DST_PUBLIC, basepath)


if __name__ == "__main__":
    main()
