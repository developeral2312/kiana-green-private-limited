import os
import re

HOME_HTML = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\public_view\home.html"
HOME_CSS = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\static\css\public_view\home.css"

def revert():
    # Revert HTML
    with open(HOME_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # We want to remove everything from:
    # <!-- =======================
    #    NEW PREMIUM SECTIONS
    # ======================= -->
    # Down to:
    # <!-- Previous Projects Hidden -->
    # <div class="section" id="projects" style="display:none;">
    
    start_marker = "<!-- =======================\n   NEW PREMIUM SECTIONS\n======================= -->"
    end_marker = '<!-- Previous Projects Hidden -->\n<div class="section" id="projects" style="display:none;">'
    
    if start_marker in html and end_marker in html:
        prefix = html.split(start_marker)[0]
        suffix = html.split(end_marker)[1]
        
        # Restore the old services block
        old_services = """
<div class="section" id="services">
    <h1>Our Services</h1>
    <p class="text-muted">Customized Solar Solutions for Every Need</p>
    <div class="card-list">
        <div class="card">
            <img src="/static/images/home.png" class="card-img-top" >
            <div class="card-body">
                <h5 class="card-title">Residential Solar</h5>
                <p class="card-text text-muted">Solar solutions for your home to reduce energy bills.</p>
            </div>
        </div>
        <div class="card">
            <img src="/static/images/com.png" class="card-img-top" >
            <div class="card-body">
                <h5 class="card-title">Commercial Solar</h5>
                <p class="card-text text-muted">Efficient Solar power for business and industries.</p>
            </div>
        </div>
        <div class="card">
            <img src="/static/images/service.jpg" class="card-img-top" >
            <div class="card-body">
                <h5 class="card-title">Solar Maintainance</h5>
                <p class="card-text text-muted">Ongoing support to keep your system running smoothly.</p>
            </div>
        </div>
    </div>
</div>

<div class="section" id="projects">"""
        
        final_html = prefix.rstrip() + "\n\n" + old_services + suffix
        with open(HOME_HTML, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print("Reverted HTML.")
    else:
        print("Could not find markers in HTML.")

    # Revert CSS
    with open(HOME_CSS, 'r', encoding='utf-8') as f:
        css = f.read()
        
    css_marker = "/* =======================\n   PREMIUM ADDED SECTIONS\n======================= */"
    if css_marker in css:
        final_css = css.split(css_marker)[0]
        with open(HOME_CSS, 'w', encoding='utf-8') as f:
            f.write(final_css.rstrip() + "\n")
        print("Reverted CSS.")
    else:
        print("Could not find marker in CSS.")

if __name__ == '__main__':
    revert()
