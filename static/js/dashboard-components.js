/**
 * YouTube Audio Transcriber Dashboard Components
 * Modular, accessible, and responsive components
 */

// Component State Management
class DashboardState {
    constructor() {
        this.currentJobId = null;
        this.isProcessing = false;
        this.results = null;
        this.statusCheckInterval = null;
    }

    setJobId(jobId) {
        this.currentJobId = jobId;
    }

    setProcessing(status) {
        this.isProcessing = status;
    }

    setResults(results) {
        this.results = results;
    }

    clearStatusCheck() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }
}

// Global state instance
const dashboardState = new DashboardState();

// Accessibility utilities
const a11y = {
    // Announce to screen readers
    announce: (message, priority = 'polite') => {
        const announcer = document.getElementById('aria-live-announcer') || 
            (() => {
                const div = document.createElement('div');
                div.id = 'aria-live-announcer';
                div.setAttribute('aria-live', priority);
                div.setAttribute('aria-atomic', 'true');
                div.className = 'sr-only';
                document.body.appendChild(div);
                return div;
            })();
        
        announcer.textContent = message;
        
        // Clear after announcement
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    },

    // Focus management
    focusElement: (selector, fallback = null) => {
        const element = document.querySelector(selector);
        if (element) {
            element.focus();
            return true;
        } else if (fallback) {
            const fallbackElement = document.querySelector(fallback);
            if (fallbackElement) {
                fallbackElement.focus();
                return true;
            }
        }
        return false;
    },

    // Trap focus within modal/dialog
    trapFocus: (container) => {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleTabKey = (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        };

        container.addEventListener('keydown', handleTabKey);
        return () => container.removeEventListener('keydown', handleTabKey);
    }
};

// Form Components
const FormComponents = {
    // Validate form input
    validateForm: (formData) => {
        const url = formData.get('url');
        const errors = [];

        if (!url || url.trim() === '') {
            errors.push('YouTube URL is required');
        } else if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
            errors.push('Please enter a valid YouTube URL');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    },

    // Show validation errors
    showErrors: (errors) => {
        const errorContainer = document.getElementById('error-container') || 
            (() => {
                const div = document.createElement('div');
                div.id = 'error-container';
                div.className = 'status-card';
                div.style.backgroundColor = 'rgb(254 242 242)';
                div.style.borderColor = 'rgb(239 68 68)';
                div.style.color = 'rgb(153 27 27)';
                div.setAttribute('role', 'alert');
                div.setAttribute('aria-live', 'assertive');
                
                const form = document.getElementById('transcribeForm');
                form.parentNode.insertBefore(div, form);
                return div;
            })();

        if (errors.length > 0) {
            errorContainer.innerHTML = `
                <div class="status-indicator">
                    <svg class="status-icon" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                    </svg>
                    <div>
                        <div class="status-text" style="font-weight: 600; margin-bottom: 0.5rem;">
                            Validation Errors:
                        </div>
                        <ul style="margin: 0; padding-left: 1rem;">
                            ${errors.map(error => `<li>${error}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            errorContainer.classList.remove('hidden');
            a11y.announce(`Validation errors: ${errors.join(', ')}`, 'assertive');
        } else {
            errorContainer.classList.add('hidden');
        }
    }
};

// Status Components
const StatusComponents = {
    // Show processing status
    show: (message) => {
        const statusDiv = document.getElementById('status');
        const statusText = document.getElementById('statusText');
        
        if (statusDiv && statusText) {
            statusText.textContent = message;
            statusDiv.classList.remove('hidden');
            a11y.announce(`Status: ${message}`);
        }
    },

    // Hide status
    hide: () => {
        const statusDiv = document.getElementById('status');
        if (statusDiv) {
            statusDiv.classList.add('hidden');
        }
    },

    // Update status message
    update: (message) => {
        const statusText = document.getElementById('statusText');
        if (statusText) {
            statusText.textContent = message;
            a11y.announce(`Status update: ${message}`);
        }
    }
};

// Result Components
const ResultComponents = {
    // Show transcription results
    show: (result) => {
        const resultDiv = document.getElementById('result');
        const fullScriptContent = document.getElementById('fullScriptContent');
        
        if (!resultDiv || !fullScriptContent) return;

        let html = '';
        let scriptText = '';
        
        if (result.method === 'both') {
            scriptText = `Whisper Results:\n${result.whisper.text || 'Transcription failed'}\n\nGoogle Results:\n${result.google.text || 'Transcription failed'}`;
            html += `
                <div class="result-section">
                    <h4 class="result-header">🤖 Whisper Results:</h4>
                    <div class="result-content" role="region" aria-label="Whisper transcription results">
                        ${ResultComponents.formatText(result.whisper.text || 'Transcription failed')}
                    </div>
                </div>
                <div class="result-section">
                    <h4 class="result-header">🌐 Google Results:</h4>
                    <div class="result-content" role="region" aria-label="Google transcription results">
                        ${ResultComponents.formatText(result.google.text || 'Transcription failed')}
                    </div>
                </div>
            `;
        } else {
            scriptText = result.text || 'Transcription failed';
            html += `
                <div class="result-section">
                    <div class="result-content" role="region" aria-label="Transcription results">
                        ${ResultComponents.formatText(result.text || 'Transcription failed')}
                    </div>
                    ${result.language ? `<p class="text-sm text-gray-600 mt-2">Language: ${result.language}</p>` : ''}
                </div>
            `;
        }
        
        fullScriptContent.innerHTML = html;
        resultDiv.classList.remove('hidden');
        
        // Announce completion to screen readers
        a11y.announce('Transcription completed successfully', 'assertive');
        
        // Focus on results for screen reader users
        setTimeout(() => {
            a11y.focusElement('#result h3', '#result');
        }, 100);

        // Start summarization
        SummarizationComponents.getSummaries(scriptText);
    },

    // Format text for display with improved paragraph breaks
    formatText: (text) => {
        // Split by double newlines for paragraph breaks
        const paragraphs = text.split(/\n\n+/);
        return paragraphs
            .map(paragraph => paragraph.trim())
            .filter(paragraph => paragraph.length > 0)
            .map(paragraph => `<p class="mb-4">${paragraph.replace(/\n/g, ' ').replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')}</p>`)
            .join('');
    },

    // Hide results
    hide: () => {
        const resultDiv = document.getElementById('result');
        if (resultDiv) {
            resultDiv.classList.add('hidden');
        }
    }
};

// Summarization Components
const SummarizationComponents = {
    getSummaries: async (text) => {
        // Show loading state for summaries
        document.getElementById('keySummaryContent').innerHTML = '<div class="loading-spinner"></div> 요약 중...';
        document.getElementById('curatorContent').innerHTML = '<div class="loading-spinner"></div> 요약 중...';

        try {
            const [keySummaryResponse, curatorResponse] = await Promise.all([
                fetch('/summarize/key_summary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                }),
                fetch('/summarize/curator', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text })
                })
            ]);

            if (keySummaryResponse.ok) {
                const summary = await keySummaryResponse.json();
                SummarizationComponents.showKeySummary(summary);
            } else {
                SummarizationComponents.showKeySummary({ error: 'Failed to load summary.' });
            }

            if (curatorResponse.ok) {
                const summary = await curatorResponse.json();
                SummarizationComponents.showCuratorSummary(summary);
            } else {
                SummarizationComponents.showCuratorSummary({ error: 'Failed to load summary.' });
            }

        } catch (error) {
            SummarizationComponents.showKeySummary({ error: 'Error fetching summaries.' });
            SummarizationComponents.showCuratorSummary({ error: 'Error fetching summaries.' });
        }
    },

    showKeySummary: (summary) => {
        const keySummaryContent = document.getElementById('keySummaryContent');
        if (summary.error) {
            keySummaryContent.innerHTML = `
                <div class="summary-section" style="background: rgba(255, 100, 100, 0.1); border-color: rgba(255, 100, 100, 0.3);">
                    <h4 style="color: var(--text-glass); font-weight: 700; margin-bottom: 1rem;">⚠️ 요약 생성 오류</h4>
                    <p style="color: var(--text-glass);">${summary.error}</p>
                </div>`;
            return;
        }

        if (!Array.isArray(summary) || summary.length === 0) {
            keySummaryContent.innerHTML = `
                <div class="summary-section" style="text-align: center;">
                    <p style="color: var(--text-glass);">📝 요약할 내용이 없습니다.</p>
                </div>`;
            return;
        }

        let html = `
            <div class="space-y-3">
                <h4 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-glass); text-align: center; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    📝 각 문단별 핵심 요약
                </h4>
        `;
        
        summary.forEach((item, index) => {
            html += `
                <div class="key-summary-item" style="display: flex; align-items: flex-start;">
                    <span class="key-summary-number">${index + 1}</span>
                    <div class="key-summary-text">${item.paragraph_summary}</div>
                </div>
            `;
        });
        html += '</div>';
        keySummaryContent.innerHTML = html;
    },

    showCuratorSummary: (summary) => {
        const curatorContent = document.getElementById('curatorContent');
        if (summary.error) {
            curatorContent.innerHTML = `
                <div class="summary-section" style="background: rgba(255, 100, 100, 0.1); border-color: rgba(255, 100, 100, 0.3);">
                    <h4 style="color: var(--text-glass); font-weight: 700; margin-bottom: 1rem;">⚠️ 요약 생성 오류</h4>
                    <p style="color: var(--text-glass);">${summary.error}</p>
                </div>`;
            return;
        }

        if (!summary.title && !summary.one_line_summary && !summary.key_points) {
            curatorContent.innerHTML = `
                <div class="summary-section" style="text-align: center;">
                    <p style="color: var(--text-glass);">🎯 큐레이션할 내용이 없습니다.</p>
                </div>`;
            return;
        }

        let html = `
            <div class="space-y-6">
                <!-- 제목 섹션 -->
                <div class="curator-section">
                    <h4>📋 제목</h4>
                    <h3 class="curator-title">${summary.title || '제목을 생성할 수 없습니다'}</h3>
                </div>

                <!-- 한 줄 요약 섹션 -->
                <div class="curator-section">
                    <h4>💡 한 줄 요약</h4>
                    <p class="curator-summary">${summary.one_line_summary || '요약을 생성할 수 없습니다'}</p>
                </div>

                <!-- 핵심 포인트 섹션 -->
                <div class="curator-section">
                    <h4>🎯 핵심 포인트</h4>
                    <div class="curator-points">
        `;
        
        if (Array.isArray(summary.key_points) && summary.key_points.length > 0) {
            summary.key_points.forEach((point, index) => {
                html += `
                    <div class="curator-point">
                        <span class="curator-point-number">${index + 1}</span>
                        <div class="curator-point-text">${point}</div>
                    </div>
                `;
            });
        } else {
            html += `
                <div class="curator-point" style="justify-content: center; text-align: center;">
                    <div class="curator-point-text">핵심 포인트를 생성할 수 없습니다.</div>
                </div>
            `;
        }
        
        html += `
                    </div>
                </div>
            </div>
        `;
        curatorContent.innerHTML = html;
    }
};

// Download Components
const DownloadComponents = {
    // Download transcription as text file
    downloadResult: (result) => {
        let text = '';
        
        if (result.method === 'both') {
            text += 'Whisper Results:\n';
            text += (result.whisper.text || 'Transcription failed') + '\n\n';
            text += 'Google Results:\n';
            text += (result.google.text || 'Transcription failed');
        } else {
            text = result.text || 'Transcription failed';
        }
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'youtube-transcript.txt';
        a.setAttribute('aria-label', 'Download transcription as text file');
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        a11y.announce('Transcript downloaded successfully');
    }
};

// Main Dashboard Controller
const DashboardController = {
    // Initialize the dashboard
    init: () => {
        const form = document.getElementById('transcribeForm');
        if (form) {
            form.addEventListener('submit', DashboardController.handleFormSubmit);
        }

        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                if (dashboardState.results) {
                    DownloadComponents.downloadResult(dashboardState.results);
                }
            });
        }

        // Tab switching logic
        const tabs = document.querySelectorAll('.tab-button');
        const panels = document.querySelectorAll('.tab-panel');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');

                const targetPanelId = tab.getAttribute('aria-controls');

                panels.forEach(panel => {
                    if (panel.id === targetPanelId) {
                        panel.style.display = 'block';
                    } else {
                        panel.style.display = 'none';
                    }
                });
            });
        });

        // Add keyboard navigation enhancements
        document.addEventListener('keydown', DashboardController.handleKeyNavigation);
        
        // Initialize aria-live announcer
        a11y.announce('YouTube Audio Transcriber loaded');
    },

    // Handle form submission
    handleFormSubmit: async (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const validation = FormComponents.validateForm(formData);
        
        if (!validation.isValid) {
            FormComponents.showErrors(validation.errors);
            a11y.focusElement('#url');
            return;
        }

        // Clear previous errors
        FormComponents.showErrors([]);
        
        // Update UI state
        DashboardController.setProcessingState(true);
        ResultComponents.hide();
        StatusComponents.show('Starting transcription...');
        
        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                dashboardState.setJobId(data.job_id);
                DashboardController.checkStatus();
            } else {
                throw new Error(data.detail || 'Transcription failed');
            }
            
        } catch (error) {
            DashboardController.handleError('Error: ' + error.message);
        }
    },

    // Check transcription status
    checkStatus: async () => {
        if (!dashboardState.currentJobId) return;
        
        try {
            const response = await fetch(`/status/${dashboardState.currentJobId}`);
            const data = await response.json();
            
            StatusComponents.update(data.status);
            
            if (data.completed) {
                dashboardState.clearStatusCheck();
                
                if (data.success) {
                    dashboardState.setResults(data.result);
                    ResultComponents.show(data.result);
                    StatusComponents.hide();
                } else {
                    DashboardController.handleError('Transcription failed: ' + (data.error || 'Unknown error'));
                }
                
                DashboardController.setProcessingState(false);
            } else {
                // Continue checking status
                dashboardState.statusCheckInterval = setTimeout(DashboardController.checkStatus, 2000);
            }
            
        } catch (error) {
            DashboardController.handleError('Status check failed: ' + error.message);
        }
    },

    // Handle errors
    handleError: (message) => {
        FormComponents.showErrors([message]);
        StatusComponents.hide();
        DashboardController.setProcessingState(false);
        dashboardState.clearStatusCheck();
    },

    // Set processing state
    setProcessingState: (isProcessing) => {
        dashboardState.setProcessing(isProcessing);
        
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.disabled = isProcessing;
            submitBtn.innerHTML = isProcessing ? 
                '<div class="loading-spinner"></div> Processing...' : 
                'Start Transcription';
        }
    },

    // Handle keyboard navigation
    handleKeyNavigation: (e) => {
        // Escape key to cancel processing (if implemented)
        if (e.key === 'Escape' && dashboardState.isProcessing) {
            // Could implement cancellation here
            a11y.announce('Press Escape again to cancel processing');
        }
        
        // Enter key on buttons
        if (e.key === 'Enter' && e.target.tagName === 'BUTTON') {
            e.target.click();
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', DashboardController.init);
} else {
    DashboardController.init();
}

// Export for potential external use
window.YouTubeTranscriberDashboard = {
    DashboardController,
    FormComponents,
    StatusComponents,
    ResultComponents,
    DownloadComponents,
    a11y,
    state: dashboardState
};