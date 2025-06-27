import { useEffect } from 'react';

/**
 * Custom hook to suppress ResizeObserver errors that are common with ReactFlow
 * These errors are harmless but can clutter the console and create error overlays
 */
export const useErrorSuppression = () => {
    useEffect(() => {
        // Store original console methods
        const originalConsoleError = console.error;

        // Override console.error to intercept ResizeObserver messages
        console.error = (...args) => {
            // Check if this is a ResizeObserver error
            if (
                args.length > 0 &&
                typeof args[0] === 'string' &&
                (args[0].includes('ResizeObserver loop') || args[0].includes('ResizeObserver'))
            ) {
                // Silently ignore ResizeObserver errors
                return;
            }

            // Pass through other errors normally
            originalConsoleError.apply(console, args);
        };

        // Clean up on unmount
        return () => {
            console.error = originalConsoleError;
        };
    }, []);

    useEffect(() => {
        const handleError = (event: ErrorEvent) => {
            // More robust pattern matching to catch any ResizeObserver related errors
            if (
                event.message &&
                (
                    event.message.includes('ResizeObserver') ||
                    event.message.includes('ResizeObserver loop')
                )
            ) {
                // Prevent default error handling
                event.preventDefault();
                event.stopPropagation();

                // Try to remove any error overlays that might appear
                const overlaySelectors = [
                    '#webpack-dev-server-client-overlay',
                    '#webpack-dev-server-client-overlay-div',
                    '[class*="overlay"]',
                    '[id*="overlay"]'
                ];

                overlaySelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => el.remove());
                });

                return false;
            }
        };

        // Use capture phase to catch errors early
        window.addEventListener('error', handleError, true);

        return () => {
            window.removeEventListener('error', handleError, true);
        };
    }, []);
}; 