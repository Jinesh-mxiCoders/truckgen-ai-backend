WELCOME_MESSAGE = (
    "Welcome to TruckGen AI.\n"
    "I can help you generate high-quality images of Schwing trucks "
    "based on your project requirements.\n\n"
    "Which product would you like to generate an image for?"
)

PRODUCT_CONFIRMATION = "Great choice. Let’s configure your {product}."

PRODUCT_QUESTIONS = {
    "boom_pump": {
        "Vertical Reach": "Please specify the minimum vertical reach you need for the boom pump. How many feet should it reach?",
        "Horizontal Reach": "Please specify the minimum horizontal reach required for the boom pump in feet.",
        "Below Grade Reach w/ Tip Hose": "What below-grade reach do you need when using a tip hose? Please provide the distance in feet.",
        "Boom Rotation": "What boom rotation (in degrees) is required for your application?",
        "Unfolding Height": "What is the maximum unfolding height allowed on your site? Please provide in feet.",
        "Pipeline Diameter": "What pipeline diameter (in inches) do you require for your boom pump?",
        "Theor. Concrete Output": "Please specify the desired theoretical concrete output of the pump. How many cubic yards per hour should it deliver?",
        "Max. Pressure on Concrete": "What is the maximum concrete pressure (in psi) the pump should safely handle?",
        "Max. Aggregate size": "What is the largest aggregate size (in inches) in your concrete mix that the pump must accommodate?",
        "Outrigger Width – Front": "What is the minimum front outrigger width available at your site? Please provide the measurement in feet."
    },

    "stationary_pump": {
        "Concrete Output Per Hour": "Please specify the desired concrete output per hour. How many cubic yards of concrete should the pump deliver each hour?",
        "Maximum Pressure on Concrete": "What is the maximum pressure (in psi) that the concrete pump needs to handle safely?",
        "Maximum Aggregate Size": "What is the largest size of aggregate (in inches) in your concrete mix that the pump must accommodate?",
        "Concrete Cylinder Diameter": "Do you require a specific concrete cylinder diameter? If yes, please specify the diameter in inches.",
        "Concrete Cylinder Stroke Length": "Do you require a specific concrete cylinder stroke length? If yes, please provide the stroke length in inches.",
        "Outlet Diameter": "What outlet diameter (in inches) do you need for the pump?",
        "Engine Power": "What is the minimum engine power (in horsepower) that the pump should have?",
        "Hydraulic Tank Capacity": "What is the minimum hydraulic tank capacity (in gallons) required for the pump?"
    },

    "placing_boom": {
        "Vertical Reach": "Please specify the vertical reach required for the placing boom in feet.",
        "Horizontal Reach": "Please specify the horizontal reach required for the placing boom in feet.",
        "Below Grade Reach w/ Tip Hose": "What below-grade reach do you need when using a tip hose? Please provide the distance in feet.",
        "Boom Rotation": "What boom rotation (in degrees) is required for your placing boom?",
        "Pipeline Diameter": "What pipeline diameter (in inches) do you need for the placing boom?",
        "Max. Free Standing Height on Octagonal Mast": "What is the maximum free-standing height required on the octagonal mast in feet?",
        "Total Picking Weight": "What is the maximum allowable picking weight at your site? Please provide the weight in pounds."
    },

    "loop_belt": {
        "Horizontal Reach (Max at 0 degrees)": "Please specify the horizontal reach required at 0 degrees in feet.",
        "Vertical Reach (Max at 30 degrees)": "Please specify the vertical reach required at 30 degrees in feet.",
        "Main and Feeder Rate Capacity at 0": "What main and feeder rate capacity is required at 0 degrees? Please provide in cubic yards per minute or per hour.",
        "Boom Rotation": "Do you require full 360-degree boom rotation? If yes, please confirm the degrees required.",
        "Unfolding Height": "What is the maximum allowable unfolding height for the loop belt in feet?",
        "Outrigger Width – Front": "What is the minimum front outrigger width available at your site in feet?",
        "Theoretical Concrete Output at 0": "Please specify the desired theoretical concrete output at 0 degrees. How many cubic yards per hour should it deliver?"
    }
    
}
