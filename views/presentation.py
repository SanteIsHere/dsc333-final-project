import streamlit as st


st.set_page_config(
    page_title="Measuring Foot Traffic at Lansing Building Products", layout="wide"
)
st.subheader("A Data Science Project by Asante Frye and Tyler Gaudino")
url_lansing = "https://lansingbp.com/wp-content/themes/lansing/images/logo-hi-res.png"

st.image(url_lansing, use_container_width=True)

##Slides for presentation
slides = [
    "Busiest Hours",
    "Busiest Days",
    "Weather vs. Foot Traffic and Revenue",
]

# Reset current slide, if one is not already in state cache.
if "current_slide" not in st.session_state:
    st.session_state.current_slide = slides[0]

# Sidebar Navigation of results
st.sidebar.title("Navigation")
st.session_state.current_slide = st.sidebar.radio(
    "Go to Slide", slides, index=slides.index(st.session_state.current_slide)
)

# Current slide

slide = st.session_state.current_slide

st.title("Measuring Foot Traffic at Lansing Building Products")


def slide_1():
    st.header("What are the busiest hours of the day?")
    
    st.subheader(
            "Throughout a workday - from 7:00 AM to 4:30 PM - Lansing Building Products sees "
            "a variable amount of customers."
    )
     
    st.subheader("We wanted to determine when the busiest hours of the day were - based on hourly foot traffic."
    )


def slide_2():
    st.header("What are the busiest days of the week?")
    
    st.subheader(
        "We also wanted to determine which days of the week were the busiest."
    )

    st.subheader(
        "Knowing peak trafficked weekdays would inform when to frontload staff."
    )


def slide_3():
    st.header("How does weather affect foot traffic and total revenue?")
    
    st.subheader(
        "We wanted to see if the weather had any effect on foot traffic."
    )

    st.subheader(
        "We looked at both temperature and precipitation to see if there was any correlation."
    )


if slide == "Busiest Hours":
    slide_1()
elif slide == "Busiest Days":
    slide_2()
else: # Weather, Foot Traffic/Rev Slide
    slide_3()

##################################
# Button based slides navigation #
##################################

# Get the index of the current slide
current_index = slides.index(slide)

# Load the next slide
if current_index < len(slides) - 1:
    if st.button("Next"):
        st.session_state.current_slide = slides[current_index + 1]

# Load the prev slide
if current_index > 0:
    if st.button("Previous"):
        st.session_state.current_slide = slides[current_index - 1]
