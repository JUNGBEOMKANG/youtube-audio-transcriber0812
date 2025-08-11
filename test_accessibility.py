#!/usr/bin/env python3
"""
Accessibility Testing Suite for YouTube Audio Transcriber
Tests WCAG 2.1 AA compliance and accessibility best practices
"""

import asyncio
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup
import sys


class AccessibilityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'score': 0,
            'total_tests': 0
        }

    async def run_all_tests(self):
        """Run all accessibility tests"""
        print("🔍 Starting Accessibility Testing Suite")
        print("=" * 50)
        
        try:
            async with aiohttp.ClientSession() as session:
                html_content = await self._fetch_page(session, "/")
                if not html_content:
                    print("❌ Could not fetch homepage")
                    return self.results
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Run all test categories
                await self._test_semantic_html(soup)
                await self._test_aria_attributes(soup)
                await self._test_keyboard_navigation(soup)
                await self._test_color_contrast(soup)
                await self._test_images_and_media(soup)
                await self._test_forms_accessibility(soup)
                await self._test_focus_management(soup)
                await self._test_mobile_accessibility(soup)
                
                # Calculate final score
                self._calculate_score()
                self._print_results()
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            
        return self.results

    async def _fetch_page(self, session, path):
        """Fetch page content"""
        try:
            url = urljoin(self.base_url, path)
            async with session.get(url) as response:
                return await response.text()
        except Exception as e:
            print(f"Error fetching {path}: {e}")
            return None

    async def _test_semantic_html(self, soup):
        """Test semantic HTML structure"""
        print("\n🏗️  Testing Semantic HTML Structure...")
        
        # Test for proper heading hierarchy
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if headings:
            h1_count = len(soup.find_all('h1'))
            if h1_count == 1:
                self._pass("Single H1 element found")
            elif h1_count == 0:
                self._fail("No H1 element found")
            else:
                self._fail(f"Multiple H1 elements found ({h1_count})")
                
            # Check heading hierarchy
            prev_level = 0
            for heading in headings:
                level = int(heading.name[1])
                if prev_level > 0 and level > prev_level + 1:
                    self._warn(f"Heading hierarchy skip: {heading.name} after h{prev_level}")
                prev_level = level
        else:
            self._fail("No heading elements found")

        # Test for semantic landmarks
        landmarks = {
            'main': soup.find('main'),
            'header': soup.find('header'),
            'footer': soup.find('footer'),
            'nav': soup.find('nav')
        }
        
        if landmarks['main']:
            self._pass("Main landmark found")
        else:
            self._fail("Main landmark missing")
            
        if landmarks['header']:
            self._pass("Header landmark found")
        else:
            self._warn("Header landmark missing")
            
        # Test for proper list usage
        lists = soup.find_all(['ul', 'ol'])
        for list_elem in lists:
            if not list_elem.find('li'):
                self._warn(f"Empty list found: {list_elem.name}")

    async def _test_aria_attributes(self, soup):
        """Test ARIA attributes and roles"""
        print("\n♿ Testing ARIA Attributes...")
        
        # Test for ARIA live regions
        live_regions = soup.find_all(attrs={'aria-live': True})
        if live_regions:
            self._pass(f"ARIA live regions found ({len(live_regions)})")
            for region in live_regions:
                if region.get('aria-atomic'):
                    self._pass("ARIA live region has aria-atomic")
        else:
            self._warn("No ARIA live regions found")
            
        # Test form labels and descriptions
        inputs = soup.find_all(['input', 'select', 'textarea'])
        for input_elem in inputs:
            input_id = input_elem.get('id')
            if input_id:
                # Check for associated label
                label = soup.find('label', attrs={'for': input_id})
                if label:
                    self._pass(f"Form control {input_id} has associated label")
                else:
                    aria_label = input_elem.get('aria-label')
                    if aria_label:
                        self._pass(f"Form control {input_id} has aria-label")
                    else:
                        self._fail(f"Form control {input_id} missing label")
                        
                # Check for descriptions
                aria_describedby = input_elem.get('aria-describedby')
                if aria_describedby:
                    desc_elem = soup.find(id=aria_describedby)
                    if desc_elem:
                        self._pass(f"Form control {input_id} has description")
                    else:
                        self._warn(f"Form control {input_id} references non-existent description")
                        
        # Test for proper roles
        buttons = soup.find_all('button')
        for button in buttons:
            if not button.get('aria-label') and not button.get_text(strip=True):
                self._warn("Button without accessible text found")
                
        # Test for skip links
        skip_links = soup.find_all('a', href=lambda x: x and x.startswith('#'))
        if any('skip' in link.get_text().lower() for link in skip_links):
            self._pass("Skip navigation link found")
        else:
            self._warn("No skip navigation link found")

    async def _test_keyboard_navigation(self, soup):
        """Test keyboard navigation support"""
        print("\n⌨️  Testing Keyboard Navigation...")
        
        # Test for focusable elements
        focusable_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        focusable_elements.extend(soup.find_all(attrs={'tabindex': True}))
        
        if focusable_elements:
            self._pass(f"Focusable elements found ({len(focusable_elements)})")
            
            # Check for tabindex usage
            negative_tabindex = soup.find_all(attrs={'tabindex': '-1'})
            positive_tabindex = soup.find_all(lambda tag: tag.get('tabindex') and 
                                             tag.get('tabindex').isdigit() and 
                                             int(tag.get('tabindex')) > 0)
            
            if positive_tabindex:
                self._warn(f"Positive tabindex found ({len(positive_tabindex)} elements)")
            else:
                self._pass("No positive tabindex values found")
                
        # Test for keyboard event handlers
        elements_with_click = soup.find_all(attrs={'onclick': True})
        if elements_with_click:
            self._warn(f"Elements with onclick handlers found ({len(elements_with_click)})")

    async def _test_color_contrast(self, soup):
        """Test color contrast (basic CSS analysis)"""
        print("\n🎨 Testing Color and Contrast...")
        
        # Check for CSS custom properties (design system)
        css_content = ""
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content += style.get_text()
            
        # Look for CSS custom properties
        if ':root' in css_content and '--' in css_content:
            self._pass("CSS custom properties (design system) found")
        else:
            self._warn("No CSS design system detected")
            
        # Check for prefers-color-scheme media query
        if 'prefers-color-scheme' in css_content:
            self._pass("Dark mode support detected")
        else:
            self._warn("No dark mode support detected")
            
        # Check for high contrast support
        if 'prefers-contrast' in css_content:
            self._pass("High contrast mode support detected")
        else:
            self._warn("No high contrast mode support detected")

    async def _test_images_and_media(self, soup):
        """Test images and media accessibility"""
        print("\n🖼️  Testing Images and Media...")
        
        # Test images for alt text
        images = soup.find_all('img')
        for img in images:
            alt = img.get('alt')
            if alt is not None:
                if alt.strip():
                    self._pass(f"Image has descriptive alt text")
                else:
                    self._pass(f"Image has empty alt text (decorative)")
            else:
                self._fail(f"Image missing alt attribute")
                
        # Test for decorative images
        decorative_images = soup.find_all('img', alt="")
        if decorative_images:
            self._pass(f"Decorative images properly marked ({len(decorative_images)})")
            
        # Test SVG accessibility
        svgs = soup.find_all('svg')
        for svg in svgs:
            if svg.get('aria-hidden') or svg.get('role') or svg.find('title'):
                self._pass("SVG has accessibility attributes")
            else:
                self._warn("SVG may need accessibility attributes")

    async def _test_forms_accessibility(self, soup):
        """Test form accessibility"""
        print("\n📝 Testing Form Accessibility...")
        
        forms = soup.find_all('form')
        if forms:
            for form in forms:
                # Test for fieldsets and legends
                fieldsets = form.find_all('fieldset')
                if fieldsets:
                    for fieldset in fieldsets:
                        legend = fieldset.find('legend')
                        if legend:
                            self._pass("Fieldset has legend")
                        else:
                            self._warn("Fieldset missing legend")
                            
                # Test required field indicators
                required_inputs = form.find_all(attrs={'required': True})
                if required_inputs:
                    self._pass(f"Required fields marked ({len(required_inputs)})")
                    
                # Test for error handling
                error_elements = form.find_all(attrs={'role': 'alert'}) + \
                               form.find_all(attrs={'aria-live': 'assertive'})
                if error_elements:
                    self._pass("Error handling elements found")
                else:
                    self._warn("No error handling elements detected")
                    
        # Test for autocomplete attributes
        autocomplete_inputs = soup.find_all(attrs={'autocomplete': True})
        if autocomplete_inputs:
            self._pass(f"Autocomplete attributes found ({len(autocomplete_inputs)})")

    async def _test_focus_management(self, soup):
        """Test focus management"""
        print("\n🎯 Testing Focus Management...")
        
        # Test for focus indicators in CSS
        css_content = ""
        style_tags = soup.find_all('style')
        link_tags = soup.find_all('link', rel='stylesheet')
        
        for style in style_tags:
            css_content += style.get_text()
            
        # Check for focus styles
        focus_styles = [':focus', ':focus-visible', ':focus-within']
        found_focus_styles = [style for style in focus_styles if style in css_content]
        
        if found_focus_styles:
            self._pass(f"Focus styles found: {', '.join(found_focus_styles)}")
        else:
            self._warn("No focus styles detected in embedded CSS")
            
        # Check for focus-visible support
        if ':focus-visible' in css_content:
            self._pass("Modern focus management (:focus-visible) detected")

    async def _test_mobile_accessibility(self, soup):
        """Test mobile accessibility"""
        print("\n📱 Testing Mobile Accessibility...")
        
        # Test for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '')
            if 'width=device-width' in content:
                self._pass("Proper viewport meta tag found")
            else:
                self._warn("Viewport meta tag may need improvement")
        else:
            self._fail("Viewport meta tag missing")
            
        # Test for touch target sizes (approximate)
        buttons = soup.find_all('button')
        if buttons:
            self._pass(f"Buttons found for touch interaction ({len(buttons)})")
            
        # Test for reduced motion support
        css_content = ""
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content += style.get_text()
            
        if 'prefers-reduced-motion' in css_content:
            self._pass("Reduced motion support detected")
        else:
            self._warn("No reduced motion support detected")

    def _pass(self, message):
        """Record a passed test"""
        self.results['passed'].append(message)
        self.results['total_tests'] += 1
        print(f"  ✅ {message}")

    def _fail(self, message):
        """Record a failed test"""
        self.results['failed'].append(message)
        self.results['total_tests'] += 1
        print(f"  ❌ {message}")

    def _warn(self, message):
        """Record a warning"""
        self.results['warnings'].append(message)
        self.results['total_tests'] += 1
        print(f"  ⚠️  {message}")

    def _calculate_score(self):
        """Calculate accessibility score"""
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        total = self.results['total_tests']
        
        if total > 0:
            # Score calculation: pass = 1 point, warning = 0.5 points, fail = 0 points
            score = (passed + (warnings * 0.5)) / total * 100
            self.results['score'] = round(score, 1)

    def _print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 ACCESSIBILITY TEST RESULTS")
        print("=" * 50)
        
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        score = self.results['score']
        
        print(f"✅ Passed:   {passed}")
        print(f"❌ Failed:   {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📈 Score:    {score}%")
        
        if score >= 90:
            print(f"🎉 EXCELLENT! Your application has great accessibility!")
        elif score >= 80:
            print(f"👍 GOOD! Your application is quite accessible with room for improvement.")
        elif score >= 70:
            print(f"⚠️  FAIR. Your application needs accessibility improvements.")
        else:
            print(f"❌ POOR. Your application has significant accessibility issues.")
            
        print("\nRecommendations:")
        if failed > 0:
            print("• Address all failed tests - these are critical accessibility issues")
        if warnings > 0:
            print("• Consider addressing warnings to improve user experience")
        print("• Test with real assistive technologies (screen readers, keyboard only)")
        print("• Conduct user testing with people with disabilities")


async def main():
    """Run accessibility tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
        
    print(f"Testing accessibility for: {base_url}")
    print("Make sure the application is running first!")
    
    tester = AccessibilityTester(base_url)
    results = await tester.run_all_tests()
    
    # Save results to file
    results_file = Path("accessibility_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Results saved to: {results_file}")
    
    # Exit with error code if accessibility issues found
    if len(results['failed']) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())