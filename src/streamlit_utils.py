"""This module contains utility functions for Streamlit applications."""

import datetime

current_time = datetime.datetime.now().strftime("%H:%M")


def render_phone_preview(card, dark_mode=False):
    """Render a phone-like flashcard preview in HTML."""
    # Get background and text colors based on mode
    if dark_mode:
        bg_color = "#121212"
        card_bg = "#1E1E1E"
        text_color = "#E0E0E0"
        accent_color = "#BB86FC"
        secondary_text = "#B0B0B0"
        border_color = "#333333"
    else:
        bg_color = "#F5F7FA"
        card_bg = "#FFFFFF"
        text_color = "#333333"
        accent_color = "#4F6BFF"
        secondary_text = "#6E7A8A"
        border_color = "#E0E6ED"

    # Create an HTML template for the phone-like flashcard preview
    html = f"""
    <div style="
        width: 320px;
        margin: 0 auto;
        border: 12px solid #222;
        border-radius: 36px;
        padding: 12px 0;
        background-color: {bg_color};
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        font-family: 'SF Pro Display', 'Segoe UI', Roboto, Arial, sans-serif;
        overflow: hidden;
        position: relative;
    ">
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 2px 20px 5px;
            font-size: 12px;
            color: {secondary_text};
        ">
            <span>{current_time}</span>
            <span>📶 📊 100%</span>
        </div>
        
        <div style="
            margin: 10px 15px;
            background-color: {card_bg};
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid {border_color};
        ">
            <div style="
                display: inline-block;
                background-color: {accent_color};
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 12px;
            ">{card.get('cefr_level', 'A1')}</div>
            
            <div style="
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
                color: {text_color};
            ">{card.get('expression', 'Untitled Card')}</div>
            
            <div style="
                font-style: italic;
                color: {secondary_text};
                margin-bottom: 15px;
                font-size: 14px;
            ">{card.get('part_of_speech', '')}</div>
            
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Definition</div>
                <div style="
                    color: {text_color};
                    font-size: 15px;
                    line-height: 1.4;
                ">{card.get('definition', '')}</div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Examples</div>
                <div style="
                    color: {text_color};
                    font-size: 15px;
                    line-height: 1.4;
                ">
                    {"".join(f'<div style="border-left: 3px solid {accent_color}; padding-left: 10px; margin-bottom: 8px; font-style: italic;">{example}</div>' for example in card.get('examples', []))}
                </div>
            </div>
            
            {f'''
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Russian</div>
                <div style="
                    color: {text_color};
                    font-size: 15px;
                    line-height: 1.4;
                ">{", ".join(card.get('russian', []))}</div>
            </div>
            ''' if card.get('russian', []) else ''}
            
            <div style="
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
                margin-top: 15px;
            ">
                {" ".join(f'<span style="background-color: {bg_color}; border: 1px solid {border_color}; color: {secondary_text}; padding: 3px 8px; border-radius: 10px; font-size: 12px;">{topic}</span>' for topic in card.get('topics', []))}
                {" ".join(f'<span style="background-color: {bg_color}; border: 1px solid {border_color}; color: {secondary_text}; padding: 3px 8px; border-radius: 10px; font-size: 12px;">syn: {syn}</span>' for syn in card.get('synonyms', [])[:2])}
                {" ".join(f'<span style="background-color: {bg_color}; border: 1px solid {border_color}; color: {secondary_text}; padding: 3px 8px; border-radius: 10px; font-size: 12px;">col: {col}</span>' for col in card.get('collocations', [])[:2])}
            </div>
        </div>
        
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 10px 20px;
        ">
            <span>•</span>
            <div>
                <span style="height: 5px; width: 5px; border-radius: 50%; background-color: {secondary_text}; margin: 0 3px; display: inline-block;"></span>
                <span style="height: 5px; width: 15px; border-radius: 3px; background-color: {accent_color}; margin: 0 3px; display: inline-block;"></span>
                <span style="height: 5px; width: 5px; border-radius: 50%; background-color: {secondary_text}; margin: 0 3px; display: inline-block;"></span>
            </div>
            <span>•</span>
        </div>
    </div>
    """
    return html
