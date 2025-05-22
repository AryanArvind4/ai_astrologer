# ai_astrologer_app.py (Streamlit Version - With Theme & Radar Chart)
 
import streamlit as st
from openai import OpenAI
import datetime
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.const import SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN, ASC


client = OpenAI(api_key="add_your_own_api_key")

st.set_page_config(page_title="AI Astrologer", layout="centered")
st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom right, #141e30, #243b55);
            color: #ffffff;
        }
        .zodiac-card {
            padding: 15px;
            margin: 10px;
            background: linear-gradient(145deg, #1f2c3a, #2d3e50);
            border-radius: 15px;
            color: white;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            text-align: center;
        }
        .zodiac-title {
            font-size: 20px;
            font-weight: bold;
            color: #ffdd57;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 AI Astrologer")
st.write("Get your personalized astrology and numerology reading using AI.")

with st.form("astro_form"):
    name = st.text_input("Your Name")
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
    time = st.text_input("Time of Birth (HH:MM format)")
    place = st.text_input("Place of Birth")
    favorite_number = st.text_input("Favorite Number")
    submit = st.form_submit_button("🔍 Get My Reading")

if submit:
    with st.spinner("Consulting the stars..."):
        prompt = (
            f"I want you to act as a professional astrologer and give a detailed astrology and numerology reading for someone named {name} born on {dob} at {time} in {place}. "
            f"Their favorite number is {favorite_number}. Also, rate their Love, Career, Health, and Spirituality from 1 to 10."
        )
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            st.success("Here's your personalized reading:")
            st.markdown(result)

            # Simulated radar data (extracted manually or via parsing in production)
            st.subheader("🔭 Life Aspect Overview")
            categories = ['Love', 'Career', 'Health', 'Spirituality']
            values = [8, 7, 6, 9]  # Placeholder values

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Your Chart',
                line=dict(color='gold')
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor="#1c1c1c",
                    radialaxis=dict(visible=True, range=[0, 10], color='white'),
                    angularaxis=dict(color='white')
                ),
                showlegend=False,
                plot_bgcolor='#1c1c1c',
                paper_bgcolor='#1c1c1c',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    # Zodiac Positions
    st.divider()
    st.subheader("🪐 Your Natal Planetary Positions")

    def decimal_to_dms(decimal_deg):
        is_negative = decimal_deg < 0
        decimal_deg = abs(decimal_deg)
        degrees = int(decimal_deg)
        minutes_full = (decimal_deg - degrees) * 60
        minutes = int(minutes_full)
        seconds = int((minutes_full - minutes) * 60)
        dms = f"{'-' if is_negative else ''}{degrees}:{minutes}:{seconds}"
        return dms

    def generate_zodiac_positions(dob, tob, place_name):
        geolocator = Nominatim(user_agent="astro_app")
        location = geolocator.geocode(place_name)
        if not location:
            return {"error": "Location not found. Please enter a valid city/town."}

        lat_dms = decimal_to_dms(location.latitude)
        lon_dms = decimal_to_dms(location.longitude)

        date_str = dob.strftime('%Y/%m/%d')
        time_str = tob if tob else "12:00"

        dt = Datetime(date_str, time_str, '+05:30')
        pos = GeoPos(lat_dms, lon_dms)

        chart = Chart(dt, pos)
        planets = [SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN, ASC]
        positions = {body: chart.get(body).sign for body in planets}

        return positions

    zodiac_data = generate_zodiac_positions(dob, time, place)
    if "error" in zodiac_data:
        st.error(zodiac_data["error"])
    else:
        st.success("Zodiac Signs for Your Planetary Positions")
        cols = st.columns(4)
        for i, (planet, sign) in enumerate(zodiac_data.items()):
            with cols[i % 4]:
                st.markdown(f"""
                    <div class='zodiac-card'>
                        <div class='zodiac-title'>{planet}</div>
                        <div>{sign}</div>
                    </div>
                """, unsafe_allow_html=True)

# Chatbot Section
st.divider()
st.subheader("💬 Ask Our AI Astrologer Anything")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert astrologer. Answer questions with deep knowledge of astrology and numerology."}
    ]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask your astrology question here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages
                )
                result = response.choices[0].message.content
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
