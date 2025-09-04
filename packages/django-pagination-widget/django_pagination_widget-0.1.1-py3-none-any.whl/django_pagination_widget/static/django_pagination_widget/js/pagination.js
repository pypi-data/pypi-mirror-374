/**
 * Django Pagination Widget JavaScript
 * Handles dynamic pagination behavior with ellipsis
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePagination);
    } else {
        initializePagination();
    }

    function initializePagination() {
        // Initialize each pagination widget separately
        const paginationWidgets = document.querySelectorAll('.pagination');
        paginationWidgets.forEach(function(widget) {
            initializeWidget(widget);
        });
    }

    function initializeWidget(widget) {
        // Add classes to first and last page buttons within this widget
        const pageButtons = widget.querySelectorAll('.page-num-btn');
        if (pageButtons.length > 0) {
            pageButtons[0].classList.add('first-page-btn');
            pageButtons[pageButtons.length - 1].classList.add('last-page-btn');
        }

        // Set active page based on current URL for this widget
        setActivePage(widget);

        // Apply ellipsis logic for this widget
        applyEllipsis(widget);
    }

    function setActivePage(widget) {
        const currentSearch = window.location.search;

        // If no query parameters, activate first page
        if (currentSearch === '' || currentSearch === '?page=1') {
            const firstButton = widget.querySelector('.page-num-btn');
            if (firstButton) {
                firstButton.classList.add('active');
            }
            return;
        }

        // Find and activate the current page button within this widget
        const pageButtons = widget.querySelectorAll('.page-num-btn');
        pageButtons.forEach(function(button) {
            if (button.getAttribute('href') === currentSearch) {
                button.classList.add('active');
            }
        });
    }

    function applyEllipsis(widget) {
        const activeBtn = widget.querySelector('.page-num-btn.active');
        if (!activeBtn) return;

        const pageButtons = widget.querySelectorAll('.page-num-btn');
        const totalPages = pageButtons.length;

        // Only apply ellipsis if we have more than 7 pages
        if (totalPages <= 7) return;

        // Find the index of the active button within this widget
        let activeIndex = -1;
        pageButtons.forEach(function(button, index) {
            if (button.classList.contains('active')) {
                activeIndex = index;
            }
        });

        // Add ellipsis before active page if not in first 3 positions
        if (activeIndex > 2) {
            const ellipsisSpan = document.createElement('span');
            ellipsisSpan.className = 'page-change-btn before-dots';
            ellipsisSpan.textContent = '…';
            ellipsisSpan.setAttribute('aria-hidden', 'true');
            activeBtn.parentNode.insertBefore(ellipsisSpan, activeBtn);
        }

        // Add ellipsis after active page if not in last 3 positions
        if (activeIndex < totalPages - 3) {
            const ellipsisSpan = document.createElement('span');
            ellipsisSpan.className = 'page-change-btn after-dots';
            ellipsisSpan.textContent = '…';
            ellipsisSpan.setAttribute('aria-hidden', 'true');
            insertAfter(ellipsisSpan, activeBtn);
        }

        // Hide buttons between ellipsis and boundaries
        hideButtonsBetweenEllipsis(widget);
    }

    function hideButtonsBetweenEllipsis(widget) {
        const beforeDots = widget.querySelector('.before-dots');
        const afterDots = widget.querySelector('.after-dots');

        // Hide buttons before the "before-dots"
        if (beforeDots) {
            hideElementsBetween(widget, beforeDots, '.first-page-btn', 'previous');
        }

        // Hide buttons after the "after-dots"
        if (afterDots) {
            hideElementsBetween(widget, afterDots, '.last-page-btn', 'next');
        }
    }

    function hideElementsBetween(widget, referenceElement, boundarySelector, direction) {
        const boundary = widget.querySelector(boundarySelector);
        if (!boundary) return;

        let currentElement = referenceElement;
        const elementsToHide = [];

        // Collect elements to hide
        while (currentElement) {
            if (direction === 'previous') {
                currentElement = currentElement.previousElementSibling;
                if (currentElement === boundary) break;
                if (currentElement && currentElement.classList.contains('page-num-btn')) {
                    elementsToHide.push(currentElement);
                }
            } else {
                currentElement = currentElement.nextElementSibling;
                if (currentElement === boundary) break;
                if (currentElement && currentElement.classList.contains('page-num-btn')) {
                    elementsToHide.push(currentElement);
                }
            }
        }

        // Hide the collected elements
        elementsToHide.forEach(function(element) {
            element.style.display = 'none';
        });
    }

    // Utility function to insert after element
    function insertAfter(newNode, referenceNode) {
        referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
    }

    // Re-initialize on dynamic content changes (for AJAX pagination)
    window.reinitializePagination = function() {
        // Remove existing ellipsis and classes from all widgets
        const paginationWidgets = document.querySelectorAll('.pagination');
        paginationWidgets.forEach(function(widget) {
            const dots = widget.querySelectorAll('.before-dots, .after-dots');
            dots.forEach(function(dot) {
                dot.remove();
            });

            // Show all hidden buttons and remove classes
            const pageButtons = widget.querySelectorAll('.page-num-btn');
            pageButtons.forEach(function(button) {
                button.style.display = '';
                button.classList.remove('first-page-btn', 'last-page-btn', 'active');
            });
        });

        // Re-initialize all widgets
        initializePagination();
    };

})();
