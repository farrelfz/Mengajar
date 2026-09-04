"""
KIR AI Document Intelligence — Playwright PDF Export.
"""
from pathlib import Path
from playwright.async_api import async_playwright


class PlaywrightRenderer:
    def __init__(self):
        pass
        
    async def export_pdf(
        self, 
        html_path: Path, 
        output_pdf: Path, 
        is_landscape: bool = False, 
        format: str = "A4",
        width: str | None = None,
        height: str | None = None,
    ) -> bool:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            page = await browser.new_page()
            
            # Use absolute file path URL
            file_url = f"file://{html_path.absolute()}"
            await page.goto(file_url, wait_until="networkidle")
            
            # Determine dimensions or format
            if format == "16:9" or (width and height):
                await page.pdf(
                    path=str(output_pdf),
                    width=width or "13.333in",
                    height=height or "7.5in",
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
                )
            else:
                await page.pdf(
                    path=str(output_pdf),
                    format=format,
                    landscape=is_landscape,
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
                )
                
            await browser.close()
        return True
