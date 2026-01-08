WELCOME_MESSAGE = (
    "Welcome to TruckGen AI.\n\n"
    "I can help you generate high-quality images of Schwing trucks "
    "based on your project requirements.\n\n"
    "Which product would you like to generate an image for?\n"
)

PRODUCT_CONFIRMATION = "Great choice. Let’s configure your {product}."

PRODUCT_QUESTIONS = {
    "boom_pump": {
            "Vertical Reach": "What minimum vertical reach is required (feet)?",
            "Horizontal Reach": "What minimum horizontal reach is required (feet)?",
            "Below Grade Reach w/ Tip Hose": "What below-grade reach is required with tip hose (feet)?",
            "Boom Rotation": "What boom rotation is required (degrees)?",
            "Unfolding Height": "What is the maximum allowable unfolding height (feet)?",
            "Pipeline Diameter": "What pipeline diameter is required (inches)?",
            "Theor. Concrete Output": "What theoretical concrete output is required (cubic yards per hour)?",
            "Max. Pressure on Concrete": "What maximum pressure on concrete is required (psi)?",
            "Max. Aggregate size": "What is the maximum aggregate size allowed (inches)?",
            "Outrigger Width – Front": "What minimum front outrigger width is available on site (feet)?"
        },

    "stationary_pump": {
        "Concrete Output Per Hour": "What concrete output is required per hour (cubic yards per hour)?",
        "Maximum Pressure on Concrete": "What maximum pressure on concrete is required (psi)?",
        "Maximum Aggregate Size": "What is the maximum aggregate size of the concrete mix you will use (inches)?",
        "Concrete Cylinder Diameter": "Is a specific concrete cylinder diameter required (inches)?",
        "Concrete Cylinder Stroke Length": "Is a specific concrete cylinder stroke length required (inches)?",
        "Outlet Diameter": "What outlet diameter is required (inches)?",
        "Engine Power": "What minimum engine power is required (horsepower)?",
        "Hydraulic Tank Capacity": "What minimum hydraulic tank capacity is required (gallons)?"
    },

    "placing_boom": {
        "Vertical Reach": "What vertical reach is required (feet)?",
        "Horizontal Reach": "What horizontal reach is required (feet)?",
        "Below Grade Reach w/ Tip Hose": "What below-grade reach is required with tip hose (feet)?",
        "Boom Rotation": "What boom rotation is required (degrees)?",
        "Pipeline Diameter": "What pipeline diameter is required (inches)?",
        "Max. Free Standing Height on Octagonal Mast": "What free-standing height is required on the octagonal mast (feet)?",
        "Total Picking Weight": "What is the maximum allowable picking weight at the site (pounds)?"
    },

    "loop_belt": {
        "Horizontal Reach (Max at 0 degrees)": "What horizontal reach is required at 0 degrees (feet)?",
        "Vertical Reach (Max at 30 degrees)": "What vertical reach is required at 30 degrees (feet)?",
        "Main and Feeder Rate Capacity at 0": "What main and feeder rate capacity is required at 0 degrees (cubic yards per minute or hour)?",
        "Boom Rotation": "Is 360-degree boom rotation required (degrees)?",
        "Unfolding Height": "What is the maximum allowable unfolding height (feet)?",
        "Outrigger Width – Front": "What minimum front outrigger width is available (feet)?",
        "Theoretical Concrete Output at 0": "What theoretical concrete output is required at 0 degrees (cubic yards per hour)?"
    }

}


COUNTER_QUESTION_PROMPT = """
    The user response was unclear.

    Field: {field}
    Original question: {question}
    User response: "{user_input}"

    Ask ONE short clarification question.
    Do not provide examples.
    Do not ask multiple questions.
"""
