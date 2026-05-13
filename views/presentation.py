import streamlit as st

def slide_database():
    st.header("🗄️ ER-Diagram for Backing SQL Database")

    st.markdown("We stored detections and daily revenue totals in their own tables as part of our Cloud SQL Database.")

    st.image("assets/ER-diagram.png")


def slide_bh():
    st.header("What are the busiest hours of the day?")
    
    st.subheader(
            "Throughout a workday - from 7:00 AM to 4:30 PM - Lansing Building Products sees "
            "a variable amount of customers."
    )
     
    st.subheader("We wanted to determine when the busiest hours of the day were - based on hourly foot traffic."
    )


def slide_bd():
    st.header("What are the busiest days of the week?")
    
    st.subheader(
        "We also wanted to determine which days of the week were the busiest."
    )

    st.subheader(
        "Knowing peak trafficked weekdays would inform when to frontload staff."
    )


def slide_weatherftr():
    st.header("How does weather affect foot traffic and total revenue?")
    
    st.subheader(
        "We wanted to see if the weather had any effect on foot traffic."
    )

    st.subheader(
        "We looked at both temperature and precipitation to see if there was any correlation."
    )

def slide_diagram():
    st.header("Project Architecture")
    st.markdown("A professional-grade decoupled system separating our presentation, logic, and data layers:")
    
    # Render the static architecture diagram
    st.image("assets/SystemArchDiagram.png", caption="RPi + Streamlit + FastAPI Data Flow", use_container_width=True)
    
    st.markdown("""
    **Frontend:** Streamlit acts as the Presentation Layer (Frontend).\n 
    **Backend:** FastAPI acts as the Orchestrator, handling the Logic/Data Layer (Backend).\n
    **Hardware:** The Raspberry Pi captures the live feed, and OpenCV processes the frames for motion detection.\n
    **Database:** Cloud SQL acts as our storage, keeping high-frequency event data separate from business metrics.
    """)

def slide_cam_setup():
    st.header("📷Camera Setup")

    st.markdown("""
    Our Raspberry Pi was positioned at a low angle view to capture customer traffic via camera.\n
    We utilized the OpenCV library to blur distinguishing customer features for privacy.
    """)

    st.image("assets/Camera_setup_store.png", caption="Storefront Location", use_container_width=True)

    st.image("assets/Camera_streamlit.png", caption="View on the Streamlit page", use_container_width=True)

st.set_page_config(
    page_title="Measuring Foot Traffic at Lansing Building Products", layout="wide"
)
st.subheader("A Data Science Project by Asante Frye and Tyler Gaudino")
url_lansing = "https://lansingbp.com/wp-content/themes/lansing/images/logo-hi-res.png"

st.image(url_lansing, use_container_width=True)



## Slides for presentation

slides = {
        "Busiest Hours": slide_bh,
        "Busiest Days": slide_bd,
        "Weather vs. Foot Traffic and Revenue": slide_weatherftr,
        "System Arch Diagram": slide_diagram,
        "Camera Setup": slide_cam_setup 
        "ER diagram": slide_database
    }

# If there is no current slide, set it to the initial slide
if "current_slide" not in st.session_state:
    st.session_state.current_slide = "Busiest Hours"

# Sidebar Navigation of results
st.sidebar.title("Navigation")
st.session_state.current_slide = st.sidebar.radio(
    "Go to Slide", slides, index=list(slides.keys()).index(st.session_state.current_slide)
)

# Current slide

slide = st.session_state.current_slide

st.title("Measuring Foot Traffic at Lansing Building Products")


# Load slide using map
slides[slide]()

##################################
# Button based slides navigation #
##################################

# Get the index of the current slide
current_index = list(slides.keys()).index(slide)

# Load the next slide
if current_index < len(slides) - 1:
    if st.button("Next"):
        st.session_state.current_slide = list(slides.keys())[current_index + 1]

# Load the prev slide
if current_index > 0:
    if st.button("Previous"):
        st.session_state.current_slide = list(slides.keys())[current_index - 1]
