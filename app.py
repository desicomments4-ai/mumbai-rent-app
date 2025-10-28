# app.py — Mumbai Rent Compare (Mumbai Orange Theme + Emojis + Simple Mode)
import streamlit as st
import pandas as pd
from pathlib import Path
import hashlib
import re
from io import StringIO

# -------------------------
# SETTINGS
# -------------------------
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSct8s0QCmkLDS73_S87vSHi4SihIef8Zxiy9QHCkl1PeXfxwg/viewform"
CSV_PATH = "mmr_rent_data.csv"  # CSV should be in the same folder

st.set_page_config(page_title="Mumbai Rent Compare", layout="wide")

# -------------------------
# THEME (Mumbai Orange) + Global CSS
# -------------------------
st.markdown("""
<style>
:root{
  --brand:#ff6b00;
  --brand-2:#ff8200;
  --chip:#fff7ed;
  --chip-border:#ffd1a8;
  --text:#111827;
  --muted:#6b7280;
  --card:#ffffff;
  --line:#eeeeee;
}
html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
.hero {
  padding: 18px 20px; border-radius: 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #fff 60%);
  border: 1px solid var(--chip-border); margin-bottom: 12px;
}
.hero h3 { margin: 0; color: var(--text); }
.tagline { color: var(--muted); margin-top: 4px; }
.badge-legend { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
.legend-chip {
  padding: 6px 12px; border-radius: 999px; font-weight: 600; font-size: 13px;
  border: 1px solid #e7e7e7; background: #fff;
}
.legend-chip.orange {
  border-color: var(--chip-border); background: var(--chip); color: var(--text);
}
.cta-btn button {
  background: var(--brand) !important; border:none !important; color:white !important;
  font-weight:700 !important; border-radius: 10px !important; padding: 10px 14px !important;
}
.cta-btn a { /* link ko button jaisa style */
  background: var(--brand) !important; border:none !important; color:white !important;
  font-weight:700 !important; border-radius: 10px !important; padding: 10px 14px !important;
  text-decoration:none !important; display:inline-block;
}
.cta-caption { color: var(--muted); margin-top: 4px; }
.metric-card { border: 1px solid var(--line); border-radius: 12px; padding: 14px; background: var(--card); }
.small { font-size: 12px; color: var(--muted); }
.compare-card { border:1px solid var(--line); border-radius:12px; padding:14px; background:var(--card); }
.kv{display:flex;justify-content:space-between;margin:4px 0;font-size:14px}
.kv b{color:var(--text)} .kv span{color:#374151}
hr{ border:none; border-top:1px solid var(--line); margin: 8px 0 16px; }
.footer { color: var(--muted); font-size: 13px; }
.section-title { display:flex; align-items:center; gap:8px; }
.download-btn button { background: #1118270d !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Cache-busting + CSV load
# -------------------------
def file_hash(path:str)->str:
  return hashlib.md5(Path(path).read_bytes()).hexdigest()

@st.cache_data
def load_csv(path:str, version:str)->pd.DataFrame:
  return pd.read_csv(path)

try:
  df = load_csv(CSV_PATH, file_hash(CSV_PATH))
except Exception as e:
  st.error(f"CSV load error: {e}")
  st.info("Ensure 'mmr_rent_data.csv' is in the same folder as app.py")
  st.stop()

# -------------------------
# Parsing & Ranking
# -------------------------
for c in ["rent_median_1bhk","rent_min_1bhk","rent_max_1bhk"]:
  df[c] = pd.to_numeric(df[c], errors="coerce")

def parse_deposit_ratio(s:str)->float:
  if pd.isna(s): return 4.0
  s = str(s).lower().strip()
  m = re.search(r"(\d+(\.\d+)?)\s*x", s)
  if m: return float(m.group(1))
  m2 = re.search(r"\d+(\.\d+)?", s)
  if m2: return float(m2.group(0))
  return 4.0
df["deposit_months_min"] = df["deposit_ratio"].apply(parse_deposit_ratio)

western = ["Bandra","Khar","Santacruz","Andheri","Jogeshwari","Goregaon","Malad","Kandivali","Borivali","Dahisar","Mira Road","Bhayander","Vasai","Naigaon","Nalasopara","Virar"]
central = ["Dadar","Matunga","Sion","Kurla","Ghatkopar","Vikhroli","Bhandup","Mulund","Thane","Kalwa","Mumbra","Diva","Dombivli","Kalyan","Ambernath","Badlapur","Vangani","Titwala"]
harbour = ["Chembur","Govandi","Mankhurd"]
south   = ["Lower Parel","Worli","Prabhadevi","Mahim","Wadala","Cuffe Parade","Malabar Hill","Colaba"]
navi    = ["Vashi","Airoli","Kopar Khairane","Ghansoli","Turbhe","Sanpada","Seawoods","Nerul","Belapur","Kharghar","Kamothe","Ulwe","New Panvel","Panvel","Taloja"]

def _first_idx(area_lower:str, names:list[str]):
  for i,name in enumerate(names):
    if name.lower() in area_lower: return i
  return None

def proximity_score(area:str, region:str)->int:
  a = (area or "").lower(); r = (region or "").lower()
  if "south" in r or any(k.lower() in a for k in south):
    i=_first_idx(a,south);  return i if i is not None else 0
  if "western" in r or any(k.lower() in a for k in western):
    i=_first_idx(a,western);return i if i is not None else 50
  if "central" in r or any(k.lower() in a for k in central):
    i=_first_idx(a,central);return i if i is not None else 50
  if "harbour" in r or "chembur" in a:
    i=_first_idx(a,harbour);return i if i is not None else 30
  if "navi" in r or any(k.lower() in a for k in navi):
    i=_first_idx(a,navi);   return i if i is not None else 40
  return 60
df["proximity_score"] = df.apply(lambda x: proximity_score(str(x["area"]), str(x["region"])), axis=1)

df = df.sort_values(
  by=["rent_median_1bhk","deposit_months_min","proximity_score","area"],
  ascending=[True, True, True, True]
).reset_index(drop=True)

df["global_rank"] = df["rent_median_1bhk"].rank(method="dense", ascending=True).astype("Int64")

def rank_badge(r:int)->str:
  if pd.isna(r): return ""
  r = int(r)
  if   1 <= r <= 15: return "🟢 Budget"
  elif 16 <= r <= 25: return "🔵 Value"
  elif 26 <= r <= 40: return "🟡 Mid"
  elif 41 <= r <= 50: return "🟠 Upper Mid"
  elif 51 <= r <= 55: return "🔴 Premium"
  else: return "👑 Luxury"
df["badge"] = df["global_rank"].apply(rank_badge)

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filters")
zones = sorted(df["zone"].dropna().unique().tolist())
zone_selected = st.sidebar.multiselect(
  "Zone choose karo",
  options=zones,
  default=[],                       # default empty
  placeholder="Type to add zones…"  # type to get suggestions
)

min_r, max_r = int(df["rent_median_1bhk"].min()), int(df["rent_median_1bhk"].max())
rent_range = st.sidebar.slider("1BHK Median (₹/mo)", min_r, max_r, (min_r, max_r), step=500)

search = st.sidebar.text_input("Area search (optional)", "")
group_zone = st.sidebar.checkbox("Zone-wise grouping (optional)", value=False)
sort_choice = st.sidebar.selectbox(
  "Sort by",
  ["Global Rank (asc)", "Median 1BHK (asc)", "Median 1BHK (desc)", "Area (A→Z)"],
  index=0
)

if st.sidebar.button("Reload latest data"):
  st.cache_data.clear()
  st.experimental_rerun()

# -------------------------
# HERO + CTA
# -------------------------
st.markdown("""
<div class="hero">
  <h3>🏙️ Mumbai Rent Compare</h3>
  <div class="tagline">Find best areas by rent • Filters • Ranking • Compare</div>
  <div class="badge-legend">
    <span class="legend-chip orange">🟢 Budget</span>
    <span class="legend-chip orange">🔵 Value</span>
    <span class="legend-chip orange">🟡 Mid</span>
    <span class="legend-chip orange">🟠 Upper Mid</span>
    <span class="legend-chip orange">🔴 Premium</span>
    <span class="legend-chip orange">👑 Luxury</span>
  </div>
</div>
""", unsafe_allow_html=True)

cta_col1, cta_col2 = st.columns([1,3])
with cta_col1:
  # Direct link to open Google Form in a new tab (iframe removed)
  st.markdown(
    f'<div class="cta-btn"><a href="{FORM_URL}" target="_blank" rel="noopener noreferrer">🏠 Flat chahiye? Submit details</a></div>',
    unsafe_allow_html=True
  )
with cta_col2:
  st.markdown('<div class="cta-caption">Phone ya Email – kisi ek se contact. No spam.</div>', unsafe_allow_html=True)

# -------------------------
# METRICS
# -------------------------
total_areas = len(df); cheapest_row = df.iloc[0]; highest_row  = df.iloc[-1]
m1, m2, m3 = st.columns(3)
with m1:
  st.markdown('<div class="metric-card">', unsafe_allow_html=True)
  st.metric("Total Areas", f"{total_areas}")
  st.markdown('<div class="small">Across full MMR coverage</div></div>', unsafe_allow_html=True)
with m2:
  st.markdown('<div class="metric-card">', unsafe_allow_html=True)
  st.metric("Cheapest Median (1BHK)", f"₹{int(cheapest_row['rent_median_1bhk']):,}", help=f"{cheapest_row['area']} • {cheapest_row['zone']}")
  st.markdown('</div>', unsafe_allow_html=True)
with m3:
  st.markdown('<div class="metric-card">', unsafe_allow_html=True)
  st.metric("Highest Median (1BHK)", f"₹{int(highest_row['rent_median_1bhk']):,}", help=f"{highest_row['area']} • {highest_row['zone']}")
  st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FILTER + SORT + TABLE
# -------------------------
# Zone filter only when user selected something; otherwise show all
mask = df["rent_median_1bhk"].between(*rent_range)
if zone_selected:
  mask &= df["zone"].isin(zone_selected)

if search.strip():
  s = search.strip().lower()
  mask &= df["area"].str.lower().str.contains(s)

filtered = df.loc[mask].copy()

if group_zone:
  filtered = filtered.sort_values(
    by=["zone","rent_median_1bhk","deposit_months_min","proximity_score","area"],
    ascending=[True, True, True, True, True]
  )
else:
  if   sort_choice == "Global Rank (asc)":
    filtered = filtered.sort_values(by=["global_rank","area"], ascending=[True, True])
  elif sort_choice == "Median 1BHK (asc)":
    filtered = filtered.sort_values(by=["rent_median_1bhk","area"], ascending=[True, True])
  elif sort_choice == "Median 1BHK (desc)":
    filtered = filtered.sort_values(by=["rent_median_1bhk","area"], ascending=[False, True])
  else:
    filtered = filtered.sort_values(by=["area"], ascending=True)

st.markdown('<div class="section-title"><span>📊</span><h4 style="margin:0">Rent Ranking</h4></div>', unsafe_allow_html=True)

def fmt_money(v):
  try: return f"₹{int(v):,}"
  except: return v

show_cols = ["global_rank","badge","zone","area","region","rent_median_1bhk","rent_min_1bhk","rent_max_1bhk","deposit_ratio"]
rename = {
  "global_rank":"Rank","badge":"Badge","zone":"Zone","area":"Area","region":"Region",
  "rent_median_1bhk":"Median 1BHK","rent_min_1bhk":"Low","rent_max_1bhk":"High","deposit_ratio":"Deposit"
}
view = filtered[show_cols].rename(columns=rename)
for col in ["Median 1BHK","Low","High"]:
  view[col] = view[col].apply(fmt_money)

st.dataframe(view, use_container_width=True, hide_index=True)

# -------------------------
# COMPARE 2 AREAS
# -------------------------
st.markdown('<div class="section-title"><span>⚖️</span><h4 style="margin:0">Compare Areas</h4></div>', unsafe_allow_html=True)
areas_list = df["area"].dropna().sort_values().unique().tolist()
colA, colB = st.columns(2)
with colA: a1 = st.selectbox("Area A", areas_list, index=0)
with colB: a2 = st.selectbox("Area B", areas_list, index=min(1,len(areas_list)-1))

def pick(a): return df.loc[df["area"]==a].iloc[0]
if a1 and a2:
  r1, r2 = pick(a1), pick(a2)
  c1, c2 = st.columns(2)
  for col, rr, title in [(c1,r1,a1),(c2,r2,a2)]:
    with col:
      st.markdown(f"<div class='compare-card'><h4 style='margin:0'>{title}</h4>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Rank</b><span>{int(rr['global_rank'])}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Badge</b><span>{rr['badge']}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Zone</b><span>{rr['zone']}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Region</b><span>{rr['region']}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Median 1BHK</b><span>₹{int(rr['rent_median_1bhk']):,}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Low–High</b><span>₹{int(rr['rent_min_1bhk']):,} – ₹{int(rr['rent_max_1bhk']):,}</span></div>", unsafe_allow_html=True)
      st.markdown(f"<div class='kv'><b>Deposit</b><span>{rr['deposit_ratio']}</span></div></div>", unsafe_allow_html=True)

# -------------------------
# DOWNLOAD FILTERED CSV
# -------------------------
st.markdown('<div class="section-title"><span>📥</span><h4 style="margin:0">Export</h4></div>', unsafe_allow_html=True)
csv_buf = StringIO()
download_cols = filtered[[
  "global_rank","zone","area","region","rent_median_1bhk","rent_min_1bhk","rent_max_1bhk","deposit_ratio","badge"
]].rename(columns={
  "global_rank":"rank","badge":"rank_badge","rent_median_1bhk":"median_1bhk","rent_min_1bhk":"low","rent_max_1bhk":"high"
})
download_cols.to_csv(csv_buf, index=False)
st.markdown('<div class="download-btn">', unsafe_allow_html=True)
st.download_button("⬇️ Download filtered CSV", csv_buf.getvalue(), file_name="mumbai_rent_compare_filtered.csv", mime="text/csv")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FOOTER
# -------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="footer">✅ No Spam • 🤝 Genuine Help • Made in Mumbai ❤️</div>', unsafe_allow_html=True)
