import os
import requests
from collections import Counter

# Configuración
ORG_NAME = os.environ["ORG_NAME"]
USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ.get("PAT")  # opcional si quieres usar PAT para privados
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# Colores estilo GitHub Stats
LANG_COLORS = {
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4F5D95",
    "C#": "#178600",
    "Python": "#3572A5",
    "Dart": "#00B4AB",
    "TypeScript": "#2b7489",
    "Node.js": "#3C873A",
    "Handlebars": "#f7931e",
    "C++": "#f34b7d",
    "Other": "#ededed"
}

def fetch_repos(url):
    repos = []
    while url:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        repos.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
    return repos

# Obtener repos de la organización
org_url = f"https://api.github.com/orgs/{ORG_NAME}/repos?per_page=100"
org_repos = fetch_repos(org_url)

# Obtener repos personales
user_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
user_repos = fetch_repos(user_url)

all_repos = org_repos + user_repos

# Contar bytes por lenguaje
lang_counter = Counter()
for repo in all_repos:
    if repo["fork"]:
        continue
    langs = requests.get(repo["languages_url"], headers=HEADERS).json()
    lang_counter.update(langs)

# Calcular porcentaje
total_bytes = sum(lang_counter.values())
top_langs = lang_counter.most_common(6)  # Top 6 lenguajes
langs, counts = zip(*top_langs) if top_langs else ([], [])
percentages = [c / total_bytes * 100 for c in counts]

# Colores para los top lenguajes
colors = [LANG_COLORS.get(lang, LANG_COLORS["Other"]) for lang in langs]

# Generar barras de progreso
bar_width = 250
bars_svg = ""
cumulative_x = 0

for i, (lang, pct, color) in enumerate(zip(langs, percentages, colors)):
    width = (pct / 100) * bar_width
    bars_svg += f'''
        <rect
          mask="url(#rect-mask)"
          data-testid="lang-progress"
          x="{cumulative_x:.2f}"
          y="0"
          width="{width:.2f}"
          height="8"
          fill="{color}"
        />
      '''
    cumulative_x += width

# Generar items de lenguajes (2 columnas)
lang_items_left = ""
lang_items_right = ""

for i, (lang, pct, color) in enumerate(zip(langs, percentages, colors)):
    delay = 450 + (i % 3) * 150
    item_svg = f'''<g transform="translate(0, {(i % 3) * 25})">
    <g class="stagger" style="animation-delay: {delay}ms">
      <circle cx="5" cy="6" r="5" fill="{color}" />
      <text data-testid="lang-name" x="15" y="10" class='lang-name'>
        {lang} {pct:.2f}%
      </text>
    </g>
  </g>'''
    
    if i < 3:
        lang_items_left += item_svg
    else:
        lang_items_right += item_svg

# Crear SVG completo
svg_content = f'''<svg
        width="300"
        height="165"
        viewBox="0 0 300 165"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-labelledby="descId"
      >
        <title id="titleId">Most Used Languages</title>
        <desc id="descId">Top languages used in repositories</desc>
        <style>
          .header {{
            font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif;
            fill: #fe428e;
            animation: fadeInAnimation 0.8s ease-in-out forwards;
          }}
          @supports(-moz-appearance: auto) {{
            .header {{ font-size: 15.5px; }}
          }}
          
    @keyframes slideInAnimation {{
      from {{
        width: 0;
      }}
      to {{
        width: calc(100%-100px);
      }}
    }}
    @keyframes growWidthAnimation {{
      from {{
        width: 0;
      }}
      to {{
        width: 100%;
      }}
    }}
    .stat {{
      font: 600 14px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif; fill: #a9fef7;
    }}
    @supports(-moz-appearance: auto) {{
      .stat {{ font-size:12px; }}
    }}
    .bold {{ font-weight: 700 }}
    .lang-name {{
      font: 400 11px "Segoe UI", Ubuntu, Sans-Serif;
      fill: #a9fef7;
    }}
    .stagger {{
      opacity: 0;
      animation: fadeInAnimation 0.3s ease-in-out forwards;
    }}
    #rect-mask rect{{
      animation: slideInAnimation 1s ease-in-out forwards;
    }}
    .lang-progress{{
      animation: growWidthAnimation 0.6s ease-in-out forwards;
    }}
    

          
      /* Animations */
      @keyframes scaleInAnimation {{
        from {{
          transform: translate(-5px, 5px) scale(0);
        }}
        to {{
          transform: translate(-5px, 5px) scale(1);
        }}
      }}
      @keyframes fadeInAnimation {{
        from {{
          opacity: 0;
        }}
        to {{
          opacity: 1;
        }}
      }}
    
          
        </style>

        

        <rect
          data-testid="card-bg"
          x="0.5"
          y="0.5"
          rx="4.5"
          height="99%"
          stroke="#e4e2e2"
          width="299"
          fill="#141321"
          stroke-opacity="1"
        />

        
      <g
        data-testid="card-title"
        transform="translate(25, 35)"
      >
        <g transform="translate(0, 0)">
      <text
        x="0"
        y="0"
        class="header"
        data-testid="header"
      >Most Used Languages</text>
    </g>
      </g>
    

        <g
          data-testid="main-card-body"
          transform="translate(0, 55)"
        >
          
    <svg data-testid="lang-items" x="25">
      
  
      <mask id="rect-mask">
          <rect x="0" y="0" width="250" height="8" fill="white" rx="5"/>
        </mask>
        {bars_svg}
      
    <g transform="translate(0, 25)">
      <g transform="translate(0, 0)">{lang_items_left}</g><g transform="translate(150, 0)">{lang_items_right}</g>
    </g>
  
    </svg>
  
        </g>
      </svg>'''

# Guardar SVG
with open("TOP_LANGUAGES.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)

print("✓ Gráfico guardado como TOP_LANGUAGES.svg")