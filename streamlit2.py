import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from openai import OpenAI
import os
from dotenv import load_dotenv  

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Hospital Location Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()  # Load environment variables from .env file
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

# Define all criteria with their weights
criteria_data = {
    "Criterion": [
        "Population density within service area",
        "Age distribution of population",
        "Income levels and economic status",
        "Population growth projections",
        "Disease prevalence patterns",
        "Healthcare utilization rates",
        "Cultural and religious considerations",
        "Language diversity",
        "Education levels",
        "Insurance coverage patterns",
        "Proximity to major roads and highways",
        "Public transportation availability",
        "Emergency vehicle access",
        "Traffic patterns and congestion",
        "Parking availability and capacity",
        "Pedestrian and bicycle accessibility",
        "Distance from residential areas",
        "Travel time analysis",
        "Helicopter landing capability",
        "Airport proximity for medical transport",
        "Electrical power supply reliability",
        "Water supply quality and quantity",
        "Sewage and waste management systems",
        "Telecommunications infrastructure",
        "Internet connectivity and bandwidth",
        "Gas supply availability",
        "Storm water drainage",
        "Soil conditions and bearing capacity",
        "Topography and site stability",
        "Environmental hazards assessment",
        "Existing hospitals within service area",
        "Specialty services availability",
        "Bed capacity in region",
        "Market share analysis",
        "Service gaps identification",
        "Quality ratings of competitors",
        "Referral patterns",
        "Medical professional availability",
        "Partnership opportunities",
        "Market saturation levels",
        "Zoning regulations compliance",
        "Building codes and standards",
        "Healthcare licensing requirements",
        "Environmental regulations",
        "Fire safety requirements",
        "Accessibility standards (ADA/local)",
        "Parking requirements",
        "Height and setback restrictions",
        "Land use permissions",
        "Future development restrictions",
        "Land acquisition costs",
        "Construction costs estimation",
        "Operational cost projections",
        "Revenue potential analysis",
        "Insurance and liability costs",
        "Tax implications",
        "Financing availability",
        "Return on investment projections",
        "Break-even analysis",
        "Economic incentives available",
        "Climate conditions analysis",
        "Environmental impact assessment",
        "Sustainability opportunities",
        "Energy efficiency potential",
        "Natural disaster risk assessment",
        "Air quality considerations",
        "Noise pollution levels",
        "Green building certification potential",
        "Renewable energy feasibility",
        "Water conservation opportunities"
    ],
    "Weight": [
        25, 25, 25, 25, 25, 25, 25, 25, 25, 25,
        20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
        15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
        15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        5, 5, 5, 5, 5, 5, 5, 5, 5, 5
    ],
    "Category": [
        "Demographic", "Demographic", "Demographic", "Demographic", "Demographic", 
        "Demographic", "Demographic", "Demographic", "Demographic", "Demographic",
        "Accessibility", "Accessibility", "Accessibility", "Accessibility", "Accessibility", 
        "Accessibility", "Accessibility", "Accessibility", "Accessibility", "Accessibility",
        "Infrastructure", "Infrastructure", "Infrastructure", "Infrastructure", "Infrastructure", 
        "Infrastructure", "Infrastructure", "Infrastructure", "Infrastructure", "Infrastructure",
        "Competitive", "Competitive", "Competitive", "Competitive", "Competitive", 
        "Competitive", "Competitive", "Competitive", "Competitive", "Competitive",
        "Regulatory", "Regulatory", "Regulatory", "Regulatory", "Regulatory", 
        "Regulatory", "Regulatory", "Regulatory", "Regulatory", "Regulatory",
        "Financial", "Financial", "Financial", "Financial", "Financial", 
        "Financial", "Financial", "Financial", "Financial", "Financial",
        "Environmental", "Environmental", "Environmental", "Environmental", "Environmental", 
        "Environmental", "Environmental", "Environmental", "Environmental", "Environmental"
    ]
}

# Create DataFrame
criteria_df = pd.DataFrame(criteria_data)

# Initialize session state for authentication and location data
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'locations_configured' not in st.session_state:
    st.session_state.locations_configured = False

if 'location_names' not in st.session_state:
    st.session_state.location_names = {
        'Location 1': 'Downtown Area',
        'Location 2': 'Suburban District',
        'Location 3': 'Rural Outskirts'
    }

if 'location_data' not in st.session_state:
    st.session_state.location_data = {}

if 'ai_inputs' not in st.session_state:
    st.session_state.ai_inputs = {}

if 'ai_explanations' not in st.session_state:
    st.session_state.ai_explanations = {}

if 'criterion_prompts' not in st.session_state:
    st.session_state.criterion_prompts = {}

# Login function
def login():
    st.title("🏥 Hospital Location Analysis Dashboard")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username == "saad" and password == "saad":
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

# Location configuration function
def configure_locations():
    st.title("🏥 Configure Hospital Locations")
    st.markdown("---")
    
    st.info("Please configure the names for your three potential hospital locations. These names will be used throughout the analysis and cannot be changed later.")
    
    with st.form("location_config_form"):
        st.subheader("Location Names")
        
        loc1 = st.text_input("Location 1 Name", value=st.session_state.location_names['Location 1'])
        loc2 = st.text_input("Location 2 Name", value=st.session_state.location_names['Location 2'])
        loc3 = st.text_input("Location 3 Name", value=st.session_state.location_names['Location 3'])
        
        submit_button = st.form_submit_button("Save Locations and Continue")
        
        if submit_button:
            if not loc1 or not loc2 or not loc3:
                st.error("Please provide names for all three locations.")
            elif loc1 == loc2 or loc1 == loc3 or loc2 == loc3:
                st.error("Location names must be unique.")
            else:
                st.session_state.location_names = {
                    'Location 1': loc1,
                    'Location 2': loc2,
                    'Location 3': loc3
                }
                st.session_state.locations_configured = True
                
                # Initialize data structures with the fixed location names
                loc_names = [loc1, loc2, loc3]
                
                st.session_state.location_data = {
                    loc1: pd.Series([np.nan] * len(criteria_df), index=criteria_df['Criterion']),
                    loc2: pd.Series([np.nan] * len(criteria_df), index=criteria_df['Criterion']),
                    loc3: pd.Series([np.nan] * len(criteria_df), index=criteria_df['Criterion'])
                }
                
                st.session_state.ai_inputs = {
                    criterion: {
                        loc1: '',
                        loc2: '',
                        loc3: ''
                    } for criterion in criteria_df['Criterion']
                }
                
                st.session_state.ai_explanations = {
                    criterion: '' for criterion in criteria_df['Criterion']
                }
                
                st.session_state.criterion_prompts = {
                    criterion: '' for criterion in criteria_df['Criterion']
                }
                
                st.success("Locations configured successfully!")
                st.rerun()

# Function to calculate scores
def calculate_scores(location_scores, weights):
    # Filter out criteria with missing values
    available_criteria = weights[~location_scores.isna()].index
    available_weights = weights[available_criteria]
    available_scores = location_scores[available_criteria]
    
    # Calculate weighted score
    if len(available_criteria) > 0:
        weighted_score = np.sum(available_scores * available_weights) / np.sum(available_weights)
        return weighted_score, len(available_criteria)
    else:
        return 0, 0

# Function for TOPSIS algorithm
def topsis_scores(data, weights, impacts):
    # Normalize the decision matrix
    norm_data = data / np.sqrt(np.sum(data**2, axis=0))
    
    # Apply weights
    weighted_norm = norm_data * weights
    
    # Determine ideal best and ideal worst
    ideal_best = np.max(weighted_norm, axis=0) if impacts else np.min(weighted_norm, axis=0)
    ideal_worst = np.min(weighted_norm, axis=0) if impacts else np.max(weighted_norm, axis=0)
    
    # Calculate separation measures
    s_best = np.sqrt(np.sum((weighted_norm - ideal_best)**2, axis=1))
    s_worst = np.sqrt(np.sum((weighted_norm - ideal_worst)**2, axis=1))
    
    # Calculate performance score
    performance = s_worst / (s_best + s_worst)
    
    return performance

# Function to get AI score for a specific criterion
def get_ai_criterion_score(criterion, weight, loc1_info, loc2_info, loc3_info, custom_prompt=""):
    if client is None:
        return {"loc_a_score": 5, "loc_b_score": 5, "loc_c_score": 5, "explanation": "OpenAI API not available. Using default scores."}
    
    try:
        prompt =f"""
        As a healthcare facility planning expert, evaluate three potential hospital locations for the criterion: {criterion} (Weight: {weight}).

        The locations to evaluate are:
        - {st.session_state.location_names['Location 1']}
        - {st.session_state.location_names['Location 2']}
        - {st.session_state.location_names['Location 3']}

        Here is the information for each location:
        - {st.session_state.location_names['Location 1']}: {loc1_info}
        - {st.session_state.location_names['Location 2']}: {loc2_info}
        - {st.session_state.location_names['Location 3']}: {loc3_info}
        """
        
        # Add custom prompt if provided
        if custom_prompt:
            prompt += f"\n\nAdditional instructions: {custom_prompt}"
        
        prompt += """
        \n\nPlease provide a score from 0 to 10 for each location, with 10 being the best possible score.
        Also provide a brief explanation for your scores.
        USe internet where necessary to inform your evaluation.
        Return your response in JSON format with the following structure:
        {
            "loc_a_score": <score>,
            "loc_b_score": <score>,
            "loc_c_score": <score>,
            "explanation": "Your explanation here"
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a healthcare facility planning expert providing analysis on potential hospital locations.USE INTERNET WHERE NECESSARY. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"loc_a_score": 5, "loc_b_score": 5, "loc_c_score": 5, "explanation": f"Error: {str(e)}"}

# Function to get AI insights for overall comparison
def get_ai_insights(location_data, criteria_df, scores, ai_inputs, location_names):
    if client is None:
        return "OpenAI API not available. Please set your API key to enable AI insights."
    
    try:
        # Prepare data for AI
        prompt = f"""
        Analyze these three hospital locations based on the following scores and criteria:
        
        {location_names[0]}: Overall Score = {scores[0]:.2f}
        {location_names[1]}: Overall Score = {scores[1]:.2f}
        {location_names[2]}: Overall Score = {scores[2]:.2f}
        
        The evaluation is based on these criteria with weights:
        {criteria_df[['Criterion', 'Weight', 'Category']].to_string()}
        
        Additional information provided for each criterion:
        """
        
        # Add the AI inputs for context
        for criterion in criteria_df['Criterion']:
            prompt += f"\n\n{criterion} (Weight: {criteria_df[criteria_df['Criterion'] == criterion]['Weight'].iloc[0]}):"
            prompt += f"\n- {location_names[0]}: {ai_inputs[criterion][location_names[0]]}"
            prompt += f"\n- {location_names[1]}: {ai_inputs[criterion][location_names[1]]}"
            prompt += f"\n- {location_names[2]}: {ai_inputs[criterion][location_names[2]]}"
        
        prompt += """
        \n\nPlease provide:
        1. A comparison of the three locations
        2. Strengths and weaknesses of each location
        3. Which location you would recommend and why
        4. Any potential risks or considerations for the recommended location
        
        Keep your response concise but informative.
        """
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a healthcare facility planning expert providing analysis on potential hospital locations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI insights: {str(e)}"

# Main application flow
if not st.session_state.authenticated:
    login()
elif not st.session_state.locations_configured:
    configure_locations()
else:
    # Main app after login and location configuration
    st.title("🏥 Hospital Location Analysis Dashboard")
    
    # Get the fixed location names
    loc_names = [
        st.session_state.location_names['Location 1'],
        st.session_state.location_names['Location 2'],
        st.session_state.location_names['Location 3']
    ]
    
    # Sidebar
    with st.sidebar:
        st.header("Current Locations")
        st.info(f"**Location 1:** {loc_names[0]}")
        st.info(f"**Location 2:** {loc_names[1]}")
        st.info(f"**Location 3:** {loc_names[2]}")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.locations_configured = False
            st.rerun()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Data Input", "AI Scoring", "Scores Overview", "Detailed Analysis", "AI Insights"])
    
    with tab1:
        st.header("Location Data Input")
        st.write("Enter scores for each location (0-10 scale) or leave blank if data is not available")
        
        # Category selection for filtered input
        categories = criteria_df['Category'].unique()
        selected_category = st.selectbox("Filter by category:", ["All"] + list(categories))
        
        if selected_category == "All":
            filtered_criteria = criteria_df
        else:
            filtered_criteria = criteria_df[criteria_df['Category'] == selected_category]
        
        # Create input form
        for idx, row in filtered_criteria.iterrows():
            criterion = row['Criterion']
            weight = row['Weight']
            category = row['Category']
            
            st.subheader(f"{criterion} (Weight: {weight}, Category: {category})")
            cols = st.columns(3)
            
            with cols[0]:
                score1 = st.slider(f"{loc_names[0]} - {criterion}", 0.0, 10.0, 
                                  value=float(st.session_state.location_data[loc_names[0]][criterion]) if not pd.isna(st.session_state.location_data[loc_names[0]][criterion]) else 5.0,
                                  key=f"loc1_{idx}", step=0.5)
                st.session_state.location_data[loc_names[0]][criterion] = score1
                
            with cols[1]:
                score2 = st.slider(f"{loc_names[1]} - {criterion}", 0.0, 10.0, 
                                  value=float(st.session_state.location_data[loc_names[1]][criterion]) if not pd.isna(st.session_state.location_data[loc_names[1]][criterion]) else 5.0,
                                  key=f"loc2_{idx}", step=0.5)
                st.session_state.location_data[loc_names[1]][criterion] = score2
                
            with cols[2]:
                score3 = st.slider(f"{loc_names[2]} - {criterion}", 0.0, 10.0, 
                                  value=float(st.session_state.location_data[loc_names[2]][criterion]) if not pd.isna(st.session_state.location_data[loc_names[2]][criterion]) else 5.0,
                                  key=f"loc3_{idx}", step=0.5)
                st.session_state.location_data[loc_names[2]][criterion] = score3
    
    with tab2:
        st.header("AI-Assisted Scoring")
        st.write("Provide information about each location for specific criteria, and AI will generate scores")
        
        if client is None:
            st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable to use AI scoring.")
        else:
            # Category selection for filtered input
            ai_selected_category = st.selectbox("Filter by category for AI scoring:", ["All"] + list(categories), key="ai_category")
            
            if ai_selected_category == "All":
                ai_filtered_criteria = criteria_df
            else:
                ai_filtered_criteria = criteria_df[criteria_df['Category'] == ai_selected_category]
            
            # Create AI input form
            for idx, row in ai_filtered_criteria.iterrows():
                criterion = row['Criterion']
                weight = row['Weight']
                category = row['Category']
                
                st.subheader(f"{criterion} (Weight: {weight}, Category: {category})")
                
                # Custom prompt for this criterion
                st.session_state.criterion_prompts[criterion] = st.text_area(
                    f"Specific instructions for evaluating {criterion}:",
                    value=st.session_state.criterion_prompts[criterion],
                    key=f"prompt_{idx}",
                    height=80,
                    help="Provide specific instructions on how you want this criterion evaluated (e.g., 'Prioritize areas with high elderly population' for Age Distribution)"
                )
                
                # Text inputs for each location
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**{loc_names[0]}**")
                    st.session_state.ai_inputs[criterion][loc_names[0]] = st.text_area(
                        "Information about this location:",
                        value=st.session_state.ai_inputs[criterion][loc_names[0]],
                        key=f"ai_loc1_{idx}",
                        height=100
                    )
                
                with col2:
                    st.write(f"**{loc_names[1]}**")
                    st.session_state.ai_inputs[criterion][loc_names[1]] = st.text_area(
                        "Information about this location:",
                        value=st.session_state.ai_inputs[criterion][loc_names[1]],
                        key=f"ai_loc2_{idx}",
                        height=100
                    )
                
                with col3:
                    st.write(f"**{loc_names[2]}**")
                    st.session_state.ai_inputs[criterion][loc_names[2]] = st.text_area(
                        "Information about this location:",
                        value=st.session_state.ai_inputs[criterion][loc_names[2]],
                        key=f"ai_loc3_{idx}",
                        height=100
                    )
                
                # Button to generate AI score for this criterion
                if st.button(f"Generate AI Score for {criterion}", key=f"ai_btn_{idx}"):
                    with st.spinner("Generating AI scores..."):
                        ai_result = get_ai_criterion_score(
                            criterion, weight,
                            st.session_state.ai_inputs[criterion][loc_names[0]],
                            st.session_state.ai_inputs[criterion][loc_names[1]],
                            st.session_state.ai_inputs[criterion][loc_names[2]],
                            st.session_state.criterion_prompts[criterion]
                        )
                        
                        # Update scores
                        st.session_state.location_data[loc_names[0]][criterion] = float(ai_result['loc_a_score'])
                        st.session_state.location_data[loc_names[1]][criterion] = float(ai_result['loc_b_score'])
                        st.session_state.location_data[loc_names[2]][criterion] = float(ai_result['loc_c_score'])
                        st.session_state.ai_explanations[criterion] = ai_result['explanation']
                        
                        st.success("Scores generated successfully!")
                        st.rerun()
                
                # Show current scores and explanation if available
                if st.session_state.ai_explanations.get(criterion):
                    st.info(f"**AI Explanation:** {st.session_state.ai_explanations[criterion]}")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric(f"{loc_names[0]} Score", f"{st.session_state.location_data[loc_names[0]][criterion]:.1f}/10")
                    with cols[1]:
                        st.metric(f"{loc_names[1]} Score", f"{st.session_state.location_data[loc_names[1]][criterion]:.1f}/10")
                    with cols[2]:
                        st.metric(f"{loc_names[2]} Score", f"{st.session_state.location_data[loc_names[2]][criterion]:.1f}/10")
                
                st.markdown("---")
    
    with tab3:
        st.header("Location Scores Overview")
        
        # Calculate scores
        weights = pd.Series(criteria_df['Weight'].values, index=criteria_df['Criterion'])
        
        score1, count1 = calculate_scores(st.session_state.location_data[loc_names[0]], weights)
        score2, count2 = calculate_scores(st.session_state.location_data[loc_names[1]], weights)
        score3, count3 = calculate_scores(st.session_state.location_data[loc_names[2]], weights)
        
        scores = [score1, score2, score3]
        criteria_counts = [count1, count2, count3]
        
        # Display overall scores
        st.subheader("Overall Scores")
        cols = st.columns(3)
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, (col, score, count, color) in enumerate(zip(cols, scores, criteria_counts, colors)):
            with col:
                st.metric(label=f"{loc_names[i]} Score", value=f"{score:.2f}/10")
                st.write(f"Based on {count} of {len(criteria_df)} criteria")
                st.progress(score/10)
        
        # Bar chart of scores
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(loc_names, scores, color=colors)
        ax.set_ylabel('Score (out of 10)')
        ax.set_title('Overall Location Scores')
        ax.set_ylim(0, 10)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{score:.2f}', ha='center', va='bottom')
        
        st.pyplot(fig)
        
        # Show ranking
        st.subheader("Ranking")
        ranked_locations = sorted(zip(loc_names, scores), key=lambda x: x[1], reverse=True)
        for i, (location, score) in enumerate(ranked_locations):
            st.write(f"{i+1}. {location}: {score:.2f}/10")
    
    with tab4:
        st.header("Detailed Analysis")
        
        # Prepare data for analysis
        category_scores = {}
        
        for category in categories:
            category_criteria = criteria_df[criteria_df['Category'] == category]
            category_weights = pd.Series(category_criteria['Weight'].values, index=category_criteria['Criterion'])
            
            cat_scores = []
            for loc in loc_names:
                loc_scores = st.session_state.location_data[loc][category_criteria['Criterion']]
                score, count = calculate_scores(loc_scores, category_weights)
                cat_scores.append(score)
            
            category_scores[category] = cat_scores
        
        # Radar chart
        st.subheader("Category Comparison - Radar Chart")
        
        # Set up the radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Close the circle
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        for i, loc in enumerate(loc_names):
            values = [category_scores[cat][i] for cat in categories]
            values += values[:1]  # Close the circle
            ax.plot(angles, values, 'o-', linewidth=2, label=loc)
            ax.fill(angles, values, alpha=0.1)
        
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, 10)
        ax.set_title("Performance by Category")
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        st.pyplot(fig)
        
        # Category breakdown table
        st.subheader("Category Breakdown")
        breakdown_data = []
        for category in categories:
            row = [category]
            for i in range(3):
                row.append(f"{category_scores[category][i]:.2f}")
            breakdown_data.append(row)
        
        breakdown_df = pd.DataFrame(breakdown_data, columns=['Category'] + loc_names)
        st.dataframe(breakdown_df)
        
        # TOPSIS analysis
        st.subheader("TOPSIS Multi-Criteria Decision Analysis")
        
        # Prepare data for TOPSIS
        topsis_data = []
        for loc in loc_names:
            loc_scores = []
            for criterion in criteria_df['Criterion']:
                score = st.session_state.location_data[loc][criterion]
                if not pd.isna(score):
                    loc_scores.append(score)
                else:
                    # Use average of available scores for missing values
                    available_scores = [st.session_state.location_data[l][criterion] for l in loc_names 
                                      if not pd.isna(st.session_state.location_data[l][criterion])]
                    if available_scores:
                        loc_scores.append(np.mean(available_scores))
                    else:
                        loc_scores.append(5.0)  # Default value if no data available
            
            topsis_data.append(loc_scores)
        
        topsis_data = np.array(topsis_data)
        weights = criteria_df['Weight'].values / np.sum(criteria_df['Weight'].values)  # Normalize weights
        
        # All criteria are beneficial (higher is better)
        impacts = [True] * len(criteria_df)
        
        topsis_scores = topsis_scores(topsis_data, weights, impacts)
        
        # Display TOPSIS results
        cols = st.columns(3)
        for i, (col, score) in enumerate(zip(cols, topsis_scores)):
            with col:
                st.metric(label=f"{loc_names[i]} TOPSIS Score", value=f"{score:.3f}")
        
        # TOPSIS ranking
        st.write("**TOPSIS Ranking**")
        topsis_ranking = sorted(zip(loc_names, topsis_scores), key=lambda x: x[1], reverse=True)
        for i, (location, score) in enumerate(topsis_ranking):
            st.write(f"{i+1}. {location}: {score:.3f}")
    
    with tab5:
        st.header("AI-Powered Insights")
        
        if client is None:
            st.warning("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable to enable AI insights.")
        else:
            st.info("This analysis uses large language  model to provide insights based on your location data and the information you provided for each criterion.")
            
            if st.button("Generate Comprehensive AI Insights"):
                with st.spinner("Generating insights..."):
                    # Calculate scores for AI analysis
                    weights = pd.Series(criteria_df['Weight'].values, index=criteria_df['Criterion'])
                    score1, count1 = calculate_scores(st.session_state.location_data[loc_names[0]], weights)
                    score2, count2 = calculate_scores(st.session_state.location_data[loc_names[1]], weights)
                    score3, count3 = calculate_scores(st.session_state.location_data[loc_names[2]], weights)
                    
                    scores = [score1, score2, score3]
                    insights = get_ai_insights(
                        st.session_state.location_data, 
                        criteria_df, 
                        scores, 
                        st.session_state.ai_inputs,
                        loc_names
                    )
                    
                    st.success("AI Insights Generated!")
                    st.write(insights)

    # Footer
    st.markdown("---")
    st.markdown("### About This Tool")
    st.markdown("""
    This hospital location analysis tool evaluates potential sites based on:
    - **Demographic Factors** (10 criteria)
    - **Accessibility & Transportation** (10 criteria)
    - **Infrastructure** (10 criteria)
    - **Competitive Landscape** (10 criteria)
    - **Regulatory Compliance** (10 criteria)
    - **Financial Considerations** (10 criteria)
    - **Environmental Factors** (10 criteria)

    Scores are calculated using weighted averages and TOPSIS multi-criteria decision analysis.
    The AI-assisted scoring feature uses LLMs to generate scores based on textual descriptions of each location.
    """)