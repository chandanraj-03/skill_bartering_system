import streamlit as st

# Streamlit configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Skill Bartering System",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

from datetime import datetime
from database.db_manager import DatabaseManager
from auth.authentication import AuthenticationManager
from utils.validators import validate_email, validate_password, validate_skill_input
from utils.helpers import get_user_skills, search_skills, get_user_exchanges, get_user_profile, send_message, get_messages_for_exchange, mark_messages_as_read, get_unread_message_count, get_unread_count_for_exchange, accept_exchange, reject_exchange, complete_exchange, submit_rating, get_user_rating_for_exchange, get_user_stats, get_skills_by_category, get_recommended_skills, get_recommended_users, create_group_exchange, add_participant_to_exchange, get_group_exchange_participants, accept_group_exchange_participation, reject_group_exchange_participation, get_user_group_exchanges, get_all_available_group_exchanges, update_user_profile_picture, update_user_bio, get_user_profile_extended, get_exchange_analytics, update_social_links, get_user_social_links, save_message_attachment
import plotly.graph_objects as go
import plotly.express as px
import base64
from io import BytesIO
from PIL import Image

# Initialize
db_manager = DatabaseManager()
auth_manager = AuthenticationManager()

# Uncomment the line below for initial database setup in production
# db_manager.initialize_database()



# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def logout():
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

def login_page():
    # Center the content
    st.markdown("""
        <div style='
            max-width: 1000px;
            margin: 2rem auto;
            padding: 3rem;
            background: white;
            border-radius: 24px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            text-align: center;
        '>
            <div style='
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            '>
                <div style='
                    font-size: 3rem;
                    margin-right: 1rem;
                '>
                    🎯
                </div>
                <div>
                    <div style='
                        background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        font-size: 2.5rem;
                        font-weight: 800;
                        margin-bottom: 0.5rem;
                        line-height: 1.2;
                    '>
                        Skill Bartering System
                    </div>
                    <div style='
                        color: #666;
                        font-size: 1.1rem;
                        font-weight: 500;
                        margin-bottom: 2rem;
                        font-family: "Inter", sans-serif;
                    '>
                        Exchange Skills, Build Community
                    </div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    # Create tabs for login and register
    tab1, tab2 = st.tabs([" 🔓Login", " 🏁Register(Create new Account)"])

    with tab1:
        
        login_email = st.text_input("📩 Email",
            key="login_email",
            placeholder="Enter your email",
            help="Enter your institution email (@geu.ac.in or @gehu.ac.in)")

        login_password = st.text_input("🔐 Password",
            type="password",
            key="login_password",
            placeholder="Enter your password")

        if st.button("Sign In", key="login_btn", use_container_width=True):
            if login_email and login_password:
                success, user, msg = auth_manager.login(login_email, login_password)
                if success:
                    st.session_state.user = user
                    st.session_state.page = 'dashboard'
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Please fill all fields")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        reg_email = st.text_input("📧 Email",
            key="reg_email",
            placeholder="Enter your institution email",
            help="Only @geu.ac.in and @gehu.ac.in emails are allowed")

        reg_password = st.text_input("🔑 Password",
            type="password",
            key="reg_password",
            placeholder="Create a strong password",
            help="Password must be at least 8 characters long")

        # Progressive disclosure: Show full name field only when register tab is active
        reg_full_name = st.text_input("👤 Full Name",
            key="reg_full_name",
            placeholder="Enter your full name",
            help="This will be visible to other users")

        if st.button("Create Account", key="register_btn", use_container_width=True):
            if reg_email and reg_password and reg_full_name:
                valid, msg = validate_password(reg_password)
                if not valid:
                    st.error(msg)
                else:
                    success, msg = auth_manager.register_user(reg_email, reg_password, reg_full_name)
                    if success:
                        st.success(msg)
                        st.info("Login with your credentials now!")
                    else:
                        st.error(msg)
            else:
                st.error("Please fill all fields")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div style='
            margin-top: 2rem;
            padding: 1rem;
            background: #EBF8FF;
            border-radius: 12px;
            color: #2B6CB0;
            text-align: center;
            font-size: 0.9rem;
        '>
             Only GEU and GEHU Students are allowed
        </div>
    </div>
    """, unsafe_allow_html=True)

def dashboard_page():
    # Get unread message count
    unread_count = get_unread_message_count(st.session_state.user['id'])
    
    # Modern dashboard header with glassmorphism effect and notification badge
    col_header, col_notification = st.columns([6, 1])
    
    with col_header:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
                padding: 2.5rem;
                border-radius: 24px;
                color: white;
                box-shadow: 0 12px 32px rgba(107, 70, 193, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            '>
                <h1 style='
                    margin: 0;
                    font-size: 2.8rem;
                    font-weight: 800;
                    letter-spacing: -1px;
                '>
                    🎓 Dashboard
                </h1>
                <p style='
                    margin: 0.8rem 0 0 0;
                    font-size: 1.4rem;
                    opacity: 0.9;
                    font-weight: 500;
                '>
                    Welcome back, {st.session_state.user['full_name']}!
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_notification:
        if unread_count > 0:
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
                    padding: 2.5rem;
                    border-radius: 24px;
                    color: white;
                    box-shadow: 0 12px 32px rgba(107, 70, 193, 0.2);
                    text-align: center;
                    position: relative;
                '>
                    <div style='font-size: 2rem;'>🔔</div>
                    <div style='
                        position: absolute;
                        top: 10px;
                        right: 10px;
                        background: #FF4444;
                        color: white;
                        border-radius: 50%;
                        width: 28px;
                        height: 28px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 0.9rem;
                        font-weight: 700;
                        box-shadow: 0 2px 8px rgba(255, 68, 68, 0.5);
                    '>
                        {unread_count}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                    <div style='font-size: 2rem;'>🔔</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern logout button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button(
            "🚪😶‍🌫️ Logout",
            key="logout_btn",
            help="Click to sign out from your account"
        ):
            logout()
    
    # Enhanced tabs with modern styling
    tabs = st.tabs([
        "🎯 My Skills",
        "🔍 Browse Skills",
        "🔄 My Exchanges",
        "📊 Analytics",
        "👤 Profile"
    ])
    
    with tabs[0]:
        my_skills_tab()

    with tabs[1]:
        browse_skills_tab()

    with tabs[2]:
        exchanges_tab()

    with tabs[3]:
        analytics_tab()

    with tabs[4]:
        profile_tab()

def my_skills_tab():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 32px rgba(107, 70, 193, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        '>
            <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>
                🎯 My Skills
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize the session state for showing form if not exists
    if 'show_skill_form' not in st.session_state:
        st.session_state.show_skill_form = False
    
    # Add Skill / Cancel button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if not st.session_state.show_skill_form:
            if st.button("➕ Add New Skill", key="show_form_btn", use_container_width=True):
                st.session_state.show_skill_form = True
        else:
            if st.button("❌ Cancel", key="hide_form_btn", use_container_width=True):
                st.session_state.show_skill_form = False
    
    # Show form if state is true
    if st.session_state.show_skill_form:
        st.markdown("""
            <div style='
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                margin: 1.5rem 0;
            '>
                <h3 style='
                    color: #2D3748;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    font-weight: 700;
                '>
                    ✨ Add New Skill
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            skill_name = st.text_input("🏷️ Skill Name",
                placeholder="Enter the name of your skill",
                help="Be specific and clear about the skill you're offering")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("📚 Category", 
                    ["Programming", "Design", "Photography", "Music", "Languages", 
                     "Writing", "Marketing", "Teaching", "Business", "Other"],
                    help="Choose the category that best fits your skill")
            with col2:
                proficiency = st.selectbox("📊 Proficiency Level", 
                    ["Beginner", "Intermediate", "Advanced", "Expert"],
                    help="Be honest about your skill level")
            
            description = st.text_area("📝 Description",
                placeholder="Describe your skill, experience, and what you can offer...",
                help="Provide details about your experience and what others can expect")
            
            if st.button("✅ Add Skill", key="submit_skill_btn", use_container_width=True):
                valid, msg = validate_skill_input(skill_name, category, description)
                if valid:
                    query = '''
                        INSERT INTO skills 
                        (user_id, skill_name, category, proficiency_level, description)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    db_manager.execute_query(query, 
                        (st.session_state.user['id'], skill_name, category, proficiency, description))
                    st.success("✨ Skill added successfully!")
                    st.session_state.show_skill_form = False
                    st.rerun()
                else:
                    st.error(msg)
    
    # Display skills
    skills = get_user_skills(st.session_state.user['id'])
    if skills:
        for skill in skills:
            st.markdown(f"""
                <div style='
                    background: rgba(255, 255, 255, 0.95);
                    padding: 1.5rem;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    margin: 1rem 0;
                    position: relative;
                '>
                    <div style='
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1rem;
                    '>
                        <div>
                            <span style='
                                font-size: 1.2rem;
                                font-weight: 700;
                                color: #2D3748;
                            '>
                                {skill['skill_name']}
                            </span>
                            <span style='
                                background: linear-gradient(135deg, #E3F2FD 0%, #90CDF4 100%);
                                color: #2B6CB0;
                                padding: 0.3rem 0.8rem;
                                border-radius: 20px;
                                font-size: 0.9rem;
                                font-weight: 600;
                                margin-left: 0.8rem;
                            '>
                                {skill['category']}
                            </span>
                            <span style='
                                background: linear-gradient(135deg, #F3E5F5 0%, #D6BCFA 100%);
                                color: #553C9A;
                                padding: 0.3rem 0.8rem;
                                border-radius: 20px;
                                font-size: 0.9rem;
                                font-weight: 600;
                                margin-left: 0.5rem;
                            '>
                                {skill['proficiency_level']}
                            </span>
                        </div>
                    </div>
                    <div style='
                        color: #4A5568;
                        background: #F7FAFC;
                        padding: 1rem;
                        border-radius: 12px;
                        border: 1px solid #E2E8F0;
                        font-size: 1rem;
                        line-height: 1.6;
                    '>
                        {skill['description']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Delete button below each skill card
            if st.button("🗑️ Delete Skill", key=f"delete_{skill['id']}", use_container_width=True,
                      help="Remove this skill from your profile"):
                db_manager.execute_query('DELETE FROM skills WHERE id = %s', (skill['id'],))
                st.rerun()
    else:
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #EBF8FF 0%, #BEE3F8 100%);
                color: #2C5282;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                margin: 2rem 0;
                font-weight: 600;
            '>
                ✨ No skills added yet. Start by adding your first skill!
            </div>
        """, unsafe_allow_html=True)

def browse_skills_tab():
    # Initialize selected category in session state if not exists
    if 'selected_browse_category' not in st.session_state:
        st.session_state.selected_browse_category = "All Skills"
    
    # Hero section with gradient background
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
            padding: 3rem 2rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        '>
            <h1 style='
                margin: 0 0 1rem 0;
                font-size: 2.8rem;
                font-weight: 900;
                letter-spacing: -1px;
            '>
                Learn Something New Today
            </h1>
            <p style='
                font-size: 1.2rem;
                margin: 0;
                opacity: 0.95;
                font-weight: 500;
            '>
                Connect with talented students who can teach you their skills
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced search section with modern styling
    st.markdown("""
        <div style='
            background: white;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            margin-bottom: 2rem;
        '>
    """, unsafe_allow_html=True)
    
    search_col1, search_col2, search_col3 = st.columns([4, 2, 1])
    with search_col1:
        search_keyword = st.text_input(
            "🔍 Search skills...",
            key="search_keyword",
            placeholder="e.g., 'guitar', 'python', 'cooking'",
            label_visibility="collapsed"
        )
    with search_col2:
        # Use the index parameter to sync with session state
        category_options = ["All Skills", "Programming", "Design", "Music", "Languages", 
                           "Sports", "Cooking", "Photography", "Writing", "Business", "Academic", "Other"]
        try:
            default_index = category_options.index(st.session_state.selected_browse_category)
        except ValueError:
            default_index = 0
            
        search_category = st.selectbox(
            "📚 Category",
            category_options,
            index=default_index,
            key="search_category_select",
            label_visibility="collapsed"
        )
        # Update session state when selectbox changes
        st.session_state.selected_browse_category = search_category
    
    with search_col3:
        st.write("")  # Spacing
        if st.button("🔄 Refresh", key="refresh_browse_skills", use_container_width=True):
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Determine the category filter - use the session state variable
    category = None if st.session_state.selected_browse_category == "All Skills" else st.session_state.selected_browse_category
    
    # Search for skills with filters
    if search_keyword:
        results = search_skills(search_keyword, category)
    else:
        # Show all skills on initial load
        results = search_skills("", category)
    
    if results:
        # Filter out user's own skills
        results = [r for r in results if r['user_id'] != st.session_state.user['id']]
        
        if results:
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #D4F1F4 0%, #75E6DA 100%);
                    color: #0C7489;
                    padding: 1rem 1.5rem;
                    border-radius: 12px;
                    text-align: center;
                    margin: 2rem 0;
                    font-weight: 700;
                    font-size: 1.1rem;
                    box-shadow: 0 4px 12px rgba(12, 116, 137, 0.15);
                '>
                    ✨ Found {len(results)} skill{'' if len(results) == 1 else 's'} available for exchange
                </div>
            """, unsafe_allow_html=True)
            
            # Display skills in a card grid
            for idx, result in enumerate(results):
                # Determine skill icon based on category
                category_icons = {
                    "Programming": "💻",
                    "Design": "🎨", 
                    "Music": "🎵",
                    "Languages": "🌍",
                    "Sports": "⚽",
                    "Cooking": "🍳",
                    "Photography": "📸",
                    "Writing": "✍️",
                    "Business": "💼",
                    "Academic": "📚",
                    "Other": "🎯"
                }
                skill_icon = category_icons.get(result['category'], "🎯")
                
                # Proficiency level badge color
                proficiency_colors = {
                    "Beginner": {"bg": "#C6F6D5", "color": "#22543D", "icon": "🌱"},
                    "Intermediate": {"bg": "#BEE3F8", "color": "#2C5282", "icon": "🌿"},
                    "Advanced": {"bg": "#E9D8FD", "color": "#44337A", "icon": "🌳"},
                    "Expert": {"bg": "#FED7D7", "color": "#742A2A", "icon": "🏆"}
                }
                prof_style = proficiency_colors.get(result['proficiency_level'], {"bg": "#E2E8F0", "color": "#2D3748", "icon": "⭐"})
                
                # Use st.container for better structure
                with st.container():
                    # Category header
                    st.markdown(f"""
                        <div style='
                            background: {prof_style["bg"]};
                            padding: 0.8rem 1.5rem;
                            border-radius: 12px 12px 0 0;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-top: 1.5rem;
                        '>
                            <span style='
                                background: rgba(255, 255, 255, 0.9);
                                color: {prof_style["color"]};
                                padding: 0.4rem 1rem;
                                border-radius: 20px;
                                font-size: 0.9rem;
                                font-weight: 700;
                            '>
                                {skill_icon} {result['category']}
                            </span>
                            <span style='
                                color: {prof_style["color"]};
                                font-weight: 700;
                                font-size: 0.95rem;
                            '>
                                {prof_style["icon"]} {result['proficiency_level']}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Card content in a white box
                    st.markdown(f"""
                        <div style='
                            background: white;
                            padding: 1.5rem;
                            border-radius: 0 0 12px 12px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        '>
                            <h3 style='
                                margin: 0 0 1rem 0;
                                font-size: 1.6rem;
                                font-weight: 800;
                                color: #2D3748;
                            '>
                                {result['skill_name']}
                            </h3>
                            <p style='
                                color: #4A5568;
                                font-size: 1rem;
                                line-height: 1.6;
                                background: #F7FAFC;
                                padding: 1rem;
                                border-radius: 8px;
                                margin-bottom: 1rem;
                            '>
                                {result['description']}
                            </p>
                            <div style='
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                padding: 1rem;
                                background: #F7FAFC;
                                border-radius: 8px;
                            '>
                                <div>
                                    <div style='font-weight: 700; color: #2D3748;'>
                                        👤 {result['full_name']}
                                    </div>
                                    <div style='color: #718096; font-size: 0.9rem;'>
                                        📧 {result['email']}
                                    </div>
                                </div>
                                <div style='
                                    background: #FFF3CD;
                                    padding: 0.5rem 1rem;
                                    border-radius: 20px;
                                    font-weight: 700;
                                    color: #F57F17;
                                '>
                                    ⭐ {result['rating']:.1f}
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Exchange proposal section
                    user_skills = get_user_skills(st.session_state.user['id'])
                    user_skills = sorted(user_skills, key=lambda x: x['skill_name'])

                    if not user_skills:
                        st.info("💡 Add your own skills first to propose exchanges!")
                    elif result['user_id'] == st.session_state.user['id']:
                        st.info("ℹ️ This is your own skill!")
                    else:
                        # Check if an exchange already exists
                        check_query = """
                            SELECT id FROM exchanges
                            WHERE ((initiator_id = %s AND recipient_id = %s) OR
                                  (initiator_id = %s AND recipient_id = %s)) AND
                                  status = 'pending'
                        """
                        existing_exchange = db_manager.fetch_one(check_query, (
                            st.session_state.user['id'], result['user_id'],
                            result['user_id'], st.session_state.user['id']
                        ))

                        if existing_exchange:
                            st.warning("⏳ You already have a pending exchange with this user!")
                        else:
                            # Create expandable form for exchange proposal
                            with st.expander("💬 Propose an Exchange", expanded=False):
                                with st.form(key=f"exchange_form_{result['id']}"):
                                    st.markdown("**🎯 Choose your skill to offer in exchange:**")

                                    # Create options for skill selection
                                    skill_options = {
                                        skill['id']: f"{skill['skill_name']} ({skill['category']} - {skill['proficiency_level']})" 
                                        for skill in user_skills
                                    }

                                    selected_skill_id = st.selectbox(
                                        "Your skill:",
                                        options=list(skill_options.keys()),
                                        format_func=lambda x: skill_options[x],
                                        key=f"skill_select_{result['id']}",
                                        label_visibility="collapsed"
                                    )

                                    col1, col2 = st.columns([1, 1])
                                    with col2:
                                        submitted = st.form_submit_button(
                                            "🚀 Send Proposal",
                                            use_container_width=True,
                                            type="primary"
                                        )

                                    if submitted:
                                        try:
                                            # Create exchange in database
                                            exchange_query = """
                                                INSERT INTO exchanges
                                                (initiator_id, recipient_id, initiator_skill_id, recipient_skill_id, status, is_group)
                                                VALUES (%s, %s, %s, %s, %s, %s)
                                            """

                                            db_manager.execute_query(exchange_query, (
                                                st.session_state.user['id'],
                                                result['user_id'],
                                                selected_skill_id,
                                                result['id'],
                                                'pending',
                                                False
                                            ))
                                            st.success("✅ Exchange proposal sent successfully!")
                                            st.balloons()
                                            st.rerun()

                                        except Exception as db_error:
                                            st.error(f"❌ Database error: {str(db_error)}")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            # All results were user's own skills
            st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #FFF5F5 0%, #FED7D7 100%);
                    color: #C53030;
                    padding: 3rem;
                    border-radius: 20px;
                    text-align: center;
                    margin: 2rem 0;
                    font-weight: 700;
                    font-size: 1.2rem;
                    box-shadow: 0 8px 24px rgba(197, 48, 48, 0.15);
                '>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>👥</div>
                    <div style='margin-bottom: 0.5rem;'>No skills from other users available yet</div>
                    <div style='font-size: 1rem; font-weight: 500; opacity: 0.9;'>
                        Invite others to join and share their skills!
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #FFF5F5 0%, #FED7D7 100%);
                color: #C53030;
                padding: 3rem;
                border-radius: 20px;
                text-align: center;
                margin: 2rem 0;
                font-weight: 700;
                font-size: 1.2rem;
                box-shadow: 0 8px 24px rgba(197, 48, 48, 0.15);
            '>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
                <div style='margin-bottom: 0.5rem;'>No skills found matching your criteria</div>
                <div style='font-size: 1rem; font-weight: 500; opacity: 0.9;'>
                    Try different search terms or browse all categories!
                </div>
            </div>
        """, unsafe_allow_html=True)

def exchanges_tab():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 32px rgba(107, 70, 193, 0.2);
        '>
            <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>
                🔄 My Exchanges
            </h2>
        </div>
    """, unsafe_allow_html=True)

    try:
        exchanges = get_user_exchanges(st.session_state.user['id'])
    except Exception as e:
        st.error(f"Error loading exchanges: {str(e)}")
        exchanges = []
    
    if exchanges:
        for exchange in exchanges:
            # Safe status style lookup with default
            status_styles_map = {
                "completed": {
                    "bg": "linear-gradient(135deg, #C6F6D5 0%, #9AE6B4 100%)",
                    "color": "#276749",
                    "icon": "✅"
                },
                "accepted": {
                    "bg": "linear-gradient(135deg, #FEFCBF 0%, #F6E05E 100%)",
                    "color": "#975A16",
                    "icon": "🤝"
                },
                "pending": {
                    "bg": "linear-gradient(135deg, #E9D8FD 0%, #D6BCFA 100%)",
                    "color": "#553C9A",
                    "icon": "⏳"
                },
                "rejected": {
                    "bg": "linear-gradient(135deg, #FED7D7 0%, #FC8181 100%)",
                    "color": "#C53030",
                    "icon": "❌"
                }
            }
            
            # Get status style with default fallback
            status_style = status_styles_map.get(
                exchange.get('status', 'pending'),
                {
                    "bg": "linear-gradient(135deg, #E2E8F0 0%, #CBD5E0 100%)",
                    "color": "#4A5568",
                    "icon": "❓"
                }
            )

            # Determine user-centric display
            if exchange['initiator_id'] == st.session_state.user['id']:
                offering_skill = exchange.get('initiator_skill') or '[Skill deleted]'
                requesting_skill = exchange.get('recipient_skill') or '[Skill deleted]'
                other_person = exchange.get('recipient_name') or '[User not found]'
            else:
                offering_skill = exchange.get('recipient_skill') or '[Skill deleted]'
                requesting_skill = exchange.get('initiator_skill') or '[Skill deleted]'
                other_person = exchange.get('initiator_name') or '[User not found]'

            # Extract style values
            status_bg = status_style['bg']
            status_color = status_style['color']
            status_icon = status_style['icon']
            exchange_status = exchange.get('status', 'unknown').upper()
            exchange_id = exchange.get('id', '')
            exchange_created = str(exchange.get('created_at', ''))

            # Use native Streamlit components with better spacing
            st.markdown("""
                <div style='
                    background:#C71585;
                    border-radius: 10px;
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-left: 4px solid """ + status_style['bg'].split('(')[1].split(',')[0] + """;
                '>
            """, unsafe_allow_html=True)
            
            with st.container():
                # Status badge and header
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{status_icon} {exchange_status}** | ID: {exchange_id}")
                with col2:
                    st.caption(f"Started: {exchange_created}")
                
                st.divider()
                
                # Exchange details
                col_offer, col_request = st.columns(2)
                with col_offer:
                    st.markdown("**You're Offering:**")
                    st.info(offering_skill)
                with col_request:
                    st.markdown("**You're Requesting:**")
                    st.info(requesting_skill)
                
                st.markdown(f"**With:** {other_person}")
                st.markdown("---")

            # Action buttons for pending exchanges
            if exchange['status'] == 'pending':
                # Check if user is the recipient (can accept/reject)
                is_recipient = exchange['recipient_id'] == st.session_state.user['id']

                col1, col2 = st.columns([1, 1])
                with col1:
                    if is_recipient:
                        if st.button("✅ Accept", key=f"accept_{exchange['id']}", use_container_width=True):
                            if accept_exchange(exchange['id'], st.session_state.user['id']):
                                st.success("Exchange accepted! You can now start chatting and complete the exchange.")
                                st.rerun()
                            else:
                                st.error("Failed to accept exchange.")
                with col2:
                    if is_recipient:
                        if st.button("❌ Reject", key=f"reject_{exchange['id']}", use_container_width=True):
                            if reject_exchange(exchange['id'], st.session_state.user['id']):
                                st.success("Exchange rejected.")
                                st.rerun()
                            else:
                                st.error("Failed to reject exchange.")
            
            # Chat section for each exchange
            # Determine the other person's name safely
            if exchange['initiator_id'] == st.session_state.user['id']:
                chat_partner_name = exchange.get('recipient_name') or 'Unknown User'
            else:
                chat_partner_name = exchange.get('initiator_name') or 'Unknown User'
            
            # Get unread message count for this exchange
            unread_count = get_unread_count_for_exchange(exchange['id'], st.session_state.user['id'])
            unread_badge = f" 🔴 {unread_count} new" if unread_count > 0 else ""
            
            with st.expander(f"💬 Chat with {chat_partner_name}{unread_badge}", expanded=False):
                # Add refresh button at the top of chat
                col_refresh, col_space = st.columns([1, 5])
                with col_refresh:
                    if st.button("🔄 Refresh", key=f"refresh_chat_{exchange['id']}", use_container_width=True):
                        st.rerun()
                
                # Mark messages as read when opening chat
                mark_messages_as_read(exchange['id'], st.session_state.user['id'])
                
                # Display messages
                messages = get_messages_for_exchange(exchange['id'])
                if messages:
                    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
                    
                    # Group messages by date
                    current_date = None
                    for msg in messages:
                        msg_date = str(msg['created_at']).split()[0]  # Get date part
                        
                        # Show date divider if date changed
                        if current_date != msg_date:
                            current_date = msg_date
                            st.markdown(f"""
                                <div class="chat-divider">
                                    <span class="chat-divider-text">📅 {msg_date}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        is_sent = msg['sender_id'] == st.session_state.user['id']
                        message_class = "message-sent" if is_sent else "message-received"
                        wrapper_class = "message-wrapper-sent" if is_sent else "message-wrapper-received"
                        
                        # Format timestamp to show only time
                        timestamp = str(msg['created_at']).split()[1].split('.')[0]  # Get time part HH:MM:SS
                        timestamp = timestamp[:-3]  # Remove seconds to show HH:MM
                        
                        # Display message
                        st.markdown(f"""
                            <div class="{wrapper_class}">
                                <div class="{message_class}">
                                    <div class="message-sender">{msg['sender_name']}</div>
                                    <div class="message-text">{msg['message']}</div>
                                    <div class="message-timestamp">🕐 {timestamp}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Handle file attachments
                        if msg.get('attachment_data') and msg.get('attachment_name'):
                            attachment_name = msg['attachment_name']
                            attachment_type = msg.get('attachment_type', 'application/octet-stream')
                            attachment_data = msg['attachment_data']
                            
                            # Determine if it's an image or video
                            is_image = attachment_type.startswith('image/')
                            is_video = attachment_type.startswith('video/')
                            
                            # Create a small contained area for attachments
                            st.markdown("""
                                <div style='
                                    background: #F7FAFC;
                                    border: 2px solid #E2E8F0;
                                    border-radius: 12px;
                                    padding: 0.5rem;
                                    margin: 0.5rem 0;
                                    max-width: 250px;
                                '>
                            """, unsafe_allow_html=True)
                            
                            if is_image:
                                # Display small image preview
                                try:
                                    image_bytes = base64.b64decode(attachment_data)
                                    image = Image.open(BytesIO(image_bytes))
                                    
                                    # Resize image to small thumbnail
                                    max_size = 200
                                    if image.width > max_size or image.height > max_size:
                                        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                                    
                                    st.image(image, caption=attachment_name, width=200)
                                except Exception as e:
                                    st.error(f"Could not display image: {str(e)}")
                            
                            elif is_video:
                                # Display small video info (no player to keep it small)
                                st.markdown(f"""
                                    <div style='
                                        padding: 0.5rem;
                                        background: white;
                                        border-radius: 8px;
                                        margin-bottom: 0.5rem;
                                        text-align: center;
                                    '>
                                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🎥</div>
                                        <div style='font-weight: 600; color: #2D3748; font-size: 0.85rem;'>
                                            {attachment_name}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            else:
                                # For non-image/video files, show small file icon
                                st.markdown(f"""
                                    <div style='
                                        padding: 0.5rem;
                                        background: white;
                                        border-radius: 8px;
                                        margin-bottom: 0.5rem;
                                        text-align: center;
                                    '>
                                        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📄</div>
                                        <div style='font-weight: 600; color: #2D3748; font-size: 0.85rem;'>
                                            {attachment_name}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            # Compact download button
                            try:
                                file_bytes = base64.b64decode(attachment_data)
                                st.download_button(
                                    label=f"⬇️ Download",
                                    data=file_bytes,
                                    file_name=attachment_name,
                                    mime=attachment_type,
                                    key=f"download_{msg['id']}_{exchange['id']}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Could not create download button: {str(e)}")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Auto-scroll to bottom using JavaScript
                    st.markdown("""
                        <script>
                            const chatContainer = document.querySelector('.chat-container');
                            if (chatContainer) {
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                            }
                        </script>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="no-messages">
                            <div class="no-messages-icon">💬</div>
                            <div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;'>
                                No messages yet
                            </div>
                            <div style='font-size: 0.9rem;'>
                                Start the conversation by sending a message below!
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Message input with improved styling
                st.markdown("""
                    <div style='
                        background: white;
                        border: 2px solid #E2E8F0;
                        border-radius: 16px;
                        padding: 1rem;
                        margin-top: 1rem;
                    '>
                        <div style='
                            font-weight: 600;
                            color: #4A5568;
                            margin-bottom: 0.5rem;
                            font-size: 0.9rem;
                        '>
                            ✍️ Send a message
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.form(key=f"message_form_{exchange['id']}"):
                    message_text = st.text_area(
                        "Type your message...",
                        key=f"message_input_{exchange['id']}",
                        height=100,
                        placeholder="Write your message here... Press Ctrl+Enter to send",
                        label_visibility="collapsed"
                    )
                    
                    # File attachment option
                    st.markdown("📎 **Attach a file** (optional)")
                    uploaded_msg_file = st.file_uploader(
                        "Attach file",
                        type=['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi'],
                        key=f"file_upload_{exchange['id']}",
                        label_visibility="collapsed",
                        help="Attach documents, images, or videos (Max 10MB recommended)"
                    )
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col2:
                        clear_btn = st.form_submit_button("🗑️ Clear", use_container_width=True)
                    with col3:
                        send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
                    
                    if send_button:
                        try:
                            # Determine recipient
                            recipient_id = exchange['recipient_id'] if exchange['initiator_id'] == st.session_state.user['id'] else exchange['initiator_id']

                            # Check if there's a message or file
                            if message_text.strip() or uploaded_msg_file is not None:
                                if uploaded_msg_file is not None:
                                    # Handle file attachment
                                    file_bytes = uploaded_msg_file.read()
                                    file_base64 = base64.b64encode(file_bytes).decode()
                                    file_type = uploaded_msg_file.type
                                    file_name = uploaded_msg_file.name
                                    
                                    # Send message with attachment
                                    save_message_attachment(
                                        exchange['id'],
                                        st.session_state.user['id'],
                                        recipient_id,
                                        file_name,
                                        file_base64,
                                        file_type
                                    )
                                    
                                    # Also send text message if provided
                                    if message_text.strip():
                                        send_message(exchange['id'], st.session_state.user['id'], recipient_id, message_text)
                                    
                                    st.success("✅ Message with attachment sent successfully!")
                                else:
                                    # Send text-only message
                                    send_message(exchange['id'], st.session_state.user['id'], recipient_id, message_text)
                                    st.success("✅ Message sent successfully!")
                                
                                st.rerun()
                            else:
                                st.warning("⚠️ Please type a message or attach a file before sending!")
                        except Exception as e:
                            st.error(f"❌ Failed to send message: {str(e)}")
            
            # Show complete button AFTER chat for accepted exchanges
            if exchange['status'] == 'accepted':
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🏁 Mark as Completed", key=f"complete_{exchange['id']}", use_container_width=True):
                    if complete_exchange(exchange['id'], st.session_state.user['id']):
                        st.success("Exchange marked as completed! 🎉")
                        st.rerun()
                    else:
                        st.error("Failed to complete exchange.")
            
            # Show rating section AFTER chat for completed exchanges
            elif exchange['status'] == 'completed':
                # Determine who to rate (the other person in the exchange)
                if exchange['initiator_id'] == st.session_state.user['id']:
                    rated_user_id = exchange['recipient_id']
                    rated_user_name = exchange.get('recipient_name') or 'Unknown User'
                else:
                    rated_user_id = exchange['initiator_id']
                    rated_user_name = exchange.get('initiator_name') or 'Unknown User'

                # Check if user has already rated this exchange
                has_rated = get_user_rating_for_exchange(exchange['id'], st.session_state.user['id'])

                if not has_rated:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style='
                            background: linear-gradient(135deg, #FFF3CD 0%, #FFE066 100%);
                            color: #856404;
                            padding: 1rem;
                            border-radius: 12px;
                            margin: 1rem 0;
                            border: 1px solid #FFE066;
                        '>
                            ⭐ How was your experience with {rated_user_name}? Please rate them!
                        </div>
                    """, unsafe_allow_html=True)

                    # Interactive star rating using Streamlit selectbox
                    with st.form(key=f"rating_form_{exchange['id']}"):
                        rating_options = {
                            1: "⭐",
                            2: "⭐⭐",
                            3: "⭐⭐⭐",
                            4: "⭐⭐⭐🌟",
                            5: "🌟🌟🌟🌟🌟"
                        }

                        rating_value = st.selectbox(
                            f"Rate {rated_user_name} (1-5 stars):",
                            options=list(rating_options.keys()),
                            format_func=lambda x: rating_options[x],
                            key=f"rating_select_{exchange['id']}",
                            help="Choose how many stars to give based on your experience"
                        )

                        if st.form_submit_button("⭐ Submit Rating", use_container_width=True):
                            success, message = submit_rating(
                                exchange['id'],
                                st.session_state.user['id'],
                                rated_user_id,
                                rating_value
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.info(f"✅ You have already rated {rated_user_name} for this exchange.")
            
            # Close the exchange card div
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #EBF8FF 0%, #BEE3F8 100%);
                color: #2C5282;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                margin: 2rem 0;
                font-weight: 600;
            '>
                🔄 No exchanges yet. Start by proposing a skill exchange!
            </div>
        """, unsafe_allow_html=True)


def analytics_tab():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 32px rgba(107, 70, 193, 0.2);
        '>
            <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>
                📊 Analytics Dashboard
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Get analytics data
    analytics = get_exchange_analytics(st.session_state.user['id'])
    user_stats = get_user_stats(st.session_state.user['id'])

    # Display key metrics
    st.markdown("""
        
            <h3 style='
                color: #2D3748;
                font-size: 1.5rem;
                margin-bottom: 1.5rem;
                font-weight: 700;
            '>
                📈 Key Metrics
            </h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
                padding: 2rem;
                border-radius: 16px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
            '>
                <div style='font-size: 2.5rem; font-weight: 800;'>{user_stats['skill_count']}</div>
                <div style='font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;'>Total Skills</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);
                padding: 2rem;
                border-radius: 16px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 16px rgba(240, 147, 251, 0.3);
            '>
                <div style='font-size: 2.5rem; font-weight: 800;'>{user_stats['total_exchanges']}</div>
                <div style='font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;'>Total Exchanges</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);
                padding: 2rem;
                border-radius: 16px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 16px rgba(79, 172, 254, 0.3);
            '>
                <div style='font-size: 2.5rem; font-weight: 800;'>{user_stats['completed_exchanges']}</div>
                <div style='font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;'>Completed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #43E97B 0%, #38F9D7 100%);
                padding: 2rem;
                border-radius: 16px;
                color: white;
                text-align: center;
                box-shadow: 0 8px 16px rgba(67, 233, 123, 0.3);
            '>
                <div style='font-size: 2.5rem; font-weight: 800;'>{user_stats['community_points']}</div>
                <div style='font-size: 1rem; opacity: 0.9; margin-top: 0.5rem;'>Points</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Skills Distribution Chart
    if analytics['skills_distribution']:
        st.markdown("""
            <div style='
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
            '>
                <h3 style='
                    color: #2D3748;
                    font-size: 1.3rem;
                    margin-bottom: 1rem;
                    font-weight: 700;
                '>
                    🎯 Skills by Category
                </h3>
            </div>
        """, unsafe_allow_html=True)

        # Create pie chart for skills distribution
        categories = [item['category'] for item in analytics['skills_distribution']]
        counts = [item['count'] for item in analytics['skills_distribution']]
        
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=counts,
            hole=0.4,
            marker=dict(
                colors=['#667EEA', '#764BA2', '#F093FB', '#F5576C', '#4FACFE', '#00F2FE', '#43E97B', '#38F9D7', '#FA709A', '#FEE140'],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=14, color='white', family='Poppins'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Poppins', size=14, color='#2D3748'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add skills to see your skills distribution!")

    # Exchange Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            
                <h3 style='
                    color: #2D3748;
                    font-size: 1.3rem;
                    margin-bottom: 1rem;
                    font-weight: 700;
                '>
                    📊 Exchange Status
                </h3>
            </div>
        """, unsafe_allow_html=True)

        if user_stats['total_exchanges'] > 0:
            status_data = {
                'Completed': user_stats['completed_exchanges'],
                'Pending': user_stats['pending_exchanges'],
                'Other': user_stats['total_exchanges'] - user_stats['completed_exchanges'] - user_stats['pending_exchanges']
            }
            
            # Remove 'Other' if it's 0
            status_data = {k: v for k, v in status_data.items() if v > 0}
            
            fig2 = go.Figure(data=[go.Bar(
                x=list(status_data.keys()),
                y=list(status_data.values()),
                marker=dict(
                    color=['#43E97B', '#F5576C', '#667EEA'],
                    line=dict(color='white', width=2)
                ),
                text=list(status_data.values()),
                textposition='outside',
                textfont=dict(size=16, color='#2D3748', family='Poppins', weight='bold'),
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )])
            
            fig2.update_layout(
                height=350,
                margin=dict(t=20, b=60, l=40, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Poppins', size=14, color='#2D3748'),
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    title=None
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)',
                    showline=False,
                    title='Count'
                )
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No exchanges yet. Start exchanging to see analytics!")

    with col2:
        st.markdown("""
            
                <h3 style='
                    color: #2D3748;
                    font-size: 1.3rem;
                    margin-bottom: 1rem;
                    font-weight: 700;
                '>
                    🏆 Achievement Badge
                </h3>
            </div>
        """, unsafe_allow_html=True)

        # Badge display
        badge_colors = {
            'Gold': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'Silver': 'linear-gradient(135deg, #C0C0C0 0%, #808080 100%)',
            'Bronze': 'linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)',
            'Newcomer': 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)'
        }
        
        badge_icons = {
            'Gold': '🥇',
            'Silver': '🥈',
            'Bronze': '🥉',
            'Newcomer': '🌟'
        }
        
        badge = user_stats['badge']
        
        st.markdown(f"""
            <div style='
                background: {badge_colors[badge]};
                padding: 3rem 2rem;
                border-radius: 16px;
                color: white;
                text-align: center;
                box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
                margin-top: 1rem;
            '>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>{badge_icons[badge]}</div>
                <div style='font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem;'>{badge}</div>
                <div style='font-size: 1.1rem; opacity: 0.9;'>{user_stats['community_points']} Points</div>
            </div>
        """, unsafe_allow_html=True)

        # Badge criteria
        st.markdown("""
            <div style='
                background: #F7FAFC;
                padding: 1rem;
                border-radius: 12px;
                margin-top: 1rem;
                font-size: 0.9rem;
                color: #4A5568;
            '>
                <b>Badge Levels:</b><br>
                🥇 Gold: 100+ points<br>
                🥈 Silver: 50-99 points<br>
                🥉 Bronze: 10-49 points<br>
                🌟 Newcomer: 0-9 points<br>
                <i style='font-size: 0.85rem; opacity: 0.8;'>Earn 10 points per completed exchange!</i>
            </div>
        """, unsafe_allow_html=True)

    # Rating Distribution
    if analytics['ratings_distribution']:
        st.markdown("""
            <div style='
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                margin: 1.5rem 0;
            '>
                <h3 style='
                    color: #2D3748;
                    font-size: 1.3rem;
                    margin-bottom: 1rem;
                    font-weight: 700;
                '>
                    ⭐ Ratings Received
                </h3>
            </div>
        """, unsafe_allow_html=True)

        ratings = [item['rating'] for item in analytics['ratings_distribution']]
        rating_counts = [item['count'] for item in analytics['ratings_distribution']]
        
        fig3 = go.Figure(data=[go.Bar(
            x=['⭐' * r for r in ratings],
            y=rating_counts,
            marker=dict(
                color='#FFD700',
                line=dict(color='#FFA500', width=2)
            ),
            text=rating_counts,
            textposition='outside',
            textfont=dict(size=16, color='#2D3748', family='Poppins', weight='bold'),
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )])
        
        fig3.update_layout(
            height=350,
            margin=dict(t=20, b=60, l=40, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Poppins', size=14, color='#2D3748'),
            xaxis=dict(
                showgrid=False,
                showline=False,
                title='Rating'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                showline=False,
                title='Count'
            )
        )
        
        st.plotly_chart(fig3, use_container_width=True)

def profile_tab():
    st.markdown("""
        <div style='
            background: linear-gradient(135deg, #6B46C1 0%, #9F7AEA 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 8px 32px rgba(107, 70, 193, 0.2);
        '>
            <h2 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>
                👤 Profile
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Get extended user profile data
    profile = get_user_profile_extended(st.session_state.user['id'])

    if profile:
        # Create two columns for profile layout
        col_left, col_right = st.columns([1, 2])
        
        with col_left:
            # Profile Picture Section
            st.markdown("""
                    <h3 style='
                        color: #2D3748;
                        font-size: 1.3rem;
                        margin-bottom: 1rem;
                        font-weight: 700;
                    '>
                        📸 Profile Picture
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Display current profile picture or placeholder
            if profile.get('profile_image'):
                try:
                    st.image(f"data:image/png;base64,{profile['profile_image']}", 
                            use_column_width=True,
                            caption="Your Profile Picture")
                except:
                    st.markdown("""
                        <div style='
                            width: 200px;
                            height: 200px;
                            background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin: 0 auto 1rem;
                            font-size: 4rem;
                        '>
                            👤
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='
                        width: 200px;
                        height: 200px;
                        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 1rem;
                        font-size: 4rem;
                    '>
                        👤
                    </div>
                """, unsafe_allow_html=True)
            
            # Upload new profile picture
            uploaded_file = st.file_uploader(
                "Upload Profile Picture",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a profile picture (PNG, JPG, JPEG)",
                key="profile_pic_upload"
            )
            
            if uploaded_file is not None:
                try:
                    # Read and resize image
                    image = Image.open(uploaded_file)
                    # Resize to max 300x300 to save space
                    image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    
                    # Convert to base64
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Preview
                    st.image(image, caption="Preview", use_column_width=True)
                    
                    if st.button("💾 Save Profile Picture", use_container_width=True):
                        update_user_profile_picture(st.session_state.user['id'], img_str)
                        st.success("✅ Profile picture updated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
        
        with col_right:
            # Profile Information Section
            st.markdown(f"""
                <div style='
                    background: rgba(255, 255, 255, 0.95);
                    padding: 2rem;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    margin: 1rem 0;
                '>
                    <h3 style='
                        color: #2D3748;
                        font-size: 1.5rem;
                        margin-bottom: 1.5rem;
                        font-weight: 700;
                    '>
                        📊 Profile Information
                    </h3>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
                        <div>
                            <strong>👤 Full Name:</strong> {profile['full_name']}
                        </div>
                        <div>
                            <strong>📧 Email:</strong> {profile['email']}
                        </div>
                        <div>
                            <strong>📅 Joined:</strong> {profile['created_at']}
                        </div>
                        <div>
                            <strong>⭐ Rating:</strong> {profile['rating']:.1f} ({profile['rating_count']} reviews)
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            
            st.markdown("""
                    <h3 style='
                        color: #2D3748;
                        font-size: 1.3rem;
                        margin-bottom: 1rem;
                        font-weight: 700;
                    '>
                        📝 Bio
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Initialize session state for bio editing
            if 'editing_bio' not in st.session_state:
                st.session_state.editing_bio = False
            
            if not st.session_state.editing_bio:
                # Display current bio
                current_bio = profile.get('bio') or "No bio added yet. Click Edit to add one!"
                st.markdown(f"""
                    <div style='
                        background: #F7FAFC;
                        padding: 1rem;
                        border-radius: 12px;
                        border: 1px solid #E2E8F0;
                        color: #2D3748;
                        margin-bottom: 1rem;
                    '>
                        {current_bio}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("✏️ Edit Bio", use_container_width=True):
                    st.session_state.editing_bio = True
                    st.rerun()
            else:
                # Bio editing form
                new_bio = st.text_area(
                    "Edit your bio",
                    value=profile.get('bio') or "",
                    height=150,
                    placeholder="Tell others about yourself, your interests, and what you're looking to learn or teach...",
                    help="Write a brief description about yourself"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Bio", use_container_width=True):
                        update_user_bio(st.session_state.user['id'], new_bio)
                        st.session_state.editing_bio = False
                        st.success("✅ Bio updated!")
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.editing_bio = False
                        st.rerun()

        # Social Media Links Section
        st.markdown("""
            
                <h3 style='
                    color: #2D3748;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    font-weight: 700;
                '>
                    🔗 Social Media(you can catch me there😊)
                </h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Get current social links
        social_links = get_user_social_links(st.session_state.user['id'])
        
        # Initialize session state for social links editing
        if 'editing_social' not in st.session_state:
            st.session_state.editing_social = False
        
        if not st.session_state.editing_social:
            # Display current links
            col1, col2 = st.columns(2)
            
            with col1:
                linkedin = social_links.get('linkedin_url') if social_links else None
                if linkedin:
                    st.markdown(f"💼 **LinkedIn:** [{linkedin}]({linkedin})")
                else:
                    st.markdown("💼 **LinkedIn:** *Not added*")
                
                github = social_links.get('github_url') if social_links else None
                if github:
                    st.markdown(f"💻 **GitHub:** [{github}]({github})")
                else:
                    st.markdown("💻 **GitHub:** *Not added*")
            
            with col2:
                twitter = social_links.get('twitter_url') if social_links else None
                if twitter:
                    st.markdown(f"🐦 **Twitter:** [{twitter}]({twitter})")
                else:
                    st.markdown("🐦 **Twitter:** *Not added*")
                
                portfolio = social_links.get('portfolio_url') if social_links else None
                if portfolio:
                    st.markdown(f"🌐 **Portfolio:** [{portfolio}]({portfolio})")
                else:
                    st.markdown("🌐 **Portfolio:** *Not added*")
            
            if st.button("✏️ Edit Social Links", use_container_width=True):
                st.session_state.editing_social = True
                st.rerun()
        else:
            # Social links editing form
            col1, col2 = st.columns(2)
            
            with col1:
                linkedin_input = st.text_input(
                    "💼 LinkedIn URL",
                    value=social_links.get('linkedin_url') if social_links else "",
                    placeholder="https://linkedin.com/in/yourprofile"
                )
                
                github_input = st.text_input(
                    "💻 GitHub URL",
                    value=social_links.get('github_url') if social_links else "",
                    placeholder="https://github.com/yourusername"
                )
            
            with col2:
                twitter_input = st.text_input(
                    "🐦 Twitter URL",
                    value=social_links.get('twitter_url') if social_links else "",
                    placeholder="https://twitter.com/yourusername"
                )
                
                portfolio_input = st.text_input(
                    "🌐 Portfolio URL",
                    value=social_links.get('portfolio_url') if social_links else "",
                    placeholder="https://yourportfolio.com"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Social Links", use_container_width=True):
                    update_social_links(
                        st.session_state.user['id'],
                        linkedin_input or None,
                        github_input or None,
                        twitter_input or None,
                        portfolio_input or None
                    )
                    st.session_state.editing_social = False
                    st.success("✅ Social links updated!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.editing_social = False
                    st.rerun()

        # Skills summary
        skills = get_user_skills(st.session_state.user['id'])
        st.markdown(f"""
            <div style='
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                margin: 1rem 0;
            '>
                <h3 style='
                    color: #2D3748;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    font-weight: 700;
                '>
                    🎯 Skills Summary
                </h3>
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;'>
                    <div style='text-align: center; padding: 1rem; background: #F7FAFC; border-radius: 12px;'>
                        <div style='font-size: 2rem; font-weight: bold; color: #6B46C1;'>{len(skills)}</div>
                        <div style='color: #4A5568;'>Total Skills</div>
                    </div>
        """, unsafe_allow_html=True)

        # Count skills by category
        category_count = {}
        for skill in skills:
            category = skill['category']
            category_count[category] = category_count.get(category, 0) + 1

        for category, count in category_count.items():
            st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: #F7FAFC; border-radius: 12px;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: #9F7AEA;'>{count}</div>
                        <div style='color: #4A5568;'>{category}</div>
                    </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

        # Exchanges summary
        exchanges = get_user_exchanges(st.session_state.user['id'])
        completed_exchanges = [e for e in exchanges if e['status'] == 'completed']
        pending_exchanges = [e for e in exchanges if e['status'] == 'pending']

        st.markdown(f"""
            <div style='
                background: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                margin: 1rem 0;
            '>
                <h3 style='
                    color: #2D3748;
                    font-size: 1.5rem;
                    margin-bottom: 1.5rem;
                    font-weight: 700;
                '>
                    🔄 Exchanges Summary
                </h3>
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;'>
                    <div style='text-align: center; padding: 1rem; background: #C6F6D5; border-radius: 12px;'>
                        <div style='font-size: 2rem; font-weight: bold; color: #276749;'>{len(completed_exchanges)}</div>
                        <div style='color: #276749;'>Completed</div>
                    </div>
                    <div style='text-align: center; padding: 1rem; background: #E9D8FD; border-radius: 12px;'>
                        <div style='font-size: 2rem; font-weight: bold; color: #553C9A;'>{len(pending_exchanges)}</div>
                        <div style='color: #553C9A;'>Pending</div>
                    </div>
                    <div style='text-align: center; padding: 1rem; background: #FEEBC8; border-radius: 12px;'>
                        <div style='font-size: 2rem; font-weight: bold; color: #C05621;'>{len(exchanges)}</div>
                        <div style='color: #C05621;'>Total</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Delete Account Section
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🗑️ Delete Account",
                       key="delete_account_btn",
                       use_container_width=True,
                       help="Permanently delete your account and all data"):
                success, message = auth_manager.delete_user(st.session_state.user['id'])
                if success:
                    st.success("Account deleted successfully. You will be redirected to the login page.")
                    st.session_state.user = None
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.error("Unable to load profile information")

# Main app logic
if __name__ == "__main__":
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'dashboard':
        dashboard_page()
