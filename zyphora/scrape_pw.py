from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('https://www.kianagreen.com/about', wait_until='networkidle')
        images = page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('img')).map(img => img.src);
            const bgImgs = Array.from(document.querySelectorAll('*')).map(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none' && bg.includes('url')) {
                    return bg.replace(/^url\\(['"]?/, '').replace(/['"]?\\)$/, '');
                }
                return null;
            }).filter(Boolean);
            return imgs.concat(bgImgs);
        }''')
        
        print("Images found:")
        for img in set(images):
            print(img)
            
        browser.close()

if __name__ == '__main__':
    run()
