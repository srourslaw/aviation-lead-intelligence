# enhanced_dashboard_fixed.py - Mobile-Optimized IP-to-ZoomInfo Dashboard
import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import os
from pathlib import Path

st.set_page_config(
    page_title="IP-to-ZoomInfo Lead Generator",
    page_icon="🎯",
    layout="wide"
)

# Load external contacts database
@st.cache_data
def load_contacts_database():
    """Load contacts from external JSON file"""
    try:
        current_dir = Path(__file__).parent
        json_path = current_dir / 'zoominfo_contacts_database.json'
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Contacts database file not found!")
        return {}
    except Exception as e:
        st.error(f"❌ Error loading contacts database: {e}")
        return {}

# Load the contacts database
CONTACTS_DATABASE = load_contacts_database()

# Mobile-First Responsive CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        font-family: 'Inter', sans-serif;
        padding: 0.5rem;
    }
    
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .section-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .result-card {
        background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,200,81,0.2);
    }
    
    .compact-metric {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .compact-metric h4 {
        margin: 0;
        font-size: 0.8rem;
        color: #666;
        font-weight: 500;
    }
    
    .compact-metric h2 {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        color: #333;
        font-weight: 600;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.25rem;
        }
        
        .section-header {
            padding: 1rem;
        }
        
        .section-header h1 {
            font-size: 1.3rem !important;
        }
        
        .section-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .result-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .compact-metric {
            padding: 0.75rem;
            margin: 0.25rem 0;
        }
        
        .compact-metric h4 {
            font-size: 0.7rem;
        }
        
        .compact-metric h2 {
            font-size: 1rem;
        }
        
        /* Stack columns on mobile */
        div[data-testid="column"] {
            min-width: 100% !important;
        }
        
        /* Touch-friendly buttons */
        .stButton > button {
            width: 100%;
            min-height: 44px;
            font-size: 0.9rem;
        }
        
        /* Smaller charts */
        .js-plotly-plot {
            height: 250px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_company_from_ip(ip_address):
    """Convert IP to Company"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('org'):
            return {
                'success': True,
                'ip': ip_address,
                'organization': data['org'],
                'city': data.get('city', 'Unknown'),
                'region': data.get('regionName', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'timezone': data.get('timezone', 'Unknown')
            }
        return {'success': False, 'error': 'No company found for this IP'}
    except Exception as e:
        return {'success': False, 'error': f'Error: {str(e)}'}

def search_zoominfo(company_name, ip_address):
    """Search ZoomInfo database with randomization"""
    company_lower = company_name.lower()
    
    # Aviation companies mapping
    aviation_companies = {
        'boeing': ['boeing', 'the boeing company'],
        'delta': ['delta', 'delta air lines', 'delta airlines'],
        'american': ['american airlines', 'american', 'aa.com'],
        'lufthansa': ['lufthansa', 'lufthansa technik', 'lht'],
        'united': ['united airlines', 'united', 'ual'],
        'rolls-royce': ['rolls-royce', 'rolls royce', 'rr.com']
    }
    
    # Search for aviation companies
    for key, search_terms in aviation_companies.items():
        if any(term in company_lower for term in search_terms):
            if key in CONTACTS_DATABASE:
                contacts_list = CONTACTS_DATABASE[key]
                
                # Randomize contacts selection based on IP - ensure different results per IP
                random.seed(hash(ip_address + company_name))  # Use both IP and company for more variety
                num_contacts = random.randint(8, min(len(contacts_list), 15))  # Minimum 8 contacts
                selected_contacts = random.sample(contacts_list, num_contacts)
                
                # Add randomized metadata and realistic matching status
                for idx, contact in enumerate(selected_contacts):
                    # Use contact name + IP for unique randomization per contact
                    random.seed(hash(ip_address + contact['name'] + str(idx)))
                    
                    contact['confidence_score'] = f"{random.randint(85, 98)}%"
                    contact['last_updated'] = f"2025-01-{random.randint(10, 30):02d}"
                    contact['verified'] = '✅ Verified' if random.random() > 0.05 else '⚠️ Pending'
                    
                    # Company-specific matching rates (aviation companies have better coverage)
                    match_chance = random.random()
                    
                    if 'boeing' in company_name.lower():
                        # Boeing - premium coverage
                        if match_chance > 0.40:  # 60% full matches
                            contact['zoominfo_match'] = '🟢 Found in ZoomInfo DB'
                            contact['match_confidence'] = f"{random.randint(92, 99)}%"
                        elif match_chance > 0.15:  # 25% partial
                            contact['zoominfo_match'] = '🟡 Partial Match'
                            contact['match_confidence'] = f"{random.randint(75, 90)}%"
                        else:  # 15% not found
                            contact['zoominfo_match'] = '🔴 Not Found in ZoomInfo'
                            contact['match_confidence'] = f"{random.randint(45, 65)}%"
                    elif any(airline in company_name.lower() for airline in ['delta', 'american', 'united']):
                        # Major airlines - good coverage
                        if match_chance > 0.50:  # 50% full matches
                            contact['zoominfo_match'] = '🟢 Found in ZoomInfo DB'
                            contact['match_confidence'] = f"{random.randint(88, 96)}%"
                        elif match_chance > 0.20:  # 30% partial
                            contact['zoominfo_match'] = '🟡 Partial Match'
                            contact['match_confidence'] = f"{random.randint(70, 85)}%"
                        else:  # 20% not found
                            contact['zoominfo_match'] = '🔴 Not Found in ZoomInfo'
                            contact['match_confidence'] = f"{random.randint(40, 65)}%"
                    elif 'rolls-royce' in company_name.lower():
                        # Rolls-Royce - good coverage
                        if match_chance > 0.45:  # 55% full matches
                            contact['zoominfo_match'] = '🟢 Found in ZoomInfo DB'
                            contact['match_confidence'] = f"{random.randint(90, 97)}%"
                        elif match_chance > 0.20:  # 25% partial
                            contact['zoominfo_match'] = '🟡 Partial Match'
                            contact['match_confidence'] = f"{random.randint(72, 87)}%"
                        else:  # 20% not found
                            contact['zoominfo_match'] = '🔴 Not Found in ZoomInfo'
                            contact['match_confidence'] = f"{random.randint(42, 68)}%"
                    else:
                        # Other aviation companies - moderate coverage
                        if match_chance > 0.65:  # 35% full matches
                            contact['zoominfo_match'] = '🟢 Found in ZoomInfo DB'
                            contact['match_confidence'] = f"{random.randint(85, 93)}%"
                        elif match_chance > 0.35:  # 30% partial
                            contact['zoominfo_match'] = '🟡 Partial Match'
                            contact['match_confidence'] = f"{random.randint(65, 82)}%"
                        else:  # 35% not found
                            contact['zoominfo_match'] = '🔴 Not Found in ZoomInfo'
                            contact['match_confidence'] = f"{random.randint(38, 65)}%"
                
                # Company info
                company_info = {
                    'name': company_name,
                    'employees': f"{random.randint(1000, 50000):,}+",
                    'revenue': f"${random.randint(100, 2000)}M+",
                    'industry': 'Aviation & Aerospace',
                    'headquarters': 'Global Operations',
                    'website': f"www.{key}.com"
                }
                
                return {
                    'success': True,
                    'company': company_info,
                    'contacts': selected_contacts
                }
    
    # Generic fallback with randomized contacts
    random.seed(hash(ip_address + company_name + "fallback"))
    
    # Pool of realistic business names
    first_names = ['Michael', 'Sarah', 'David', 'Jennifer', 'Robert', 'Lisa', 'James', 'Maria', 'John', 'Amanda', 
                   'Christopher', 'Jessica', 'Daniel', 'Ashley', 'Matthew', 'Emily', 'Anthony', 'Melissa', 'Mark', 'Deborah',
                   'Steven', 'Dorothy', 'Paul', 'Carol', 'Andrew', 'Ruth', 'Kenneth', 'Sharon', 'Kevin', 'Michelle',
                   'Brian', 'Laura', 'George', 'Sarah', 'Edward', 'Kimberly', 'Ronald', 'Nancy', 'Timothy', 'Linda']
    
    last_names = ['Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez',
                  'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee',
                  'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
                  'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green']
    
    titles = [
        {'title': 'Chief Executive Officer', 'seniority': 'C-Level'},
        {'title': 'Chief Financial Officer', 'seniority': 'C-Level'},
        {'title': 'Chief Technology Officer', 'seniority': 'C-Level'},
        {'title': 'Chief Operations Officer', 'seniority': 'C-Level'},
        {'title': 'VP Business Development', 'seniority': 'VP-Level'},
        {'title': 'VP Operations', 'seniority': 'VP-Level'},
        {'title': 'VP Sales', 'seniority': 'VP-Level'},
        {'title': 'VP Marketing', 'seniority': 'VP-Level'},
        {'title': 'Director Supply Chain', 'seniority': 'Director'},
        {'title': 'Director Procurement', 'seniority': 'Director'},
        {'title': 'Director Business Development', 'seniority': 'Director'},
        {'title': 'Director Operations', 'seniority': 'Director'},
        {'title': 'Senior Manager Strategic Partnerships', 'seniority': 'Director'},
        {'title': 'Manager Business Operations', 'seniority': 'Manager'}
    ]
    
    # Generate 3-6 random contacts
    num_contacts = random.randint(3, 6)
    selected_names = random.sample([(f, l) for f in first_names for l in last_names], num_contacts)
    selected_titles = random.sample(titles, num_contacts)
    
    contacts = []
    company_domain = company_name.lower().replace(' ', '').replace('inc', '').replace('corp', '').replace('ltd', '')[:10]
    
    for i, ((first, last), title_info) in enumerate(zip(selected_names, selected_titles)):
        # Use unique randomization per contact
        random.seed(hash(ip_address + f"{first}{last}" + str(i)))
        
        contact = {
            'name': f"{first} {last}",
            'title': title_info['title'],
            'email': f"{first.lower()}.{last.lower()}@{company_domain}.com",
            'phone': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            'seniority': title_info['seniority'],
            'confidence_score': f"{random.randint(70, 88)}%",
            'last_updated': f"2025-01-{random.randint(5, 25):02d}",
            'verified': '✅ Verified' if random.random() > 0.25 else '⚠️ Pending'
        }
        
        # More varied matching for unknown companies
        match_chance = random.random()
        if match_chance > 0.85:  # 15% chance for full match
            contact['zoominfo_match'] = '🟢 Found in ZoomInfo DB'
            contact['match_confidence'] = f"{random.randint(85, 95)}%"
        elif match_chance > 0.50:  # 35% chance for partial match
            contact['zoominfo_match'] = '🟡 Partial Match'
            contact['match_confidence'] = f"{random.randint(60, 80)}%"
        else:  # 50% chance for not found
            contact['zoominfo_match'] = '🔴 Not Found in ZoomInfo'
            contact['match_confidence'] = f"{random.randint(35, 65)}%"
            
        contacts.append(contact)
    
    return {
        'success': True,
        'company': {
            'name': company_name,
            'employees': f"{random.randint(500, 10000):,}+",
            'revenue': f"${random.randint(50, 500)}M+",
            'industry': 'Business Services',
            'headquarters': 'Various Locations',
            'website': f"www.{company_domain}.com"
        },
        'contacts': contacts
    }

# App Header
st.markdown("""
<div class="section-header">
    <h1>✈️ B&H Worldwide: Aviation Lead Intelligence</h1>
    <p>Convert Website Visitors → Aviation Companies → Decision Maker Contacts</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = []

# Load and display B&H Worldwide's visitor tracking data
st.markdown("""
<div class="section-card">
    <h2 style="color: #667eea; margin-top: 0;">📊 B&H Worldwide Visitor Intelligence Dashboard</h2>
    <p style="color: #666; margin: 0.5rem 0;">Real-time tracking of bhworldwide.com visitors with ZoomInfo lead generation</p>
</div>
""", unsafe_allow_html=True)

# Create sample visitor data that looks like real website analytics
@st.cache_data
def generate_visitor_data():
    """Generate realistic visitor data for B&H Worldwide"""
    import datetime
    
    visitors = []
    base_time = datetime.datetime.now()
    
    # Recent visitors from aviation companies
    visitor_scenarios = [
        {"company": "Boeing Company", "ip": "52.16.0.0", "page": "/aog-services", "country": "United States", "duration": "4:32"},
        {"company": "Delta Air Lines", "ip": "199.168.0.0", "page": "/dangerous-goods", "country": "United States", "duration": "2:18"},
        {"company": "American Airlines", "ip": "104.244.0.0", "page": "/trade-compliance", "country": "United States", "duration": "3:45"},
        {"company": "Lufthansa Technik", "ip": "64.233.160.0", "page": "/expertise", "country": "Germany", "duration": "5:12"},
        {"company": "United Airlines", "ip": "157.240.0.0", "page": "/our-delivery", "country": "United States", "duration": "1:56"},
        {"company": "Rolls-Royce", "ip": "208.67.222.0", "page": "/working-with-us", "country": "United Kingdom", "duration": "6:23"},
        {"company": "Emirates", "ip": "173.252.66.0", "page": "/aog-services", "country": "UAE", "duration": "3:17"},
        {"company": "British Airways", "ip": "216.58.194.0", "page": "/services", "country": "United Kingdom", "duration": "2:44"},
        {"company": "Singapore Airlines", "ip": "192.30.253.0", "page": "/dangerous-goods", "country": "Singapore", "duration": "4:08"},
        {"company": "Air France-KLM", "ip": "104.18.0.0", "page": "/aog-services", "country": "France", "duration": "3:52"}
    ]
    
    for i, scenario in enumerate(visitor_scenarios):
        time_offset = datetime.timedelta(minutes=random.randint(5, 180))
        visit_time = base_time - time_offset
        
        visitors.append({
            'timestamp': visit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ip': scenario['ip'],
            'organization': scenario['company'],
            'page_visited': scenario['page'],
            'country': scenario['country'],
            'session_duration': scenario['duration'],
            'pages_viewed': random.randint(2, 8),
            'lead_potential': 'High' if i < 6 else 'Medium',
            'status': 'New' if i < 3 else 'Analyzed' if i < 7 else 'Processed'
        })
    
    return visitors

visitor_data = generate_visitor_data()

# Website Analytics Overview
st.markdown("#### 🌐 Recent bhworldwide.com Visitors")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="compact-metric">
        <h4>Today's Visitors</h4>
        <h2>{len(visitor_data)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    high_potential = len([v for v in visitor_data if v['lead_potential'] == 'High'])
    st.markdown(f"""
    <div class="compact-metric">
        <h4>High-Value Leads</h4>
        <h2>{high_potential}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    new_visitors = len([v for v in visitor_data if v['status'] == 'New'])
    st.markdown(f"""
    <div class="compact-metric">
        <h4>Unprocessed</h4>
        <h2>{new_visitors}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_pages = sum(v['pages_viewed'] for v in visitor_data) / len(visitor_data)
    st.markdown(f"""
    <div class="compact-metric">
        <h4>Avg Pages/Visit</h4>
        <h2>{avg_pages:.1f}</h2>
    </div>
    """, unsafe_allow_html=True)

# Visitor tracking table
st.markdown("##### 📋 Website Visitor Log")

# Convert to dataframe for display
visitor_df = pd.DataFrame(visitor_data)
visitor_df = visitor_df[['timestamp', 'organization', 'ip', 'page_visited', 'country', 'session_duration', 'lead_potential', 'status']]
visitor_df.columns = ['Visit Time', 'Organization', 'IP Address', 'Page Visited', 'Country', 'Duration', 'Lead Potential', 'Status']

# Color code by status
def highlight_status(row):
    if row['Status'] == 'New':
        return ['background-color: #fff3cd'] * len(row)  # Yellow for new
    elif row['Status'] == 'Analyzed':
        return ['background-color: #d4edda'] * len(row)  # Green for analyzed
    else:
        return ['background-color: #f8f9fa'] * len(row)  # Gray for processed

st.dataframe(
    visitor_df.style.apply(highlight_status, axis=1),
    use_container_width=True, 
    hide_index=True
)

# Action section
st.markdown("#### 🚀 Lead Generation Actions")

action_col1, action_col2 = st.columns(2)

with action_col1:
    st.markdown("**📈 Analyze Visitor:**")
    selected_visitor = st.selectbox(
        "Select visitor to analyze",
        options=range(len(visitor_data)),
        format_func=lambda x: f"{visitor_data[x]['organization']} ({visitor_data[x]['ip']})",
        help="Choose a visitor from your website analytics to generate leads"
    )
    
    analyze_visitor = st.button("🔍 Generate Lead Intelligence", type="primary", use_container_width=True)

with action_col2:
    st.markdown("**⚡ Quick Actions:**")
    if st.button("📊 Analyze All New Visitors", use_container_width=True):
        st.info("Processing all new visitors... This may take a few moments.")
    if st.button("📥 Export Visitor Data", use_container_width=True):
        csv = visitor_df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv, "bhworldwide_visitors.csv", "text/csv")

# Process selected visitor
process_single = False
if analyze_visitor and selected_visitor is not None:
    selected_data = visitor_data[selected_visitor]
    single_ip = selected_data['ip']
    process_single = True
    
    # Show context about the visitor
    st.markdown(f"""
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196F3; margin: 1rem 0;">
        <h5 style="margin: 0 0 0.5rem 0; color: #1976D2;">🎯 Analyzing Visitor</h5>
        <p style="margin: 0; font-size: 0.9rem;"><strong>Company:</strong> {selected_data['organization']}</p>
        <p style="margin: 0; font-size: 0.9rem;"><strong>IP Address:</strong> {selected_data['ip']}</p>
        <p style="margin: 0; font-size: 0.9rem;"><strong>Page Visited:</strong> {selected_data['page_visited']}</p>
        <p style="margin: 0; font-size: 0.9rem;"><strong>Visit Duration:</strong> {selected_data['session_duration']}</p>
        <p style="margin: 0; font-size: 0.9rem;"><strong>Lead Potential:</strong> {selected_data['lead_potential']}</p>
    </div>
    """, unsafe_allow_html=True)

# Process and display results
if process_single and single_ip:
    with st.spinner("🔍 Processing IP address..."):
        company_result = get_company_from_ip(single_ip)
        
        if company_result['success']:
            zoominfo_result = search_zoominfo(company_result['organization'], single_ip)
            
            # Add to results
            new_result = {
                'ip': single_ip,
                'company_data': company_result,
                'zoominfo_data': zoominfo_result
            }
            
            # Update or add result
            existing_index = None
            for idx, existing in enumerate(st.session_state.processed_results):
                if existing['ip'] == single_ip:
                    existing_index = idx
                    break
            
            if existing_index is not None:
                st.session_state.processed_results[existing_index] = new_result
            else:
                st.session_state.processed_results.append(new_result)
        else:
            st.error(f"❌ {company_result['error']}")

# Display Results
if st.session_state.processed_results:
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    if st.button("🗑️ Clear All Results", type="secondary"):
        st.session_state.processed_results = []
        st.rerun()
    
    for i, result in enumerate(st.session_state.processed_results):
        ip = result['ip']
        company_data = result['company_data']
        zoominfo_data = result['zoominfo_data']
        company_info = zoominfo_data['company']
        
        st.markdown(f"""
        <div class="result-card">
            <h3>✅ Result #{i+1}: Lead from IP {ip}</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{company_info['name']} • {company_info['industry']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs
        company_tab, contacts_tab, database_tab, summary_tab = st.tabs(["🏢 Company", "👥 Contacts", "🗄️ ZoomInfo DB", "📊 Summary"])
        
        with company_tab:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🌐 IP Analysis")
                st.write(f"**IP:** {company_data['ip']}")
                st.write(f"**Organization:** {company_data['organization']}")
                st.write(f"**Location:** {company_data['city']}, {company_data['country']}")
                
            with col2:
                st.markdown("#### 🏢 Company Profile")
                st.write(f"**Company:** {company_info['name']}")
                st.write(f"**Employees:** {company_info['employees']}")
                st.write(f"**Revenue:** {company_info['revenue']}")
                st.write(f"**Industry:** {company_info['industry']}")
        
        with contacts_tab:
            st.markdown("#### 👥 Contact Database")
            
            # Create contacts dataframe with matching status
            contacts_data = []
            for contact in zoominfo_data['contacts']:
                contacts_data.append({
                    'Name': contact['name'],
                    'Title': contact['title'],
                    'Email': contact['email'],
                    'Phone': contact['phone'],
                    'Seniority': contact.get('seniority', 'Director'),
                    'ZoomInfo Match': contact.get('zoominfo_match', '🟢 Found in ZoomInfo DB'),
                    'Match Confidence': contact.get('match_confidence', '95%'),
                    'Last Updated': contact.get('last_updated', '2025-01-15')
                })
            
            contacts_df = pd.DataFrame(contacts_data)
            st.dataframe(contacts_df, use_container_width=True, hide_index=True)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv = contacts_df.to_csv(index=False)
                st.download_button(
                    "📥 Export CSV", 
                    csv, 
                    f"contacts_{company_info['name']}.csv", 
                    "text/csv",
                    key=f"export_csv_{i}"
                )
            with col2:
                st.button("📧 Send to CRM", use_container_width=True, key=f"crm_button_{i}")
        
        with database_tab:
            st.markdown("#### 🗄️ ZoomInfo Database Matching Process")
            
            # Show the matching process
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea;">
                <h5 style="margin: 0 0 0.5rem 0; color: #667eea;">🔍 Database Query Process</h5>
                <p style="margin: 0; font-size: 0.9rem;"><strong>1. IP Analysis:</strong> {company_data['ip']} → {company_data['organization']}</p>
                <p style="margin: 0; font-size: 0.9rem;"><strong>2. Company Matching:</strong> Searching for "{company_info['name']}" in ZoomInfo database</p>
                <p style="margin: 0; font-size: 0.9rem;"><strong>3. Contact Extraction:</strong> Found {len(zoominfo_data['contacts'])} verified contacts</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Contact Matching Results
            st.markdown("##### 🎯 Contact Matching Results")
            
            # Calculate matching statistics
            total_contacts = len(zoominfo_data['contacts'])
            full_matches = len([c for c in zoominfo_data['contacts'] if '🟢' in c.get('zoominfo_match', '')])
            partial_matches = len([c for c in zoominfo_data['contacts'] if '🟡' in c.get('zoominfo_match', '')])
            no_matches = len([c for c in zoominfo_data['contacts'] if '🔴' in c.get('zoominfo_match', '')])
            
            # Matching results display
            match_col1, match_col2, match_col3, match_col4 = st.columns(4)
            
            with match_col1:
                st.markdown(f"""
                <div class="compact-metric" style="border-left: 4px solid #00C851;">
                    <h4>Full Matches</h4>
                    <h2>{full_matches}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with match_col2:
                st.markdown(f"""
                <div class="compact-metric" style="border-left: 4px solid #ffbb33;">
                    <h4>Partial Matches</h4>
                    <h2>{partial_matches}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with match_col3:
                st.markdown(f"""
                <div class="compact-metric" style="border-left: 4px solid #ff4444;">
                    <h4>Not Found</h4>
                    <h2>{no_matches}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with match_col4:
                match_rate = (full_matches + partial_matches) / total_contacts * 100 if total_contacts > 0 else 0
                st.markdown(f"""
                <div class="compact-metric" style="border-left: 4px solid #667eea;">
                    <h4>Match Rate</h4>
                    <h2>{match_rate:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed matching breakdown
            if total_contacts > 0:
                st.markdown("**📋 Contact Matching Breakdown:**")
                
                matching_data = []
                for contact in zoominfo_data['contacts']:
                    matching_data.append({
                        'Contact Name': contact['name'],
                        'Title': contact['title'],
                        'Match Status': contact.get('zoominfo_match', '🟢 Found in ZoomInfo DB'),
                        'Match Confidence': contact.get('match_confidence', '95%'),
                        'Data Source': 'ZoomInfo Professional' if '🟢' in contact.get('zoominfo_match', '') else 'External Enrichment'
                    })
                
                matching_df = pd.DataFrame(matching_data)
                st.dataframe(matching_df, use_container_width=True, hide_index=True)
                
                # Matching algorithm explanation
                st.markdown("""
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; border-left: 4px solid #00C851;">
                    <h6 style="margin: 0 0 0.5rem 0; color: #2e7d32;">✅ Matching Logic Explained:</h6>
                    <ul style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li><strong>🟢 Full Match:</strong> Contact found with verified email and phone in ZoomInfo database</li>
                        <li><strong>🟡 Partial Match:</strong> Name and company match, but some details need verification</li>
                        <li><strong>🔴 Not Found:</strong> Contact discovered through external sources, not yet in ZoomInfo</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Show database statistics
            st.markdown("##### 📊 Database Coverage Statistics")
            
            # Show available companies in database
            if CONTACTS_DATABASE:
                st.markdown("**Available Companies in ZoomInfo Database:**")
                
                db_stats = []
                for company_key, contacts_list in CONTACTS_DATABASE.items():
                    db_stats.append({
                        'Company': company_key.title(),
                        'Total Contacts': len(contacts_list),
                        'C-Level': len([c for c in contacts_list if c.get('seniority') == 'C-Level']),
                        'VP-Level': len([c for c in contacts_list if c.get('seniority') == 'VP-Level']),
                        'Directors': len([c for c in contacts_list if c.get('seniority') == 'Director']),
                        'Coverage': '🟢 Complete' if len(contacts_list) > 15 else '🟡 Partial'
                    })
                
                db_df = pd.DataFrame(db_stats)
                st.dataframe(db_df, use_container_width=True, hide_index=True)
                
                # Database summary metrics
                total_contacts = sum(len(contacts) for contacts in CONTACTS_DATABASE.values())
                total_companies = len(CONTACTS_DATABASE)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="compact-metric">
                        <h4>Total Companies</h4>
                        <h2>{total_companies}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col2:
                    st.markdown(f"""
                    <div class="compact-metric">
                        <h4>Total Contacts</h4>
                        <h2>{total_contacts:,}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col3:
                    avg_contacts = total_contacts // total_companies if total_companies > 0 else 0
                    st.markdown(f"""
                    <div class="compact-metric">
                        <h4>Avg per Company</h4>
                        <h2>{avg_contacts}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col4:
                    st.markdown(f"""
                    <div class="compact-metric">
                        <h4>Database Status</h4>
                        <h2>🟢 Online</h2>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show matching algorithm
            st.markdown("##### 🤖 Matching Algorithm")
            
            st.markdown("""
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px;">
                <h6 style="margin: 0 0 0.5rem 0; color: #1976D2;">How We Match Contacts:</h6>
                <ol style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">
                    <li><strong>IP Geolocation:</strong> Extract organization name from IP address</li>
                    <li><strong>Company Recognition:</strong> Match against aviation industry database</li>
                    <li><strong>Contact Selection:</strong> Randomly select 8-15 verified contacts</li>
                    <li><strong>Data Enrichment:</strong> Add confidence scores and verification status</li>
                    <li><strong>Quality Assurance:</strong> Ensure contact diversity across seniority levels</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
            
            # Show data freshness
            st.markdown("##### 🔄 Data Freshness & Verification")
            
            verification_stats = {
                'Verified': len([c for c in zoominfo_data['contacts'] if '✅' in c.get('verified', '')]),
                'Pending': len([c for c in zoominfo_data['contacts'] if '⚠️' in c.get('verified', '')])
            }
            
            fig_verification = go.Figure(data=[go.Pie(
                labels=list(verification_stats.keys()),
                values=list(verification_stats.values()),
                hole=0.4,
                marker_colors=['#00C851', '#ffbb33']
            )])
            fig_verification.update_layout(
                title="Contact Verification Status",
                height=250,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_verification, use_container_width=True, key=f"verification_pie_{i}")
            
            # Show API simulation
            st.markdown("##### 🔌 API Integration Status")
            st.markdown("""
            <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h6 style="margin: 0 0 0.5rem 0; color: #856404;">📡 Demo Mode Active</h6>
                <p style="margin: 0; font-size: 0.9rem;">Currently using simulated ZoomInfo database for demonstration.</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;"><strong>Production Setup:</strong> Connect to real ZoomInfo API for live data access.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_tab:
            # Mobile-optimized summary
            company_name = company_info['name'].lower()
            
            # Company-specific scoring
            if 'boeing' in company_name:
                lead_score = "🔥 AEROSPACE GIANT"
                revenue_potential = "$500K - $2M+"
                priority = "PLATINUM"
                score_value = 95
            elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                lead_score = "✈️ MAJOR AIRLINE"
                revenue_potential = "$200K - $800K"
                priority = "GOLD"
                score_value = 85
            else:
                lead_score = "✅ QUALIFIED LEAD"
                revenue_potential = "$50K - $300K"
                priority = "SILVER"
                score_value = 70
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Lead Score</h4>
                    <h2>{lead_score}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Revenue Potential</h4>
                    <h2>{revenue_potential}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Contacts Found</h4>
                    <h2>{len(zoominfo_data['contacts'])}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Priority</h4>
                    <h2>{priority}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Business Intelligence Visualizations
            st.markdown("#### 📊 Business Intelligence Analysis")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Lead Score Gauge Chart with IP-specific variation
                random.seed(hash(ip + company_name))
                actual_score = score_value + random.randint(-8, 8)  # Add variation based on IP
                actual_score = max(50, min(100, actual_score))  # Keep in range
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=actual_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Lead Score: {company_info['name']}", 'font': {'size': 14}},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [None, 100], 'tickfont': {'size': 12}},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 50], 'color': "#ffebee"},
                            {'range': [50, 80], 'color': "#e3f2fd"},
                            {'range': [80, 100], 'color': "#e8f5e8"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_chart_{i}")
                
            with viz_col2:
                # Revenue Potential Distribution Curve - IP-specific
                random.seed(hash(ip + company_name + "revenue"))
                if 'boeing' in company_name:
                    revenue_min, revenue_max = 500000, 2000000
                elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                    revenue_min, revenue_max = 200000, 800000
                elif 'lufthansa' in company_name:
                    revenue_min, revenue_max = 100000, 500000
                elif 'rolls-royce' in company_name:
                    revenue_min, revenue_max = 300000, 1000000
                else:
                    revenue_min, revenue_max = 50000, 300000
                
                # Add IP-specific variation to revenue ranges
                actual_rev_min = revenue_min + random.randint(-50000, 50000)
                actual_rev_max = revenue_max + random.randint(-100000, 100000)
                actual_rev_min = max(10000, actual_rev_min)
                actual_rev_max = max(actual_rev_min + 50000, actual_rev_max)
                
                # Create revenue probability distribution
                revenue_range = np.linspace(actual_rev_min, actual_rev_max, 100)
                center = (actual_rev_min + actual_rev_max) / 2
                width_factor = 4 + random.randint(1, 4)  # Vary curve width
                probability = np.exp(-((revenue_range - center)**2) / (2 * ((actual_rev_max - actual_rev_min)/width_factor)**2))
                
                fig_revenue = go.Figure()
                fig_revenue.add_trace(go.Scatter(
                    x=revenue_range/1000,  # Convert to thousands
                    y=probability,
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.3)',
                    line=dict(color='#667eea', width=2),
                    name='Revenue Probability',
                    hovertemplate='Revenue: $%{x}K<br>Probability: %{y:.2f}<extra></extra>'
                ))
                fig_revenue.update_layout(
                    title={'text': f'Revenue Potential: {company_info["name"]}', 'font': {'size': 14}},
                    xaxis_title={'text': 'Revenue (K$)', 'font': {'size': 12}},
                    yaxis_title={'text': 'Probability', 'font': {'size': 12}},
                    height=300,
                    margin=dict(l=40, r=20, t=40, b=40),
                    showlegend=False
                )
                st.plotly_chart(fig_revenue, use_container_width=True, key=f"revenue_curve_{i}")
            
            # Company Analysis Charts
            st.markdown("#### 🏢 Company Profile Analysis")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Industry Comparison Bar Chart - Realistic data based on IP/Company
                random.seed(hash(ip + "industry"))
                
                # Base industry scores with realistic variations
                base_industry_data = {
                    'Aerospace & Defense': (82, 92),
                    'Commercial Aviation': (85, 95), 
                    'Aircraft Maintenance': (70, 85),
                    'Engine Manufacturing': (78, 88),
                    'Business Services': (55, 75)
                }
                
                industry_data = {}
                for industry, (min_score, max_score) in base_industry_data.items():
                    industry_data[industry] = random.randint(min_score, max_score)
                
                current_industry = company_info['industry']
                if current_industry in industry_data:
                    industry_data[current_industry] = int(actual_score)
                
                colors = ['#667eea' if industry == current_industry else '#e0e0e0' for industry in industry_data.keys()]
                
                fig_industry = go.Figure(data=[
                    go.Bar(
                        x=list(industry_data.keys()),
                        y=list(industry_data.values()),
                        marker_color=colors,
                        text=list(industry_data.values()),
                        textposition='auto',
                        hovertemplate='Industry: %{x}<br>Score: %{y}<extra></extra>'
                    )
                ])
                fig_industry.update_layout(
                    title={'text': 'Industry Lead Score Comparison', 'font': {'size': 14}},
                    xaxis_title={'text': 'Industry', 'font': {'size': 12}},
                    yaxis_title={'text': 'Avg Lead Score', 'font': {'size': 12}},
                    height=300,
                    margin=dict(l=40, r=20, t=40, b=80),
                    xaxis={'tickangle': -45, 'tickfont': {'size': 10}}
                )
                st.plotly_chart(fig_industry, use_container_width=True, key=f"industry_chart_{i}")
                
            with chart_col2:
                # Contact Roles Distribution Pie Chart - Based on actual contacts
                contact_roles = {}
                for contact in zoominfo_data['contacts']:
                    seniority = contact.get('seniority', 'Director')
                    if seniority == 'C-Level':
                        category = 'C-Level Executives'
                    elif seniority == 'VP-Level':
                        category = 'VP/Senior Directors'
                    else:
                        category = 'Directors/Managers'
                    
                    contact_roles[category] = contact_roles.get(category, 0) + 1
                
                fig_contacts = go.Figure(data=[go.Pie(
                    labels=list(contact_roles.keys()),
                    values=list(contact_roles.values()),
                    hole=.3,
                    marker_colors=['#667eea', '#764ba2', '#00C851'],
                    hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig_contacts.update_layout(
                    title={'text': 'Contact Seniority Distribution', 'font': {'size': 14}},
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_contacts, use_container_width=True, key=f"contacts_pie_{i}")
            
            # ROI Calculator - IP-specific values
            st.markdown("#### 💰 ROI Calculator & Financial Analysis")
            
            roi_col1, roi_col2, roi_col3 = st.columns(3)
            
            with roi_col1:
                # Realistic conversion rates based on company type
                random.seed(hash(ip + "conversion"))
                if 'boeing' in company_name:
                    conversion_rate = random.uniform(0.18, 0.25)
                elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                    conversion_rate = random.uniform(0.12, 0.18)
                elif 'lufthansa' in company_name:
                    conversion_rate = random.uniform(0.08, 0.14)
                elif 'rolls-royce' in company_name:
                    conversion_rate = random.uniform(0.15, 0.22)
                else:
                    conversion_rate = random.uniform(0.05, 0.12)
                    
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Est. Conversion Rate</h4>
                    <h2>{conversion_rate:.1%}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with roi_col2:
                expected_value = (actual_rev_min + actual_rev_max) / 2 * conversion_rate
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>Expected Value</h4>
                    <h2>${expected_value:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
            with roi_col3:
                # Realistic cost per lead based on company complexity
                random.seed(hash(ip + "cost"))
                if 'boeing' in company_name:
                    cost_per_lead = random.randint(12000, 18000)
                elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                    cost_per_lead = random.randint(7000, 12000)
                elif 'lufthansa' in company_name:
                    cost_per_lead = random.randint(8000, 14000)
                elif 'rolls-royce' in company_name:
                    cost_per_lead = random.randint(10000, 15000)
                else:
                    cost_per_lead = random.randint(4000, 8000)
                
                roi_percentage = (expected_value / cost_per_lead) * 100 if cost_per_lead > 0 else 0
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>ROI Potential</h4>
                    <h2>{roi_percentage:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Revenue Distribution Histogram
            st.markdown("#### 📈 Revenue Distribution Analysis")
            
            # Create histogram of potential revenue outcomes
            random.seed(hash(ip + "histogram"))
            revenue_samples = np.random.normal(
                (actual_rev_min + actual_rev_max) / 2, 
                (actual_rev_max - actual_rev_min) / 6, 
                1000
            )
            revenue_samples = np.clip(revenue_samples, actual_rev_min * 0.5, actual_rev_max * 1.5)
            
            fig_hist = go.Figure(data=[go.Histogram(
                x=revenue_samples/1000,
                nbinsx=30,
                marker_color='rgba(102, 126, 234, 0.7)',
                name='Revenue Distribution',
                hovertemplate='Revenue Range: $%{x}K<br>Frequency: %{y}<extra></extra>'
            )])
            
            fig_hist.update_layout(
                title=f'Revenue Potential Distribution - {company_info["name"]}',
                xaxis_title='Revenue (K$)',
                yaxis_title='Frequency',
                height=350,
                margin=dict(l=40, r=20, t=40, b=40),
                showlegend=False
            )
            
            st.plotly_chart(fig_hist, use_container_width=True, key=f"revenue_histogram_{i}")
            
            # Debug info for verification
            st.markdown(f"**🔍 Analysis Summary for IP {ip}:**")
            st.markdown(f"- **Lead Score:** {actual_score}/100")
            st.markdown(f"- **Revenue Range:** ${actual_rev_min:,} - ${actual_rev_max:,}")
            st.markdown(f"- **Conversion Rate:** {conversion_rate:.1%}")
            st.markdown(f"- **Expected Value:** ${expected_value:,.0f}")
            st.markdown(f"- **Cost per Lead:** ${cost_per_lead:,}")
            st.markdown(f"- **ROI:** {roi_percentage:.0f}%")
            st.markdown(f"- **Contacts Found:** {len(zoominfo_data['contacts'])}")

else:
    st.info("👆 Enter an IP address or click a demo button to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>🎯 Aviation Lead Intelligence Dashboard</strong></p>
    <p>Convert anonymous website visitors into qualified business leads</p>
</div>
""", unsafe_allow_html=True)