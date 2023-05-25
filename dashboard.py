import streamlit as st
import pandas as pd
import plotly.express as px


#-----Define the set-up for background-----
def set_background_color(color):
    """
    Function to set the background color of the application.
    """
    # Generate custom CSS code
    css_code = f"""
    <style>
    .stApp {{
        background-color: {color};
    }}
    </style>
    """
    # Render the CSS code
    st.markdown(css_code, unsafe_allow_html=True)

#-----Set the page configuration-----
st.set_page_config(page_title='Books',
                   page_icon=':📗:',
                   layout='wide'
                   )

#-----set the coulor -----
set_background_color('#668ba4')  # Change the value to your desired color

@st.cache_data
def load_data():
    return pd.read_parquet('dashfile.parquet')
dashboard=load_data()

#-----MAIN PAGE-----
st.markdown("<h1 style='text-align: center;'>Books Around Europe 📚🌎 </h1>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size: 26px;'>Have you ever wondered what people at your age, country or even continent have been reading? Here you will find the answers!</h1>", unsafe_allow_html=True)

#----- Calculate average rating, not considerenig 0.-----
filter_df = dashboard[dashboard['Book-Rating'] != 0]
average_rating_by_country = filter_df.groupby('Country')['Book-Rating'].mean()
average_rating_by_country = average_rating_by_country[average_rating_by_country != 0]
dashboard['Average-Rating'] = dashboard['Country'].map(average_rating_by_country).fillna(0)

dashboard = dashboard[(dashboard['Book-Rating'] != 0) & (dashboard['Year-Of-Publication'] != 0)]

#-----Adding the countries codes-----
import pycountry
def get_country_code(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        return country.alpha_3
    except:
        return None

dashboard['Country_Code'] = dashboard['Country'].apply(get_country_code)


#----- Filter the dataset to show only rows with European countries-----
europe = ['Germany', 'United Kingdom', 'Croatia', 'France',
                      'Portugal', 'Netherlands', 'Cyprus', 'Denmark',
                      'Spain', 'Austria', 'Romania', 'Italy', 'Switzerland',
                      'Finland', 'Ireland', 'Greece', 'Luxembourg', 'Slovenia',
                      'Poland', 'Belgium', 'Bulgaria', 'Sweden', 'Norway', 'Latvia',
                      'Slovakia', 'Lithuania', 'Georgia',
                      'Iceland', 'Hungary', 'Guernsey', 'Andorra', 'Malta',
                      'Ukraine', 'Monaco']
dashboard = dashboard[dashboard['Country'].isin(europe)]


#-----Europe Map-----
data_for_choropleth = dashboard[['Country_Code', 'Average-Rating', 'Country', 'Year-Of-Publication']]
#----- Sort the dataframe by 'Year-Of-Publication' column in ascending order-----
data_for_choropleth = data_for_choropleth.sort_values('Year-Of-Publication')
europe_map = px.choropleth(data_for_choropleth, locations="Country_Code",
                    color="Average-Rating",
                    hover_name="Country",
                    animation_frame="Year-Of-Publication",
                    color_continuous_scale='Purples')
europe_map.update_layout(
    title_text='Average-Rating x Year of Publication',
    title_font=dict(color='#ffffff', family='Arial, bold', size=20),
    geo=dict(projection={'type': 'natural earth'}),
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)')

europe_map.update_geos(fitbounds="locations")

container = st.container()
# Definir a largura desejada para o gráfico (90% da largura total da página)
width = '90%'
# Inserir o gráfico no contêiner com a largura definida
with container:
    st.plotly_chart(europe_map, use_container_width=True)


#-----Book x Rating (Widgets)----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='color: white;font-size: 15px;'>Selecting the Country, your views for Year of Publication and Age will change.</p>", unsafe_allow_html=True)
selected_country = st.selectbox('Select a country', sorted(dashboard['Country'].unique()))
filtered_data = dashboard[
(dashboard['Country'] == selected_country)]
st.markdown("<hr>", unsafe_allow_html=True)

years_of_publication = sorted(filtered_data['Year-Of-Publication'].unique())
selected_year = st.selectbox('Select the Year of Publication:', years_of_publication)
filtered_year = filtered_data[filtered_data['Year-Of-Publication'] == selected_year]


#-----Book x Rating (Graph)----
top_books = filtered_year.sort_values('Book-Rating', ascending=True)[:10]
yearbar = px.bar(top_books,x='Book-Rating',y='Book-Title',orientation='h', color='Book-Rating',color_continuous_scale='Blues')
yearbar.update_layout(
        title=f"Top Books for {selected_country} in {selected_year}",
        title_font=dict(color='#ffffff ', family='Arial, bold', size=20),
        height=600,
        width=800,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis_title="",
        yaxis_title="")

st.plotly_chart(yearbar)


#-----Top Book by Age (Widget)-----
ages = sorted(filtered_data['Age'].unique())
selected_age = st.selectbox('Select Age:', ages)
#-----Top Book by Age (Graph)-----
filtered_age = filtered_data[filtered_data['Age'] == selected_age]
filtered_age = filtered_age.drop_duplicates(subset='Book-Title')
top_books1 = filtered_age.sort_values('Book-Rating', ascending=False)[:10]
agebar = px.bar(top_books1,x='Book-Rating',y='Book-Title',orientation='h',color='Book-Rating',color_continuous_scale='Blues')
agebar.update_layout(
    title=f"Top Books for Age {selected_age} in {selected_country}",
    title_font=dict(color='#ffffff ', family='Arial, bold', size=20),
    height=600,
    width=1000,
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)',
    xaxis_title="",
    yaxis_title="")

st.plotly_chart(agebar)

st.markdown("<hr>", unsafe_allow_html=True)

container = st.container()
col1_width = 0.5
col2_width = 0.5
col1, col2 = st.columns([col1_width, col2_width])

#-----Correlation Age x Average_Rating-----
with col1:
    scatterplot = px.scatter(filtered_data, x='Age', y='Book-Rating', color='Country')
    scatterplot.update_layout(
    title=f"Correlation between Age and Rating in {selected_country}",
    title_font=dict(color='#ffffff ', family='Arial, bold', size=20),
    width=800,
    height=600,
    plot_bgcolor='rgba(0, 0, 0, 0)',
    paper_bgcolor='rgba(0, 0, 0, 0)')

st.plotly_chart(scatterplot, use_container_width=True)


#-----Top 10 Authors-----
with col2:
    author_counts = dashboard['Book-Author'].value_counts().reset_index()
    author_counts.columns = ['Book-Author', 'Count']
    author_counts = author_counts.sort_values('Count', ascending=False)
    top_10_authors = author_counts.head(10)
    color_palette = ['#A7C5EB', '#BFD4B6', '#E8C9A9', '#C4D9D6', '#E5D8C4', '#D2C7B0', '#A6D5D5', '#D9C9E3', '#E1D0D0', '#D8BFD8']
    author = px.bar(top_10_authors, x='Book-Author', y='Count', title='Top 10 Authors by Appearance')
    author.update_traces(marker=dict(color=color_palette))
    author.update_layout(
        title=f"Top 10 Authors in Europe",
        title_font=dict(color='#ffffff ', family='Arial, bold', size=20),
        width=800,
        height=600,
        autosize=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)')

st.plotly_chart(author, use_container_width=True)

container.markdown("""
    <style>
    .stApp {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .st-bf.st-cn.st-cq.st-co {
        width: 50%;
        padding-right: 20px;
    }
    .st-bf.st-cn.st-cq.st-co:nth-child(2) {
        padding-right: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
