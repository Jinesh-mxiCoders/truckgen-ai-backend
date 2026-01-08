from app.conversation.state.states import ProductType

PRODUCT_SPEC_TEMPLATES = {
    ProductType.BOOM_PUMP: [
        "Vertical Reach",
        "Horizontal Reach",
        "Below Grade Reach w/ Tip Hose",
        "Boom Rotation",
        "Unfolding Height",
        "Pipeline Diameter",
        "Theor. Concrete Output",
        "Max. Pressure on Concrete",
        "Max. Aggregate size",
        "Outrigger Width – Front"
    ],

    ProductType.STATIONARY_PUMP: [
        "Concrete Output Per Hour",
        "Maximum Pressure on Concrete",
        "Maximum Aggregate Size",
        "Concrete Cylinder Diameter",
        "Concrete Cylinder Stroke Length",
        "Outlet Diameter",
        "Engine Power",
        "Hydraulic Tank Capacity"
    ],

    ProductType.PLACING_BOOM: [
        "Vertical Reach",
        "Horizontal Reach",
        "Below Grade Reach w/ Tip Hose",
        "Boom Rotation",
        "Pipeline Diameter",
        "Max. Free Standing Height on Octagonal Mast",
        "Total Picking Weight"
    ],

    ProductType.LOOP_BELT: [
        "Horizontal Reach (Max at 0 degrees)",
        "Vertical Reach (Max at 30 degrees)",
        "Main and Feeder Rate Capacity at 0",
        "Boom Rotation",
        "Unfolding Height",
        "Outrigger Width – Front",
        "Theoretical Concrete Output at 0"
    ]
}
