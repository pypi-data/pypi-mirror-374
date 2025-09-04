// Progressive enhancement for focus management and accessibility announcements.
// This file provides enhancements while maintaining native radio button keyboard behavior.

(function() {
    'use strict';

    // Only enhance if the extension's HTML is present on the page.
    if (!document.querySelector('.sft-container')) return;

    /**
     * Moves focus to the content panel associated with a given radio button.
     * This improves accessibility by directing screen reader users to the new content.
     * @param {HTMLInputElement} radio The radio button that was selected.
     */
    function focusOnPanel(radio) {
        if (!radio.checked) return;

        // Derive the panel's ID from the radio button's ID.
        // e.g., 'filter-group-1-radio-0' becomes 'filter-group-1-panel-0'
        const panelId = radio.id.replace('-radio-', '-panel-');
        const panel = document.getElementById(panelId);

        if (panel) {
            panel.focus();
        }
    }

    /**
     * Creates or updates a live region to announce tab changes to screen readers.
     * @param {string} tabName The name of the selected tab.
     */
    function announceTabChange(tabName) {
        // Create or find the live region for screen reader announcements.
        let liveRegion = document.getElementById('tab-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'tab-live-region';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            // Hide the element visually but keep it accessible.
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }

        // Update the announcement text.
        liveRegion.textContent = `${tabName} tab selected`;

        // Clear the announcement after a short delay to prevent clutter.
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }

    /**
     * Initializes progressive enhancements for all filter-tab components.
     * REMOVED: Custom keyboard navigation (now uses native radio button behavior)
     * KEPT: Focus management and screen reader announcements
     */
    function initTabEnhancements() {
        const containers = document.querySelectorAll('.sft-container');

        containers.forEach(container => {
            const tabBar = container.querySelector('.sft-radio-group');
            if (!tabBar) return;

            const radios = tabBar.querySelectorAll('input[type="radio"]');
            const labels = tabBar.querySelectorAll('label');

            if (radios.length === 0 || labels.length === 0) return;

            // Add change listeners for announcements and focus management
            radios.forEach((radio, index) => {
                radio.addEventListener('change', () => {
                    if (radio.checked) {
                        // Get the tab name from the associated label
                        const label = labels[index];
                        const tabName = label ? label.textContent.trim() : 'Unknown';
                        
                        // Announce the change to screen readers
                        announceTabChange(tabName);
                        
                        // Move focus to the newly visible panel
                        focusOnPanel(radio);
                    }
                });
            });
        });
    }

    // Initialize the enhancements once the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTabEnhancements);
    } else {
        initTabEnhancements();
    }
})();
