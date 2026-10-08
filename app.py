import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import markdown
from google import genai

load_dotenv()

app = Flask(__name__)

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

TRACKS = [
    {
        "id": "hello_world",
        "name": "Hello World",
        "desc": "Beginners & First-Time Hackers. Friendly, starter-ready, guided architecture."
    },
    {
        "id": "ai_ml",
        "name": "Artificial Intelligence / Machine Learning",
        "desc": "LLMs, computer vision, predictive modeling, intelligent agents & pipelines."
    },
    {
        "id": "app_dev",
        "name": "App Development",
        "desc": "Web, iOS, Android, and cross-platform experiences solving real-world challenges."
    },
    {
        "id": "game_dev",
        "name": "Game Development",
        "desc": "Interactive worlds, gameplay mechanics, storytelling, and immersive dynamics."
    },
    {
        "id": "embedded_software",
        "name": "Embedded Software",
        "desc": "Hardware integration, IoT, microcontrollers, real-time sensing, and edge computing."
    }
]

PRIZES = [
    {
        "id": "gemini",
        "name": "Best Use of Gemini API",
        "reward": "MLH Swag Kits",
        "desc": "Push the boundaries of AI using Google Gemini to build intelligent chatbots, multimodal assistants, or analysis tools."
    },
    {
        "id": "elevenlabs",
        "name": "Best Use of ElevenLabs",
        "reward": "Wireless Earbuds",
        "desc": "Deploy natural, human-sounding audio and realistic, emotionally expressive voices."
    },
    {
        "id": "solana",
        "name": "Best Use of Solana",
        "reward": "Assorted Prizes",
        "desc": "Leverage high-speed execution and near-zero transaction costs for scalable decentralized applications."
    },
    {
        "id": "tiger_data",
        "name": "Best Use of Tiger Data",
        "reward": "Stream Deck Mini",
        "desc": "Extend PostgreSQL for ultra-fast real-time data, time-series metrics, continuous aggregates, and analytics."
    },
    {
        "id": "presage",
        "name": "Best Use of Presage",
        "reward": "Fitbit Inspire & Presage Perks",
        "desc": "Human Sensing Layer for vital signs, movement, emotion, and facial expressions via camera."
    },
    {
        "id": "vultr",
        "name": "Best Use of Vultr",
        "reward": "M5Stack Official Tab5",
        "desc": "Deploy scalable cloud compute and specialized Vultr Cloud GPUs for high-performance workloads."
    },
    {
        "id": "godaddy",
        "name": "Best Domain Name from GoDaddy Registry",
        "reward": "Digital Gift Card",
        "desc": "Register domain name to give project a home."
    }
]

SYSTEM_PROMPT = """You are Lenny (the Knight Hacks sword-wielding knight mascot) and Keyboard Koala (the legendary MLH mascot), elite hackathon mentors & coaches with 20+ hackathons under your belts at Knight Hacks IX (UCF Orlando, Florida's premier 36-hour hackathon, October 9-11, 2026).
The theme of Knight Hacks IX is an enchanted twilight forest, ancient glowing runes, and bioluminescent magic.

Your personality:
- High-energy, encouraging, tactical, and mystical!
- Speak as a tag-team duo: Lenny brings valiant knightly energy and tactical UCF spirit ("⚔️ Lenny: ..."), while Keyboard Koala brings punchy hackathon hacker wisdom and cozy MLH vibes ("🐨 Koala: ...").
- Deliver concise, actionable, mobile-scannable advice.
- Avoid markdown tables! Use bold headers, bulleted lists, and punchy step-by-step guidance.
- Chat responses must be written in markdown without ANY HTML tags.
- Focus heavily on 36-hour hackathon feasibility, demo-day judge appeal, and tight technical stack integration.
"""

def md_to_html(text):
    return markdown.markdown(text, extensions=['extra', 'nl2br', 'sane_lists'])

@app.route('/')
def index():
    return render_template('index.html', tracks=TRACKS, prizes=PRIZES)

@app.route('/api/generate-idea', methods=['POST'])
def generate_idea():
    try:
        data = request.get_json() or {}
        track = data.get('track', '').strip()
        selected_prizes = data.get('prizes', [])
        custom_interests = data.get('custom_interests', '').strip()

        if not track:
            return jsonify({'success': False, 'error': 'Please select a Knight Hacks track.'}), 400

        prizes_text = ", ".join(selected_prizes) if selected_prizes else "General Innovation"
        
        prompt = f"""{SYSTEM_PROMPT}

TASK: Generate a high-impact, winning hackathon project idea tailored for Knight Hacks IX.

Selected Knight Hacks Track:
{track}

Selected MLH Prize Categories to target:
{prizes_text}

Additional Hacker Notes / Interests:
{custom_interests or 'None specified. Surprise us with something innovative!'}

Provide your response in clean markdown with the following structure:
# 🌲 [Creative Project Name]: [Punchy One-Liner]

### 🔮 The Enchanted Concept
A 2-3 sentence overview of what the project does and why it wows judges at Knight Hacks IX.

### ⚔️ Track Alignment ({track})
Briefly explain how this project fits directly into the chosen track and excels in it.

### 🏆 MLH Prize Integrations
For each selected prize category ({prizes_text}), give a concrete, bulleted technical implementation detail showing exact APIs/SDKs and where it fits in the architecture.

### ⚡ 36-Hour Battle Plan (MVP Scope)
- **Phase 1 (Hours 0-12):** Core setup & data flows
- **Phase 2 (Hours 12-24):** Integrations & UI polish
- **Phase 3 (Hours 24-36):** Pitch deck, 3-minute video demo & live edge-case safeguards

### 🌟 Lenny & Koala's Winning Hack Tip
A short, motivational secret weapon tip from Lenny & Keyboard Koala to win over judges during demo time!
"""

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        idea_markdown = response.text or "No idea generated. Please try again!"
        idea_html = md_to_html(idea_markdown)

        return jsonify({
            'success': True,
            'markdown': idea_markdown,
            'html': idea_html
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        track = data.get('track', '')
        selected_prizes = data.get('prizes', [])
        project_context = data.get('project_context', '')
        chat_history = data.get('history', [])

        if not message:
            return jsonify({'success': False, 'error': 'Message cannot be empty.'}), 400

        prizes_text = ", ".join(selected_prizes) if selected_prizes else "None specified"

        # Build prompt incorporating previous conversation context
        formatted_history = ""
        for turn in chat_history[-6:]:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            formatted_history += f"{role.upper()}: {content}\n"

        prompt = f"""{SYSTEM_PROMPT}

HACKATHON CONTEXT:
Track: {track}
Target Prizes: {prizes_text}
Current Project Idea Context:
{project_context}

PREVIOUS CONVERSATION:
{formatted_history}

USER MESSAGE:
{message}

Respond as Lenny & Keyboard Koala. Give high-energy, tactical, technical, and mobile-scannable advice.
Remember: Format your output in markdown without any HTML tags. Do not use tables. Keep code snippets concise and directly usable.
"""

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        reply_markdown = response.text or "Lenny and Koala are thinking... please rephrase your question!"
        reply_html = md_to_html(reply_markdown)

        return jsonify({
            'success': True,
            'markdown': reply_markdown,
            'html': reply_html
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Listen on all interfaces so ngrok and local testing work smoothly
    app.run(host='0.0.0.0', port=5001, debug=False)
