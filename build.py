#!/usr/bin/env python3
"""Собирает README профиля: живые проекты-сайты (sites.json, только отвечающие) и публичные репозитории, свежие сверху."""
import json, os, urllib.request, datetime
USER = os.environ.get("GH_USER", "VADBIZ")
def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme", **(headers or {})})
    return urllib.request.urlopen(req, timeout=20)
def alive(url):
    try: return get(url).status == 200
    except Exception: return False
cfg = json.load(open("sites.json", encoding="utf-8"))
auto = json.load(open("projects.json", encoding="utf-8")) if os.path.exists("projects.json") else []
sites = []
for s in auto:
    if s["url"] in cfg.get("exclude", []): continue
    s = dict(s, about=cfg.get("about", {}).get(s["url"], s.get("about", "")))
    sites.append(s)
for e in cfg.get("extra", []):
    i = next((k + 1 for k, s in enumerate(sites) if s["url"] == e.get("after")), len(sites))
    sites.insert(i, {k: v for k, v in e.items() if k != "after"})
sites = [s for s in sites if alive(s["url"])]
h = {"Accept": "application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"): h["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
repos = json.load(get(f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=100", h))
repos = [r for r in repos if not r["private"] and r["name"] != USER]
repos.sort(key=lambda r: r["pushed_at"], reverse=True)
months = "января февраля марта апреля мая июня июля августа сентября октября ноября декабря".split()
def ru(d):
    d = datetime.date.fromisoformat(d[:10]); return f"{d.day} {months[d.month-1]} {d.year}"
L = ["## Привет! Я Александр Вербецкий", "",
     "Делаю сайты, Telegram-ботов, игры и сервисы с нейросетями. 22 года в IT.", "",
     "### Живые проекты", "", "| Проект | Что это |", "|---|---|"]
L += [f"| [{s['name']}]({s['url']}) | {s['about']} |" for s in sites]
L += ["", "### Репозитории — свежие сверху", "", "| Репозиторий | Описание | Язык | Обновлён |", "|---|---|---|---|"]
for r in repos[:12]:
    desc = (r["description"] or "").replace("|", "/")
    L.append(f"| [{r['name']}]({r['html_url']}){' (форк)' if r['fork'] else ''} | {desc} | {r['language'] or ''} | {ru(r['pushed_at'])} |")
L += ["", f"<sub>Обновляется автоматически: сайты — с сервера, репозитории — с GitHub, каждые 6 часов. Последнее обновление: {ru(datetime.datetime.now(datetime.timezone.utc).isoformat())}.</sub>", ""]
open("README.md", "w", encoding="utf-8").write("\n".join(L))
print(f"сайтов {len(sites)}, репозиториев {len(repos)}")
