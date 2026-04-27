import streamlit as st


st.set_page_config(
    page_title="Measuring Foot Traffic at Lansing Building Products", layout="wide"
)
st.subheader("A Data Science Project by Asante Frye and Tyler Gaudino")
url_lansing = "https://lansingbp.com/wp-content/themes/lansing/images/logo-hi-res.png"

st.image(url_lansing, use_container_width=True)

##Slides for presentation
slides = [
    "What Are the busiest times of the day?(By Hour)",
    "What Days of the week are the busiest?",
    "Does the Weather Affect Foot Traffic?",
    "Does the Amount of Money Made in a Day Affect Foot Traffic?",
]
# weather we can do a chart for temperatre and foot traffic, or we can do a chart for weather conditions(precip or no precip?) and foot traffic.
# both would be good
##Da

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
    st.header("What Are the busiest times of the day?(By Hour)")
    st.subheader(
        "Throughout a work day customers in at all times through 7am to 430pm. One of our main goals was to find "
        "out when the busiest times of the day were."
    )


def slide_2():
    st.header("What Days of the week are the busiest?")
    st.subheader(
        "We also wanted to find out which days of the week were the busiest. This would help us know when to have more staff on hand and when to expect more customers."
    )


def slide_3():
    st.header("Does the Weather Affect Foot Traffic?")
    st.subheader(
        "We wanted to find out if the weather had any effect on foot traffic. We looked at both temperature and precipitation to see if there was any correlation."
    )


def slide_4():
    st.header("Does the Amount of Money Made in a Day Affect Foot Traffic?")
    st.subheader(
        "We also wanted to find out if there was any correlation between the amount of money made in a day and foot traffic."
        "More money mad in a day should indicate more customers."
    )


if slide == "What Are the busiest times of the day?(By Hour)":
    slide_1()
elif slide == "What Days of the week are the busiest?":
    slide_2()
elif slide == "Does the Weather Affect Foot Traffic?":
    slide_3()
elif slide == "Does the Amount of Money Made in a Day Affect Foot Traffic?":
    slide_4()

    ##Adding a next and previous button to navigate through the slides if user would like to use instead of the sidebar.

current_index = slides.index(slide)
if current_index < len(slides) - 1:
    if st.button("Next"):
        st.session_state.current_slide = slides[current_index + 1]

if current_index > 0:
    if st.button("Previous"):
        st.session_state.current_slide = slides[current_index - 1]
