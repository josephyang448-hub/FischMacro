import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, json
from pathlib import Path

CONFIG = Path.home() / "FischSwiftStyle_config.json"
DEFAULTS = {"toggle_key":"f6","stop_key":"f8","scan_ms":40,"region_x":500,"region_y":700,"region_w":700,"region_h":110}
try:
    import mss, numpy as np, cv2, keyboard
    DEPS=True
except Exception:
    DEPS=False

class App:
    def __init__(self, root):
        self.root=root; root.title("Fisch Macro — Swift-style V1"); root.geometry("510x520")
        self.cfg=DEFAULTS.copy()
        try: self.cfg.update(json.loads(CONFIG.read_text()))
        except Exception: pass
        self.running=False; self.stop_event=threading.Event()
        self.fish=None; self.marker=None; self.delta=None; self.error=""
        self.vars={}
        ttk.Label(root,text="Fisch Macro V1",font=("Segoe UI",18,"bold")).pack(pady=(12,0))
        ttk.Label(root,text="Swift-style screen-tracking prototype").pack(pady=(0,12))
        box=ttk.LabelFrame(root,text="Live status",padding=10); box.pack(fill="x",padx=14)
        for label,key in [("Screen capture","capture"),("Macro","macro"),("Fish candidate X","fish"),("Marker candidate X","marker"),("Delta (px)","delta")]:
            row=ttk.Frame(box); row.pack(fill="x",pady=3)
            ttk.Label(row,text=label+":",width=20).pack(side="left")
            self.vars[key]=tk.StringVar(value="—")
            ttk.Label(row,textvariable=self.vars[key],font=("Segoe UI",9,"bold")).pack(side="left")
        buttons=ttk.Frame(root); buttons.pack(pady=12)
        ttk.Button(buttons,text="START / F6",command=self.start).pack(side="left",padx=5)
        ttk.Button(buttons,text="STOP / F8",command=self.stop).pack(side="left",padx=5)
        box2=ttk.LabelFrame(root,text="Settings",padding=10); box2.pack(fill="x",padx=14)
        self.entries={}
        for i,(label,key) in enumerate([("Toggle key","toggle_key"),("Emergency stop key","stop_key"),("Scan interval ms","scan_ms"),("Region X","region_x"),("Region Y","region_y"),("Region width","region_w"),("Region height","region_h")]):
            cell=ttk.Frame(box2); cell.grid(row=i//2,column=i%2,sticky="ew",padx=4,pady=3)
            ttk.Label(cell,text=label).pack(anchor="w")
            e=ttk.Entry(cell,width=15); e.insert(0,str(self.cfg[key])); e.pack(anchor="w"); self.entries[key]=e
        box2.columnconfigure(0,weight=1); box2.columnconfigure(1,weight=1)
        ttk.Button(root,text="Save settings",command=self.save).pack(pady=8)
        self.status=tk.StringVar(value=("Ready" if DEPS else "Install requirements first"))
        ttk.Label(root,textvariable=self.status,wraplength=470).pack(padx=14,pady=4)
        ttk.Label(root,text="Screen-based only • no Roblox memory access or injection",foreground="#555").pack(pady=5)
        if DEPS:
            self.hotkeys()
        self.refresh()
        root.protocol("WM_DELETE_WINDOW",self.close)

    def save(self):
        try:
            for k,e in self.entries.items():
                v=e.get().strip()
                if k.endswith("_key"):
                    if not v: raise ValueError("Hotkey cannot be empty")
                    self.cfg[k]=v.lower()
                else: self.cfg[k]=int(v)
            if not 10<=self.cfg["scan_ms"]<=1000: raise ValueError("Scan interval must be 10–1000 ms")
            CONFIG.write_text(json.dumps(self.cfg,indent=2))
            if DEPS: self.hotkeys()
            self.status.set("Settings saved.")
        except Exception as ex: messagebox.showerror("Settings",str(ex))

    def hotkeys(self):
        try:
            keyboard.unhook_all_hotkeys()
            keyboard.add_hotkey(self.cfg["toggle_key"],lambda:self.root.after(0,self.toggle))
            keyboard.add_hotkey(self.cfg["stop_key"],lambda:self.root.after(0,self.stop))
        except Exception as ex: self.status.set("Hotkey issue: "+str(ex))

    def toggle(self): self.stop() if self.running else self.start()
    def start(self):
        if not DEPS:
            messagebox.showerror("Dependencies missing","Run: py -m pip install -r requirements.txt"); return
        self.save()
        if self.running:return
        self.stop_event.clear(); self.running=True
        threading.Thread(target=self.loop,daemon=True).start()
        self.status.set("Tracking active. Adjust region to cover the fishing bar.")
    def stop(self):
        self.running=False; self.stop_event.set()
        self.status.set("Stopped.")
    def loop(self):
        with mss.mss() as sct:
            while not self.stop_event.is_set():
                try:
                    region={"left":int(self.cfg["region_x"]),"top":int(self.cfg["region_y"]),"width":int(self.cfg["region_w"]),"height":int(self.cfg["region_h"])}
                    a=np.array(sct.grab(region)); bgr=cv2.cvtColor(a,cv2.COLOR_BGRA2BGR); hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV)
                    # Generic visual candidates only; needs calibration for Fisch's current UI.
                    mask=cv2.inRange(hsv,np.array([0,0,190]),np.array([180,75,255]))
                    counts=np.sum(mask>0,axis=0); cand=np.where(counts>=max(2,int(region["height"]*.10)))[0]
                    marker=int(np.median(cand))+region["left"] if len(cand) else None
                    sat=np.sum(hsv[:,:,1]>100,axis=0); fc=np.where(sat>=max(2,int(region["height"]*.08)))[0]
                    fish=int(fc[np.argmax(sat[fc])])+region["left"] if len(fc) else None
                    self.marker=marker; self.fish=fish
                    self.delta=fish-marker if fish is not None and marker is not None else None
                    self.error=""
                except Exception as ex:self.error=str(ex)
                time.sleep(max(.01,int(self.cfg["scan_ms"])/1000))
    def refresh(self):
        self.vars["capture"].set("Available" if DEPS else "Missing dependencies")
        self.vars["macro"].set("RUNNING" if self.running else "STOPPED")
        self.vars["fish"].set(str(self.fish) if self.fish is not None else "—")
        self.vars["marker"].set(str(self.marker) if self.marker is not None else "—")
        self.vars["delta"].set(str(self.delta) if self.delta is not None else "—")
        if self.error:self.status.set("Detection error: "+self.error[:120])
        self.root.after(150,self.refresh)
    def close(self):
        self.stop()
        try:
            if DEPS: keyboard.unhook_all()
        except Exception: pass
        self.root.destroy()

if __name__=="__main__":
    r=tk.Tk()
    try: ttk.Style().theme_use("vista")
    except Exception: pass
    App(r); r.mainloop()
