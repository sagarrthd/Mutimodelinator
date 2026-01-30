"""
Custom Gradio theme and CSS styling for premium dark glassmorphism design.
Provides modern, professional styling for the MultiModelinator interface.
"""


import gradio as gr


class GlassmorphismTheme(gr.Theme):
    """Custom dark glassmorphism theme for modern UI."""
    
    def __init__(self):
        super().__init__(
            primary_hue="slate",
            secondary_hue="slate",
            neutral_hue="slate",
            spacing_size="md",
            radius_size="md",
        )


def get_custom_css() -> str:
    """
    Get custom CSS for glassmorphism styling.
    
    Returns:
        CSS string for custom styling
    """
    return """
    /* ==================== GLOBAL STYLES ==================== */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border-color: rgba(148, 163, 184, 0.2);
        --glass-bg: rgba(15, 23, 42, 0.7);
        --glass-border: rgba(148, 163, 184, 0.25);
    }
    
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
        color: var(--text-primary);
        background-attachment: fixed;
    }
    
    /* ==================== CONTAINER STYLES ==================== */
    .gradio-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(20, 30, 50, 0.95) 100%);
        color: var(--text-primary);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid var(--glass-border);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        max-width: 100%;
    }
    
    /* ==================== HEADER & TITLE ==================== */
    .gradio-container > .prose {
        color: var(--text-primary);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .prose > p {
        color: var(--text-secondary);
    }
    
    /* ==================== TEXTBOX & INPUT STYLES ==================== */
    .gradio-textbox textarea,
    .gradio-textbox input,
    .gradio-textarea textarea {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        padding: 12px 16px;
        font-size: 14px;
        backdrop-filter: blur(10px);
    }
    
    .gradio-textbox textarea:focus,
    .gradio-textbox input:focus,
    .gradio-textarea textarea:focus {
        border-color: var(--primary-color);
        background: rgba(30, 41, 59, 0.7);
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.1),
            0 0 0 3px rgba(99, 102, 241, 0.2);
        outline: none;
    }
    
    .gradio-textbox::placeholder {
        color: rgba(148, 163, 184, 0.6);
    }
    
    /* ==================== BUTTON STYLES ==================== */
    button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 
            0 4px 15px rgba(99, 102, 241, 0.3),
            0 2px 8px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
        pointer-events: none;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 6px 20px rgba(99, 102, 241, 0.4),
            0 4px 12px rgba(0, 0, 0, 0.3);
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
    }
    
    button:hover:before {
        left: 100%;
    }
    
    button:active {
        transform: translateY(0);
        box-shadow: 
            0 2px 8px rgba(99, 102, 241, 0.3),
            inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    button.secondary {
        background: linear-gradient(135deg, var(--secondary-color) 0%, #a78bfa 100%);
        box-shadow: 
            0 4px 15px rgba(139, 92, 246, 0.3),
            0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    button.secondary:hover {
        box-shadow: 
            0 6px 20px rgba(139, 92, 246, 0.4),
            0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* ==================== SLIDER STYLES ==================== */
    .gradio-slider {
        margin: 1rem 0;
    }
    
    .gradio-slider input[type="range"] {
        width: 100%;
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        outline: none;
        -webkit-appearance: none;
        appearance: none;
    }
    
    .gradio-slider input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .gradio-slider input[type="range"]::-webkit-slider-thumb:hover {
        transform: scale(1.2);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.6);
    }
    
    .gradio-slider input[type="range"]::-moz-range-thumb {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    /* ==================== DROPDOWN STYLES ==================== */
    .gradio-dropdown select {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        cursor: pointer;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .gradio-dropdown select:hover {
        border-color: var(--primary-color);
        background: rgba(30, 41, 59, 0.7);
    }
    
    .gradio-dropdown select:focus {
        border-color: var(--primary-color);
        outline: none;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    /* ==================== TABS STYLES ==================== */
    .gradio-tabs {
        background: transparent;
    }
    
    .gradio-tabs > div > .tab-nav {
        border-bottom: 2px solid var(--border-color);
        display: flex;
        gap: 0;
        background: transparent;
    }
    
    .gradio-tabs > div > .tab-nav > button {
        background: transparent;
        color: var(--text-secondary);
        border: none;
        border-bottom: 3px solid transparent;
        border-radius: 0;
        padding: 12px 20px;
        font-weight: 600;
        box-shadow: none;
        transition: all 0.3s ease;
    }
    
    .gradio-tabs > div > .tab-nav > button:hover {
        color: var(--primary-color);
        background: rgba(99, 102, 241, 0.05);
        transform: none;
        box-shadow: none;
    }
    
    .gradio-tabs > div > .tab-nav > button.selected {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
        background: transparent;
    }
    
    /* ==================== CARD & PANEL STYLES ==================== */
    .gradio-box,
    .gradio-row,
    .gradio-column {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 1px rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .gradio-box:hover {
        border-color: rgba(99, 102, 241, 0.3);
        background: rgba(30, 41, 59, 0.4);
        box-shadow: 
            0 12px 48px rgba(99, 102, 241, 0.15),
            inset 0 1px 1px rgba(255, 255, 255, 0.05);
    }
    
    /* ==================== IMAGE & OUTPUT STYLES ==================== */
    .gradio-image,
    .gradio-audio,
    .gradio-video {
        border-radius: 15px;
        border: 1px solid var(--border-color);
        background: rgba(20, 30, 50, 0.5);
        overflow: hidden;
    }
    
    .gradio-image img,
    .gradio-video video {
        border-radius: 14px;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* ==================== LOADING & ANIMATION ==================== */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .gradio-container.loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* ==================== LABEL STYLES ==================== */
    .gradio-label {
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* ==================== PROGRESSBAR STYLES ==================== */
    .gradio-progress {
        border-radius: 10px;
        overflow: hidden;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid var(--border-color);
    }
    
    .gradio-progress > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        height: 8px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
    }
    
    /* ==================== STATUS/INFO TEXT ==================== */
    .info-text {
        color: var(--text-secondary);
        font-size: 13px;
        line-height: 1.6;
        padding: 1rem;
        background: rgba(16, 185, 129, 0.05);
        border-left: 3px solid var(--success-color);
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-text {
        color: #fca5a5;
        background: rgba(239, 68, 68, 0.05);
        border-left-color: var(--error-color);
    }
    
    .warning-text {
        color: #fcd34d;
        background: rgba(245, 158, 11, 0.05);
        border-left-color: var(--warning-color);
    }
    
    /* ==================== SCROLLBAR STYLING ==================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--primary-light), #a78bfa);
    }
    
    /* ==================== RESPONSIVE DESIGN ==================== */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 1rem;
            border-radius: 15px;
        }
        
        button {
            padding: 10px 16px;
            font-size: 14px;
        }
        
        .gradio-label {
            font-size: 12px;
        }
        
        .gradio-tabs > div > .tab-nav > button {
            padding: 10px 14px;
            font-size: 13px;
        }
    }
    
    /* ==================== DARK MODE ENHANCEMENTS ==================== */
    @media (prefers-color-scheme: dark) {
        body {
            background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
        }
        
        .gradio-container {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(20, 30, 50, 0.98) 100%);
        }
    }
    """


def create_custom_theme() -> gr.Theme:
    """
    Create and return the custom glassmorphism theme.
    
    Returns:
        Configured Gradio theme
    """
    return GlassmorphismTheme()


# Example usage in Gradio blocks:
# with gr.Blocks(theme=create_custom_theme(), css=get_custom_css()) as demo:
#     # Your components here
#     pass
