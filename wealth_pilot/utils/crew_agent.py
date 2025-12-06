import google.generativeai as genai
import json

# --- Lightweight Framework mimicking CrewAI structure ---

class Agent:
    def __init__(self, role, goal, backstory, verbose=False, llm_config=None):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.api_key = llm_config.get('api_key') if llm_config else None

class Task:
    def __init__(self, description, agent, expected_output):
        self.description = description
        self.agent = agent
        self.expected_output = expected_output

class Crew:
    def __init__(self, agents, tasks, verbose=False):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose

    def kickoff(self, status_callback=None):
        results = {}
        context = ""
        
        if self.agents and hasattr(self.agents[0], 'api_key'):
             genai.configure(api_key=self.agents[0].api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')

        for i, task in enumerate(self.tasks):
            agent = task.agent
            
            if self.verbose:
                print(f"🤖 Agent {agent.role} is working...")
            
            # UI Callback
            if status_callback:
                status_callback(f"🤖 Agent {agent.role} is working...")
            
            # Chain of Thought Prompting with JSON enforcement
            prompt = f"""
            You are currently acting as the following agent:
            **Role:** {agent.role}
            **Goal:** {agent.goal}
            **Backstory:** {agent.backstory}
            
            **Current Task:**
            {task.description}
            
            **Expected Output Format:**
            {task.expected_output}
            
            **Prior Context (from previous agents):**
            {context}
            
            IMPORTANT: Return ONLY the raw JSON content (no markdown code blocks) if JSON is requested.
            """
            
            try:
                response = model.generate_content(prompt)
                task_result = response.text
                
                # Clean up json if model wrapped it in backticks
                cleaned_result = task_result.replace("```json", "").replace("```", "").strip()
                
                results[agent.role] = cleaned_result
                context += f"\n\n--- Output from {agent.role} ---\n{task_result}"
                
            except Exception as e:
                return f"Error connecting to AI: {e}"
                
        return results

# --- Workflow Implementation ---

def run_crew_analysis(client_profile, portfolio, market_data, api_key=None, status_callback=None):
    """
    Runs a Multi-Agent team to analyze the client's portfolio.
    Returns a Dict of results for visualization.
    """
    if not api_key:
        return {"error": "API Key is required for Agentic features."}

    # 1. Market Analyst Agent
    market_analyst = Agent(
        role='Market Analyst',
        goal='Analyze current market trends for the specific holdings.',
        backstory="""You are a veteran market analyst. You provide raw data and trends with sources.""",
        verbose=True,
        llm_config={'api_key': api_key}
    )

    # 2. Risk Manager Agent
    risk_manager = Agent(
        role='Risk Manager',
        goal='Evaluate portfolio risk against client profile.',
        backstory="""You are the Chief Risk Officer. You identify misalignment and concentration risks.""",
        verbose=True,
        llm_config={'api_key': api_key}
    )

    # 3. Wealth Manager Agent (Leader)
    wealth_manager = Agent(
        role='Wealth Manager',
        goal='Synthesize insights into a strategy.',
        backstory="""You are the Senior Wealth Manager. You create the final empathetic strategy report.""",
        verbose=True,
        llm_config={'api_key': api_key}
    )

    # --- TASKS ---

    # Task 1: Market Analysis
    task_analysis = Task(
        description=f"""
        Analyze the following portfolio holdings based on: {json.dumps(portfolio)}
        
        Identify 3 Top Opportunities and 3 Top Threats.
        For each, cite the "Source" (e.g., "Market Trend", "Tech Sector News") and "Reasoning".
        """,
        agent=market_analyst,
        expected_output="""
        JSON format:
        {
            "opportunities": [
                {"ticker": "AAPL", "insight": "...", "source": "...", "reasoning": "..."},
                ...
            ],
            "threats": [
                {"ticker": "...", "insight": "...", "source": "...", "reasoning": "..."}
            ]
        }
        """
    )

    # Task 2: Risk Assessment
    task_risk = Task(
        description=f"""
        Evaluate alignment:
        Client: {json.dumps(client_profile)}
        Portfolio: {json.dumps(portfolio)}
        
        Calculate a "Risk Score" (0-100, where 100 is extremely risky).
        Provide a "Risk Summary" and "Concerns".
        """,
        agent=risk_manager,
        expected_output="""
        JSON format:
        {
            "risk_score": 75,
            "risk_level": "High",
            "summary": "...",
            "concerns": ["Concern 1", "Concern 2"]
        }
        """
    )

    # Task 3: Final Strategy (Consolidation)
    task_strategy = Task(
        description=f"""
        Create a "Strategic Investment Report".
        Synthesize the Market Analysis and Risk Assessment into a final readable report.
        Include detailed Buy/Sell recommendations.
        """,
        agent=wealth_manager,
        expected_output="""
        A standard Markdown string (NOT JSON) with headers:
        # Executive Summary
        # Risk Analysis
        # Market Outlook
        # Recommended Actions
        """
    )

    # Create Crew
    investment_crew = Crew(
        agents=[market_analyst, risk_manager, wealth_manager],
        tasks=[task_analysis, task_risk, task_strategy],
        verbose=True
    )

    results = investment_crew.kickoff(status_callback=status_callback)
    return results
