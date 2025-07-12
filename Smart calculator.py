import matplotlib.pyplot as plt
import re
import math
import webbrowser
import os
import threading
import time

from flask import Flask, render_template

# Flask app setup
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return render_template("template.html")

def launch_website():
    time.sleep(1)
    webbrowser.open("file:///C:/Users/Archit/OneDrive/Desktop/smartarc16.html.html")

def start_website():
    threading.Thread(target=launch_website).start()
    flask_app.run(debug=False)

memory = {}

# Identity matcher
identities = {
    "a**2 + b**2 + 2*a*b": "(a + b)^2",
    "a**2 + b**2 - 2*a*b": "(a - b)^2",
    "a**2 - b**2": "(a + b)(a - b)",
    "x**2 + 2*a*x + a**2": "(x + a)^2",
    "x**2 - 2*a*x + a**2": "(x - a)^2",
    "x**2 - a**2": "(x - a)(x + a)",
}

def match_identity(expr):
    try:
        expr = expr.replace("^", "**")
        expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)
        for pattern, form in identities.items():
            if expr.replace(" ", "") == pattern.replace(" ", ""):
                return f"💡 Identity matched: {form}"
        return f"🧮 Result: {eval(expr, {}, memory)}"
    except Exception as e:
        return f"⚠️ Error: {e}"

def motion_eqs(u, a, t):
    v = u + a * t
    s = u * t + 0.5 * a * t**2
    v2 = u**2 + 2 * a * s
    return {
        "Final velocity (v = u + at)": v,
        "Displacement (s = ut + ½at²)": s,
        "v² = u² + 2as": v2
    }

def geometry(shape, **kw):
    if shape == "rectangle":
        return {"area": kw['l'] * kw['b'], "perimeter": 2 * (kw['l'] + kw['b'])}
    elif shape == "circle":
        return {"area": math.pi * kw['r']**2, "perimeter": 2 * math.pi * kw['r']}
    elif shape == "square":
        return {"area": kw['s']**2, "perimeter": 4 * kw['s']}
    elif shape == "triangle":
        a, b, c = kw['a'], kw['b'], kw['c']
        s = (a + b + c) / 2
        try:
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
        except ValueError:
            return "⚠️ Invalid triangle dimensions."
        return {"area": area, "perimeter": a + b + c}
    return "Unsupported shape."

def plot_points(points):
    x, y = zip(*points)
    plt.plot(x, y, marker='o')
    plt.title("Point Plot")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.show()

def vt_graph(u, a, t):
    times = list(range(t + 1))
    vels = [u + a * time for time in times]
    plt.plot(times, vels, marker='o')
    plt.title("Velocity-Time Graph")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.grid(True)
    plt.show()

def parse_input(text):
    text = text.lower().strip()

    if text in ["hi", "hello", "hey"]:
        return "👋 Hello! I’m SmartArc16. How can I help you with math or physics?"

    if "source" in text or "website" in text or "open source" in text:
        try:
            start_website()
            return "🌐 SmartArc16 website launching at http://localhost:5000"
        except Exception as e:
            return f"⚠️ Unable to start website: {e}"

    if "remember" in text:
        match = re.search(r'remember (\w+) (?:as )?([\d.-]+)', text)
        if match:
            var, val = match.groups()
            memory[var] = float(val)
            return f"✅ Remembered: {var} = {val}"

    if "refresh" in text or "clear" in text:
        memory.clear()
        return "🧹 Memory Cleared!"

    if "about" in text or "help" in text:
        return (
            "📘 SmartArc16 Help:\n"
            "- ✅ 7 Algebraic Identities auto-recognized\n"
            "- 🔢 Say: 'remember x as 10'\n"
            "- 📈 'Plot (1,2), (-3,4)', supports negative points\n"
            "- 📊 'graph u=5 a=2 t=4' for velocity-time graphs\n"
            "- ➕ Math like '2+2' or 'x^2 + 2x + 1'\n"
            "- 🧹 'refresh' to clear memory, 'exit' to quit"
        )

    if re.match(r'^[a-z] *=', text):
        expr = text.split('=')[1].split("with")[0].strip()
        if "with" in text:
            vars_part = text.split("with")[1]
            vars_found = re.findall(r'([a-z])\s*=\s*([\d.-]+)', vars_part)
            for var, val in vars_found:
                memory[var] = float(val)
        return match_identity(expr)

    if "velocity" in text or "motion" in text:
        found = re.findall(r'([uat])\s*=?\s*([\d.-]+)', text)
        values = {k: float(v) for k, v in found}
        if all(k in values for k in ['u', 'a', 't']):
            return motion_eqs(values['u'], values['a'], values['t'])

    if "area" in text or "perimeter" in text or "geometry" in text:
        try:
            if "rectangle" in text:
                l = float(re.search(r'length\s*=?\s*([\d.-]+)', text).group(1))
                b = float(re.search(r'breadth\s*=?\s*([\d.-]+)', text).group(1))
                return geometry("rectangle", l=l, b=b)
            if "circle" in text:
                r = float(re.search(r'radius\s*=?\s*([\d.-]+)', text).group(1))
                return geometry("circle", r=r)
            if "square" in text:
                s = float(re.search(r'side\s*=?\s*([\d.-]+)', text).group(1))
                return geometry("square", s=s)
            if "triangle" in text:
                a = float(re.search(r'a\s*=?\s*([\d.-]+)', text).group(1))
                b = float(re.search(r'b\s*=?\s*([\d.-]+)', text).group(1))
                c = float(re.search(r'c\s*=?\s*([\d.-]+)', text).group(1))
                return geometry("triangle", a=a, b=b, c=c)
        except:
            return "⚠️ Geometry input format error."

    if "plot" in text and "(" in text:
        try:
            points = re.findall(r'\(([^)]+)\)', text)
            parsed = [tuple(map(float, p.strip().split(','))) for p in points]
            plot_points(parsed)
            return "✅ Points plotted, even with negative values!"
        except:
            return (
                "⚠️ Invalid plot format. Try: plot (1,2), (-3,4)\n"
                "💡 Tip: Use correct comma and bracket placement."
            )

    if "graph" in text or "v-t" in text:
        found = re.findall(r'([uat])\s*=?\s*([\d.-]+)', text)
        vals = {k: float(v) for k, v in found}
        if all(k in vals for k in ['u', 'a', 't']):
            vt_graph(vals['u'], vals['a'], int(vals['t']))
            return "✅ v-t Graph plotted."
        return "⚠️ Please provide values like: graph u=5 a=2 t=4"

    try:
        expr = re.sub(r'([a-z])([a-z])', r'\1*\2', text)
        expr = expr.replace("^", "**")
        result = eval(expr, {}, memory)
        return f"🧮 Result: {result}"
    except:
        return "❌ I didn't understand that. Type 'about' for help or retry your input."

if __name__ == "__main__":
    print("🤖 Welcome to SmartArc16 — AI Math & Physics Assistant with Identity Matching and Web View!")
    while True:
        user_input = input(">> ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye from SmartArc16!")
            break
        print(parse_input(user_input))
