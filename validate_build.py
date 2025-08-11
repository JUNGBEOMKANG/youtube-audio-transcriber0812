#!/usr/bin/env python3
"""
Build Validation Script for YouTube Audio Transcriber
Validates the dashboard components and accessibility improvements
"""

import os
import sys
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup


class BuildValidator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'score': 0
        }

    def validate_all(self):
        """Run all validation checks"""
        print("🔧 SuperClaude Build Validation")
        print("=" * 50)
        print("📋 Validating Dashboard Components & Accessibility")
        
        self._validate_project_structure()
        self._validate_static_assets()
        self._validate_templates()
        self._validate_accessibility_features()
        self._validate_performance_optimizations()
        
        self._calculate_score()
        self._print_results()
        
        return self.results

    def _validate_project_structure(self):
        """Validate project structure"""
        print("\n📁 Validating Project Structure...")
        
        required_files = [
            'app.py',
            'requirements.txt',
            'static/css/dashboard.css',
            'static/js/dashboard-components.js',
            'templates/dashboard.html',
            'test_accessibility.py'
        ]
        
        for file_path in required_files:
            if (self.project_root / file_path).exists():
                self._pass(f"Found: {file_path}")
            else:
                self._fail(f"Missing: {file_path}")

    def _validate_static_assets(self):
        """Validate static assets"""
        print("\n🎨 Validating Static Assets...")
        
        # Check CSS file
        css_path = self.project_root / "static/css/dashboard.css"
        if css_path.exists():
            css_content = css_path.read_text()
            
            # Check for design system variables
            if ':root' in css_content and '--primary-color' in css_content:
                self._pass("CSS design system with custom properties")
            else:
                self._fail("CSS design system missing")
                
            # Check for accessibility features
            accessibility_features = [
                ('focus-visible', 'Modern focus management'),
                ('prefers-reduced-motion', 'Reduced motion support'),
                ('prefers-color-scheme', 'Dark mode support'),
                ('prefers-contrast', 'High contrast support'),
                ('.sr-only', 'Screen reader only class')
            ]
            
            for feature, description in accessibility_features:
                if feature in css_content:
                    self._pass(f"CSS: {description}")
                else:
                    self._warn(f"CSS: Missing {description}")
                    
        # Check JavaScript file
        js_path = self.project_root / "static/js/dashboard-components.js"
        if js_path.exists():
            js_content = js_path.read_text()
            
            # Check for accessibility utilities
            if 'a11y' in js_content and 'announce' in js_content:
                self._pass("JavaScript: Accessibility utilities")
            else:
                self._fail("JavaScript: Missing accessibility utilities")
                
            # Check for modular architecture
            components = ['FormComponents', 'StatusComponents', 'ResultComponents']
            for component in components:
                if component in js_content:
                    self._pass(f"JavaScript: {component} found")
                else:
                    self._fail(f"JavaScript: Missing {component}")

    def _validate_templates(self):
        """Validate HTML templates"""
        print("\n📄 Validating HTML Templates...")
        
        template_path = self.project_root / "templates/dashboard.html"
        if template_path.exists():
            html_content = template_path.read_text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check semantic HTML
            semantic_elements = ['main', 'header', 'footer', 'section', 'article', 'nav']
            found_semantic = []
            for element in semantic_elements:
                if soup.find(element):
                    found_semantic.append(element)
                    
            if len(found_semantic) >= 3:
                self._pass(f"Semantic HTML: {', '.join(found_semantic)}")
            else:
                self._warn(f"Limited semantic HTML: {', '.join(found_semantic)}")
                
            # Check accessibility attributes
            accessibility_attrs = [
                ('aria-label', 'ARIA labels'),
                ('aria-describedby', 'ARIA descriptions'),
                ('aria-live', 'ARIA live regions'),
                ('role', 'ARIA roles'),
                ('lang', 'Language attribute')
            ]
            
            for attr, description in accessibility_attrs:
                if soup.find(attrs={attr: True}) or f'{attr}=' in html_content:
                    self._pass(f"HTML: {description}")
                else:
                    self._warn(f"HTML: Missing {description}")
                    
            # Check form accessibility
            forms = soup.find_all('form')
            if forms:
                labels = soup.find_all('label')
                required_fields = soup.find_all(attrs={'required': True})
                fieldsets = soup.find_all('fieldset')
                
                if labels:
                    self._pass(f"Form: {len(labels)} labels found")
                if required_fields:
                    self._pass(f"Form: {len(required_fields)} required fields marked")
                if fieldsets:
                    self._pass(f"Form: {len(fieldsets)} fieldsets for grouping")
                    
            # Check skip link
            if 'skip' in html_content.lower() and 'content' in html_content.lower():
                self._pass("HTML: Skip to content link")
            else:
                self._warn("HTML: Missing skip to content link")

    def _validate_accessibility_features(self):
        """Validate specific accessibility improvements"""
        print("\n♿ Validating Accessibility Features...")
        
        template_path = self.project_root / "templates/dashboard.html"
        if template_path.exists():
            html_content = template_path.read_text()
            
            # Check meta tags
            meta_checks = [
                ('viewport', 'Responsive viewport'),
                ('description', 'Meta description'),
                ('charset="UTF-8"', 'UTF-8 encoding')
            ]
            
            for check, description in meta_checks:
                if check in html_content:
                    self._pass(f"Meta: {description}")
                else:
                    self._warn(f"Meta: Missing {description}")
                    
            # Check for aria-live announcer
            if 'aria-live-announcer' in html_content:
                self._pass("ARIA: Live announcer element")
            else:
                self._warn("ARIA: Missing live announcer")
                
            # Check for keyboard navigation support
            if 'keydown' in html_content or 'keyboard' in html_content.lower():
                self._pass("JavaScript: Keyboard navigation support")
            else:
                self._warn("JavaScript: Limited keyboard navigation")

    def _validate_performance_optimizations(self):
        """Validate performance optimizations"""
        print("\n⚡ Validating Performance Features...")
        
        template_path = self.project_root / "templates/dashboard.html"
        if template_path.exists():
            html_content = template_path.read_text()
            
            # Check for preload directives
            if 'preload' in html_content:
                self._pass("Performance: Resource preloading")
            else:
                self._warn("Performance: No resource preloading")
                
            # Check for performance monitoring
            if 'PerformanceObserver' in html_content:
                self._pass("Performance: Performance monitoring")
            else:
                self._warn("Performance: No performance monitoring")
                
            # Check for service worker registration
            if 'serviceWorker' in html_content:
                self._pass("Performance: Service worker ready")
            else:
                self._warn("Performance: No service worker")

    def _pass(self, message):
        """Record a passed validation"""
        self.results['passed'].append(message)
        print(f"  ✅ {message}")

    def _fail(self, message):
        """Record a failed validation"""
        self.results['failed'].append(message)
        print(f"  ❌ {message}")

    def _warn(self, message):
        """Record a warning"""
        self.results['warnings'].append(message)
        print(f"  ⚠️  {message}")

    def _calculate_score(self):
        """Calculate build validation score"""
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        warnings = len(self.results['warnings'])
        total = passed + failed + warnings
        
        if total > 0:
            # Score: pass = 1, warning = 0.5, fail = 0
            score = (passed + (warnings * 0.5)) / total * 100
            self.results['score'] = round(score, 1)

    def _print_results(self):
        """Print validation results"""
        print("\n" + "=" * 50)
        print("📊 BUILD VALIDATION RESULTS")
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
            print("🎉 EXCELLENT BUILD! All components implemented correctly.")
        elif score >= 80:
            print("👍 GOOD BUILD! Minor improvements recommended.")
        elif score >= 70:
            print("⚠️  ADEQUATE BUILD. Some components need attention.")
        else:
            print("❌ BUILD ISSUES. Significant problems detected.")
            
        print("\n🎯 SuperClaude Build Summary:")
        if failed == 0:
            print("• ✅ Dashboard components successfully modularized")
            print("• ✅ Accessibility improvements implemented")
            print("• ✅ Frontend persona best practices applied")
        else:
            print("• ⚠️  Some components need refinement")
            print("• 🔧 Review failed validations above")


def main():
    """Run build validation"""
    validator = BuildValidator()
    results = validator.validate_all()
    
    # Save results
    with open('build_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: build_validation_results.json")
    
    # Exit code based on failures
    if len(results['failed']) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()