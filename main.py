import os
from crewai import Agent, Crew, Process, Task, LLM
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

gemini_llm = LLM(
    model="gemini/gemini-3.5-flash",
    api_key=api_key,
    temperature=0.2
)

# 1. ఏజెంట్ల నిర్వచనం
junk_filter = Agent(
    role="Spam & Junk Filter Specialist",
    goal="Identify and eliminate irrelevant, spam, or promotional emails accurately.",
    backstory="Expert gatekeeper ensuring zero spam enters customer service queues.",
    verbose=False,
    llm=gemini_llm
)

email_categorizer = Agent(
    role="Email Triage Specialist",
    goal="Categorize legitimate business inquiries accurately based on complexity.",
    backstory="Analyzes incoming emails and classifies them strictly as EASY_RESPONSE or HARD_RESPONSE.",
    verbose=False,
    llm=gemini_llm
)

response_writer = Agent(
    role="Customer Support Response Executive",
    goal="Generate highly professional draft responses or formal escalation tickets.",
    backstory="Writes professional email replies or structured internal escalation tickets.",
    verbose=False,
    llm=gemini_llm
)

# 2. టెస్ట్ చేయాల్సిన 3 వేర్వేరు ఈమెయిల్స్
test_scenarios = [
    {
        "name": "1. Easy Inquiry (Rajesh)",
        "email": "Hi Team, I came across your AI automation services and would like to learn more about your starter package. Could you share pricing details and delivery timeframes? Best regards, Rajesh Kumar",
        "file": "report_1_easy_response.md"
    },
    {
        "name": "2. Junk / Spam Phishing",
        "email": "CONGRATULATIONS! You have won a $1,000,000 Walmart Gift Card! Click here immediately to claim your cash reward before it expires!",
        "file": "report_2_junk_trashed.md"
    },
    {
        "name": "3. Hard Escalation (Legal Threat)",
        "email": "URGENT: Your automation platform crashed during our live demo! We lost critical customer data and demand an immediate full refund or we will initiate legal action by Monday.",
        "file": "report_3_hard_escalation.md"
    }
]

if __name__ == "__main__":
    print("\n=== STARTING AUTOMATED BATCH TRIAGE (3 SCENARIOS) ===\n")

    for scenario in test_scenarios:
        print(f"[*] Processing: {scenario['name']}...")

        task_filter = Task(
            description=(
                f"Analyze the incoming email below:\n'''{scenario['email']}'''\n"
                "Determine if this is genuine communication or junk/spam. "
                "Output strictly 'JUNK' or 'NOT_JUNK' with a one-sentence rationale."
            ),
            expected_output="Decision: 'JUNK' or 'NOT_JUNK' along with brief explanation.",
            agent=junk_filter
        )

        task_triage = Task(
            description=(
                "If the previous step determined the message is NOT_JUNK, analyze its complexity:\n"
                "- RULE 1: Any inquiry asking about pricing, starter packages, delivery timelines, "
                "or general service questions MUST STRICTLY BE CLASSIFIED AS 'EASY_RESPONSE'. Do NOT escalate general sales questions.\n"
                "- RULE 2: Classify as 'HARD_RESPONSE' ONLY IF the email contains explicit anger, system outages/bugs, "
                "data loss, refund demands, or legal threats."
            ),
            expected_output="Strictly output: 'Classification: EASY_RESPONSE' or 'Classification: HARD_RESPONSE' with brief reasoning.",
            agent=email_categorizer
        )

        task_response = Task(
            description=(
                "Review the previous classification:\n"
                "1. If 'EASY_RESPONSE': Draft an empathetic and professional customer reply email to the client (e.g. Rajesh). "
                "Include standard pricing ($99/month), a 2-day delivery estimate, and an onboarding calendar link.\n"
                "2. If 'HARD_RESPONSE': Generate an internal escalation ticket with 'STATUS: LEAVE_FOR_HUMAN - Manual review required'.\n"
                "3. If 'JUNK': Output strictly 'ACTION: TRASHED - No response required'."
            ),
            expected_output="A polished email response draft, escalation ticket, or trash confirmation.",
            agent=response_writer,
            output_file=scenario["file"]
        )

        crew = Crew(
            agents=[junk_filter, email_categorizer, response_writer],
            tasks=[task_filter, task_triage, task_response],
            process=Process.sequential,
            verbose=False
        )

        crew.kickoff()
        print(f"[✓] Created: {scenario['file']}\n")

    print("=== ALL 3 REPORTS CREATED SUCCESSFULLY ===")