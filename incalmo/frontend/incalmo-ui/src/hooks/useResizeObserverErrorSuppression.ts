import { useEffect } from 'react';

/**
 * Custom hook to suppress ResizeObserver errors that commonly occur with ReactFlow
 * These errors are typically harmless but can clutter the console and cause dev overlay issues
 */
export const useResizeObserverErrorSuppression = () => {
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
                // Silently ignore
                return;
            }

            // Pass through other errors normally
            originalConsoleError.apply(console, args);
        };

        // Handle window error events
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

                // Try to remove any error overlays
                const overlayElements = [
                    document.getElementById('webpack-dev-server-client-overlay'),
                    document.getElementById('webpack-dev-server-client-overlay-div'),
                    // Additional overlay containers that might be created
                    ...Array.from(document.querySelectorAll('[class*="overlay"]')),
                    ...Array.from(document.querySelectorAll('[id*="overlay"]'))
                ];

                // Remove overlay elements if they exist
                overlayElements.forEach(el => el && el.remove());

                return false;
            }
        };

        // Use capture phase
        window.addEventListener('error', handleError, true);

        // Clean up
        return () => {
            console.error = originalConsoleError;
            window.removeEventListener('error', handleError, true);
        };
    }, []);
}; 