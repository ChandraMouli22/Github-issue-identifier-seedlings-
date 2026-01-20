document.addEventListener('DOMContentLoaded', () => {

    // UI References
    const form = document.getElementById('analyze-form');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultContainer = document.getElementById('result-container');
    const errorContainer = document.getElementById('error-container');

    // Modal References
    const aboutModal = document.getElementById('aboutModal');
    const aboutLink = document.getElementById('aboutLink');
    const closeModal = document.getElementById('closeModal');
    const homeLink = document.getElementById('homeLink');

    // Progress Indicator
    const progressIndicator = document.getElementById('progressIndicator');

    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const sunIcon = themeToggle.querySelector('.sun-icon');
    const moonIcon = themeToggle.querySelector('.moon-icon');

    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);

    // Download References
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadMenu = document.getElementById('downloadMenu');
    const downloadMarkdown = document.getElementById('downloadMarkdown');
    const downloadPDF = document.getElementById('downloadPDF');
    let currentAnalysisData = null;

    // Output References
    const jsonOutput = document.getElementById('json-output');
    const displaySummary = document.getElementById('display-summary');
    const displayImpact = document.getElementById('display-impact');
    const displayLabels = document.getElementById('display-labels');
    const badgeType = document.getElementById('badge-type');
    const badgePriority = document.getElementById('badge-priority');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        setLoading(true);
        setProgressStep(1); // Start: Fetching Issue

        const repoUrl = document.getElementById('repoUrl').value;
        const issueNumber = document.getElementById('issueNumber').value;

        try {
            // Step 1: Fetching
            setProgressStep(1);

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ repoUrl, issueNumber })
            });

            // Step 2: Analyzing
            setProgressStep(2);

            const data = await response.json();

            if (!response.ok) throw new Error(data.detail || data.error || 'Request failed');

            // Step 3: Complete
            setProgressStep(3);

            setTimeout(() => {
                renderData(data);
                setProgressStep(0); // Hide progress
            }, 500);

        } catch (err) {
            errorContainer.textContent = err.message;
            errorContainer.classList.remove('hidden');
        } finally {
            setLoading(false);
        }
    });

    document.getElementById('copyBtn').addEventListener('click', (e) => {
        navigator.clipboard.writeText(jsonOutput.textContent);
        const originalText = e.target.textContent;
        e.target.textContent = 'Copied!';
        setTimeout(() => e.target.textContent = originalText, 2000);
    });

    function renderData(data) {
        // Store data for exports
        currentAnalysisData = data;

        // 1. JSON
        jsonOutput.textContent = JSON.stringify(data, null, 2);

        // 2. Human Readable
        displaySummary.textContent = data.summary || "No summary provided.";
        displayImpact.textContent = data.potential_impact || "No impact analysis provided.";
        badgeType.textContent = data.type || "Issue";
        badgePriority.textContent = data.priority_score || "Normal";

        // Populate metadata under Impact Assessment
        const displayType = document.getElementById('display-type');
        const displayPriority = document.getElementById('display-priority');
        if (displayType) displayType.textContent = data.type || "N/A";
        if (displayPriority) displayPriority.textContent = data.priority_score || "N/A";

        displayLabels.innerHTML = '';
        if (data.suggested_labels && data.suggested_labels.length) {
            data.suggested_labels.forEach(label => {
                const tag = document.createElement('span');
                tag.className = 'tag-pill';
                tag.textContent = label;
                displayLabels.appendChild(tag);
            });
        } else {
            displayLabels.textContent = "No labels suggest.";
        }

        // Show
        resultContainer.classList.remove('hidden');
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function setLoading(isLoading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const loader = analyzeBtn.querySelector('.loader');
        analyzeBtn.disabled = isLoading;
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
        } else {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    }

    function setProgressStep(step) {
        if (step === 0) {
            progressIndicator.classList.add('hidden');
            return;
        }

        progressIndicator.classList.remove('hidden');
        const steps = progressIndicator.querySelectorAll('.progress-step');

        steps.forEach((stepEl, index) => {
            const stepNum = index + 1;
            stepEl.classList.remove('active', 'complete');

            if (stepNum < step) {
                stepEl.classList.add('complete');
            } else if (stepNum === step) {
                stepEl.classList.add('active');
            }
        });
    }

    // Modal and Navigation Handlers
    homeLink.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    aboutLink.addEventListener('click', (e) => {
        e.preventDefault();
        aboutModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    });

    closeModal.addEventListener('click', () => {
        aboutModal.classList.add('hidden');
        document.body.style.overflow = ''; // Restore scroll
    });

    // Close modal when clicking overlay
    aboutModal.querySelector('.modal-overlay').addEventListener('click', () => {
        aboutModal.classList.add('hidden');
        document.body.style.overflow = '';
    });

    // Footer link handlers
    const footerHomeLink = document.getElementById('footerHomeLink');
    const footerAboutLink = document.getElementById('footerAboutLink');

    if (footerHomeLink) {
        footerHomeLink.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    if (footerAboutLink) {
        footerAboutLink.addEventListener('click', (e) => {
            e.preventDefault();
            aboutModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !aboutModal.classList.contains('hidden')) {
            aboutModal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    });

    // Theme Toggle Handler
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcons(newTheme);
    });

    function updateThemeIcons(theme) {
        if (theme === 'light') {
            sunIcon.classList.add('hidden');
            moonIcon.classList.remove('hidden');
        } else {
            sunIcon.classList.remove('hidden');
            moonIcon.classList.add('hidden');
        }
    }

    // Download Handlers
    downloadBtn.addEventListener('click', () => {
        downloadMenu.classList.toggle('hidden');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!downloadBtn.contains(e.target) && !downloadMenu.contains(e.target)) {
            downloadMenu.classList.add('hidden');
        }
    });

    downloadMarkdown.addEventListener('click', () => {
        if (!currentAnalysisData) return;

        const markdown = generateMarkdown(currentAnalysisData);
        downloadFile(markdown, 'analysis-report.md', 'text/markdown');
        downloadMenu.classList.add('hidden');
    });

    downloadPDF.addEventListener('click', () => {
        if (!currentAnalysisData) return;

        downloadMenu.classList.add('hidden');
        window.print(); // Simple PDF export using browser print
    });

    function generateMarkdown(data) {
        return `# GitHub Issue Analysis Report

## Summary
${data.summary || 'No summary provided'}

## Type
${data.type || 'N/A'}

## Priority Score
${data.priority_score || 'N/A'}

## Impact Assessment
${data.potential_impact || 'No impact analysis provided'}

## Suggested Labels
${data.suggested_labels && data.suggested_labels.length ? data.suggested_labels.join(', ') : 'No labels suggested'}

---

*Generated by IssueAnalyzer - Powered by Google Gemini AI*
`;
    }

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});
