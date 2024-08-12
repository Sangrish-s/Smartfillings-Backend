from .special_forms import SPECIAL_FORMS


class EmptyException(Exception):
    pass


def select_prompt(prompt_type, form_type, option, min_sentences, max_sentences):
    # hard-coded, to do
    supported_prompt_types = [
        "summary",
        "key_points",
        "red_flags",
        "1_click_analysis",
        "major_changes",
        "activity",
        "contradictions"
    ]

    supported_key_points_options = ["investors", "competitors", "banks", "traders"]

    if prompt_type.lower() not in supported_prompt_types:
        raise EmptyException("Not supported prompt type")

    if (
        prompt_type == "key_points"
        and option.lower() not in supported_key_points_options
    ):
        raise EmptyException("Not supported key points option")

    if prompt_type == "summary":
        return (
            """
            The following is a set of summaries:
            {docs}
            Take these and distill it into a final, consolidated summary of the main themes.
            Helpful Answer:
        """
            + f"""
            Please provide a response that is between {min_sentences} and {max_sentences} sentences long.
        """
        )

    elif prompt_type == "key_points":
        return "List out key points of {docs} that are important for" + option + ":"

    elif prompt_type == "activity":
        return (
            """
            List out activity that occurred within this: 
            {docs}
        """
            + f"""
            Please provide a response that is between {min_sentences} and {max_sentences} sentences long.
        """
        )

    elif prompt_type == "major_changes":
        return (
            """
            List out major changes that occurred with this, if no major changes, have ‘none’: 
            {docs}
        """
        )

    elif prompt_type == "contradictions":
        return (
            """
            Find contradictions in it, but only if they clearly contradict, not by a tiny bit, but by a lot:
            {docs}
        """
        )

    elif prompt_type == "red_flags":
        return "Find red flags in this: {docs}"

    elif prompt_type == "1_click_analysis":
        for config in SPECIAL_FORMS:
            if config["form_type"] == form_type:
                filing_name = config["filing_name"]
                keys = config["keys"]
                key_prompts = "\n\n".join([f"{key}:" for key in keys])

                prompt = (
                    """
                The following is a set of summaries:
                {docs}
                """
                    + f"""
                Please provide a concise summary (5-20 sentences) that addresses the following key topics:
                Filing Name : {filing_name}
                
                Summary:
                
                {key_prompts}
                """
                )
                return prompt

        return (
            f"""Please provide both a concise summary between {min_sentences} and {max_sentences} sentences
        """
            + """
            and a bulleted list of key points for the following text:
            {docs}
            Summary:
            Key Points:
        """
        )

    return ""
