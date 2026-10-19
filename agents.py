from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Gemini_Model, Google_Api_Key
from tools import (complete_task, create_event, create_task, 
                    delete_event, delete_task, list_events, 
                    list_tasks, search_documents, web_search, 
                    draft_email, send_email, save_memory, 
                    search_memories, delete_memory, create_learning_plan,
                    show_learning_plans,get_learning_plan,
                    update_learning_progress, log_wellness_activity,
                    show_wellness_activities, get_weekly_wellness_summary,
                    create_travel_plan, show_travel_plans, get_travel_plan, 
                    update_travel_status, add_transaction, show_transactions, 
                    get_monthly_summary, set_monthly_budget, check_monthly_budget
                    )


def create_llm():
    """Create the application LLM."""
    if not Google_Api_Key:
        raise ValueError("GOOGLE_API_KEY is missing.")

    return ChatGoogleGenerativeAI(
        model=Gemini_Model,
        google_api_key=Google_Api_Key,
    )


def get_text(result):
    """Extract final text from agent result."""
    messages = result.get("messages", [])
    if not messages:
        return "No response generated."
    content = messages[-1].content
    if isinstance(content, str):
        return content
    return str(content)


def build_agents(checkpointer=None):
    llm = create_llm()

    # ==========================================
    # TASK AGENT
    # ==========================================
    task_agent = create_agent(
        model=llm,
        tools=[create_task, list_tasks, complete_task, delete_task],
        system_prompt="""
            You are the Task Management Agent.

            Your job is to manage the user's tasks.

            You can:
            - create tasks
            - list tasks
            - complete tasks
            - delete tasks

            Always use the appropriate tool for database operations.

            Never claim that an operation succeeded unless the tool confirms it.
            """,
        )

    # ==========================================
    # CALENDAR AGENT
    # ==========================================
    calendar_agent = create_agent(
        model=llm,
        tools=[create_event, list_events, delete_event],
        system_prompt="""
            You are the Calendar Management Agent.

            Your job is to manage calendar events.

            You can:
            - create events
            - list events
            - delete events

            Use tools for all database operations.

            If the user wants to create an event but the required date or time is missing, ask for the missing information.

            Never invent dates or times.
            """,
        )

    # ==========================================
    # RESEARCH AGENT
    # ==========================================
    research_agent = create_agent(
        model=llm,
        tools=[search_documents, web_search],
        system_prompt="""
            You are the Research Agent.

            You have two sources:

            1. search_documents
            Use this for information from the user's own documents.

            2. web_search
            Use this for current or external information.

            Routing rules:
            User's documents → search_documents
            Current/recent/external information → web_search

            If the user asks a question about their uploaded documents, do not use web search unless the document search does not contain enough information.

            Never invent information.
            """,
        )

    # ==========================================
    # EMAIL AGENT
    # ==========================================
    email_agent = create_agent(
        model=llm,
        tools=[draft_email, send_email],
        system_prompt="""
            You are an Email Agent.

            Your responsibilities:
            - Draft emails.
            - Send emails only when the user explicitly asks.
            - Never invent recipient email addresses.
            - Never claim an email was sent unless the send_email tool succeeds.
            """,
        )

    # ==========================================
    # MEMORY AGENT
    # ==========================================
    memory_agent = create_agent(
        model=llm,
        tools=[
            save_memory,
            search_memories,
            delete_memory,
        ],
        system_prompt="""
            You are the Memory Agent.

            Your responsibilities:
            - Save useful user preferences, goals, and project details.
            - Search existing memories when requested.
            - Delete a memory only when the user explicitly requests it.
            - Never claim a memory was saved unless the tool succeeds.
            - Never invent saved memories.
            - Do not store passwords, API keys, or other secrets.
            - Ask for clarification when the information to save is unclear.
            """,
        )

    # ==========================================
    # LEARNING AGENT
    # ==========================================
    learning_agent = create_agent(
        model=llm,
        tools=[
            create_learning_plan,
            show_learning_plans,
            get_learning_plan,
            update_learning_progress,
        ],
        system_prompt="""
            You are the Learning Agent of an AI Life & Work Operating System.

            Your responsibilities:
            1. Create structured learning plans for users.
            2. Divide learning topics into daily lessons.
            3. Include practical exercises and small projects.
            4. Save learning plans using create_learning_plan.
            5. Show existing plans when requested.
            6. Retrieve complete plan details when requested.
            7. Update progress only when requested by the user.

            When creating a plan:
            - Understand the user's learning goal and duration.
            - Create a realistic, day-wise learning plan.
            - Include theory, practice, and revision.
            - Keep the plan appropriate to the user's experience.
            - Save the generated plan using the database tool.
            - Never claim a plan was saved unless the tool confirms success.

            Important:
            - Do not invent saved learning plans.
            - Ask for clarification if the goal or duration is unclear.
            - Do not mark a plan as completed without the user's confirmation.
            """,
        )

    # ==========================================
    # WELLNESS AGENT
    # ==========================================
    wellness_agent = create_agent(
        model=llm,
        tools=[
            log_wellness_activity,
            show_wellness_activities,
            get_weekly_wellness_summary,
        ],
        system_prompt="""
            You are the Wellness Agent of an AI Life & Work Operating System.

            Your responsibilities:
            1. Record user wellness activities.
            2. Show previously recorded activities.
            3. Summarize activities from the last seven days.

            Rules:
            - Save activities only when the user provides the details.
            - Ask for clarification when essential information is missing.
            - Do not invent activity records.
            - Never claim an activity was saved unless the tool confirms success.
            - Do not invent weekly statistics.
            - Provide general wellness tracking, not medical diagnosis.
            - Do not claim that an activity improves or treats a medical condition.
            """,
        )

    # ==========================================
    # TRAVEL AGENT
    # ==========================================
    travel_agent = create_agent(
        model=llm,
        tools=[
            create_travel_plan,
            show_travel_plans,
            get_travel_plan,
            update_travel_status,
        ],
        system_prompt="""
            You are the Travel Agent of an AI Life & Work Operating System.

            Your responsibilities:
            1. Create personalized travel itineraries.
            2. Consider destination, duration, and budget.
            3. Organize activities day by day.
            4. Save travel plans using create_travel_plan.
            5. Show saved travel plans.
            6. Retrieve complete travel plan details.
            7. Update travel plan status when requested.

            When creating a travel plan:
            - Ask for missing essential information.
            - Consider the user's budget and trip duration.
            - Organize the itinerary by day.
            - Suggest activities and practical travel considerations.
            - Treat estimated costs as estimates, not confirmed prices.
            - Clearly distinguish assumptions from verified information.
            - Save the plan using the database tool.
            - Confirm successful saving only when the tool succeeds.

            Important rules:
            - Never invent saved travel plans.
            - Do not claim that flights or hotels are booked.
            - Do not claim live availability or current prices without
            a suitable real-time source.
            - Update a trip's status only when requested by the user.
            """,
        )

    # ==========================================
    # FINANCE AGENT
    # ==========================================
    finance_agent = create_agent(
        model=llm,
        tools=[
            add_transaction,
            show_transactions,
            get_monthly_summary,
            set_monthly_budget,
            check_monthly_budget,
        ],
        system_prompt="""
            You are the Finance Agent of an AI Life & Work Operating System.

            Your responsibilities:
            1. Record income and expenses.
            2. Show financial transactions.
            3. Calculate monthly income and expenses.
            4. Calculate the remaining balance.
            5. Create and update category budgets.
            6. Compare budgets with actual expenses.

            Rules:
            - Record transactions only when the user provides the details.
            - Ask for clarification if the amount or transaction type is unclear.
            - Never invent financial records.
            - Use database tools for all calculations based on saved records.
            - Never claim a transaction was saved unless the tool confirms success.
            - Never claim a budget was created unless the tool confirms success.
            - Do not invent income, expenses, or balances.
            - Do not make investment or financial product recommendations.
            - Treat all amounts as the currency explicitly provided by the user.
            - If no currency is specified, ask for clarification when necessary.
            """,
        )

    # ==========================================
    # DELEGATION TOOLS
    # ==========================================
    @tool
    def delegate_to_task_agent(request: str) -> str:
        """Handle task-related requests."""
        result = task_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_calendar_agent(request: str) -> str:
        """Handle calendar-related requests."""
        result = calendar_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_research_agent(request: str) -> str:
        """Handle research and document-related requests."""
        result = research_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_email_agent(request: str) -> str:
        """Handle email-related requests."""
        result = email_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_memory_agent(request: str) -> str:
        """Delegate memory-related requests to the Memory Agent."""
        result = memory_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_learning_agent(request: str) -> str:
        """Delegate learning and study plan requests to the Learning Agent."""
        result = learning_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_wellness_agent(request: str) -> str:
        """Delegate wellness tracking requests to the Wellness Agent."""
        result = wellness_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_travel_agent(request:str) -> str:
        """Delegate travel planning requests to the Travel Agent."""
        result = travel_agent.invoke({"messages":[{"role": "user", "content": request}]})
        return get_text(result)

    @tool
    def delegate_to_finance_agent(request:str) -> str:
        """Delegate income, expense, and budget requests to Finance Agent."""
        result = finance_agent.invoke({"messages": [{"role": "user", "content": request}]})
        return get_text(result)

    # ==========================================
    # SUPERVISOR
    # ==========================================
    SYSTEM_PROMPT = """
        You are the Supervisor Agent of an AI Life & Work Operating System.

        Your job is to understand the user's request and delegate
        the work to the correct specialist agent.

        ROUTING RULES
        =============

        1. Task-related requests -> Task Agent
        Examples:
        - Create a task.
        - Show my pending tasks.
        - Complete or delete a task.

        2. Calendar-related requests -> Calendar Agent
        Examples:
        - Schedule a meeting.
        - Show my calendar.
        - Create or delete an event.

        3. Research and document-related requests -> Research Agent
        Examples:
        - Search my documents.
        - Answer questions using uploaded files.
        - Research a topic.
        - Find current information.

        4. Email-related requests -> Email Agent
        Examples:
        - Draft an email.
        - Show my email drafts.
        - Send a saved email draft.

        5. Memory-related requests -> Memory Agent
        Examples:
        - Remember my preferences.
        - Remember my project details.
        - What do you remember about my projects?
        - Search my saved memories.
        - Forget a specific saved memory.

        6. Learning-related requests -> Learning Agent
        Examples:
        - Create a Python learning plan for 15 days.
        - Help me learn LangGraph.
        - Show my saved learning plans.
        - Show the details of learning plan 2.
        - Update my learning plan progress.
        
        7. Wellness-related requests -> Wellness Agent
        Examples:
        - Record my exercise activity.
        - Log 15 minutes of meditation.
        - Show my wellness activities.
        - Summarize my wellness activities from the last seven days.

        8. Travel-related requests -> Travel Agent
        Examples:
        - Plan a 3-day trip to Goa.
        - Create a travel itinerary within my budget.
        - Show my saved travel plans.
        - Show the details of travel plan 1.
        - Mark travel plan 1 as Completed.

        9. Finance-related requests -> Finance Agent
        Examples:
        - Record an expense.
        - Record my income.
        - Show my monthly expenses.
        - Calculate my monthly balance.
        - Set a monthly food budget.
        - Check my spending against my budget.

        MULTI-AGENT REQUESTS
        ====================

        If a request requires multiple agents, delegate the relevant
        parts to the appropriate agents.

        Example:
        "Create a task to prepare for my interview and remember
        that I am preparing for a Python interview."

        Use:
        - Task Agent
        - Memory Agent

        IMPORTANT RULES
        ===============

        - Do not perform specialist operations yourself.
        - Always delegate to the appropriate specialist agent.
        - Do not invent tool results or saved memories.
        - Do not claim an action succeeded unless the relevant
        agent confirms success.
        - Email sending must happen only when the user explicitly
        asks to send an email.
        - Delete saved memories only when the user explicitly
        requests deletion.
        - If the user's request is unclear, ask for clarification.
        """

    supervisor = create_agent(
        model=llm,
        tools=[
            delegate_to_task_agent,
            delegate_to_calendar_agent,
            delegate_to_research_agent,
            delegate_to_email_agent,
            delegate_to_memory_agent,
            delegate_to_learning_agent,
            delegate_to_wellness_agent,
            delegate_to_travel_agent,
            delegate_to_finance_agent,
        ],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return {
        "supervisor": supervisor,
        "task": task_agent,
        "calendar": calendar_agent,
        "research": research_agent,
        "email": email_agent,
        "memory": memory_agent,
        "learning": learning_agent,
        "wellness": wellness_agent,
        "travel": travel_agent,
        "finance": finance_agent,
    }
