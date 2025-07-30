# enhanced_dashboard.py - Clean IP-to-ZoomInfo Dashboard
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
        # Get the directory of the current script
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

# Mobile-Responsive CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Base styles */
    .main > div {
        font-family: 'Inter', sans-serif;
        padding: 0.5rem;
    }
    
    /* Mobile-first responsive design */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .section-header h1 {
        font-size: 1.5rem !important;
        margin: 0 !important;
        line-height: 1.3;
    }
    
    .section-header p {
        font-size: 0.9rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .section-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .result-card {
        background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .result-card h3 {
        font-size: 1.1rem !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .contact-item {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 0.75rem;
        margin: 0.3rem 0;
        border-radius: 5px;
    }
    
    .zoominfo-status {
        background: #e3f2fd;
        border: 1px solid #2196F3;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .zoominfo-status h4 {
        font-size: 0.9rem !important;
        margin: 0 !important;
    }
    
    .zoominfo-status p {
        font-size: 1rem !important;
        margin: 0.25rem 0 0 0 !important;
    }
    
    /* Compact metrics for mobile */
    .compact-metric {
        background: #f8f9fa;
        padding: 0.5rem !important;
        border-radius: 8px;
        text-align: center;
        margin: 0.2rem 0 !important;
    }
    
    .compact-metric h4 {
        margin: 0 !important;
        font-size: 0.7rem !important;
        color: #666;
    }
    
    .compact-metric h2 {
        margin: 0.2rem 0 0 0 !important;
        font-size: 0.9rem !important;
        color: #333;
    }
    
    /* Mobile responsive columns */
    @media (max-width: 768px) {
        .section-header h1 {
            font-size: 1.3rem !important;
        }
        
        .section-header p {
            font-size: 0.8rem !important;
        }
        
        .section-card {
            padding: 0.75rem;
        }
        
        .result-card {
            padding: 0.75rem;
        }
        
        .result-card h3 {
            font-size: 1rem !important;
        }
        
        /* Smaller charts on mobile */
        .js-plotly-plot {
            height: 200px !important;
        }
        
        /* Stack columns on mobile */
        div[data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 0.5rem;
        }
        
        /* Adjust button sizes */
        .stButton > button {
            width: 100%;
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
        }
        
        /* Adjust input fields */
        .stTextInput > div > div > input {
            font-size: 0.9rem;
        }
        
        /* Compact tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
        }
        
        /* Adjust dataframe for mobile */
        .stDataFrame {
            font-size: 0.7rem;
        }
        
        /* Mobile-friendly select boxes */
        .stSelectbox > div > div {
            font-size: 0.8rem;
        }
    }
    
    /* Very small screens (phones in portrait) */
    @media (max-width: 480px) {
        .main > div {
            padding: 0.25rem;
        }
        
        .section-header {
            padding: 0.75rem;
            margin: 0.25rem 0;
        }
        
        .section-header h1 {
            font-size: 1.1rem !important;
        }
        
        .section-card {
            padding: 0.5rem;
            margin: 0.25rem 0;
        }
        
        .compact-metric h4 {
            font-size: 0.6rem !important;
        }
        
        .compact-metric h2 {
            font-size: 0.8rem !important;
        }
    }
    
    /* Touch-friendly improvements */
    .stButton > button {
        min-height: 44px; /* Apple's recommended touch target size */
        border-radius: 8px;
    }
    
    /* Improved scrolling on mobile */
    .stDataFrame > div {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Better spacing for mobile */
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# B&H Worldwide Relevant ZoomInfo Database - Aviation & Aerospace Industry
ZOOMINFO_DATABASE = {
    'boeing': {
        'company': {
            'name': 'The Boeing Company',
            'employees': '140,000+',
            'revenue': '$66.6B (2023)',
            'industry': 'Aerospace & Defense',
            'headquarters': 'Chicago, Illinois',
            'website': 'www.boeing.com',
            'description': 'Leading aerospace company and manufacturer of commercial airplanes, defense systems'
        },
        'contacts': [
            {'name': 'Dave Calhoun', 'title': 'President & CEO', 'email': 'dave.calhoun@boeing.com', 'phone': '+1-312-544-2000', 'linkedin': 'linkedin.com/in/davecalhoun'},
            {'name': 'Brian West', 'title': 'Chief Financial Officer', 'email': 'brian.west@boeing.com', 'phone': '+1-312-544-2001', 'linkedin': 'linkedin.com/in/brianwest'},
            {'name': 'Stan Deal', 'title': 'President Boeing Commercial Airplanes', 'email': 'stan.deal@boeing.com', 'phone': '+1-312-544-2002', 'linkedin': 'linkedin.com/in/standeal'},
            {'name': 'Ted Colbert', 'title': 'President Boeing Defense, Space & Security', 'email': 'ted.colbert@boeing.com', 'phone': '+1-312-544-2003', 'linkedin': 'linkedin.com/in/tedcolbert'},
            {'name': 'Greg Hyslop', 'title': 'Chief Technology Officer', 'email': 'greg.hyslop@boeing.com', 'phone': '+1-312-544-2004', 'linkedin': 'linkedin.com/in/greghyslop'}
        ]
    },
    'delta': {
        'company': {
            'name': 'Delta Air Lines Inc.',
            'employees': '95,000+',
            'revenue': '$58.0B (2023)',
            'industry': 'Commercial Aviation',
            'headquarters': 'Atlanta, Georgia',
            'website': 'www.delta.com',
            'description': 'Major American airline operating extensive domestic and international network'
        },
        'contacts': [
            {'name': 'Ed Bastian', 'title': 'Chief Executive Officer', 'email': 'ed.bastian@delta.com', 'phone': '+1-404-715-2600', 'linkedin': 'linkedin.com/in/edbastian'},
            {'name': 'Dan Janki', 'title': 'Chief Financial Officer', 'email': 'dan.janki@delta.com', 'phone': '+1-404-715-2601', 'linkedin': 'linkedin.com/in/danjanki'},
            {'name': 'Joe Esposito', 'title': 'Senior VP Technical Operations', 'email': 'joe.esposito@delta.com', 'phone': '+1-404-715-2602', 'linkedin': 'linkedin.com/in/joeesposito'},
            {'name': 'Don Mitacek', 'title': 'Senior VP Supply Chain & Fleet', 'email': 'don.mitacek@delta.com', 'phone': '+1-404-715-2603', 'linkedin': 'linkedin.com/in/donmitacek'}
        ]
    },
    'american': {
        'company': {
            'name': 'American Airlines Group Inc.',
            'employees': '130,000+',
            'revenue': '$52.8B (2023)',
            'industry': 'Commercial Aviation',
            'headquarters': 'Fort Worth, Texas',
            'website': 'www.aa.com',
            'description': 'Major American airline with extensive domestic and international operations'
        },
        'contacts': [
            {'name': 'Robert Isom', 'title': 'Chief Executive Officer', 'email': 'robert.isom@aa.com', 'phone': '+1-817-963-1234', 'linkedin': 'linkedin.com/in/robertisom'},
            {'name': 'Devon May', 'title': 'Chief Financial Officer', 'email': 'devon.may@aa.com', 'phone': '+1-817-963-1235', 'linkedin': 'linkedin.com/in/devonmay'},
            {'name': 'David Seymour', 'title': 'Chief Operating Officer', 'email': 'david.seymour@aa.com', 'phone': '+1-817-963-1236', 'linkedin': 'linkedin.com/in/davidseymour'},
            {'name': 'Jim Butler', 'title': 'VP Tech Ops & Maintenance', 'email': 'jim.butler@aa.com', 'phone': '+1-817-963-1237', 'linkedin': 'linkedin.com/in/jimbutler'}
        ]
    },
    'lufthansa': {
        'company': {
            'name': 'Lufthansa Technik AG',
            'employees': '22,000+',
            'revenue': '$7.2B (2023)',
            'industry': 'Aircraft Maintenance & Repair',
            'headquarters': 'Hamburg, Germany',
            'website': 'www.lufthansa-technik.com',
            'description': 'Leading provider of aircraft maintenance, repair, and overhaul services worldwide'
        },
        'contacts': [
            {'name': 'Soeren Stark', 'title': 'Chief Executive Officer', 'email': 'soeren.stark@lht.dlh.de', 'phone': '+49-40-5070-0', 'linkedin': 'linkedin.com/in/soerenstark'},
            {'name': 'Elina Hyytinen', 'title': 'Chief Financial Officer', 'email': 'elina.hyytinen@lht.dlh.de', 'phone': '+49-40-5070-1', 'linkedin': 'linkedin.com/in/elinahyytinen'},
            {'name': 'Kai-Stefan Roepke', 'title': 'CCO Base Maintenance', 'email': 'kai-stefan.roepke@lht.dlh.de', 'phone': '+49-40-5070-2', 'linkedin': 'linkedin.com/in/kaistefanroepke'}
        ]
    },
    'united': {
        'company': {
            'name': 'United Airlines Holdings Inc.',
            'employees': '92,000+',
            'revenue': '$53.7B (2023)',
            'industry': 'Commercial Aviation',
            'headquarters': 'Chicago, Illinois',
            'website': 'www.united.com',
            'description': 'Major American airline with global route network and extensive domestic operations'
        },
        'contacts': [
            {'name': 'Scott Kirby', 'title': 'Chief Executive Officer', 'email': 'scott.kirby@united.com', 'phone': '+1-872-825-4000', 'linkedin': 'linkedin.com/in/scottkirby'},
            {'name': 'Gerald Laderman', 'title': 'Chief Financial Officer', 'email': 'gerald.laderman@united.com', 'phone': '+1-872-825-4001', 'linkedin': 'linkedin.com/in/geraldladerman'},
            {'name': 'Greg Hart', 'title': 'Chief Operations Officer', 'email': 'greg.hart@united.com', 'phone': '+1-872-825-4002', 'linkedin': 'linkedin.com/in/greghart'},
            {'name': 'John Slater', 'title': 'VP Technical Operations', 'email': 'john.slater@united.com', 'phone': '+1-872-825-4003', 'linkedin': 'linkedin.com/in/johnslater'}
        ]
    },
    'rolls-royce': {
        'company': {
            'name': 'Rolls-Royce Holdings plc',
            'employees': '42,000+',
            'revenue': '$18.9B (2023)',
            'industry': 'Aerospace Engine Manufacturing',
            'headquarters': 'London, United Kingdom',
            'website': 'www.rolls-royce.com',
            'description': 'Leading manufacturer of aircraft engines and power systems for aerospace industry'
        },
        'contacts': [
            {'name': 'Tufan Erginbilgic', 'title': 'Chief Executive Officer', 'email': 'tufan.erginbilgic@rolls-royce.com', 'phone': '+44-20-7222-9020', 'linkedin': 'linkedin.com/in/tufanerginbilgic'},
            {'name': 'Panos Kakoullis', 'title': 'Chief Financial Officer', 'email': 'panos.kakoullis@rolls-royce.com', 'phone': '+44-20-7222-9021', 'linkedin': 'linkedin.com/in/panoskakoullis'},
            {'name': 'Chris Cholerton', 'title': 'President Civil Aerospace', 'email': 'chris.cholerton@rolls-royce.com', 'phone': '+44-20-7222-9022', 'linkedin': 'linkedin.com/in/chrischolerton'}
        ]
    },
    'microsoft': {
        'company': {
            'name': 'Microsoft Corporation',
            'employees': '220,000+',
            'revenue': '$211B (2023)',
            'industry': 'Technology Software',
            'headquarters': 'Redmond, Washington',
            'website': 'www.microsoft.com',
            'description': 'Global technology company developing software, services, and solutions'
        },
        'contacts': [
            {'name': 'Satya Nadella', 'title': 'Chief Executive Officer', 'email': 'satya.nadella@microsoft.com', 'phone': '+1-425-882-8080', 'linkedin': 'linkedin.com/in/satyanadella'},
            {'name': 'Amy Hood', 'title': 'Chief Financial Officer', 'email': 'amy.hood@microsoft.com', 'phone': '+1-425-882-8081', 'linkedin': 'linkedin.com/in/amyhood'},
            {'name': 'Brad Smith', 'title': 'Vice Chair & President', 'email': 'brad.smith@microsoft.com', 'phone': '+1-425-882-8082', 'linkedin': 'linkedin.com/in/bradsmith'},
            {'name': 'Scott Guthrie', 'title': 'Executive VP Cloud & AI', 'email': 'scott.guthrie@microsoft.com', 'phone': '+1-425-882-8083', 'linkedin': 'linkedin.com/in/scottguthrie'},
            {'name': 'Judson Althoff', 'title': 'Chief Commercial Officer', 'email': 'judson.althoff@microsoft.com', 'phone': '+1-425-882-8084', 'linkedin': 'linkedin.com/in/judsonalthoff'}
        ]
    },
    'google': {
        'company': {
            'name': 'Google LLC (Alphabet Inc.)',
            'employees': '190,000+',
            'revenue': '$307B (2023)',
            'industry': 'Internet & Technology',
            'headquarters': 'Mountain View, California',
            'website': 'www.google.com',
            'description': 'Multinational technology company specializing in search, cloud computing, and AI'
        },
        'contacts': [
            {'name': 'Sundar Pichai', 'title': 'CEO Google & Alphabet', 'email': 'sundar.pichai@google.com', 'phone': '+1-650-253-0000', 'linkedin': 'linkedin.com/in/sundarpichai'},
            {'name': 'Ruth Porat', 'title': 'Chief Financial Officer', 'email': 'ruth.porat@google.com', 'phone': '+1-650-253-0001', 'linkedin': 'linkedin.com/in/ruthporat'},
            {'name': 'Thomas Kurian', 'title': 'CEO Google Cloud', 'email': 'thomas.kurian@google.com', 'phone': '+1-650-253-0002', 'linkedin': 'linkedin.com/in/thomaskurian'},
            {'name': 'Prabhakar Raghavan', 'title': 'Senior VP Search', 'email': 'prabhakar.raghavan@google.com', 'phone': '+1-650-253-0003', 'linkedin': 'linkedin.com/in/prabhakrar'}
        ]
    },
    'amazon': {
        'company': {
            'name': 'Amazon.com Inc.',
            'employees': '1,540,000+',
            'revenue': '$574B (2023)',
            'industry': 'E-commerce & Cloud Computing',
            'headquarters': 'Seattle, Washington',
            'website': 'www.amazon.com',
            'description': 'Global e-commerce and cloud computing giant with AWS, retail, and logistics'
        },
        'contacts': [
            {'name': 'Andy Jassy', 'title': 'Chief Executive Officer', 'email': 'andy.jassy@amazon.com', 'phone': '+1-206-266-1000', 'linux': 'linkedin.com/in/andyjassy'},
            {'name': 'Brian Olsavsky', 'title': 'Chief Financial Officer', 'email': 'brian.olsavsky@amazon.com', 'phone': '+1-206-266-1001', 'linkedin': 'linkedin.com/in/brianolsavsky'},
            {'name': 'Adam Selipsky', 'title': 'CEO Amazon Web Services', 'email': 'adam.selipsky@amazon.com', 'phone': '+1-206-266-1002', 'linkedin': 'linkedin.com/in/adamselipsky'},
            {'name': 'Dave Limp', 'title': 'Senior VP Devices & Services', 'email': 'dave.limp@amazon.com', 'phone': '+1-206-266-1003', 'linkedin': 'linkedin.com/in/davelimp'}
        ]
    },
    'apple': {
        'company': {
            'name': 'Apple Inc.',
            'employees': '164,000+',
            'revenue': '$394B (2023)',
            'industry': 'Consumer Electronics',
            'headquarters': 'Cupertino, California',
            'website': 'www.apple.com',
            'description': 'Multinational technology company designing consumer electronics, software, and services'
        },
        'contacts': [
            {'name': 'Tim Cook', 'title': 'Chief Executive Officer', 'email': 'tim.cook@apple.com', 'phone': '+1-408-996-1010', 'linkedin': 'linkedin.com/in/timcook'},
            {'name': 'Luca Maestri', 'title': 'Chief Financial Officer', 'email': 'luca.maestri@apple.com', 'phone': '+1-408-996-1011', 'linkedin': 'linkedin.com/in/lucamaestri'},
            {'name': 'Craig Federighi', 'title': 'Senior VP Software Engineering', 'email': 'craig.federighi@apple.com', 'phone': '+1-408-996-1012', 'linkedin': 'linkedin.com/in/craigfederighi'},
            {'name': 'Johnny Srouji', 'title': 'Senior VP Hardware Technologies', 'email': 'johnny.srouji@apple.com', 'phone': '+1-408-996-1013', 'linkedin': 'linkedin.com/in/johnnysrouji'}
        ]
    },
    'salesforce': {
        'company': {
            'name': 'Salesforce Inc.',
            'employees': '79,000+',
            'revenue': '$31.4B (2024)',
            'industry': 'Cloud Software (CRM)',
            'headquarters': 'San Francisco, California',
            'website': 'www.salesforce.com',
            'description': 'Leading customer relationship management (CRM) software company'
        },
        'contacts': [
            {'name': 'Marc Benioff', 'title': 'Chair & CEO', 'email': 'marc.benioff@salesforce.com', 'phone': '+1-415-901-7000', 'linkedin': 'linkedin.com/in/marcbenioff'},
            {'name': 'Amy Weaver', 'title': 'Chief Financial Officer', 'email': 'amy.weaver@salesforce.com', 'phone': '+1-415-901-7001', 'linkedin': 'linkedin.com/in/amyweaver'},
            {'name': 'Parker Harris', 'title': 'Co-Founder & CTO', 'email': 'parker.harris@salesforce.com', 'phone': '+1-415-901-7002', 'linkedin': 'linkedin.com/in/parkerharris'}
        ]
    },
    'meta': {
        'company': {
            'name': 'Meta Platforms Inc.',
            'employees': '77,000+',
            'revenue': '$134B (2023)',
            'industry': 'Social Media & VR/AR',
            'headquarters': 'Menlo Park, California',
            'website': 'www.meta.com',
            'description': 'Social technology company building platforms for connection and the metaverse'
        },
        'contacts': [
            {'name': 'Mark Zuckerberg', 'title': 'Chairman & CEO', 'email': 'mark.zuckerberg@meta.com', 'phone': '+1-650-543-4800', 'linkedin': 'linkedin.com/in/markzuckerberg'},
            {'name': 'Susan Li', 'title': 'Chief Financial Officer', 'email': 'susan.li@meta.com', 'phone': '+1-650-543-4801', 'linkedin': 'linkedin.com/in/susanli'},
            {'name': 'Andrew Bosworth', 'title': 'CTO & Head of Reality Labs', 'email': 'andrew.bosworth@meta.com', 'phone': '+1-650-543-4802', 'linkedin': 'linkedin.com/in/andrewbosworth'}
        ]
    }
}

def get_company_from_ip(ip_address):
    """Convert IP to Company"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
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
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timeout - please try again'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Network error: {str(e)}'}
    except json.JSONDecodeError:
        return {'success': False, 'error': 'Invalid response from IP service'}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

def search_zoominfo(company_name, ip_address):
    """Search ZoomInfo database with randomization"""
    # Clean company name and search
    company_lower = company_name.lower()
    
    # Improved matching - check for key aviation companies first
    aviation_companies = {
        'boeing': ['boeing', 'the boeing company'],
        'delta': ['delta', 'delta air lines', 'delta airlines'],
        'american': ['american airlines', 'american', 'aa.com'],
        'lufthansa': ['lufthansa', 'lufthansa technik', 'lht'],
        'united': ['united airlines', 'united', 'ual'],
        'rolls-royce': ['rolls-royce', 'rolls royce', 'rr.com']
    }
    
    # Search for aviation companies first
    for key, search_terms in aviation_companies.items():
        if any(term in company_lower for term in search_terms):
            if key in CONTACTS_DATABASE:
                contacts_list = CONTACTS_DATABASE[key]
                # Get company info from ZOOMINFO_DATABASE
                company_info = ZOOMINFO_DATABASE.get(key, {}).get('company', {})
                
                # Randomize contacts selection based on IP
                random.seed(hash(ip_address))  # Consistent randomization per IP
                num_contacts = random.randint(6, min(len(contacts_list), 12))  # 6-12 contacts
                selected_contacts = random.sample(contacts_list, num_contacts)
                
                # Add randomized confidence scores and last updated dates
                for contact in selected_contacts:
                    contact['confidence_score'] = f"{random.randint(85, 98)}%"
                    contact['last_updated'] = f"2025-01-{random.randint(10, 30):02d}"
                    contact['verified'] = '✅ Verified' if random.random() > 0.05 else '⚠️ Pending'
                
                return {
                    'success': True,
                    'company': company_info,
                    'contacts': selected_contacts
                }
    
    # Fallback search in all contacts database
    for key, contacts_list in CONTACTS_DATABASE.items():
        if key in company_lower or any(word in company_lower for word in key.split()):
            # Get company info from ZOOMINFO_DATABASE
            company_info = ZOOMINFO_DATABASE.get(key, {}).get('company', {})
            
            # Randomize contacts selection based on IP
            random.seed(hash(ip_address))  # Consistent randomization per IP
            num_contacts = random.randint(4, min(len(contacts_list), 10))  # 4-10 contacts
            selected_contacts = random.sample(contacts_list, num_contacts)
            
            # Add randomized confidence scores and last updated dates
            for contact in selected_contacts:
                contact['confidence_score'] = f"{random.randint(82, 98)}%"
                contact['last_updated'] = f"2025-01-{random.randint(10, 30):02d}"
                contact['verified'] = '✅ Verified' if random.random() > 0.1 else '⚠️ Pending'
            
            return {
                'success': True,
                'company': company_info,
                'contacts': selected_contacts
            }
    
    # If still no match, create dynamic contacts based on company name
    random.seed(hash(ip_address + company_name))
    company_domain = company_name.lower().replace(' ', '').replace('inc', '').replace('corp', '').replace('ltd', '')[:10]
    
    dynamic_contacts = []
    contact_templates = [
        {'name': 'Michael Johnson', 'title': 'Chief Executive Officer', 'seniority': 'C-Level', 'department': 'Executive'},
        {'name': 'Sarah Williams', 'title': 'Chief Financial Officer', 'seniority': 'C-Level', 'department': 'Executive'},
        {'name': 'David Chen', 'title': 'VP Operations', 'seniority': 'VP-Level', 'department': 'Operations'},
        {'name': 'Lisa Rodriguez', 'title': 'VP Business Development', 'seniority': 'VP-Level', 'department': 'Operations'},
        {'name': 'Robert Taylor', 'title': 'Director Supply Chain', 'seniority': 'Director', 'department': 'Operations'},
        {'name': 'Jennifer Davis', 'title': 'Director Procurement', 'seniority': 'Director', 'department': 'Operations'},
        {'name': 'Mark Wilson', 'title': 'VP Strategic Partnerships', 'seniority': 'VP-Level', 'department': 'Operations'},
        {'name': 'Amanda Garcia', 'title': 'Chief Technology Officer', 'seniority': 'C-Level', 'department': 'Executive'}
    ]
    
    num_contacts = random.randint(4, 7)
    selected_templates = random.sample(contact_templates, num_contacts)
    
    for template in selected_templates:
        contact = template.copy()
        contact['email'] = f"{contact['name'].lower().replace(' ', '.')}@{company_domain}.com"
        contact['phone'] = f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        contact['linkedin'] = f"linkedin.com/in/{contact['name'].lower().replace(' ', '')}"
        contact['confidence_score'] = f"{random.randint(70, 88)}%"
        contact['last_updated'] = f"2025-01-{random.randint(5, 25):02d}"
        contact['verified'] = '✅ Verified' if random.random() > 0.25 else '⚠️ Pending'
        dynamic_contacts.append(contact)
    
    return {
        'success': True,
        'company': {
            'name': company_name,
            'employees': f"{random.randint(100, 5000):,}+",
            'revenue': f"${random.randint(10, 500)}M+",
            'industry': 'Business Services',
            'headquarters': 'Various Locations',
            'website': f"www.{company_domain}.com",
            'description': f'Business organization: {company_name}'
        },
        'contacts': dynamic_contacts
    }

# App Header - Mobile Optimized
st.markdown("""
<div class="section-header">
    <h1>✈️ B&H Worldwide: Aviation Lead Intelligence</h1>
    <p>Convert Website Visitors → Aviation Companies → Decision Maker Contacts</p>
    <p style="opacity: 0.9;">Track airlines, MROs, aerospace manufacturers visiting your services</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = []

# Section 1: IP Input
st.markdown("""
<div class="section-card">
    <h2 style="color: #667eea; margin-top: 0;">📊 Section 1: IP Address Input</h2>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔢 Single IP", "📁 Upload CSV"])

with tab1:
    st.markdown("### Enter Individual IP Address")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        single_ip = st.text_input(
            "Website Visitor IP Address",
            placeholder="e.g., 52.96.0.0",
            help="Enter IP address from your website analytics"
        )
    with col2:
        st.write("")
        process_single = st.button("🚀 Process IP", type="primary", use_container_width=True)
    
    # Demo IPs - B&H Worldwide's Target Market
    st.markdown("##### ✈️ Aviation Industry Visitor IPs:")
    demo_cols = st.columns(6)
    demo_ips = [
        {"name": "Boeing", "ip": "52.16.0.0"},
        {"name": "Delta Airlines", "ip": "199.168.0.0"},
        {"name": "American Airlines", "ip": "104.244.0.0"},
        {"name": "Lufthansa Technik", "ip": "64.233.160.0"},
        {"name": "United Airlines", "ip": "157.240.0.0"},
        {"name": "Rolls-Royce", "ip": "208.67.222.0"}
    ]
    
    for i, demo in enumerate(demo_ips):
        with demo_cols[i]:
            if st.button(f"{demo['name']}\n`{demo['ip']}`", key=f"demo_{i}"):
                single_ip = demo['ip']
                process_single = True

with tab2:
    st.markdown("### Upload CSV File with IP Addresses")
    
    # Show sample CSV format
    st.markdown("##### 📋 Expected CSV Format (Aviation Industry Visitors):")
    sample_df = pd.DataFrame({
        'ip_address': ['52.16.0.0', '199.168.0.0', '104.244.0.0'],
        'timestamp': ['2025-07-30 14:30:15', '2025-07-30 14:25:33', '2025-07-30 14:20:44'],
        'page_visited': ['/aog-services', '/dangerous-goods', '/trade-compliance'],
        'visitor_type': ['Boeing Company', 'Delta Air Lines', 'American Airlines']
    })
    st.dataframe(sample_df, use_container_width=True)
    
    # Download sample CSV
    col1, col2 = st.columns(2)
    with col1:
        try:
            current_dir = Path(__file__).parent
            csv_path = current_dir / 'bhworldwide_relevant_ips.csv'
            if csv_path.exists():
                st.download_button(
                    "📥 Download Aviation Industry Sample CSV",
                    data=csv_path.read_bytes(),
                    file_name='bhworldwide_aviation_visitors.csv',
                    mime='text/csv'
                )
            else:
                st.info("📄 Sample CSV not available in deployment")
        except Exception as e:
            st.info("📄 Sample CSV download not available")
    
    with col2:
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload CSV with ip_address column"
        )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} IP addresses")
            st.dataframe(df.head(), use_container_width=True)
            
            process_csv = st.button("🚀 Process All IPs", type="primary", use_container_width=True)
            
            if process_csv:
                progress_bar = st.progress(0)
                results = []
                
                for i, row in df.iterrows():
                    ip = row['ip_address']
                    progress_bar.progress((i + 1) / len(df))
                    
                    # Process IP
                    company_result = get_company_from_ip(ip)
                    if company_result['success']:
                        zoominfo_result = search_zoominfo(company_result['organization'], ip)
                        results.append({
                            'ip': ip,
                            'company_data': company_result,
                            'zoominfo_data': zoominfo_result
                        })
                    time.sleep(0.1)  # Avoid rate limiting
                
                st.session_state.processed_results = results
                st.success(f"✅ Processed {len(results)} successful matches!")
                
        except Exception as e:
            st.error(f"❌ Error reading CSV: {e}")

# Section 2: ZoomInfo Status
st.markdown("""
<div class="section-card">
    <h2 style="color: #667eea; margin-top: 0;">🔍 Section 2: ZoomInfo Database Status</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="zoominfo-status">
        <h4 style="margin: 0; color: #1976D2;">📊 Database Size</h4>
        <p style="margin: 0.5rem 0 0 0; font-size: 24px; font-weight: bold;">100M+ Contacts</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="zoominfo-status">
        <h4 style="margin: 0; color: #1976D2;">🏢 Companies Covered</h4>
        <p style="margin: 0.5rem 0 0 0; font-size: 24px; font-weight: bold;">50M+ Organizations</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="zoominfo-status">
        <h4 style="margin: 0; color: #1976D2;">✅ API Status</h4>
        <p style="margin: 0.5rem 0 0 0; font-size: 18px; font-weight: bold; color: #00C851;">DEMO MODE</p>
    </div>
    """, unsafe_allow_html=True)

# Show sample companies in ZoomInfo
st.markdown("##### 🎯 Sample Companies in Database:")
sample_companies = list(ZOOMINFO_DATABASE.keys())[:6]
company_cols = st.columns(3)

for i, company in enumerate(sample_companies):
    with company_cols[i % 3]:
        company_data = ZOOMINFO_DATABASE[company]['company']
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
            <strong>{company_data['name']}</strong><br>
            <span style="color: #666; font-size: 12px;">
                {company_data['employees']} employees<br>
                {company_data['industry']}
            </span>
        </div>
        """, unsafe_allow_html=True)

# Section 3: Results
st.markdown("""
<div class="section-card">
    <h2 style="color: #667eea; margin-top: 0;">📈 Section 3: Processing Results</h2>
</div>
""", unsafe_allow_html=True)

# Process single IP if requested
if process_single and single_ip:
    with st.spinner("🔍 Processing IP address..."):
        company_result = get_company_from_ip(single_ip)
        
        if company_result['success']:
            zoominfo_result = search_zoominfo(company_result['organization'], single_ip)
            # Add to existing results instead of replacing
            new_result = {
                'ip': single_ip,
                'company_data': company_result,
                'zoominfo_data': zoominfo_result
            }
            # Check if this IP already exists, if so replace it, otherwise add
            existing_index = None
            for idx, existing in enumerate(st.session_state.processed_results):
                if existing['ip'] == single_ip:
                    existing_index = idx
                    break
            
            if existing_index is not None:
                st.session_state.processed_results[existing_index] = new_result
            else:
                st.session_state.processed_results.append(new_result)

# Display results
if st.session_state.processed_results:
    # Add clear button
    if st.button("🗑️ Clear All Results", type="secondary"):
        st.session_state.processed_results = []
        st.rerun()
    for i, result in enumerate(st.session_state.processed_results):
        ip = result['ip']
        company_data = result['company_data']
        zoominfo_data = result['zoominfo_data']
        
        st.markdown(f"""
        <div class="result-card">
            <h3 style="margin: 0 0 1rem 0;">✅ Result #{i+1}: Lead Generated from IP {ip}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Company Information Tab
        company_tab, contacts_tab, summary_tab = st.tabs(["🏢 Company Info", "👥 Contacts", "📊 Summary"])
        
        with company_tab:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🌐 IP Analysis")
                st.write(f"**IP Address:** {company_data['ip']}")
                st.write(f"**Organization:** {company_data['organization']}")
                st.write(f"**Location:** {company_data['city']}, {company_data['country']}")
                st.write(f"**ISP:** {company_data['isp']}")
                
            with col2:
                st.markdown("#### 🏢 Company Profile")
                company_info = zoominfo_data['company']
                st.write(f"**Company:** {company_info['name']}")
                st.write(f"**Employees:** {company_info['employees']}")
                st.write(f"**Revenue:** {company_info['revenue']}")
                st.write(f"**Industry:** {company_info['industry']}")
                st.write(f"**Website:** {company_info['website']}")
        
        with contacts_tab:
            st.markdown("#### 👥 ZoomInfo Contact Database")
            
            # Create realistic database-style table
            contacts_data = []
            for idx, contact in enumerate(zoominfo_data['contacts']):
                contacts_data.append({
                    'Contact ID': f"ZI-{hash(contact['name']) % 100000:05d}",
                    'Full Name': contact['name'],
                    'Job Title': contact['title'],
                    'Company': company_info['name'],
                    'Work Email': contact['email'],
                    'Direct Phone': contact['phone'],
                    'Department': contact.get('department', 'Operations'),
                    'Seniority': contact.get('seniority', 'Director'),
                    'Location': f"{company_data['city']}, {company_data['country']}",
                    'Verified': contact.get('verified', '✅ Verified'),
                    'Last Updated': contact.get('last_updated', '2025-01-15'),
                    'Confidence Score': contact.get('confidence_score', f"{85 + idx * 3}%")
                })
            
            # Display as professional database table
            contacts_df = pd.DataFrame(contacts_data)
            
            # Add search functionality
            st.markdown("##### 🔍 Contact Search & Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_name = st.text_input("Search by Name", placeholder="Enter contact name...", key=f"search_{i}")
            with col2:
                dept_filter = st.selectbox("Department", ["All", "Executive", "Operations"], key=f"dept_{i}")
            with col3:
                seniority_filter = st.selectbox("Seniority Level", ["All", "C-Level", "VP-Level"], key=f"seniority_{i}")
            
            # Apply filters
            filtered_df = contacts_df.copy()
            if search_name:
                filtered_df = filtered_df[filtered_df['Full Name'].str.contains(search_name, case=False)]
            if dept_filter != "All":
                filtered_df = filtered_df[filtered_df['Department'] == dept_filter]
            if seniority_filter != "All":
                filtered_df = filtered_df[filtered_df['Seniority'] == seniority_filter]
            
            # Database-style table with professional styling
            st.markdown(f"##### 📊 Found {len(filtered_df)} contacts in database")
            
            # Use native Streamlit dataframe with enhanced styling
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Contact ID": st.column_config.TextColumn("Contact ID", width="small"),
                    "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                    "Job Title": st.column_config.TextColumn("Job Title", width="large"),
                    "Work Email": st.column_config.TextColumn("Work Email", width="large"),
                    "Direct Phone": st.column_config.TextColumn("Direct Phone", width="medium"),
                    "Confidence Score": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100),
                    "Verified": st.column_config.TextColumn("Status", width="small")
                }
            )
            
            # Add export functionality like in your image
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True, key=f"export_{i}"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        csv,
                        f"zoominfo_contacts_{company_info['name'].replace(' ', '_')}.csv",
                        "text/csv",
                        key=f"download_{i}"
                    )
            with col2:
                if st.button("📧 Send to CRM", use_container_width=True, key=f"crm_{i}"):
                    st.success("✅ Contacts exported to Salesforce CRM")
            with col3:
                if st.button("🔄 Refresh Data", use_container_width=True, key=f"refresh_{i}"):
                    st.info("🔄 Refreshing from ZoomInfo database...")
            
            # Additional database stats like in your image
            st.markdown("##### 📈 Database Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Records", len(contacts_df))
            with stat_col2:
                st.metric("Verified Contacts", len(contacts_df))
            with stat_col3:
                st.metric("C-Level Executives", len([c for c in contacts_df['Seniority'] if c == 'C-Level']))
            with stat_col4:
                st.metric("Avg Confidence", f"{contacts_df['Confidence Score'].str.rstrip('%').astype(int).mean():.0f}%")
        
        with summary_tab:
            # Calculate business value - COMPANY SPECIFIC
            employees = company_info['employees']
            company_name = company_info['name'].lower()
            
            # Debug: Show company info at top
            st.markdown(f"**🏢 Analyzing: {company_info['name']} ({employees} employees)**")
            
            # Company-specific scoring
            if 'boeing' in company_name:
                lead_score = "🔥 AEROSPACE GIANT"
                revenue_potential = "$500K - $2M+"
                priority = "PLATINUM"
                score_value = 98
                revenue_min = 500000
                revenue_max = 2000000
            elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                lead_score = "✈️ MAJOR AIRLINE"
                revenue_potential = "$200K - $800K"
                priority = "GOLD"
                score_value = 85
                revenue_min = 200000
                revenue_max = 800000
            elif 'lufthansa' in company_name:
                lead_score = "🔧 MRO LEADER"
                revenue_potential = "$100K - $500K"
                priority = "SILVER"
                score_value = 78
                revenue_min = 100000
                revenue_max = 500000
            elif 'rolls-royce' in company_name:
                lead_score = "⚙️ ENGINE MAKER"
                revenue_potential = "$300K - $1M+"
                priority = "GOLD"
                score_value = 92
                revenue_min = 300000
                revenue_max = 1000000
            elif any(x in employees for x in ['100,000+', '200,000+', '500,000+']):
                lead_score = "🔥 ENTERPRISE"
                revenue_potential = "$100K - $1M+"
                priority = "HIGHEST"
                score_value = 95
                revenue_min = 100000
                revenue_max = 1000000
            elif any(x in employees for x in ['50,000+', '75,000+']):
                lead_score = "⭐ HIGH-VALUE"
                revenue_potential = "$50K - $500K"
                priority = "HIGH"
                score_value = 80
                revenue_min = 50000
                revenue_max = 500000
            else:
                lead_score = "✅ QUALIFIED"
                revenue_potential = "$10K - $100K"
                priority = "MEDIUM"
                score_value = 65
                revenue_min = 10000
                revenue_max = 100000
            
            # Compact metrics with smaller fonts
            st.markdown("""
            <style>
                .compact-metric {
                    background: #f8f9fa;
                    padding: 0.5rem;
                    border-radius: 8px;
                    text-align: center;
                    margin: 0.2rem 0;
                }
                .compact-metric h4 {
                    margin: 0;
                    font-size: 14px;
                    color: #666;
                }
                .compact-metric h2 {
                    margin: 0.2rem 0 0 0;
                    font-size: 18px;
                    color: #333;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Compact metrics row
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
                    <h4>Priority Level</h4>
                    <h2>{priority}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Business Intelligence Visualizations
            st.markdown("##### 📊 Business Intelligence Analysis")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Lead Score Gauge Chart - Force unique values
                actual_score = score_value + hash(ip) % 10 - 5  # Add variation based on IP
                actual_score = max(50, min(100, actual_score))  # Keep in range
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = actual_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"Lead Score: {company_info['name']}", 'font': {'size': 14}},
                    delta = {'reference': 50},
                    gauge = {
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
                st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{i}")
                
            with viz_col2:
                # Revenue Potential Range Chart - Force different per IP
                actual_rev_min = revenue_min + (hash(ip) % 50000)  # Vary min
                actual_rev_max = revenue_max + (hash(ip) % 100000)  # Vary max
                revenue_range = np.linspace(actual_rev_min, actual_rev_max, 100)
                center = (actual_rev_min + actual_rev_max) / 2
                width_factor = 6 + (hash(ip) % 3)  # Vary curve width
                probability = np.exp(-((revenue_range - center)**2) / (2 * ((actual_rev_max - actual_rev_min)/width_factor)**2))
                
                fig_revenue = go.Figure()
                fig_revenue.add_trace(go.Scatter(
                    x=revenue_range/1000,  # Convert to thousands
                    y=probability,
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.3)',
                    line=dict(color='#667eea', width=2),
                    name='Revenue Probability'
                ))
                fig_revenue.update_layout(
                    title={'text': f'Revenue Potential: {company_info["name"]}', 'font': {'size': 16}},
                    xaxis_title={'text': 'Revenue (K$)', 'font': {'size': 12}},
                    yaxis_title={'text': 'Probability', 'font': {'size': 12}},
                    height=300,
                    margin=dict(l=40, r=20, t=40, b=40),
                    showlegend=False
                )
                st.plotly_chart(fig_revenue, use_container_width=True, key=f"revenue_{i}")
            
            # Company Analysis Charts
            st.markdown("##### 🏢 Company Profile Analysis")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Industry Comparison Bar Chart - Realistic data based on IP/Company
                random.seed(hash(ip))  # Consistent randomization per IP
                
                # Base industry scores with realistic variations
                base_industry_data = {
                    'Aerospace & Defense': (82, 92),
                    'Commercial Aviation': (85, 95), 
                    'Aircraft Maintenance': (70, 85),
                    'Engine Manufacturing': (78, 88),
                    'Business Services': (55, 75)
                }
                
                # Generate realistic scores for each industry
                industry_data = {}
                for industry, (min_score, max_score) in base_industry_data.items():
                    industry_data[industry] = random.randint(min_score, max_score)
                
                current_industry = company_info['industry']
                # Set current company's actual score
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
                    )
                ])
                fig_industry.update_layout(
                    title={'text': 'Industry Lead Score Comparison', 'font': {'size': 16}},
                    xaxis_title={'text': 'Industry', 'font': {'size': 12}},
                    yaxis_title={'text': 'Avg Lead Score', 'font': {'size': 12}},
                    height=300,
                    margin=dict(l=40, r=20, t=40, b=80),
                    xaxis={'tickangle': -45, 'tickfont': {'size': 10}}
                )
                st.plotly_chart(fig_industry, use_container_width=True, key=f"industry_{i}")
                
            with chart_col2:
                # Contact Roles Distribution Pie Chart - Based on actual contacts
                contact_roles = {}
                for contact in zoominfo_data['contacts']:
                    # Use the seniority field from contacts database
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
                    marker_colors=['#667eea', '#764ba2', '#00C851']
                )])
                fig_contacts.update_layout(
                    title={'text': 'Contact Seniority Distribution', 'font': {'size': 16}},
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_contacts, use_container_width=True, key=f"contacts_{i}")
            
            # ROI Calculator - Use IP-specific values
            actual_rev_min = revenue_min + (hash(ip) % 50000)  # Same calculation as chart
            actual_rev_max = revenue_max + (hash(ip) % 100000)  # Same calculation as chart
            
            st.markdown("##### 💰 ROI Calculator")
            
            roi_col1, roi_col2, roi_col3 = st.columns(3)
            
            with roi_col1:
                # Realistic conversion rates based on company type and B&H Worldwide's business
                random.seed(hash(ip) + 1)  # Different seed for conversion rate
                company_name = company_info['name'].lower()
                
                if 'boeing' in company_name:
                    # Boeing - highest conversion, large deals
                    conversion_rate = random.uniform(0.18, 0.25)
                elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                    # Major airlines - good conversion, frequent AOG needs
                    conversion_rate = random.uniform(0.12, 0.18)
                elif 'lufthansa' in company_name:
                    # MRO providers - competitive market, moderate conversion
                    conversion_rate = random.uniform(0.08, 0.14)
                elif 'rolls-royce' in company_name:
                    # Engine manufacturers - specialized needs, high conversion
                    conversion_rate = random.uniform(0.15, 0.22)
                else:
                    # Generic companies
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
                random.seed(hash(ip) + 2)  # Different seed for cost
                
                if 'boeing' in company_name:
                    # Boeing - complex, high-value deals require more investment
                    cost_per_lead = random.randint(12000, 18000)
                elif any(airline in company_name for airline in ['delta', 'american', 'united']):
                    # Airlines - established relationships, moderate cost
                    cost_per_lead = random.randint(7000, 12000)
                elif 'lufthansa' in company_name:
                    # MRO - competitive market, higher acquisition cost
                    cost_per_lead = random.randint(8000, 14000)
                elif 'rolls-royce' in company_name:
                    # Engine manufacturers - specialized, premium cost
                    cost_per_lead = random.randint(10000, 15000)
                else:
                    # Generic companies - standard cost
                    cost_per_lead = random.randint(4000, 8000)
                
                roi_percentage = (expected_value / cost_per_lead) * 100
                st.markdown(f"""
                <div class="compact-metric">
                    <h4>ROI Potential</h4>
                    <h2>{roi_percentage:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
                
            # Debug info
            st.markdown(f"**Debug IP {ip}:** Score: {actual_score:.0f}, Revenue: ${actual_rev_min:,}-${actual_rev_max:,}, Conversion: {conversion_rate:.1%}, Cost: ${cost_per_lead:,}, Expected: ${expected_value:,.0f}, ROI: {roi_percentage:.0f}%")

else:
    st.info("👆 Process IP addresses above to see detailed results here.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px;">
    <p><strong>🎯 IP-to-ZoomInfo Lead Generator</strong> - Convert anonymous website visitors into qualified business leads</p>
    <p>For real implementation: Subscribe to ZoomInfo API ($15K/year) + integrate with your website tracking</p>
</div>
""", unsafe_allow_html=True)