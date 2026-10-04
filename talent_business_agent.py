
import json
import sqlite3
import numpy as np
from groq import Groq


# =========================================================
# 1. USER STATE
# =========================================================

user_state = {
    "skill": None,
    "experience": None,
    "current_products": None,
    "materials": None,
    "business_goal": None,
    "selected_product": None,
    "target_customer": None,
    "pricing": None,
    "brand": None,
    "digital_presence": None,
    "marketing": None,
    "roadmap": None
}


def update_user_state(updates):
    for key, value in updates.items():
        if key in user_state and value is not None:
            user_state[key] = value
    return user_state


def get_user_state_summary():
    return {
        k: v for k, v in user_state.items()
        if v is not None
    }


def get_missing_user_information():
    required = [
        "skill",
        "experience",
        "current_products",
        "materials",
        "business_goal"
    ]

    return [
        field for field in required
        if not user_state.get(field)
    ]


def get_business_state():
    return {
        "state": get_user_state_summary(),
        "missing_information": get_missing_user_information()
    }


def save_business_information(
    skill=None,
    experience=None,
    current_products=None,
    materials=None,
    business_goal=None,
    selected_product=None,
    target_customer=None
):
    update_user_state({
        "skill": skill,
        "experience": experience,
        "current_products": current_products,
        "materials": materials,
        "business_goal": business_goal,
        "selected_product": selected_product,
        "target_customer": target_customer
    })

    return get_business_state()


# =========================================================
# 2. BUSINESS TOOLS
# =========================================================

def calculate_price(
    material_cost,
    labor_hours,
    hourly_labor_rate,
    packaging_cost,
    delivery_cost,
    other_costs,
    profit_margin
):
    values = [
        material_cost,
        labor_hours,
        hourly_labor_rate,
        packaging_cost,
        delivery_cost,
        other_costs,
        profit_margin
    ]

    if any(v < 0 for v in values):
        raise ValueError("Costs, hours and profit margin cannot be negative.")

    if profit_margin > 100:
        raise ValueError("Profit margin must be 100% or less.")

    labor_cost = labor_hours * hourly_labor_rate

    total_cost = (
        material_cost
        + labor_cost
        + packaging_cost
        + delivery_cost
        + other_costs
    )

    profit = total_cost * (profit_margin / 100)
    suggested_price = total_cost + profit

    result = {
        "material_cost": material_cost,
        "labor_cost": labor_cost,
        "packaging_cost": packaging_cost,
        "delivery_cost": delivery_cost,
        "other_costs": other_costs,
        "total_cost": total_cost,
        "profit_margin": profit_margin,
        "estimated_profit": profit,
        "suggested_price": suggested_price
    }

    update_user_state({"pricing": result})

    return result


def assess_skill(
    skill,
    experience,
    current_products,
    materials,
    interests=None,
    business_goal=None
):
    missing = []

    if not skill:
        missing.append("skill")
    if not experience:
        missing.append("experience level")
    if not current_products:
        missing.append("what the user currently makes")
    if not materials:
        missing.append("available materials/resources")
    if not business_goal:
        missing.append("business goal")

    result = {
        "skill": skill,
        "experience": experience,
        "current_products": current_products,
        "materials": materials,
        "interests": interests,
        "business_goal": business_goal,
        "missing_information": missing
    }

    update_user_state({
        "skill": skill,
        "experience": experience,
        "current_products": current_products,
        "materials": materials,
        "business_goal": business_goal
    })

    return result


def plan_product(
    skill,
    product,
    materials,
    target_customer,
    difficulty_level,
    production_time
):
    result = {
        "skill": skill,
        "product": product,
        "materials": materials,
        "target_customer": target_customer,
        "difficulty_level": difficulty_level,
        "production_time": production_time,
        "note": "Planning inputs and assumptions, not verified market facts."
    }

    update_user_state({
        "skill": skill,
        "selected_product": product,
        "target_customer": target_customer
    })

    return result


def create_business_roadmap(
    skill,
    selected_product,
    business_goal,
    current_stage
):
    roadmap = [
        "Validate skill and product idea",
        "Select first product",
        "Calculate product cost and price",
        "Create brand identity",
        "Create digital presence",
        "Create initial marketing content",
        "Reach potential customers",
        "Collect feedback and improve",
        "Scale gradually"
    ]

    result = {
        "skill": skill,
        "selected_product": selected_product,
        "business_goal": business_goal,
        "current_stage": current_stage,
        "roadmap": roadmap
    }

    update_user_state({"roadmap": result})

    return result


def generate_brand_ideas(skill, selected_product, business_goal):
    result = {
        "skill": skill,
        "selected_product": selected_product,
        "business_goal": business_goal,
        "ideas": [
            "Create a simple memorable brand name related to the craft.",
            "Choose a clear visual identity matching the product.",
            "Use consistent fonts, colors and presentation.",
            "Keep the brand easy to remember and spell."
        ],
        "note": "Creative suggestions, not verified market facts."
    }

    update_user_state({"brand": result})

    return result


def generate_digital_content(
    product,
    brand_name,
    platform,
    content_type
):
    result = {
        "product": product,
        "brand_name": brand_name,
        "platform": platform,
        "content_type": content_type,
        "suggestions": [
            f"Create a clear post introducing {product}.",
            "Show the product clearly with good lighting.",
            "Explain important product details honestly.",
            "Include a simple call to action.",
            "Use consistent branding."
        ],
        "note": "Content suggestions, not verified market claims."
    }

    update_user_state({"digital_presence": result})

    return result


def create_marketing_plan(
    product,
    platform,
    business_goal,
    available_time
):
    result = {
        "product": product,
        "platform": platform,
        "business_goal": business_goal,
        "available_time": available_time,
        "plan": [
            "Create clear product content.",
            "Post consistently according to available time.",
            "Respond to genuine customer questions.",
            "Collect customer feedback.",
            "Improve content based on observed responses."
        ],
        "note": "Planning suggestion, not a prediction of results."
    }

    update_user_state({"marketing": result})

    return result


def get_business_progress():
    journey = [
        ("Skill Assessment", "skill"),
        ("Product Selection", "selected_product"),
        ("Pricing", "pricing"),
        ("Brand", "brand"),
        ("Digital Presence", "digital_presence"),
        ("Marketing", "marketing"),
        ("Roadmap", "roadmap")
    ]

    completed = [
        stage for stage, field in journey
        if user_state.get(field) is not None
    ]

    remaining = [
        stage for stage, field in journey
        if user_state.get(field) is None
    ]

    return {
        "completed_stages": completed,
        "remaining_stages": remaining,
        "completed_count": len(completed),
        "remaining_count": len(remaining)
    }


# =========================================================
# 3. SIMPLE VERIFIED KNOWLEDGE BASE
# =========================================================

KNOWLEDGE_BASE = {
    "pricing": """
Basic product pricing should consider material cost, labor cost,
packaging, delivery and other relevant costs. A business owner can
then choose a profit margin. Actual market prices should not be invented.
""",

    "branding": """
A simple brand can use a memorable name, consistent visual identity,
clear product presentation and easy-to-read communication.
""",

    "social_media": """
Product content should clearly show the product, explain important
details honestly and include a simple call to action.
""",

    "photography": """
Product photos should use clear lighting, a clean background and
show the product from useful angles.
""",

    "customer_communication": """
Customer communication should be clear, honest and respectful.
Important product details should not be exaggerated or invented.
"""
}


def search_business_knowledge(query):
    query_lower = query.lower()

    matches = []

    keywords = {
        "pricing": ["price", "pricing", "cost", "profit"],
        "branding": ["brand", "branding", "name", "logo"],
        "social_media": ["social", "post", "content", "instagram", "facebook"],
        "photography": ["photo", "photography", "picture", "image"],
        "customer_communication": ["customer", "communication", "message"]
    }

    for topic, words in keywords.items():
        if any(word in query_lower for word in words):
            matches.append({
                "source": topic,
                "content": KNOWLEDGE_BASE[topic]
            })

    if not matches:
        return {
            "query": query,
            "found": False,
            "results": [],
            "context": "No relevant verified knowledge was found."
        }

    return {
        "query": query,
        "found": True,
        "results": matches,
        "context": "\n\n---\n\n".join(
            item["content"] for item in matches
        )
    }


# =========================================================
# 4. SQLITE
# =========================================================

DB_PATH = "talent_business.db"


def initialize_database():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill TEXT,
        experience TEXT,
        current_products TEXT,
        materials TEXT,
        business_goal TEXT,
        selected_product TEXT,
        target_customer TEXT,
        pricing TEXT,
        brand TEXT,
        digital_presence TEXT,
        marketing TEXT,
        roadmap TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_business_to_db(state):
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    INSERT INTO businesses (
        skill, experience, current_products, materials,
        business_goal, selected_product, target_customer,
        pricing, brand, digital_presence, marketing, roadmap
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        state.get("skill"),
        state.get("experience"),
        state.get("current_products"),
        state.get("materials"),
        state.get("business_goal"),
        state.get("selected_product"),
        state.get("target_customer"),
        json.dumps(state.get("pricing")),
        json.dumps(state.get("brand")),
        json.dumps(state.get("digital_presence")),
        json.dumps(state.get("marketing")),
        json.dumps(state.get("roadmap"))
    ))

    conn.commit()

    row_id = conn.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    conn.close()

    return row_id


def load_business_from_db(business_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT * FROM businesses WHERE id = ?",
        (business_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def list_saved_businesses():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT id, skill, selected_product, business_goal, created_at
        FROM businesses
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def persist_current_business_state():
    return save_business_to_db(user_state)


# =========================================================
# 5. TOOL SCHEMAS
# =========================================================

def tool_schema(name, description, properties, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False
            }
        }
    }


tools = [
    tool_schema(
        "calculate_price",
        "Calculate product cost, profit and suggested price using Python.",
        {
            "material_cost": {"type": "number"},
            "labor_hours": {"type": "number"},
            "hourly_labor_rate": {"type": "number"},
            "packaging_cost": {"type": "number"},
            "delivery_cost": {"type": "number"},
            "other_costs": {"type": "number"},
            "profit_margin": {"type": "number"}
        },
        [
            "material_cost",
            "labor_hours",
            "hourly_labor_rate",
            "packaging_cost",
            "delivery_cost",
            "other_costs",
            "profit_margin"
        ]
    ),

    tool_schema(
        "assess_skill",
        "Assess the user's skill using information explicitly provided.",
        {
            "skill": {"type": "string"},
            "experience": {"type": "string"},
            "current_products": {"type": "string"},
            "materials": {"type": "string"},
            "interests": {"type": ["string", "null"]},
            "business_goal": {"type": "string"}
        },
        [
            "skill",
            "experience",
            "current_products",
            "materials",
            "business_goal"
        ]
    ),

    tool_schema(
        "plan_product",
        "Plan a first product using user-provided information.",
        {
            "skill": {"type": "string"},
            "product": {"type": "string"},
            "materials": {"type": "string"},
            "target_customer": {"type": "string"},
            "difficulty_level": {"type": "string"},
            "production_time": {"type": "string"}
        },
        [
            "skill",
            "product",
            "materials",
            "target_customer",
            "difficulty_level",
            "production_time"
        ]
    ),

    tool_schema(
        "create_business_roadmap",
        "Create a practical business journey roadmap.",
        {
            "skill": {"type": "string"},
            "selected_product": {"type": "string"},
            "business_goal": {"type": "string"},
            "current_stage": {"type": "string"}
        },
        [
            "skill",
            "selected_product",
            "business_goal",
            "current_stage"
        ]
    ),

    tool_schema(
        "search_business_knowledge",
        "Search verified business knowledge.",
        {
            "query": {"type": "string"}
        },
        ["query"]
    ),

    tool_schema(
        "get_business_state",
        "Retrieve saved business information and missing information.",
        {},
        []
    ),

    tool_schema(
        "save_business_information",
        "Save information explicitly provided by the user.",
        {
            "skill": {"type": ["string", "null"]},
            "experience": {"type": ["string", "null"]},
            "current_products": {"type": ["string", "null"]},
            "materials": {"type": ["string", "null"]},
            "business_goal": {"type": ["string", "null"]},
            "selected_product": {"type": ["string", "null"]},
            "target_customer": {"type": ["string", "null"]}
        }
    ),

    tool_schema(
        "generate_brand_ideas",
        "Generate creative brand suggestions.",
        {
            "skill": {"type": "string"},
            "selected_product": {"type": "string"},
            "business_goal": {"type": "string"}
        },
        ["skill", "selected_product", "business_goal"]
    ),

    tool_schema(
        "generate_digital_content",
        "Generate digital content suggestions.",
        {
            "product": {"type": "string"},
            "brand_name": {"type": "string"},
            "platform": {"type": "string"},
            "content_type": {"type": "string"}
        },
        ["product", "brand_name", "platform", "content_type"]
    ),

    tool_schema(
        "create_marketing_plan",
        "Create a practical marketing plan.",
        {
            "product": {"type": "string"},
            "platform": {"type": "string"},
            "business_goal": {"type": "string"},
            "available_time": {"type": "string"}
        },
        ["product", "platform", "business_goal", "available_time"]
    ),

    tool_schema(
        "get_business_progress",
        "Show completed and remaining business journey stages.",
        {},
        []
    ),

    tool_schema(
        "save_business_to_database",
        "Save current business state to SQLite.",
        {
            "state": {"type": "object"}
        },
        ["state"]
    ),

    tool_schema(
        "load_business_from_database",
        "Load a saved business by ID.",
        {
            "business_id": {"type": "integer"}
        },
        ["business_id"]
    ),

    tool_schema(
        "list_saved_businesses",
        "List saved business records.",
        {},
        []
    )
]


available_functions = {
    "calculate_price": calculate_price,
    "assess_skill": assess_skill,
    "plan_product": plan_product,
    "create_business_roadmap": create_business_roadmap,
    "search_business_knowledge": search_business_knowledge,
    "get_business_state": get_business_state,
    "save_business_information": save_business_information,
    "generate_brand_ideas": generate_brand_ideas,
    "generate_digital_content": generate_digital_content,
    "create_marketing_plan": create_marketing_plan,
    "get_business_progress": get_business_progress,
    "save_business_to_database": save_business_to_db,
    "load_business_from_database": load_business_from_db,
    "list_saved_businesses": list_saved_businesses
}


def execute_tool_call(tool_call):
    function_name = tool_call.function.name
    arguments = json.loads(
        tool_call.function.arguments or "{}"
    )

    if function_name not in available_functions:
        return json.dumps({
            "error": f"Unknown tool: {function_name}"
        })

    try:
        result = available_functions[function_name](**arguments)
        return json.dumps(result, default=str)

    except Exception as e:
        return json.dumps({
            "error": str(e)
        })


# =========================================================
# 6. AGENT
# =========================================================

FULL_SYSTEM_PROMPT = """
You are Talent-to-Business AI Agent.

Your purpose is to help home-based and rural women turn their
existing skills into small digital businesses.

BUSINESS JOURNEY:
Skill → Product → Pricing → Brand → Digital Presence → Marketing → Customers → Growth

RULES:
- Never invent user information.
- Never invent prices, sales, profits, customers, competitors or market demand.
- Ask for missing information.
- AI ideas are suggestions, not verified facts.
- Use tools whenever appropriate.
- Pricing calculations MUST use calculate_price.
- Save only information explicitly provided by the user.
- Use search_business_knowledge for verified business knowledge.
- Do not invent facts outside retrieved knowledge.
- Never invent database IDs.
- Never claim data was saved unless the database tool succeeds.
"""


def create_agent(groq_api_key):
    return Groq(api_key=groq_api_key)


def run_agent(client, user_message, max_iterations=5):
    messages = [
        {"role": "system", "content": FULL_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    for iteration in range(max_iterations):

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        if not assistant_message.tool_calls:
            return {
                "answer": assistant_message.content,
                "iterations": iteration + 1,
                "messages": messages
            }

        for tool_call in assistant_message.tool_calls:
            result = execute_tool_call(tool_call)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })

    return {
        "answer": "The agent reached its tool-call limit.",
        "iterations": max_iterations,
        "messages": messages
    }


initialize_database()

print("Talent-to-Business agent module created.")
print("Tools:", len(tools))
print("Functions:", len(available_functions))
print("Database:", DB_PATH)
