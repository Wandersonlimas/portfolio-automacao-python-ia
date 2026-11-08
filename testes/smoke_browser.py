"""Smoke test funcional em Chromium, incluindo filtros, navegação e viewport móvel."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/'index.html').as_uri()

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        errors=[]
        page=browser.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(URL,wait_until='load')
        page.locator('body').wait_for(state='visible')
        page.wait_for_timeout(350)
        assert page.locator('button[data-tab="gerencial"]').count()==1
        page.locator('#fMonth').select_option(index=1)
        page.locator('#fChannel').select_option(index=1)
        page.locator('#clearFilters').click()
        for tab in ('operacional','engenharia','gerencial'):
            target=page.locator('button[data-tab="'+tab+'"]')
            target.click()
            assert 'active' in target.get_attribute('class')
        page.set_viewport_size({'width':390,'height':844})
        page.locator('#fMonth').select_option(index=1)

        assert not errors,'Erros de JavaScript: '+repr(errors)
        browser.close()
        print('OK: navegação, filtros e responsividade testados com Chromium')

if __name__=='__main__':
    run()
