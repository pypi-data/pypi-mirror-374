import os
import subprocess
from playwright.sync_api import sync_playwright

def md_to_revealjs_html(slide_md, theme: str = "white"):
    # Convert input markdown to pandoc reveal.js html
    result = subprocess.run([
        "pandoc", "-f", "markdown", "-t", "revealjs", "-s", "-V", f"theme={theme}"
    ], input=slide_md , capture_output=True, text=True, check=True)
    return result.stdout

def revealjs_html_to_slide_images(
    html_path: str,
    output_dir: str,
    width: int = 1920,
    height: int = 1080,
    output_pdf: bool = True,
    headless = True,
) -> None:
    """
    Convert a Markdown file into Reveal.js slides and capture each slide as an image using Playwright.

    Steps:
    1. Uses Pandoc to generate an HTML slideshow (Reveal.js) from the Markdown.
    2. Uses headless Chromium via Playwright to load the generated HTML.
    3. Iterates through each slide, takes a full-page screenshot, and saves it as PNG.

    Args:
        md_path: Path to the input Markdown file.
        output_dir: Directory where slide images will be saved.
        theme: Reveal.js theme (e.g., "white", "black", "solarized").
        width: Width of the viewport for screenshots.
        height: Height of the viewport for screenshots.

    Prerequisites:
        - pandoc installed and in PATH
        - playwright installed (`pip install playwright`) and browsers installed (`playwright install`)
        - Internet access if using the default CDN for Reveal.js
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    assert os.path.exists(html_path)

    # 2. Launch headless browser and capture slides
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()

        # Load the generated slideshow
        page.goto(f"file://{os.path.abspath(html_path)}", wait_until="domcontentloaded")
        # Wait for Reveal.js to load and initialize
        page.wait_for_selector(".reveal")
        page.wait_for_function("() => typeof Reveal !== 'undefined' && Reveal.isReady()")

        # Count slides
        slide_count = page.evaluate("() => Reveal.getTotalSlides()")
        
        if output_pdf:
            page.pdf(path=os.path.join(output_dir, f"all.pdf"), print_background=True, width='1920px', height='1080px')

        # Capture each slide
        for i in range(1, slide_count+1):
            # Navigate to slide i
            if i != 1:
                page.evaluate(f"Reveal.next();")

            # Wait for transitions/layout
            page.wait_for_timeout(2000)
            out_path = os.path.join(output_dir, f"{i}.png")
            page.screenshot(path=out_path, full_page=True)
            # print(f"Saved slide {i} to {out_path}")


        if output_pdf:
            # page.emulate_media(media="screen")
            for i in range(1, slide_count+1):
                pdf_path = os.path.join(output_dir, f"{i}.pdf")
                page.pdf(page_ranges = f'{i}', path=pdf_path, print_background=True, width='1920px', height='1080px')

        # import time; time.sleep(999)
        browser.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert Markdown to Reveal.js slides and capture each as an image using Playwright."
    )
    parser.add_argument("md", help="Path to the Markdown file")
    parser.add_argument("outdir", help="Directory to save slide images")
    parser.add_argument("--theme", default="white", help="Reveal.js theme (e.g., white, black, league)")
    args = parser.parse_args()
    
    with open(args.md, 'r') as f:
        input_md_data = f.read()
    
    slide_html = md_to_revealjs_html(input_md_data)
    out_html = f'{args.md}.html'
    with open(out_html, 'w') as f:
        f.write(slide_html)
    revealjs_html_to_slide_images(out_html, args.outdir, theme=args.theme)
