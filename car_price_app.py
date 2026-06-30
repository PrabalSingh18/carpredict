import tkinter as tk
from tkinter import ttk, font
import pickle

# ── Helpers ────────────────────────────────────────────────────────────────────

def format_value(value):
    if value >= 10_000_000:
        return f"₹ {value/10_000_000:.2f} Cr"
    elif value >= 100_000:
        return f"₹ {value/100_000:.2f} Lakhs"
    else:
        return f"₹ {int(value):,}"

# ── Load model & scaler ────────────────────────────────────────────────────────

with open('./saved_models/RandomForestRegressor.pkl', 'rb') as f:
    model = pickle.load(f)

with open('./saved_scaling/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# ── Colour palette ─────────────────────────────────────────────────────────────

C = {
    "bg":        "#0F0F0F",   # near-black background
    "surface":   "#1A1A1A",   # card background
    "border":    "#2C2C2C",   # subtle border
    "green":     "#1DB965",   # primary accent
    "green_dim": "#0F6E3A",   # darker green (hover / pressed)
    "text":      "#F2F2F2",   # primary text
    "muted":     "#888888",   # secondary/muted text
    "pill_bg":   "#252525",   # unselected pill
    "pill_sel":  "#1DB965",   # selected pill
    "pill_txt":  "#AAAAAA",   # unselected pill text
    "error":     "#E24B4A",
}

# ── State ──────────────────────────────────────────────────────────────────────

seller_var = None
fuel_var = None
trans_var = None

# ── Prediction ─────────────────────────────────────────────────────────────────

def predict():
    try:
        vals = []
        vals.append(int(age_entry.get()))
        vals.append(int(km_entry.get()))
        vals.append(float(mileage_entry.get()))
        vals.append(int(engine_entry.get()))
        vals.append(float(power_entry.get()))

        seats = int(seats_entry.get())
        if not (2 <= seats <= 7):
            show_error("Seats must be between 2 and 7.")
            return
        vals.append(seats)

        seller = seller_var.get()
        if seller == "Dealer":          vals.extend([1, 0, 0])
        elif seller == "Individual":    vals.extend([0, 1, 0])
        else:                           vals.extend([0, 0, 1])

        fuel_map = {
            "CNG":      [1,0,0,0,0], "Diesel":   [0,1,0,0,0],
            "Electric": [0,0,1,0,0], "LPG":      [0,0,0,1,0],
            "Petrol":   [0,0,0,0,1],
        }
        vals.extend(fuel_map.get(fuel_var.get(), [0,0,0,0,0]))

        if trans_var.get() == "Automatic":  vals.extend([1, 0])
        else:                                vals.extend([0, 1])

        if len(vals) != 16:
            show_error("Please fill in all fields.")
            return

        scaled = scaler.transform([vals])
        price  = model.predict(scaled)[0]
        result_label.config(text=format_value(price), fg=C["green"])
        car_name = car_name_entry.get().strip()
        name_part = f"{car_name}  ·  " if car_name else ""
        sub_label.config(text=f"{name_part}{age_entry.get()} yr  ·  {int(km_entry.get()):,} km  ·  {fuel_var.get()}  ·  {trans_var.get()}")
        error_label.config(text="")
    except ValueError:
        show_error("Please enter valid numeric values in all fields.")
    except Exception as e:
        show_error(f"Error: {e}")

def show_error(msg):
    error_label.config(text=msg)
    result_label.config(text="—", fg=C["muted"])
    sub_label.config(text="")

# ── Widget helpers ──────────────────────────────────────────────────────────────

def rounded_frame(parent, **kw):
    f = tk.Frame(parent, bg=C["surface"], highlightbackground=C["border"],
                 highlightthickness=1, **kw)
    return f

def section_label(parent, text):
    tk.Label(parent, text=text.upper(), bg=C["bg"], fg=C["muted"],
             font=("Helvetica", 8, "bold"), pady=0).pack(anchor="w", padx=32, pady=(18, 4))

def styled_entry(parent, width=14):
    e = tk.Entry(parent, width=width, bg=C["surface"], fg=C["text"],
                 insertbackground=C["text"], relief="flat",
                 font=("Helvetica", 13), bd=0, highlightbackground=C["border"],
                 highlightthickness=1, highlightcolor=C["green"])
    return e

def labeled_entry(parent, label, col, row, entry_width=10, colspan=1):
    cell = tk.Frame(parent, bg=C["surface"])
    cell.grid(row=row, column=col, columnspan=colspan, padx=10, pady=8, sticky="w")
    tk.Label(cell, text=label, bg=C["surface"], fg=C["muted"],
             font=("Helvetica", 9)).pack(anchor="w")
    e = styled_entry(cell, width=entry_width)
    e.pack(anchor="w", pady=(2, 0))
    return e

def pill_group(parent, options, variable, default=None):
    f = tk.Frame(parent, bg=C["surface"])
    f.pack(padx=20, pady=(8, 12), anchor="w")
    if default:
        variable.set(default)
    buttons = []
    for opt in options:
        def make_cmd(val, btns):
            def cmd():
                variable.set(val)
                for b in btns:
                    is_sel = b.cget("text") == val
                    b.config(
                        bg=C["pill_sel"] if is_sel else C["pill_bg"],
                        fg="#FFFFFF"      if is_sel else C["pill_txt"],
                        relief="flat",
                    )
            return cmd
        b = tk.Button(f, text=opt, bg=C["pill_bg"], fg=C["pill_txt"],
                      font=("Helvetica", 10), relief="flat", bd=0,
                      padx=18, pady=7, cursor="hand2",
                      activebackground=C["green_dim"], activeforeground="#fff")
        b.pack(side="left", padx=4)
        buttons.append(b)
    for b in buttons:
        b.config(command=make_cmd(b.cget("text"), buttons))
    # set default visual
    for b in buttons:
        if b.cget("text") == variable.get():
            b.config(bg=C["pill_sel"], fg="#FFFFFF")

# ── Root window ────────────────────────────────────────────────────────────────

root = tk.Tk()
root.title("Car Price Predictor")
root.geometry("620x820")
root.minsize(480, 500)
root.config(bg=C["bg"])
root.resizable(True, True)

# ScrollCanvas for overflow
canvas = tk.Canvas(root, bg=C["bg"], highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

main = tk.Frame(canvas, bg=C["bg"])
canvas_window = canvas.create_window((0, 0), window=main, anchor="nw")

def on_canvas_resize(event):
    canvas.itemconfig(canvas_window, width=event.width)
canvas.bind("<Configure>", on_canvas_resize)
main.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Mouse-wheel scroll
root.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

# ── Header ─────────────────────────────────────────────────────────────────────

header = tk.Frame(main, bg=C["bg"])
header.pack(fill="x", padx=32, pady=(28, 4))

tk.Label(header, text="Car Price", bg=C["bg"], fg=C["text"],
         font=("Helvetica", 30, "bold")).pack(side="left")
tk.Label(header, text=" Predictor", bg=C["bg"], fg=C["green"],
         font=("Helvetica", 30, "bold")).pack(side="left")

tk.Label(main, text="Enter your car's specifications for an estimated market value.",
         bg=C["bg"], fg=C["muted"], font=("Helvetica", 11)).pack(anchor="w", padx=32, pady=(0, 8))

# ── Vehicle details card ───────────────────────────────────────────────────────

section_label(main, "Vehicle Details")
card1 = rounded_frame(main)
card1.pack(fill="x", padx=24, pady=2)

name_frame = tk.Frame(card1, bg=C["surface"])
name_frame.pack(fill="x", padx=10, pady=(8, 0))
tk.Label(name_frame, text="Car Name", bg=C["surface"], fg=C["muted"],
         font=("Helvetica", 9)).pack(anchor="w")
car_name_entry = styled_entry(name_frame, width=40)
car_name_entry.pack(fill="x", pady=(2, 0))

grid = tk.Frame(card1, bg=C["surface"])
grid.pack(fill="x", padx=4, pady=4)
grid.columnconfigure(0, weight=1)
grid.columnconfigure(1, weight=1)

age_entry     = labeled_entry(grid, "Vehicle Age (yrs)", 0, 0)
km_entry      = labeled_entry(grid, "KM Driven", 1, 0)
mileage_entry = labeled_entry(grid, "Mileage (km/l)", 0, 1)
engine_entry  = labeled_entry(grid, "Engine (cc)", 1, 1)
power_entry   = labeled_entry(grid, "Max Power (bhp)", 0, 2)
seats_entry   = labeled_entry(grid, "Seats (2–7)", 1, 2)

# ── Seller type ────────────────────────────────────────────────────────────────

section_label(main, "Seller Type")
card2 = rounded_frame(main)
card2.pack(fill="x", padx=24, pady=2)
seller_var = tk.StringVar(value="Dealer")
pill_group(card2, ["Dealer", "Individual", "Trustmark Dealer"], seller_var, "Dealer")

# ── Fuel type ──────────────────────────────────────────────────────────────────

section_label(main, "Fuel Type")
card3 = rounded_frame(main)
card3.pack(fill="x", padx=24, pady=2)
fuel_var = tk.StringVar(value="Petrol")
pill_group(card3, ["CNG", "Diesel", "Electric", "LPG", "Petrol"], fuel_var, "Petrol")

# ── Transmission ───────────────────────────────────────────────────────────────

section_label(main, "Transmission")
card4 = rounded_frame(main)
card4.pack(fill="x", padx=24, pady=2)
trans_var = tk.StringVar(value="Manual")
pill_group(card4, ["Automatic", "Manual"], trans_var, "Manual")

# ── Predict button ─────────────────────────────────────────────────────────────

btn_frame = tk.Frame(main, bg=C["bg"])
btn_frame.pack(fill="x", padx=24, pady=(20, 4))

predict_btn = tk.Button(btn_frame, text="Predict Price", command=predict,
                        bg=C["green"], fg="#FFFFFF", font=("Helvetica", 14, "bold"),
                        relief="flat", bd=0, padx=24, pady=14, cursor="hand2",
                        activebackground=C["green_dim"], activeforeground="#fff")
predict_btn.pack(fill="x")

error_label = tk.Label(main, text="", bg=C["bg"], fg=C["error"], font=("Helvetica", 10))
error_label.pack(pady=(4, 0))

# ── Result card ────────────────────────────────────────────────────────────────

result_card = rounded_frame(main)
result_card.pack(fill="x", padx=24, pady=(12, 28))

tk.Label(result_card, text="ESTIMATED MARKET VALUE", bg=C["surface"], fg=C["muted"],
         font=("Helvetica", 8, "bold"), pady=6).pack(pady=(16, 0))

result_label = tk.Label(result_card, text="—", bg=C["surface"], fg=C["muted"],
                        font=("Helvetica", 36, "bold"))
result_label.pack(pady=(4, 0))

sub_label = tk.Label(result_card, text="", bg=C["surface"], fg=C["muted"],
                     font=("Helvetica", 10))
sub_label.pack(pady=(4, 20))

# ── Launch ─────────────────────────────────────────────────────────────────────

root.mainloop()