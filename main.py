import os
import json
import tkinter as tk
from tkinter import ttk
import webbrowser
import urllib.request
import threading
from dotenv import load_dotenv

# Load key from hidden .env file
load_dotenv()


class NewsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live News API Dashboard")
        self.root.geometry("500x700")
        self.root.configure(bg="#121212")

        # Header Banner
        header = tk.Label(
            self.root, text="📰 LIVE GLOBAL WIRE",
            font=("Helvetica", 12, "bold"), bg="#1e1e1e", fg="#00dfa2", pady=10
        )
        header.pack(fill=tk.X)

        # 2G Optimization Loading Label
        self.loading_label = tk.Label(
            self.root, text="Connecting directly to News API...\nStreaming live text feed...",
            font=("Helvetica", 10), bg="#121212", fg="#ffffff", justify="center"
        )
        self.loading_label.pack(expand=True)

        # Scrollable Layout Setup
        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#121212")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        # Fetch live data stream instantly in background
        threading.Thread(target=self.fetch_real_news, daemon=True).start()

        self.root.mainloop()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def fetch_real_news(self):
        api_key = os.getenv("NEWS_API_KEY")

        # We query top global headlines. We set pageSize to 15 to keep data packets tiny over 2G.
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=15&apiKey={api_key}"

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                raw_data = response.read().decode('utf-8')
                self.data = json.loads(raw_data)
                print("Real news data packet received!")
        except Exception as e:
            print(f"Network error: {e}")
            self.data = {"articles": [{"title": "Network connection timeout.",
                                       "description": "Your 2G signal dropped. Click close and rerun.",
                                       "url": "https://google.com"}]}

        # Hand over the array layout rendering safely back to the GUI thread
        self.root.after(0, self.display_news_feed)

    def display_news_feed(self):
        if self.loading_label.winfo_exists():
            self.loading_label.pack_forget()

        self.canvas.pack(side="left", fill="both", expand=True, padx=5)
        self.scrollbar.pack(side="right", fill="y")

        articles = self.data.get("articles", [])

        for article in articles:
            # Skip articles that are deleted or empty from the server
            if not article.get("title") or "[Removed]" in article.get("title"):
                continue

            # Minimalist Card Box Container
            card = tk.Frame(self.scrollable_frame, bg="#1e1e1e", bd=1, relief=tk.RIDGE, padx=12, pady=12)
            card.pack(fill=tk.X, pady=8, padx=15)

            # 1. Source Label (e.g., BBC News, CNN, TechCrunch)
            source_info = article.get("source", {}).get("name", "General News")
            source_lbl = tk.Label(
                card, text=source_info.upper(),
                font=("Helvetica", 8, "bold"), bg="#1e1e1e", fg="#00dfa2"
            )
            source_lbl.pack(anchor="w", pady=(0, 3))

            # 2. Real News Headline Title
            title_lbl = tk.Label(
                card, text=article.get("title", "No Title"),
                font=("Helvetica", 11, "bold"), bg="#1e1e1e", fg="#ffffff",
                wraplength=440, justify="left"
            )
            title_lbl.pack(anchor="w", pady=(0, 5))

            # 3. Short Description Snippet
            desc_text = article.get("description")
            if not desc_text:
                desc_text = "Click below to open and review full coverage text summary directly on source web host."

            desc_lbl = tk.Label(
                card, text=desc_text,
                font=("Helvetica", 10), bg="#1e1e1e", fg="#b3b3b3",
                wraplength=440, justify="left"
            )
            desc_lbl.pack(anchor="w", pady=(0, 8))

            # 4. Verified Interactive URL Click Action
            url = article.get("url", "https://google.com")
            link_lbl = tk.Label(
                card, text="Read official article →", font=("Helvetica", 9, "underline"),
                bg="#1e1e1e", fg="#ffffff", cursor="hand2"
            )
            link_lbl.pack(anchor="e")
            link_lbl.bind("<Button-1>", lambda e, url_path=url: webbrowser.open(url_path))


if __name__ == "__main__":
    app = NewsApp()