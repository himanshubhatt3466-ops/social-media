import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3, os, datetime, random, threading, time

APP_DIR = os.path.join(os.path.expanduser("~"), "SocialHubManager")
os.makedirs(APP_DIR, exist_ok=True)
DB = os.path.join(APP_DIR, "socialhub.db")
PLATFORMS = ["Facebook", "Instagram", "YouTube", "WhatsApp Business"]

def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT, kind TEXT, media TEXT,
        caption TEXT, hashtags TEXT, schedule TEXT, status TEXT, created TEXT, notes TEXT)""")
    con.commit()
    return con

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SocialHub Manager")
        self.geometry("1120x720")
        self.minsize(900, 600)
        self.configure(bg="#f3f5fb")
        self.style = ttk.Style(self)
        try: self.style.theme_use("clam")
        except Exception: pass
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.build()
        self.refresh()
        self.after(15000, self.scheduler_tick)

    def build(self):
        top = tk.Frame(self, bg="#18233f", height=78); top.pack(fill="x")
        tk.Label(top, text="SocialHub Manager", bg="#18233f", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(side="left", padx=24, pady=18)
        tk.Label(top, text="SOCIAL MEDIA CONTROL CENTER", bg="#18233f", fg="#aebbe0",
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=24)
        nav = tk.Frame(self, bg="#e9edfa"); nav.pack(fill="x")
        for label, fn in [("Dashboard", self.refresh), ("Create / Schedule", self.open_create),
                          ("API Setup Guide", self.api_guide), ("Refresh", self.refresh)]:
            tk.Button(nav, text=label, command=fn, relief="flat", bg="#e9edfa",
                      fg="#25345b", padx=14, pady=10, cursor="hand2").pack(side="left")
        body = tk.Frame(self, bg="#f3f5fb"); body.pack(fill="both", expand=True, padx=22, pady=18)
        self.cards = tk.Frame(body, bg="#f3f5fb"); self.cards.pack(fill="x")
        self.card_labels = {}
        for key, title in [("total","Total Posts"),("queued","Scheduled"),("published","Published"),
                           ("failed","Needs Attention")]:
            card = tk.Frame(self.cards, bg="white", highlightbackground="#dce2f1", highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=(0,10), pady=(0,14))
            tk.Label(card, text=title, bg="white", fg="#66708a", font=("Segoe UI",10)).pack(anchor="w", padx=16,pady=(13,2))
            val = tk.Label(card, text="0", bg="white", fg="#18233f", font=("Segoe UI",22,"bold"))
            val.pack(anchor="w", padx=16, pady=(0,12)); self.card_labels[key] = val
        tk.Label(body, text="Content calendar & publishing queue", bg="#f3f5fb", fg="#18233f",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(4,10))
        cols = ("id","platform","kind","caption","schedule","status","notes")
        self.tree = ttk.Treeview(body, columns=cols, show="headings")
        headings = {"id":"ID","platform":"Platform","kind":"Type","caption":"Caption","schedule":"Scheduled time","status":"Status","notes":"Details"}
        widths = {"id":45,"platform":125,"kind":80,"caption":240,"schedule":145,"status":110,"notes":230}
        for c in cols:
            self.tree.heading(c, text=headings[c]); self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(fill="both", expand=True)
        actions = tk.Frame(body, bg="#f3f5fb"); actions.pack(fill="x", pady=12)
        tk.Button(actions, text="+ New post", command=self.open_create, bg="#4259e8", fg="white",
                  relief="flat", padx=18, pady=9).pack(side="left")
        tk.Button(actions, text="Delete selected", command=self.delete_selected, bg="#fff0f1",
                  fg="#b42336", relief="flat", padx=14, pady=9).pack(side="left", padx=8)
        tk.Button(actions, text="Export CSV", command=self.export_csv, bg="white",
                  fg="#25345b", relief="flat", padx=14, pady=9).pack(side="left")
        self.footer = tk.Label(self, text="Local draft mode • Real publishing and analytics require official API setup",
                               bg="#f3f5fb", fg="#66708a", anchor="w", padx=22, pady=8)
        self.footer.pack(fill="x")

    def refresh(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        con=db(); rows=con.execute("SELECT id,platform,kind,caption,schedule,status,notes FROM posts ORDER BY schedule DESC").fetchall()
        for row in rows: self.tree.insert("", "end", values=row)
        counts={"total":len(rows),"queued":sum(r[6]=="Scheduled" for r in rows),
                "published":sum(r[6]=="Published" for r in rows),
                "failed":sum(r[6] in ("Failed","Needs API setup") for r in rows)}
        for k,v in counts.items(): self.card_labels[k].config(text=str(v))
        con.close()

    def open_create(self):
        w=tk.Toplevel(self); w.title("Create / Schedule Post"); w.geometry("640x650"); w.transient(self)
        w.configure(bg="white")
        tk.Label(w,text="Create content",font=("Segoe UI",18,"bold"),bg="white",fg="#18233f").pack(anchor="w",padx=22,pady=(18,10))
        form=tk.Frame(w,bg="white"); form.pack(fill="both",expand=True,padx=22)
        def label(text): tk.Label(form,text=text,bg="white",fg="#34405f",font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(8,3))
        label("Platform")
        platform=ttk.Combobox(form,values=PLATFORMS,state="readonly"); platform.set(PLATFORMS[0]); platform.pack(fill="x")
        label("Content type")
        kind=ttk.Combobox(form,values=["Text / link post","Image","Video / Reel","YouTube video","WhatsApp template message"],state="readonly"); kind.set("Video / Reel"); kind.pack(fill="x")
        label("Media file (optional for draft)")
        media_var=tk.StringVar()
        mf=tk.Frame(form,bg="white"); mf.pack(fill="x")
        tk.Entry(mf,textvariable=media_var).pack(side="left",fill="x",expand=True)
        tk.Button(mf,text="Browse",command=lambda:media_var.set(filedialog.askopenfilename())).pack(side="left",padx=5)
        label("Caption / title / message")
        caption=tk.Text(form,height=5,wrap="word"); caption.pack(fill="x")
        label("Hashtags (e.g. #newvideo #business)")
        hashtags=tk.Entry(form); hashtags.pack(fill="x")
        label("Schedule (YYYY-MM-DD HH:MM, local time)")
        when=tk.Entry(form); when.insert(0,(datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")); when.pack(fill="x")
        label("Status")
        status=ttk.Combobox(form,values=["Draft","Scheduled"],state="readonly"); status.set("Scheduled"); status.pack(fill="x")
        tk.Label(form,text="Note: this starter saves schedules locally; it does not publish until APIs are connected.",bg="white",fg="#9a4b13",wraplength=580).pack(anchor="w",pady=8)
        def gen():
            topic=caption.get("1.0","end").strip() or "our latest update"
            hashtags.delete(0,"end")
            hashtags.insert(0,"#"+ "".join(x for x in topic.split()[0].lower() if x.isalnum())+" #newpost #updates")
            if not caption.get("1.0","end").strip():
                caption.insert("1.0",f"Check out {topic}! Follow us for more updates.")
        def save():
            p=platform.get(); c=caption.get("1.0","end").strip(); h=hashtags.get().strip(); media=media_var.get(); sch=when.get().strip(); st=status.get()
            try: datetime.datetime.strptime(sch,"%Y-%m-%d %H:%M")
            except ValueError: messagebox.showerror("Invalid date","Use YYYY-MM-DD HH:MM format.",parent=w); return
            if not c and not media: messagebox.showerror("Missing content","Add a caption or choose a media file.",parent=w); return
            note="Local draft — API not connected"
            con=db(); con.execute("INSERT INTO posts(platform,kind,media,caption,hashtags,schedule,status,created,notes) VALUES(?,?,?,?,?,?,?,?,?)",
                (p,kind.get(),media,c,h,sch,st,datetime.datetime.now().isoformat(timespec="minutes"),note)); con.commit(); con.close()
            w.destroy(); self.refresh()
        btns=tk.Frame(form,bg="white"); btns.pack(fill="x",pady=12)
        tk.Button(btns,text="Suggest hashtags",command=gen,bg="#eef1ff",fg="#25345b",relief="flat",padx=12,pady=8).pack(side="left")
        tk.Button(btns,text="Save schedule",command=save,bg="#4259e8",fg="white",relief="flat",padx=16,pady=8).pack(side="right")

    def delete_selected(self):
        selected=self.tree.selection()
        if not selected: messagebox.showinfo("Select a post","Choose a row first."); return
        if not messagebox.askyesno("Delete","Delete selected local record?"): return
        con=db()
        for item in selected: con.execute("DELETE FROM posts WHERE id=?",(self.tree.item(item,"values")[0],))
        con.commit(); con.close(); self.refresh()

    def export_csv(self):
        import csv
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path:return
        con=db(); rows=con.execute("SELECT id,platform,kind,media,caption,hashtags,schedule,status,created,notes FROM posts").fetchall(); con.close()
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            wr=csv.writer(f); wr.writerow(["ID","Platform","Type","Media","Caption","Hashtags","Schedule","Status","Created","Notes"]); wr.writerows(rows)
        messagebox.showinfo("Export complete","CSV saved successfully.")

    def api_guide(self):
        msg=("API connection checklist\\n\\n"
        "FACEBOOK: Meta developer app + Page access; request pages_show_list, pages_read_engagement, pages_manage_posts.\\n\\n"
        "INSTAGRAM: Professional Business/Creator account and required Meta permissions (such as instagram_basic and instagram_content_publish); media often must be publicly reachable for publishing.\\n\\n"
        "YOUTUBE: Google Cloud project, YouTube Data API v3, OAuth consent and youtube.upload; analytics uses yt-analytics.readonly. App verification may be required.\\n\\n"
        "WHATSAPP BUSINESS: Meta WhatsApp Business Platform Cloud API, business phone number, access token and approved message templates for business-initiated messages. It sends messages, not social feed posts or public video posts.\\n\\n"
        "This build is a local scheduling/content-planning starter. It does NOT claim real account connection, publishing or analytics until OAuth/API integration is configured and tested.")
        messagebox.showinfo("API Setup Guide",msg)

    def scheduler_tick(self):
        # Intentionally does not fake publishing. It marks due items for attention until API adapters are connected.
        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        con=db()
        con.execute("UPDATE posts SET status='Needs API setup', notes='Schedule due; connect official platform API to publish' WHERE status='Scheduled' AND schedule<=?",(now,))
        con.commit(); con.close(); self.refresh()
        self.after(15000,self.scheduler_tick)

if __name__=="__main__":
    App().mainloop()
