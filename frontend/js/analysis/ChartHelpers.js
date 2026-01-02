const ChartHelpers = {
    createChart: (canvas, config) => {
        if (!canvas) return null;
        // Destroy existing chart if present
        if (canvas.chart) {
            canvas.chart.destroy();
        }
        canvas.chart = new Chart(canvas, config);
        return canvas.chart;
    },
    destroyChart: (canvas) => {
        if (canvas && canvas.chart) {
            canvas.chart.destroy();
            canvas.chart = null;
        }
    },
    formatTitle: (key) => {
        // Remove 'by_' prefix and format title
        return key.includes('by_') ? 
            key.replace('by_', '').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) :
            key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    extractLabel: (item) => {
        // Use centralized field mapping for consistency
        return FieldMapping.extractLabel(item);
    },
    generateColors: (count) => {
        // Generate an array of colors for charts
        return Array.from({ length: count }, (_, i) => {
            const hue = (i * 360 / count);
            return `hsla(${hue}, 70%, 60%, 0.7)`;
        });
    }
};

