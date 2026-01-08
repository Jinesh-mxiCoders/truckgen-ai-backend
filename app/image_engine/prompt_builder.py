class ImagePromptBuilder:
    """
    Converts structured model specifications into a photorealistic image prompt.
    """

    SYSTEM_PROMPT = (
        "You are a professional industrial vehicle photography generator. "
        "Generate ultra-realistic photographs of heavy construction machines. "
        "No CGI, no illustration, no 3D render."
    )

    NEGATIVE_PROMPT = (
        "cartoon, illustration, CGI, 3D render, toy, miniature, unreal engine, "
        "concept art, anime, distorted proportions, watermark, blurry"
    )

    def build_prompt(
        self,
        category: str,
        model_name: str,
        specifications: dict,
        user_prompt: str | None = None
    ) -> str:
        spec_lines = "\n".join(
            f"- {k}: {v}" for k, v in specifications.items()
        )

        base_prompt = f"""
            Photorealistic industrial photograph of a {category} named "{model_name}".

            Machine specifications:
            {spec_lines}

            Visual characteristics:
            - Industrial-grade steel construction
            - Visible hydraulic hoses, joints, and mechanical components
            - Realistic wear, dust, grease, and concrete residue
            - Safety labels, bolts, and weld seams clearly visible

            Camera:
            - DSLR photograph
            - Natural lighting
            - True-to-scale proportions
            - Sharp focus

            Environment:
            Outdoor construction site, daytime

            Angle:
            Three-quarter view at eye level

            Style:
            Ultra-realistic industrial photography
            """

        if user_prompt:
            base_prompt += f"\nAdditional user instruction:\n{user_prompt}"

        return base_prompt.strip()
