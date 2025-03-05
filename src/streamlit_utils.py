"""Utility functions for Streamlit apps."""

import base64
import datetime


def get_audio_base64(file_path):
    """Read an audio file and return a base64 data URI."""
    if not file_path:
        return ""
    # Prepare the file path by removing unwanted markers
    file_path = "data/audio/" + file_path.replace("[sound:", "").replace("]", "")
    with open(file_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:audio/mpeg;base64,{encoded}"


def get_audio_html(card, audio_key, icon_size="15px"):
    """Return HTML for a hidden audio element plus a clickable icon that toggles the audio playback.

    If no audio file is provided, returns an empty string.
    """
    audio_file = card.get(audio_key, "")
    if audio_file:
        audio_src = get_audio_base64(audio_file)
        return f"""
        <audio id="{audio_key}" loop style="display:none;">
            <source src="{audio_src}" type="audio/mpeg">
        </audio>
        <span id="{audio_key}-icon" style="
            cursor: pointer;
            color: #fff;
            width: {icon_size};
            height: {icon_size};
            display: inline-block;
            background: url('https://img.icons8.com/ios-filled/50/BB86FC/play--v1.png') no-repeat center center;
            background-size: {icon_size} {icon_size};
            margin-left: 5px;
        " onclick="toggleAudio('{audio_key}')"></span>
        """
    return ""


def render_phone_preview(card, dark_mode=False):
    """Render a phone-like flashcard preview with embedded audio players for every text except Russian."""
    current_time = datetime.datetime.now().strftime("%H:%M")

    # Set colors based on dark mode flag
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

    html = f"""
    <div style="
        width: 350px;
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
        <!-- Header -->
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

        <!-- Content -->
        <div style="
            margin: 10px 15px;
            background-color: {card_bg};
            border-radius: 18px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid {border_color};
        ">
            <!-- Level -->
            <div style="
                display: inline-block;
                background-color: {accent_color};
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 12px;
            ">{card.get("cefr_level", "A1")}</div>

            <!-- Expression with audio -->
            <div style="display: flex; align-items: center;">
                <div style="
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: {text_color};
                ">{card.get("expression", "Untitled Card")}</div>
                {get_audio_html(card, "audio_expression")}
            </div>

            <!-- Definition with audio -->
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Definition{get_audio_html(card, "audio_definition")}</div>
                <div style="display: flex; align-items: center; color: {
        text_color
    }; font-size: 15px; line-height: 1.4;">
                    <div>{card.get("definition", "")}</div>
                </div>
            </div>

            <!-- Examples with audio -->
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Examples{get_audio_html(card, "audio_examples")}</div>
                <div style="color: {text_color}; font-size: 15px; line-height: 1.4;">
                    {
        "".join(
            f'<div style="display: flex; align-items: center; border-left: 3px solid {accent_color}; padding-left: 10px; margin-bottom: 8px; font-style: italic;">'
            f"{example}"
            f"</div>"
            for example in card.get("examples", [])
        )
    }
                </div>
            </div>

            <!-- Collocations with audio -->
            {
        f'''
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Collocations{get_audio_html(card, "audio_collocations")}</div>
                <div style="display: flex; align-items: center; color: {text_color}; font-size: 15px; line-height: 1.4;">
                    <div>{", ".join(card.get("collocations", []))}</div>
                </div>
            </div>
            '''
        if card.get("collocations", [])
        else ""
    }

            <!-- Synonyms with audio -->
            {
        f'''
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Synonyms{get_audio_html(card, "audio_synonyms")}</div>
                <div style="display: flex; align-items: center; color: {text_color}; font-size: 15px; line-height: 1.4;">
                    <div>{", ".join(card.get("synonyms", []))}</div>
                </div>
            </div>
            '''
        if card.get("synonyms", [])
        else ""
    }

            <!-- Topics with audio -->
            {
        f'''
            <div style="margin-bottom: 15px;">
                <div style="
                    font-weight: bold;
                    color: {accent_color};
                    margin-bottom: 5px;
                    font-size: 14px;
                ">Topics</div>
                <div style="display: flex; align-items: center; color: {text_color}; font-size: 15px; line-height: 1.4;">
                    <div>{", ".join(card.get("topics", []))}</div>
                </div>
            </div>
            '''
        if card.get("topics", [])
        else ""
    }

            <!-- Russian (no audio) -->
            {
        f'''
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
                ">{", ".join(card.get("russian", []))}</div>
            </div>
            '''
        if card.get("russian", [])
        else ""
    }
        </div>

        <!-- JavaScript to handle individual audio toggling -->
        <script>
            function toggleAudio(audioKey) {{
                var audio = document.getElementById(audioKey);
                var icon = document.getElementById(audioKey + '-icon');
                if (audio.paused) {{
                    audio.play();
                    icon.style.backgroundImage = "url('https://img.icons8.com/ios-filled/50/000000/pause--v1.png')";
                }} else {{
                    audio.pause();
                    icon.style.backgroundImage = "url('https://img.icons8.com/ios-filled/50/000000/play--v1.png')";
                }}
            }}
        </script>

        <!-- Footer -->
        <div style="
            display: flex;
            justify-content: space-between;
            padding: 10px 20px;
        ">
            <span>•</span>
            <div>
                <span style="height: 5px; width: 5px; border-radius: 50%; background-color: {
        secondary_text
    }; margin: 0 3px; display: inline-block;"></span>
                <span style="height: 5px; width: 15px; border-radius: 3px; background-color: {
        accent_color
    }; margin: 0 3px; display: inline-block;"></span>
                <span style="height: 5px; width: 5px; border-radius: 50%; background-color: {
        secondary_text
    }; margin: 0 3px; display: inline-block;"></span>
            </div>
            <span>•</span>
        </div>
    </div>
    """
    return html
