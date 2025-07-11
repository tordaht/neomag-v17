export const THEME = {
    bgPrimary: '#0a0e1a',
    bgSecondary: '#121829',
    panelBg: 'rgba(25, 31, 52, 0.7)',
    panelBorder: 'rgba(56, 73, 125, 0.6)',
    textPrimary: '#e6e6e6',
    textSecondary: '#9aa5c5',
    accentPrimary: '#4d7cff',
    accentSecondary: '#17e1a7',
    danger: '#ff5252',
};

export function createPlotlyLayout(title = '', xaxis_title = '', yaxis_title = '') {
    return {
        title: {
            text: title,
            font: {
                color: THEME.textPrimary,
                size: 14
            }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: THEME.textSecondary
        },
        xaxis: {
            title: xaxis_title,
            gridcolor: THEME.panelBorder,
            linecolor: THEME.panelBorder,
        },
        yaxis: {
            title: yaxis_title,
            gridcolor: THEME.panelBorder,
            linecolor: THEME.panelBorder,
        },
        margin: { l: 40, r: 20, b: 40, t: 40, pad: 4 },
        legend: {
            orientation: 'h',
            y: 1.2
        }
    };
}

// Performans panel CSS'ini head'e ekle
const performancePanelStyles = `
.performance-panel {
    margin-top: 20px;
    padding: 15px;
    background: rgba(25, 31, 52, 0.7);
    border-radius: 10px;
    border: 1px solid rgba(56, 73, 125, 0.6);
}

.performance-panel h3 {
    margin: 0 0 15px 0;
    color: #17e1a7;
    font-size: 16px;
    font-weight: 600;
}

.performance-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
}

.perf-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: rgba(77, 124, 255, 0.1);
    border-radius: 6px;
    border: 1px solid rgba(56, 73, 125, 0.3);
}

.perf-item label {
    font-size: 12px;
    color: #9aa5c5;
    font-weight: 500;
}

.perf-item span {
    font-size: 13px;
    color: #e6e6e6;
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

@media (max-width: 768px) {
    .performance-grid {
        grid-template-columns: 1fr;
    }
}
`;

// CSS'i document head'ine ekle
const styleSheet = document.createElement('style');
styleSheet.textContent = performancePanelStyles;
document.head.appendChild(styleSheet); 