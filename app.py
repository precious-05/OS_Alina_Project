import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# Page configuration
st.set_page_config(
    page_title="Deadlock Detection & Recovery Simulator",
    page_icon="⚡",
    layout="wide"
)

# User Guide Data
USER_GUIDE_SECTIONS = [
    {
        "title": "Getting Started",
        "content": """
        This simulator demonstrates deadlock detection and recovery algorithms for single-instance resources (0 or 1 only). 
        Each resource in this system exists as only ONE instance, making it ideal for understanding resource allocation conflicts.
        
        **Key Concepts:**
        - **Processes**: Running applications that require resources
        - **Resources**: Hardware/software components (CPU, RAM, etc.) with single instances
        - **Allocation**: Resources currently held by processes (0=not allocated, 1=allocated)
        - **Request**: Resources currently requested by processes (0=not requested, 1=requested)
        - **Available**: Resources currently free and available (0=not available, 1=available)
        
        **How Deadlock Occurs:**
        A deadlock occurs when processes form a circular wait condition where each process holds a resource 
        needed by the next process in the cycle, creating an impasse where no process can proceed.
        """
    },
    {
        "title": "System Configuration",
        "content": """
        **Step 1: Configure System**
        1. Set the number of processes (3-10) using the slider
        2. Set the number of resources (2-8) using the slider
        3. Click "Initialize System" to create a random configuration
        
        **What happens during initialization:**
        - Allocation matrix is randomly generated (0s and 1s only)
        - Request matrix is randomly generated (0s and 1s only)
        - Available resources are calculated based on allocations
        - Process names are assigned from a predefined list
        - Resource names are assigned from a predefined list
        """
    },
    {
        "title": "Monitoring System State",
        "content": """
        **Left Panel - System Monitoring:**
        - **Resource Monitor**: Shows current availability of each resource
          - Green ✓ = Resource is available
          - Red ✘ = Resource is allocated to a process
          
        - **Process Status Monitor**: Shows status of each process
          - Green RUNNING = Process is executing normally
          - Red BLOCKED = Process is deadlocked
          - Yellow WAITING = Process is waiting for resources
          - Gray TERMINATED = Process has been terminated
        
        **Center Panel - System Matrices:**
        - **Allocation Matrix**: Shows which resources each process currently holds
          - ✔ = Resource allocated to process (value: 1)
          - ✘ = Resource not allocated (value: 0)
          
        - **Request Matrix**: Shows which resources each process is requesting
          - ↑ = Resource requested by process (value: 1)
          - – = Resource not requested (value: 0)
          
        - **Available Resources**: Shows which resources are currently free
          - Available = Resource is free (value: 1)
          - Allocated = Resource is in use (value: 0)
        """
    },
    {
        "title": "Deadlock Detection",
        "content": """
        **Step 2: Run Deadlock Detection**
        1. Click "Run Deadlock Detection" button
        2. System runs Wait-For Graph algorithm for single instances
        3. Results are displayed:
           - **No Deadlock**: Green message with "NO DEADLOCK DETECTED"
           - **Deadlock Found**: Red message listing blocked processes
        
        **Algorithm Used:**
        The simulator uses a modified Banker's algorithm adapted for single-instance resources. 
        It checks if there exists a sequence where all processes can complete without deadlock.
        
        **What happens when deadlock is detected:**
        - Deadlocked processes change status to "BLOCKED"
        - Event is recorded in Deadlock History
        - System prompts for recovery actions
        """
    },
    {
        "title": "Resource Request Simulation",
        "content": """
        **Step 3: Simulate Resource Requests**
        1. Select a process from the dropdown menu
        2. Use the toggle buttons to set resource requests:
           - Click "↑ Requested" to request a resource (turns to "– Not Requested")
           - Click "– Not Requested" to remove a request (turns to "↑ Requested")
        3. Click "Update Request" to apply changes
        
        **Visual Indicators:**
        - Red button with white text indicates requested resource
        - Gray button with white text indicates no request
        
        **What happens after update:**
        - Request matrix is updated
        - Process status may change to "WAITING"
        - Detection should be run again to check for deadlocks
        """
    },
    {
        "title": "Deadlock Recovery",
        "content": """
        **Step 4: Recover from Deadlock (when detected)**
        Two recovery methods are available:
        
        **1. Process Termination:**
        - Terminates one deadlocked process
        - Releases ALL its allocated resources
        - Makes resources available to other processes
        - Process status changes to "TERMINATED"
        
        **2. Resource Preemption:**
        - Takes a resource from its current holder
        - Makes the resource available immediately
        - Process that lost the resource will request it again
        - Less disruptive than termination
        
        **Choosing Recovery Method:**
        - **Termination**: Use when you want to completely remove a process
        - **Preemption**: Use when you want to keep all processes but break the deadlock
        """
    },
    {
        "title": "System Operations",
        "content": """
        **Additional Features:**
        
        **Run Complete Cycle:**
        - Automatically runs detection
        - If deadlock found, automatically applies recovery
        - Chooses between termination and preemption randomly
        - Shows results of the complete cycle
        
        **Reset All Requests:**
        - Resets all request matrices to random values
        - Clears all toggle button states
        - Resets process statuses
        - Useful for starting fresh experiments
        
        **Clear All Messages:**
        - Removes all status messages from the top
        - Cleans up the interface for better readability
        
        **Deadlock History:**
        - Shows recent deadlock events
        - Includes timestamp and affected processes
        - Shows whether deadlock was resolved
        - Limited to last 3 events for clarity
        """
    },
    {
        "title": "Interpreting Results",
        "content": """
        **Understanding the Output:**
        
        **Safe State Indicators:**
        - All processes in "RUNNING" or "WAITING" status
        - No red "BLOCKED" status indicators
        - At least some resources shown as "AVAILABLE"
        - Detection shows "NO DEADLOCK DETECTED"
        
        **Deadlock Indicators:**
        - One or more processes in "BLOCKED" status (red)
        - Detection shows "DEADLOCK DETECTED"
        - Deadlock History shows unresolved events
        - Recovery options become active
        
        **Resource Utilization:**
        - Check Resource Monitor for availability status
        - High allocation = many resources in use
        - Low availability = potential for deadlock
        - Balance allocation for optimal performance
        """
    },
    {
        "title": "Best Practices",
        "content": """
        **For Effective Learning:**
        
        1. **Start Simple**: Begin with 3 processes and 3 resources
        2. **Observe Patterns**: Notice how requests affect deadlock probability
        3. **Experiment**: Try different request patterns and observe results
        4. **Use Recovery**: Practice both recovery methods
        5. **Track History**: Monitor Deadlock History for patterns
        
        **Common Scenarios to Test:**
        - Request resources already allocated to others
        - Create circular wait conditions manually
        - Test recovery effectiveness
        - Observe how reset affects system state
        
        **Learning Objectives:**
        - Understand deadlock conditions (Circular Wait, Hold and Wait, No Preemption, Mutual Exclusion)
        - Learn detection algorithms for single-instance resources
        - Practice recovery strategies
        - Develop intuition for resource allocation
        """
    }
]

st.markdown("""
<style>
    /* Modern Dark Tech Theme */
    :root {
        --bg-dark: #0F172A;
        --panel-dark: #1E293B;
        --panel-darker: #0F172A;
        --accent-purple: #A855F7;
        --accent-purple-light: #C084FC;
        --accent-blue: #38BDF8;
        --accent-blue-light: #7DD3FC;
        --success: #10B981;
        --success-light: #34D399;
        --danger: #EF4444;
        --danger-light: #F87171;
        --warning: #F59E0B;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --border-color: #334155;
        --shadow-color: rgba(0, 0, 0, 0.3);
    }
    
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #0D1524 100%);
        color: var(--text-primary) !important;
    }
    
    /* Fix ALL Streamlit text colors */
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, div, span, label {
        color: var(--text-primary) !important;
    }
    
    /* Fix Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
        background: linear-gradient(135deg, var(--accent-purple-light), var(--accent-blue-light));
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Toggle Button Special Styling - FIXED WITH CLEAR VISIBILITY */
    div[data-testid="column"] button[kind="secondary"] {
        background: linear-gradient(135deg, #DC2626, #B91C1C) !important;
        color: white !important;
        border: 2px solid #FCA5A5 !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 10px !important;
        min-height: 50px !important;
        width: 100% !important;
        transition: all 0.3s !important;
        font-size: 14px !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #EF4444, #DC2626) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
        border-color: #F87171 !important;
    }
    
    /* Inactive toggle button state */
    div[data-testid="column"] button[kind="secondary"].toggle-inactive {
        background: linear-gradient(135deg, #4B5563, #374151) !important;
        border: 2px solid #6B7280 !important;
        box-shadow: 0 2px 8px rgba(75, 85, 99, 0.3) !important;
    }
    
    div[data-testid="column"] button[kind="secondary"].toggle-inactive:hover {
        background: linear-gradient(135deg, #6B7280, #4B5563) !important;
        border-color: #9CA3AF !important;
        box-shadow: 0 6px 20px rgba(107, 114, 128, 0.4) !important;
    }
    
    /* Fix Number Input Styling */
    div[data-baseweb="input"] {
        background: var(--panel-dark) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] input {
        color: var(--text-primary) !important;
        background: transparent !important;
    }

    /* Add these lines */
    div[data-baseweb="input"] input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }

    div[data-baseweb="input"] input[type="number"] {
        color: black !important;
    }
    
    /* Fix Select Box Styling */
    div[data-baseweb="select"] {
        background: var(--panel-dark) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] div {
        color: var(--text-primary) !important;
        background: transparent !important;
    }
    
    /* Fix Placeholder Text */
    input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7 !important;
    }
    
    /* Fix Labels */
    label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        display: block !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--panel-dark);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(to bottom, var(--accent-purple), var(--accent-blue));
        border-radius: 4px;
    }
    
    /* Main Header - Tech Style */
    .tech-header {
        background: linear-gradient(90deg, var(--panel-darker), var(--panel-dark));
        padding: 30px 40px;
        margin: -20px -20px 30px -20px;
        border-bottom: 1px solid var(--accent-purple);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .tech-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
    }
    
    .tech-header h1 {
        color: var(--text-primary);
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 8px;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .tech-header p {
        color: var(--accent-blue);
        font-size: 16px;
        margin: 0;
        font-weight: 400;
    }
    
    /* Tech Cards */
    .tech-card {
        background: var(--panel-dark);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px var(--shadow-color);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .tech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tech-card:hover::before {
        opacity: 1;
    }
    
    .tech-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(168, 85, 247, 0.2);
        border-color: var(--accent-purple);
    }
    
    .tech-card-title {
        color: var(--accent-blue);
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    /* User Guide Styles */
    .guide-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid var(--border-color);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .guide-section {
        margin-bottom: 25px;
        padding-bottom: 25px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    .guide-section:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    
    .guide-section-title {
        color: var(--accent-purple);
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .guide-section-content {
        color: var(--text-primary);
        line-height: 1.7;
        font-size: 15px;
    }
    
    .guide-section-content strong {
        color: var(--accent-blue-light);
        font-weight: 600;
    }
    
    .guide-bullet {
        display: flex;
        margin: 10px 0;
        align-items: flex-start;
        gap: 10px;
    }
    
    .guide-bullet::before {
        content: "•";
        color: var(--accent-purple);
        font-size: 20px;
        line-height: 1;
        margin-top: 2px;
    }
    
    .guide-step {
        background: rgba(168, 85, 247, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border-left: 4px solid var(--accent-purple);
    }
    
    .guide-step-number {
        display: inline-block;
        background: var(--accent-purple);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        text-align: center;
        line-height: 28px;
        font-weight: 700;
        margin-right: 10px;
        font-size: 14px;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 5px;
        color: white !important;
    }
    
    .status-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    
    .status-deadlock {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
        color: var(--danger-light) !important;
        border: 1px solid rgba(239, 68, 68, 0.3);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.4); }
        100% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
    }
    
    /* Resource Status Indicators */
    .resource-status {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
        display: inline-block;
    }
    
    .resource-available {
        background: rgba(16, 185, 129, 0.2);
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .resource-allocated {
        background: rgba(56, 189, 248, 0.2);
        color: var(--accent-blue) !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .resource-requested {
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning) !important;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Matrix Tables - FIXED FOR ALL TABLES */
    .matrix-container {
        overflow-x: auto;
        margin: 15px 0;
    }
    
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        background: rgba(15, 23, 42, 0.5) !important;
        color: var(--text-primary) !important;
    }
    
    .matrix-table th {
        background: linear-gradient(90deg, var(--panel-dark), rgba(56, 189, 248, 0.1)) !important;
        padding: 14px;
        text-align: center;
        font-weight: 600;
        color: var(--accent-blue) !important;
        border: 1px solid var(--border-color);
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .matrix-table td {
        padding: 14px;
        text-align: center;
        border: 1px solid var(--border-color);
        color: var(--text-primary) !important;
        background: rgba(15, 23, 42, 0.3) !important;
        transition: background 0.3s;
    }
    
    .matrix-table tr:hover td {
        background: rgba(168, 85, 247, 0.1) !important;
    }
    
    /* Process Status Indicators */
    .process-status {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .process-running {
        background: rgba(16, 185, 129, 0.2);
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .process-blocked {
        background: rgba(239, 68, 68, 0.2);
        color: var(--danger-light) !important;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .process-waiting {
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning) !important;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    /* Footer */
    .tech-footer {
        text-align: center;
        padding: 30px;
        margin-top: 50px;
        background: rgba(15, 23, 42, 0.8);
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary) !important;
        font-size: 14px;
        position: relative;
    }
    
    .tech-footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 20%;
        right: 20%;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-purple), transparent);
    }
    
    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: var(--panel-dark);
        padding: 6px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        gap: 8px;
        padding: 10px 20px;
        font-weight: 500;
        color: var(--text-secondary) !important;
        border: 1px solid transparent;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(168, 85, 247, 0.1);
        color: var(--text-primary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(168, 85, 247, 0.2), rgba(56, 189, 248, 0.1));
        color: var(--accent-blue) !important;
        border: 1px solid var(--accent-purple);
        box-shadow: 0 2px 8px rgba(168, 85, 247, 0.2);
    }
    
    /* Success/Error Messages */
    .stAlert {
        border: 1px solid !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 10px 0 !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), transparent) !important;
        border-color: rgba(16, 185, 129, 0.3) !important;
        color: var(--success-light) !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), transparent) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
        color: var(--danger-light) !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), transparent) !important;
        border-color: rgba(245, 158, 11, 0.3) !important;
        color: var(--warning) !important;
    }
    
    /* Process Names - ORIGINAL STYLE */
    .process-name {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 500;
        color: var(--accent-blue-light) !important;
    }
    
    .resource-name {
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 500;
        color: var(--accent-purple-light) !important;
    }
    
    /* Dataframe Styling - FIXED */
    .dataframe {
        color: var(--text-primary) !important;
        background: rgba(15, 23, 42, 0.5) !important;
    }
    
    .dataframe th {
        color: var(--accent-blue) !important;
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    .dataframe td {
        color: var(--text-primary) !important;
        background: rgba(15, 23, 42, 0.3) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Info Boxes */
    .info-box {
        padding: 15px;
        background: rgba(56, 189, 248, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin: 10px 0;
        color: var(--accent-blue-light) !important;
    }
    
    /* Sequence Display */
    .sequence-display {
        font-family: 'Courier New', monospace;
        padding: 12px;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 6px;
        border: 1px solid var(--border-color);
        color: var(--success-light) !important;
        margin: 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Request History Items */
    .request-item {
        border-left: 3px solid;
        padding: 12px;
        margin-bottom: 10px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 0 8px 8px 0;
    }
    
    .request-item.granted {
        border-left-color: var(--success);
    }
    
    .request-item.denied {
        border-left-color: var(--danger);
    }
    
    /* Deadlock Cycle Visualization */
    .deadlock-cycle {
        padding: 15px;
        background: rgba(239, 68, 68, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        text-align: center;
    }
    
    .deadlock-cycle span {
        color: var(--danger-light) !important;
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
        background: rgba(239, 68, 68, 0.2);
        margin: 0 5px;
    }
    
    .deadlock-cycle .arrow {
        color: var(--accent-blue) !important;
        margin: 0 10px;
    }

    /* Persistent Messages */
    .persistent-message {
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 4px solid;
        background: rgba(30, 41, 59, 0.7);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-success {
        border-left-color: var(--success);
    }
    
    .message-error {
        border-left-color: var(--danger);
    }
    
    .message-info {
        border-left-color: var(--accent-blue);
    }
    
    .message-warning {
        border-left-color: var(--warning);
    }

    /* Single Instance Indicators */
    .single-instance-cell {
        font-weight: bold;
        text-align: center;
        padding: 8px;
        border-radius: 4px;
        margin: 2px;
        display: inline-block;
        min-width: 30px;
    }
    
    .allocated-true {
        background: rgba(16, 185, 129, 0.3);
        color: var(--success-light) !important;
        border: 1px solid rgba(16, 185, 129, 0.5);
    }
    
    .allocated-false {
        background: rgba(56, 189, 248, 0.3);
        color: var(--accent-blue) !important;
        border: 1px solid rgba(56, 189, 248, 0.5);
    }
    
    .requested-true {
        background: rgba(245, 158, 11, 0.3);
        color: var(--warning) !important;
        border: 1px solid rgba(245, 158, 11, 0.5);
    }
    
    .requested-false {
        background: rgba(30, 41, 59, 0.5);
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-color);
    }
    
    /* Toggle Button Styling - IMPROVED */
    .toggle-button-container {
        text-align: center;
        margin: 5px 0;
    }
    
    /* Available Resources Display - FIXED */
    .available-resource-box {
        padding: 10px;
        margin: 8px 0;
        border-radius: 8px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid var(--border-color);
    }
    
    .available-resource-box.available {
        border-left: 4px solid var(--success);
        background: rgba(16, 185, 129, 0.1);
    }
    
    .available-resource-box.allocated {
        border-left: 4px solid var(--accent-blue);
        background: rgba(56, 189, 248, 0.1);
    }
    
    /* FIX: Hide Streamlit's default dataframe styling */
    .stDataFrame {
        background: transparent !important;
    }
    
    /* FIX: Force table background colors */
    table {
        background: rgba(15, 23, 42, 0.5) !important;
        color: var(--text-primary) !important;
    }
    
    table th {
        background: rgba(30, 41, 59, 0.8) !important;
        color: var(--accent-blue) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    table td {
        background: rgba(15, 23, 42, 0.3) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }

</style>
""", unsafe_allow_html=True)

# Deadlock Detection & Recovery Algorithms for SINGLE RESOURCE INSTANCES
class DeadlockDetectorSingleInstance:
    def __init__(self, num_processes, num_resources):
        self.num_processes = num_processes
        self.num_resources = num_resources
        
    def detect_deadlock(self, allocation, request, available):
        """
        Detect deadlock using Wait-For Graph algorithm for SINGLE INSTANCE resources
        Returns list of deadlocked processes
        """
        n = self.num_processes
        m = self.num_resources
        
        # Initialize work vector (copy of available)
        work = available.copy()
        
        # Finish[i] = true if process has no allocated resources
        finish = [False] * n
        for i in range(n):
            if sum(allocation[i]) == 0:  # No resources allocated
                finish[i] = True
        
        # Detection algorithm for single instance resources
        while True:
            found = False
            for i in range(n):
                if not finish[i]:
                    # Check if all requests can be satisfied (single instance check)
                    can_allocate = True
                    for j in range(m):
                        # For single instance: request[i][j] is either 0 or 1
                        # work[j] is either 0 or 1
                        if request[i][j] == 1 and work[j] == 0:
                            can_allocate = False
                            break
                    
                    if can_allocate:
                        # Process can complete - release its SINGLE INSTANCE resources
                        for j in range(m):
                            if allocation[i][j] == 1:
                                work[j] = 1  # Resource becomes available
                        finish[i] = True
                        found = True
            
            if not found:
                break
        
        # Identify deadlocked processes
        deadlocked = [i for i in range(n) if not finish[i]]
        return deadlocked
    
    def find_deadlock_cycle(self, request, allocation):
        """
        Find the cycle in deadlock if exists for SINGLE INSTANCE resources
        Returns list of processes in the cycle
        """
        n = self.num_processes
        
        # Build wait-for graph for single instance resources
        wait_for = [[] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Process i waits for process j if:
                    # i requests a resource that j holds
                    waiting = False
                    for k in range(self.num_resources):
                        if request[i][k] == 1 and allocation[j][k] == 1:
                            waiting = True
                            break
                    if waiting:
                        wait_for[i].append(j)
        
        # Detect cycle using DFS
        visited = [False] * n
        rec_stack = [False] * n
        cycle = []
        
        def dfs(v, path):
            visited[v] = True
            rec_stack[v] = True
            path.append(v)
            
            for neighbor in wait_for[v]:
                if not visited[neighbor]:
                    if dfs(neighbor, path):
                        return True
                elif rec_stack[neighbor]:
                    # Cycle detected
                    start_idx = path.index(neighbor)
                    global cycle
                    cycle = path[start_idx:]
                    return True
            
            path.pop()
            rec_stack[v] = False
            return False
        
        for i in range(n):
            if not visited[i]:
                if dfs(i, []):
                    break
        
        return cycle
    
    def recover_by_process_termination(self, deadlocked, allocation, request, available):
        """
        Recover from deadlock by terminating processes for SINGLE INSTANCE resources
        Returns modified matrices
        """
        if not deadlocked:
            return allocation, request, available, []
        
        # Select process with maximum wait dependencies
        terminated = deadlocked[0]
        max_dependencies = 0
        
        for pid in deadlocked:
            # Count how many resources this process is requesting
            dependencies = sum(request[pid])
            if dependencies > max_dependencies:
                max_dependencies = dependencies
                terminated = pid
        
        # Release SINGLE INSTANCE resources of terminated process
        new_allocation = [row[:] for row in allocation]
        new_request = [row[:] for row in request]
        new_available = available[:]
        
        for j in range(self.num_resources):
            if new_allocation[terminated][j] == 1:
                new_available[j] = 1  # Resource becomes available
                new_allocation[terminated][j] = 0
            new_request[terminated][j] = 0  # Clear all requests
        
        return new_allocation, new_request, new_available, [terminated]
    
    def recover_by_resource_preemption(self, deadlocked, allocation, request, available):
        """
        Recover from deadlock by resource preemption for SINGLE INSTANCE resources
        Returns modified matrices
        """
        if not deadlocked:
            return allocation, request, available, []
        
        # Find resource that is most requested among deadlocked processes
        preempted_resource = -1
        max_requests = -1
        
        for j in range(self.num_resources):
            request_count = sum(request[pid][j] for pid in deadlocked)
            if request_count > max_requests:
                max_requests = request_count
                preempted_resource = j
        
        if preempted_resource == -1:
            return allocation, request, available, []
        
        # Find process holding this resource
        preempted_process = -1
        for pid in range(self.num_processes):
            if allocation[pid][preempted_resource] == 1:
                preempted_process = pid
                break
        
        if preempted_process == -1:
            return allocation, request, available, []
        
        # Preempt the SINGLE INSTANCE resource
        new_allocation = [row[:] for row in allocation]
        new_request = [row[:] for row in request]
        new_available = available[:]
        
        # Release resource from current holder
        new_allocation[preempted_process][preempted_resource] = 0
        new_request[preempted_process][preempted_resource] = 1  # Process will request it back
        
        # Make resource available
        new_available[preempted_resource] = 1
        
        return new_allocation, new_request, new_available, [(preempted_process, preempted_resource)]

# Process and Resource Names - ORIGINAL NAMES AS BEFORE
PROCESS_NAMES = [
    "Chrome Browser",
    "VS Code Editor", 
    "Spotify Player",
    "Discord Client",
    "Zoom Meeting",
    "Adobe Photoshop",
    "Blender 3D",
    "MySQL Server",
    "Docker Engine",
    "Node.js Server"
]

RESOURCE_NAMES = [
    "CPU Cores",
    "GPU Memory", 
    "RAM Allocation",
    "Disk I/O",
    "Network Bandwidth",
    "USB Ports",
    "Audio Channels",
    "File Handles"
]

# Initialize session state
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
    st.session_state.num_processes = 5
    st.session_state.num_resources = 3
    st.session_state.allocation = []
    st.session_state.request = []
    st.session_state.available = []
    st.session_state.deadlock_history = []
    st.session_state.process_status = []
    
    # Message states for persistence
    st.session_state.message_init = None
    st.session_state.message_detect = None
    st.session_state.message_update = None
    st.session_state.message_terminate = None
    st.session_state.message_preempt = None
    st.session_state.message_cycle = None
    st.session_state.message_reset = None
    
    # Toggle button states
    st.session_state.toggle_states = {}
    
    # User guide state
    st.session_state.show_user_guide = False

def initialize_system():
    """Initialize system with SINGLE INSTANCE resource values (0 or 1 only)"""
    np.random.seed(42)
    
    n = st.session_state.num_processes
    m = st.session_state.num_resources
    
    # Generate SINGLE INSTANCE allocation matrix (only 0 or 1)
    allocation = np.random.randint(0, 2, (n, m)).tolist()
    
    # Generate SINGLE INSTANCE request matrix (only 0 or 1)
    request = np.random.randint(0, 2, (n, m)).tolist()
    
    # Generate available SINGLE INSTANCE resources
    # For single instance: each resource is either available (1) or not (0)
    total_allocated = np.sum(allocation, axis=0)
    available = []
    for j in range(m):
        # If no one has allocated this resource, it's available
        if total_allocated[j] == 0:
            available.append(1)
        else:
            # If someone has it, it's not available
            available.append(0)
    
    # Ensure at least one resource is available
    if sum(available) == 0:
        available[random.randint(0, m-1)] = 1
    
    # Store in session state
    st.session_state.allocation = allocation
    st.session_state.request = request
    st.session_state.available = available
    st.session_state.system_initialized = True
    st.session_state.deadlock_history = []
    
    # Initialize process status
    st.session_state.process_status = ["Running"] * n
    
    # Initialize toggle states
    st.session_state.toggle_states = {}
    
    # Clear messages
    st.session_state.message_init = " System initialized with SINGLE INSTANCE resources (0 or 1 only)!"
    st.session_state.message_detect = None
    st.session_state.message_update = None
    st.session_state.message_terminate = None
    st.session_state.message_preempt = None
    st.session_state.message_cycle = None
    st.session_state.message_reset = None

# Header with User Guide Toggle
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("""
    <div class="tech-header">
        <h1>Deadlock Detection & Recovery Simulator</h1>
        <p>Advanced Wait-For Graph Algorithm with Single Resource Instances</p>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    if st.button("📖 User Guide", use_container_width=True, key="toggle_guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()

# User Guide Section
if st.session_state.show_user_guide:
    st.markdown('<div class="guide-container">', unsafe_allow_html=True)
    
    for section in USER_GUIDE_SECTIONS:
        st.markdown(f"""
        <div class="guide-section">
            <div class="guide-section-title">{section["title"]}</div>
            <div class="guide-section-content">{section["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close Guide Button
    if st.button("Close User Guide", use_container_width=True, key="close_guide"):
        st.session_state.show_user_guide = False
        st.rerun()

# Display persistent messages at the top
message_displayed = False
if st.session_state.message_init:
    st.markdown(f"""
    <div class="persistent-message message-success">
        <strong>System Initialization:</strong> {st.session_state.message_init}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_detect:
    message_type = "success" if "NO DEADLOCK" in st.session_state.message_detect else "error"
    st.markdown(f"""
    <div class="persistent-message message-{message_type}">
        <strong>Detection Result:</strong> {st.session_state.message_detect}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_update:
    st.markdown(f"""
    <div class="persistent-message message-info">
        <strong>Request Update:</strong> {st.session_state.message_update}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_terminate:
    st.markdown(f"""
    <div class="persistent-message message-success">
        <strong>Process Termination:</strong> {st.session_state.message_terminate}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_preempt:
    st.markdown(f"""
    <div class="persistent-message message-warning">
        <strong>Resource Preemption:</strong> {st.session_state.message_preempt}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_cycle:
    st.markdown(f"""
    <div class="persistent-message message-info">
        <strong>Complete Cycle:</strong> {st.session_state.message_cycle}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

if st.session_state.message_reset:
    st.markdown(f"""
    <div class="persistent-message message-info">
        <strong>System Reset:</strong> {st.session_state.message_reset}
    </div>
    """, unsafe_allow_html=True)
    message_displayed = True

# Clear messages button
if message_displayed:
    if st.button("Clear All Messages", key="clear_messages"):
        st.session_state.message_init = None
        st.session_state.message_detect = None
        st.session_state.message_update = None
        st.session_state.message_terminate = None
        st.session_state.message_preempt = None
        st.session_state.message_cycle = None
        st.session_state.message_reset = None
        st.rerun()

# Main Layout
col1, col2, col3 = st.columns([1.2, 1.8, 1])

with col1:
    # Configuration Card
    st.markdown("""
    <div class="tech-card">
        <div class="tech-card-title">
            System Configuration
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<label>Number of Processes</label>', unsafe_allow_html=True)
    num_processes = st.number_input(
        "",
        min_value=3,
        max_value=10,
        value=st.session_state.num_processes,
        key="input_processes",
        label_visibility="collapsed"
    )
    
    st.markdown('<label>Number of Resources</label>', unsafe_allow_html=True)
    num_resources = st.number_input(
        "",
        min_value=2,
        max_value=8,
        value=st.session_state.num_resources,
        key="input_resources",
        label_visibility="collapsed"
    )
    
    st.session_state.num_processes = num_processes
    st.session_state.num_resources = num_resources
    
    if st.button("Initialize System", use_container_width=True, key="init_btn"):
        with st.spinner("Initializing system with single instance resources..."):
            time.sleep(0.5)
            initialize_system()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Available Resources Card
    if st.session_state.system_initialized:
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                Resource Monitor
            </div>
        """, unsafe_allow_html=True)
        
        for j in range(st.session_state.num_resources):
            resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
            is_available = st.session_state.available[j] == 1
            
            if is_available:
                status_class = "resource-available"
                status_text = "AVAILABLE"
                icon = "✓"
                box_class = "available"
            else:
                status_class = "resource-allocated"
                status_text = "ALLOCATED"
                icon = "✘"
                box_class = "allocated"
            
            # Find which process has this resource
            holder = None
            for i in range(st.session_state.num_processes):
                if st.session_state.allocation[i][j] == 1:
                    holder = i
                    break
            
            holder_info = ""
            if holder is not None:
                holder_info = f"<div style='color: var(--text-secondary); font-size: 12px; margin-top: 4px;'>Held by: {PROCESS_NAMES[holder % len(PROCESS_NAMES)]}</div>"
            else:
                holder_info = "<div style='color: var(--text-secondary); font-size: 12px; margin-top: 4px;'>Not allocated to any process</div>"
            
            st.markdown(f"""
            <div class="available-resource-box {box_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="resource-name">{resource_name}</span>
                    </div>
                    <div class="resource-status {status_class}">
                        {icon} {status_text}
                    </div>
                </div>
                {holder_info}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Process Status Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                Process Status Monitor
            </div>
        """, unsafe_allow_html=True)
        
        for i in range(st.session_state.num_processes):
            process_name = PROCESS_NAMES[i % len(PROCESS_NAMES)]
            status = st.session_state.process_status[i]
            
            # Count allocated and requested resources
            allocated_count = sum(st.session_state.allocation[i])
            requested_count = sum(st.session_state.request[i])
            
            if status == "Running":
                status_class = "process-running"
                status_text = "RUNNING"
            elif status == "Blocked":
                status_class = "process-blocked"
                status_text = "BLOCKED"
            elif status == "Terminated":
                status_class = "process-blocked"
                status_text = "TERMINATED"
            else:
                status_class = "process-waiting"
                status_text = "WAITING"
            
            st.markdown(f"""
            <div style="margin: 8px 0; padding: 12px; background: rgba(30, 41, 59, 0.5); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span class="process-name">{process_name}</span>
                    </div>
                    <div class="process-status {status_class}">
                        {status_text}
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; color: var(--text-secondary); font-size: 12px;">
                    <div>Allocated: {allocated_count}</div>
                    <div>Requested: {requested_count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if st.session_state.system_initialized:
        # System Matrices Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                System Matrices (Single Instance: 0/1 only)
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Allocation", "Request", "Available"])
        
        with tab1:
            # Display allocation matrix with symbols
            st.markdown("""
            <div style="color: var(--text-secondary); margin-bottom: 10px;">
                <strong>Legend:</strong> ✔ = Resource Allocated (1), ✘ = Not Allocated (0)
            </div>
            """, unsafe_allow_html=True)
            
            # Create DataFrame for allocation
            alloc_data = []
            for i in range(st.session_state.num_processes):
                row = {}
                for j in range(st.session_state.num_resources):
                    resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
                    value = st.session_state.allocation[i][j]
                    row[resource_name] = "✔" if value == 1 else "✘"
                alloc_data.append(row)
            
            alloc_df = pd.DataFrame(
                alloc_data,
                index=PROCESS_NAMES[:st.session_state.num_processes]
            )
            
            # Apply custom styling
            def color_allocation(val):
                if val == "✔":
                    return 'background-color: rgba(16, 185, 129, 0.2); color: var(--success-light);'
                else:
                    return 'background-color: rgba(56, 189, 248, 0.2); color: var(--accent-blue);'
            
            styled_alloc = alloc_df.style.applymap(color_allocation)
            st.write(styled_alloc.to_html(escape=False), unsafe_allow_html=True)
        
        with tab2:
            # Display request matrix with symbols
            st.markdown("""
            <div style="color: var(--text-secondary); margin-bottom: 10px;">
                <strong>Legend:</strong> ↑ = Resource Requested (1), – = Not Requested (0)
            </div>
            """, unsafe_allow_html=True)
            
            # Create DataFrame for request
            request_data = []
            for i in range(st.session_state.num_processes):
                row = {}
                for j in range(st.session_state.num_resources):
                    resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
                    value = st.session_state.request[i][j]
                    row[resource_name] = "↑" if value == 1 else "–"
                request_data.append(row)
            
            request_df = pd.DataFrame(
                request_data,
                index=PROCESS_NAMES[:st.session_state.num_processes]
            )
            
            # Apply custom styling
            def color_request(val):
                if val == "↑":
                    return 'background-color: rgba(245, 158, 11, 0.2); color: var(--warning);'
                else:
                    return 'background-color: rgba(30, 41, 59, 0.5); color: var(--text-secondary);'
            
            styled_request = request_df.style.applymap(color_request)
            st.write(styled_request.to_html(escape=False), unsafe_allow_html=True)
        
        with tab3:
            # Display available resources - USING DATAFRAME FOR PROPER DISPLAY
            st.markdown("""
            <div style="color: var(--text-secondary); margin-bottom: 10px;">
                <strong>Available Resources (Single Instance: 0/1 only):</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Create DataFrame for available resources
            available_data = []
            for j in range(st.session_state.num_resources):
                resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
                is_available = st.session_state.available[j] == 1
                available_data.append({
                    "Resource": resource_name,
                    "Status": "Available" if is_available else "Allocated",
                    "Value": "1" if is_available else "0"
                })
            
            avail_df = pd.DataFrame(available_data)
            
            # Apply custom styling
            def color_available(row):
                if row['Status'] == "Available":
                    return ['background-color: rgba(16, 185, 129, 0.2); color: var(--success-light);'] * 3
                else:
                    return ['background-color: rgba(56, 189, 248, 0.2); color: var(--accent-blue);'] * 3
            
            styled_avail = avail_df.style.apply(color_available, axis=1)
            st.write(styled_avail.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # Summary
            total_available = sum(st.session_state.available)
            st.markdown(f"""
            <div style="margin-top: 15px; padding: 10px; background: rgba(30, 41, 59, 0.5); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <div style="color: var(--text-secondary);">Total Available Resources:</div>
                    <div style="color: var(--accent-blue); font-weight: 600;">{total_available}/{st.session_state.num_resources}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Deadlock Detection Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                Deadlock Detection
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Run Deadlock Detection", use_container_width=True, key="detect_btn"):
            with st.spinner("Running single instance detection algorithm..."):
                time.sleep(0.8)
                detector = DeadlockDetectorSingleInstance(st.session_state.num_processes, st.session_state.num_resources)
                
                # Detect deadlock
                deadlocked = detector.detect_deadlock(
                    st.session_state.allocation,
                    st.session_state.request,
                    st.session_state.available
                )
                
                # Find cycle
                cycle = detector.find_deadlock_cycle(
                    st.session_state.request,
                    st.session_state.allocation
                )
                
                if deadlocked:
                    # Update process status
                    for i in range(st.session_state.num_processes):
                        if i in deadlocked:
                            st.session_state.process_status[i] = "Blocked"
                    
                    deadlocked_names = [PROCESS_NAMES[i % len(PROCESS_NAMES)] for i in deadlocked]
                    st.session_state.message_detect = f"DEADLOCK DETECTED! {len(deadlocked)} process(es) are blocked: {', '.join(deadlocked_names)}"
                    
                    # Add to history
                    st.session_state.deadlock_history.append({
                        'time': time.strftime("%H:%M:%S"),
                        'deadlocked': len(deadlocked),
                        'processes': deadlocked.copy(),
                        'resolved': False
                    })
                    
                else:
                    # Update process status
                    for i in range(st.session_state.num_processes):
                        if sum(st.session_state.request[i]) > 0:
                            st.session_state.process_status[i] = "Waiting"
                        else:
                            st.session_state.process_status[i] = "Running"
                    
                    st.session_state.message_detect = "NO DEADLOCK DETECTED! All processes can proceed normally."
                
                st.rerun()
        
        # Show detection status if exists
        if st.session_state.message_detect:
            if "DEADLOCK DETECTED" in st.session_state.message_detect:
                st.markdown(f"""
                <div style="margin: 10px 0; padding: 15px; background: rgba(239, 68, 68, 0.1); 
                          border-radius: 8px; border-left: 4px solid var(--danger);">
                    <strong>Detection Status:</strong><br>
                    {st.session_state.message_detect}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin: 10px 0; padding: 15px; background: rgba(16, 185, 129, 0.1); 
                          border-radius: 8px; border-left: 4px solid var(--success);">
                    <strong>Detection Status:</strong><br>
                    {st.session_state.message_detect}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Resource Request Simulation Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                Simulate Resource Request (Single Instance)
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<label>Select Process</label>', unsafe_allow_html=True)
        selected_process = st.selectbox(
            "",
            PROCESS_NAMES[:st.session_state.num_processes],
            key="selected_process",
            label_visibility="collapsed"
        )
        pid = PROCESS_NAMES.index(selected_process)
        
        st.markdown('<label>Toggle Resource Requests (Single Instance: 0 or 1)</label>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: var(--text-secondary); font-size: 13px; margin-bottom: 10px;">
            <strong>Instructions:</strong> Click buttons to toggle resource requests<br>
            <span style="color: #F87171;">Red button</span> = Resource Requested (1)<br>
            <span style="color: #9CA3AF;">Gray button</span> = Not Requested (0)
        </div>
        """, unsafe_allow_html=True)
        
        # Create toggle buttons in a grid
        cols_per_row = min(4, st.session_state.num_resources)
        num_rows = (st.session_state.num_resources + cols_per_row - 1) // cols_per_row
        
        # Initialize session state for toggle buttons if not exists
        if f'toggle_state_{pid}' not in st.session_state:
            st.session_state[f'toggle_state_{pid}'] = st.session_state.request[pid].copy()
        
        # Use session state for toggle values
        current_toggle_state = st.session_state[f'toggle_state_{pid}']
        
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                j = row * cols_per_row + col_idx
                if j < st.session_state.num_resources:
                    with cols[col_idx]:
                        resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
                        current_value = current_toggle_state[j]
                        
                        # Create the toggle button with JavaScript for visual feedback
                        button_text = f"Requested" if current_value == 1 else f"Not Requested"
                        
                        # Create the toggle button
                        if st.button(
                            button_text,
                            key=f"toggle_{pid}_{j}",
                            help=f"Click to toggle request for {resource_name}",
                            use_container_width=True
                        ):
                            # Toggle the value
                            current_toggle_state[j] = 1 if current_value == 0 else 0
                            st.session_state[f'toggle_state_{pid}'] = current_toggle_state
                            st.rerun()
                        
                        # Visual indicator for current state
                        indicator_color = "#F87171" if current_value == 1 else "#9CA3AF"
                        st.markdown(f"""
                        <div style='text-align: center; margin-top: 5px;'>
                            <div style='font-size: 11px; color: {indicator_color}; font-weight: 600;'>{resource_name}</div>
                            <div style='font-size: 10px; color: var(--text-secondary);'>Value: {current_value}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Update request button
        if st.button("Update Request", use_container_width=True, key="update_request"):
            with st.spinner("Updating request..."):
                time.sleep(0.3)
                
                # Update request matrix with toggle state
                st.session_state.request[pid] = st.session_state[f'toggle_state_{pid}'].copy()
                
                # Update process status
                if sum(st.session_state.request[pid]) > 0:
                    st.session_state.process_status[pid] = "Waiting"
                else:
                    st.session_state.process_status[pid] = "Running"
                
                st.session_state.message_update = f"Request updated for {selected_process}"
                st.rerun()
        
        # Show update status if exists
        if st.session_state.message_update:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 15px; background: rgba(56, 189, 248, 0.1); 
                      border-radius: 8px; border-left: 4px solid var(--accent-blue);">
                <strong>Last Update:</strong><br>
                {st.session_state.message_update}
            </div>
            """, unsafe_allow_html=True)
        
        # Show current request status
        st.markdown(f"""
        <div style="margin: 15px 0; padding: 12px; background: rgba(30, 41, 59, 0.5); border-radius: 8px;">
            <div style="color: var(--text-secondary); font-size: 12px; margin-bottom: 5px;">
                Current Request Status for {selected_process}:
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
        """, unsafe_allow_html=True)
        
        requested_resources = []
        for j in range(st.session_state.num_resources):
            current_value = st.session_state.request[pid][j]
            resource_name = RESOURCE_NAMES[j % len(RESOURCE_NAMES)]
            if current_value == 1:
                requested_resources.append(resource_name)
        
        if requested_resources:
            for resource in requested_resources:
                st.markdown(f'<div style="background: rgba(245, 158, 11, 0.2); color: var(--warning); padding: 4px 8px; border-radius: 4px; font-size: 11px;">{resource}: ↑</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: var(--text-secondary); font-size: 11px;">No resources requested</div>', unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

with col3:
    if st.session_state.system_initialized:
        # Recovery Methods Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                Deadlock Recovery
            </div>
        """, unsafe_allow_html=True)
        
        # First, check current deadlock status
        detector = DeadlockDetectorSingleInstance(st.session_state.num_processes, st.session_state.num_resources)
        deadlocked = detector.detect_deadlock(
            st.session_state.allocation,
            st.session_state.request,
            st.session_state.available
        )
        
        if deadlocked:
            st.warning(f"""
            **Recovery Required!**
            
            {len(deadlocked)} process(es) are deadlocked.
            Choose a recovery method for single instance resources:
            """)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Process Termination", use_container_width=True, key="terminate_btn"):
                    with st.spinner("Terminating process to recover..."):
                        time.sleep(1)
                        
                        new_allocation, new_request, new_available, terminated = detector.recover_by_process_termination(
                            deadlocked,
                            st.session_state.allocation,
                            st.session_state.request,
                            st.session_state.available
                        )
                        
                        # Update system state
                        st.session_state.allocation = new_allocation
                        st.session_state.request = new_request
                        st.session_state.available = new_available
                        
                        # Update process status
                        if terminated:
                            pid = terminated[0]
                            st.session_state.process_status[pid] = "Terminated"
                            # Mark as resolved in history
                            if st.session_state.deadlock_history:
                                st.session_state.deadlock_history[-1]['resolved'] = True
                            
                            st.session_state.message_terminate = f"Process {PROCESS_NAMES[pid % len(PROCESS_NAMES)]} terminated. Resources released."
                        
                        st.rerun()
            
            with col_b:
                if st.button("Resource Preemption", use_container_width=True, key="preempt_btn"):
                    with st.spinner("Preempting resource..."):
                        time.sleep(1)
                        
                        new_allocation, new_request, new_available, preempted = detector.recover_by_resource_preemption(
                            deadlocked,
                            st.session_state.allocation,
                            st.session_state.request,
                            st.session_state.available
                        )
                        
                        # Update system state
                        st.session_state.allocation = new_allocation
                        st.session_state.request = new_request
                        st.session_state.available = new_available
                        
                        # Update process status
                        if preempted:
                            pid, resource = preempted[0]
                            st.session_state.process_status[pid] = "Waiting"
                            # Mark as resolved in history
                            if st.session_state.deadlock_history:
                                st.session_state.deadlock_history[-1]['resolved'] = True
                            
                            st.session_state.message_preempt = f"Resource {RESOURCE_NAMES[resource % len(RESOURCE_NAMES)]} preempted from {PROCESS_NAMES[pid % len(PROCESS_NAMES)]}"
                        
                        st.rerun()
            
            st.markdown("""
            <div class="info-box">
                <strong>Recovery Methods:</strong><br>
                1. <strong>Process Termination</strong>: Kill process to release its single instance resources<br>
                2. <strong>Resource Preemption</strong>: Take single resource from holder and make available
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("""
            **No Recovery Needed**
            
            System is currently deadlock-free.
            Run detection first to check for deadlocks.
            """)
        
        # Show recovery messages if exist
        if st.session_state.message_terminate:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 15px; background: rgba(16, 185, 129, 0.1); 
                      border-radius: 8px; border-left: 4px solid var(--success);">
                <strong>Termination Successful:</strong><br>
                {st.session_state.message_terminate}
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.message_preempt:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 15px; background: rgba(245, 158, 11, 0.1); 
                      border-radius: 8px; border-left: 4px solid var(--warning);">
                <strong>Preemption Successful:</strong><br>
                {st.session_state.message_preempt}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # System Operations Card
        st.markdown("""
        <div class="tech-card">
            <div class="tech-card-title">
                System Operations
            </div>
        """, unsafe_allow_html=True)
        
        col_x, col_y = st.columns(2)
        
        with col_x:
            if st.button("Run Complete Cycle", use_container_width=True, key="complete_cycle"):
                with st.spinner("Running detection-recovery cycle..."):
                    time.sleep(1)
                    
                    # Step 1: Detect
                    detector = DeadlockDetectorSingleInstance(st.session_state.num_processes, st.session_state.num_resources)
                    deadlocked = detector.detect_deadlock(
                        st.session_state.allocation,
                        st.session_state.request,
                        st.session_state.available
                    )
                    
                    if deadlocked:
                        # Step 2: Auto-recover
                        recovery_type = random.choice(['termination', 'preemption'])
                        
                        if recovery_type == 'termination':
                            new_allocation, new_request, new_available, terminated = detector.recover_by_process_termination(
                                deadlocked,
                                st.session_state.allocation,
                                st.session_state.request,
                                st.session_state.available
                            )
                            st.session_state.allocation = new_allocation
                            st.session_state.request = new_request
                            st.session_state.available = new_available
                            
                            if terminated:
                                pid = terminated[0]
                                st.session_state.process_status[pid] = "Terminated"
                                st.session_state.message_cycle = f"Auto-recovery: {PROCESS_NAMES[pid % len(PROCESS_NAMES)]} terminated"
                        
                        else:
                            new_allocation, new_request, new_available, preempted = detector.recover_by_resource_preemption(
                                deadlocked,
                                st.session_state.allocation,
                                st.session_state.request,
                                st.session_state.available
                            )
                            st.session_state.allocation = new_allocation
                            st.session_state.request = new_request
                            st.session_state.available = new_available
                            
                            if preempted:
                                pid, resource = preempted[0]
                                st.session_state.process_status[pid] = "Waiting"
                                st.session_state.message_cycle = f"Auto-recovery: {RESOURCE_NAMES[resource % len(RESOURCE_NAMES)]} preempted"
                        
                    else:
                        st.session_state.message_cycle = "System verified as deadlock-free."
                    
                    st.rerun()
        
        with col_y:
            if st.button("Reset All Requests", use_container_width=True, key="reset_requests"):
                with st.spinner("Resetting requests..."):
                    time.sleep(0.5)
                    
                    # Reset request matrix (0/1 only)
                    n = st.session_state.num_processes
                    m = st.session_state.num_resources
                    st.session_state.request = np.random.randint(0, 2, (n, m)).tolist()
                    
                    # Reset toggle states
                    for pid in range(n):
                        if f'toggle_state_{pid}' in st.session_state:
                            st.session_state[f'toggle_state_{pid}'] = st.session_state.request[pid].copy()
                    
                    # Reset process status
                    st.session_state.process_status = ["Running"] * n
                    
                    st.session_state.message_reset = "All requests have been reset to random values"
                    
                    st.rerun()
        
        # Show operation messages if exist
        if st.session_state.message_cycle:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 15px; background: rgba(56, 189, 248, 0.1); 
                      border-radius: 8px; border-left: 4px solid var(--accent-blue);">
                <strong>Cycle Result:</strong><br>
                {st.session_state.message_cycle}
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.message_reset:
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 15px; background: rgba(168, 85, 247, 0.1); 
                      border-radius: 8px; border-left: 4px solid var(--accent-purple);">
                <strong>Reset Result:</strong><br>
                {st.session_state.message_reset}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Deadlock History Card
        if st.session_state.deadlock_history:
            st.markdown("""
            <div class="tech-card">
                <div class="tech-card-title">
                    Deadlock History
                </div>
            """, unsafe_allow_html=True)
            
            for history in reversed(st.session_state.deadlock_history[-3:]):
                status_color = "var(--success)" if history['resolved'] else "var(--danger)"
                status_icon = "✓" if history['resolved'] else "✗"
                status_text = "Resolved" if history['resolved'] else "Pending"
                
                process_names = [PROCESS_NAMES[pid % len(PROCESS_NAMES)] for pid in history['processes']]
                process_list = ", ".join(process_names)
                
                st.markdown(f"""
                <div class="request-item {'granted' if history['resolved'] else 'denied'}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-weight: 600; color: var(--text-primary) !important;">
                                Deadlock Event
                            </div>
                            <div style="color: var(--text-secondary) !important; font-size: 12px; margin-top: 4px;">
                                {history['time']} • {history['deadlocked']} processes
                            </div>
                        </div>
                        <div style="font-size: 18px; color: {status_color} !important;">
                            {status_icon}
                        </div>
                    </div>
                    <div style="color: var(--accent-blue-light) !important; font-size: 13px; margin-top: 8px;">
                        Processes: {process_list}
                    </div>
                    <div style="color: {'var(--success-light)' if history['resolved'] else 'var(--danger-light)'} !important; 
                              font-size: 12px; margin-top: 4px;">
                        Status: {status_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="tech-footer">
    <div style="margin-bottom: 15px; font-size: 16px; color: var(--accent-blue) !important; font-weight: 500;">
        Deadlock Detection & Recovery System
    </div>
    <div style="color: var(--text-primary) !important; margin-bottom: 8px; font-weight: 500;">
        Developed by Alina Liaquat
    </div>
    <div style="color: var(--text-secondary) !important; font-size: 13px;">
        Advanced Wait-For Graph Algorithm with Single Resource Instances | Operating Systems Project
    </div>
</div>
""", unsafe_allow_html=True)

# Initialization Message
if not st.session_state.system_initialized:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 60px 40px; background: rgba(30, 41, 59, 0.8); 
                    border-radius: 16px; margin-top: 40px; border: 2px solid rgba(168, 85, 247, 0.3);
                    box-shadow: 0 0 30px rgba(168, 85, 247, 0.1);">
            <div style="font-size: 72px; color: var(--accent-purple) !important; margin-bottom: 20px;">
                ⚙️
            </div>
            <h3 style="color: var(--accent-blue) !important; margin-bottom: 15px; font-weight: 600;">
                Deadlock Detection & Recovery System
            </h3>
            <p style="color: var(--text-secondary) !important; margin-bottom: 30px; line-height: 1.6;">
                Configure system parameters and initialize to begin single instance deadlock simulation<br>
                Each resource has only ONE instance (0 or 1 allocation/request)
            </p>
            <div style="color: var(--accent-purple-light) !important; font-size: 14px; padding: 12px; 
                      background: rgba(168, 85, 247, 0.1); border-radius: 8px;">
                Set processes & resources, then click "Initialize System"
            </div>
        </div>
        """, unsafe_allow_html=True)