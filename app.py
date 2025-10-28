import streamlit as st

# -------------------------------
# Page config & light styling
# -------------------------------
st.set_page_config(
    page_title="GharJugaad – Mumbai Rent Finder",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
/* Softer look */
.block-container {padding-top: 1rem;}
h1, h2, h3 { letter-spacing: 0.2px; }
.hero {padding: 24px; border-radius: 18px; background: #f7f7fb; border:1px solid #eee;}
.badge {display:inline-block; padding: 4px 10px; border:1px solid #e5e7eb; border-radius: 999px; font-size: 12px;}
.card {padding: 16px; border:1px solid #eee; border-radius: 16px; background: white;}
.cta {display:inline-block; padding: 10px 14px; border-radius:12px; text-decoration:none; border:1px solid #e5e7eb;}
.cta:hover{background:#f1f5f9}
.stButton>button {border-radius:12px; padding:10px 16px;}
.stSelectbox > div > div {border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Data: Zones & Areas (edit to your real list)
# -------------------------------
ZONES = ["South Mumbai", "Western Suburbs", "Central Mumbai", "Harbour", "Navi Mumbai", "Thane"]
AREAS_BY_ZONE = {
    "South Mumbai": ["Colaba","Cuffe Parade","Fort","Marine Drive","Churchgate","Nariman Point"],
    "Western Suburbs": ["Bandra","Khar","Santacruz","Juhu","Andheri","Goregaon","Malad","Kandivali","Borivali"],
    "Central Mumbai": ["Dadar","Parel","Lower Parel","Worli","Sion","Matunga"],
    "Harbour": ["Chembur","Wadala","Anushakti Nagar","Govandi","Mankhurd"],
    "Navi Mumbai": ["Vashi","Nerul","Seawoods","Kharghar","Belapur","Airoli","Ghansoli","Kopar Khairane"],
    "Thane": ["Thane West","Thane East","Hiranandani Estate","Ghodbunder Road","Vartak Nagar"]
}
ALL_AREAS = sorted({a for lst in AREAS_BY_ZONE.values() for a in lst})

# -------------------------------
# Helpers: simple “multi-page” via query params
# -------------------------------
def get_page() -> str:
    # Streamlit ≥1.32 has st.query_params
    qp = st.query_params
    return qp.get("page", "home")

def go_to(page: str):
    # Switch page in same tab
    st.query_params["page"] = page
    st.rerun()

# -------------------------------
# Sidebar filters (used on both pages)
# -------------------------------
def sidebar_filters():
    with st.sidebar:
        st.markdown("### Filters")

        zone = st.selectbox(
            "Zone चुनें",
            options=ZONES,
            index=None,  # <- no auto-select
            placeholder="Select a zone…"
        )

        if zone:
            area_options = AREAS_BY_ZONE.get(zone, [])
        else:
            area_options = ALL_AREAS

        area = st.selectbox(
            "Area (type to search)",
            options=area_options,
            index=None,
            placeholder="Start typing area name…"
        )

        ptype = st.selectbox(
            "Property Type",
            options=["1 RK","1 BHK","2 BHK","3 BHK","Studio","Other"],
            index=None,
            placeholder="Select property type…"
        )

        budget = st.number_input(
            "Monthly Budget (₹)",
            min_value=5000,
            step=1000,
            value=None,
            placeholder="e.g. 30000"
        )

    return {"zone": zone, "area": area, "ptype": ptype, "budget": budget}

# -------------------------------
# HOME PAGE
# -------------------------------
def render_home():
    st.markdown(
        "<div class='hero'><h2>🏠 Mumbai Rent Finder</h2>"
        "<p>Compare rents by zone, area & property type. Share with friends & find the best deal.</p>"
        "<span class='badge'>GharJugaad</span></div>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1,1], gap="large")
    with col1:
        st.subheader("Need a flat?")
        st.write("Fill a quick form and we’ll contact you with options matched to your budget & areas.")
        if st.button("📝 Flat chahiye (Open Form)"):
            go_to("form")

        # New tab link using query param (?page=form)
        st.markdown(
            "<br><a class='cta' href='/?page=form' target='_blank'>📝 Flat chahiye (Open in New Tab)</a>",
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("Quick search")
        st.write("Use filters in the left sidebar. No defaults selected—choose your own zone & area.")
        st.markdown("<div class='card'>Tip: Start typing the area name to see suggestions.</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("##### Recently searched hotspots (demo)")
    st.markdown("Bandra • Andheri • Vashi • Kharghar • Dadar • Chembur")

# -------------------------------
# FORM PAGE
# -------------------------------
def render_form():
    st.title("📝 Flat Request Form")

    st.markdown(
        "[← Back to Home](/?page=home)",
        unsafe_allow_html=False
    )

    st.caption("Tell us what you’re looking for. We’ll reach out on WhatsApp with shortlisted options.")

    # We can show the same filters on the left for context if you want
    # (already rendered outside)

    with st.form("flat_request", clear_on_submit=False):
        name = st.text_input("Your Name")
        phone = st.text_input("Phone (WhatsApp preferred)")
        move_in = st.text_input("Preferred Move-in (Month/Timeline)")
        notes = st.text_area("Any special requirement (near metro, pet friendly, furnished, etc.)")

        submitted = st.form_submit_button("Submit Request ✅")
        if submitted:
            # TODO: Hook to Google Sheet / DB / Email.
            # For now just show success.
            st.success("Thanks! Your request has been received. Our team will contact you soon.")
            st.balloons()

    st.divider()
    st.markdown("**Privacy:** We never share your number. We’ll only use it to contact you about rentals.")

# -------------------------------
# APP ENTRY
# -------------------------------
filters = sidebar_filters()
page = get_page()

if page == "form":
    render_form()
else:
    render_home()
