import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import shutil
from pathlib import Path
from textnode import TextType, TextNode
from src.markdown import extract_title
from src.markdown_to_html import markdown_to_html_node

# Paths anchored to project root
ROOT = Path(__file__).resolve().parents[1]
SRC_STATIC = ROOT / "static"
DST_PUBLIC = ROOT / "public"
CONTENT_DIR = ROOT / "content"
TEMPLATE_PATH = ROOT / "template.html"



def _clean_dir(path: Path) -> None:
    # Delete the destination directory entirely for a clean build
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

def _copy_dir(src: Path, dst: Path) -> None:
    # Recursively copy all files/dirs from src to dst, logging each copy
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
    # Clean public/, then recursively copy static/ into it
    _clean_dir(public_dir)
    _copy_dir(static_dir, public_dir)

def main():
    # Copy static files into public
    copy_static_to_public()

    # Generate the site from Markdown + template
    generate_pages_recursive(
        CONTENT_DIR,
        TEMPLATE_PATH,
        DST_PUBLIC
    )


def generate_page(from_path: Path, template_path: Path, dest_path: Path) -> None:
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")
    
    # Read markdown content
    markdown_content = from_path.read_text(encoding="utf-8")

    # Read template HTML
    template_html = template_path.read_text(encoding="utf-8")

    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    content_html = html_node.to_html()

    # Extract title from markdown
    title = extract_title(markdown_content)

    # Replace placeholders in the template
    final_html = (
        template_html.replace("{{ Title }}", title)
                     .replace("{{ Content }}", content_html)
    )

    # Ensure destination directories exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the generated HTML file
    dest_path.write_text(final_html, encoding="utf-8")

def generate_pages_recursive(content_dir: Path, template_path: Path, dest_dir: Path) -> None:
    """
    Walk `content_dir` recursively.
    - For every .md file, generate a matching .html file in `dest_dir`.
    - For directories, recurse and mirror the structure.
    Rules:
      * `foo.md` -> `foo.html`
      * `index.md` in a folder -> `that_folder/index.html`
    """
    if not content_dir.exists():
        raise FileNotFoundError(f"Content directory does not exist: {content_dir}")

    for item in content_dir.iterdir():
        rel = item.relative_to(content_dir)
        out_path = dest_dir / rel

        if item.is_dir():
            # Mirror folder and recurse
            generate_pages_recursive(item, template_path, out_path)
        elif item.is_file() and item.suffix.lower() == ".md":
            # Map .md -> .html (index.md stays index.html)
            if item.stem == "index":
                dest_file = out_path.with_suffix(".html")
            else:
                dest_file = out_path.with_suffix(".html")
            generate_page(item, template_path, dest_file)
        else:
            # Non-markdown content is ignored here (static/ handles assets)
            continue

if __name__ == "__main__":
    main()
