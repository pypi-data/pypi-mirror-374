def parse_chat_interface_output(agent_executor_result):
    """
        Parses agent executor result into chat interface response
        return_intermediate_steps must be set as true on the AgentExecutor in order to properly parse plot and suggestions
    """
    messages = [{"role": "assistant", "content": [
                {
                    "type": "text",
                    "text": agent_executor_result["output"]
                }
            ]}]
    suggestions = []
    intermediate_steps = agent_executor_result.get('intermediate_steps', [])
    for step, output  in intermediate_steps:
        if step.tool == "generate_plot":
            messages.append({"role": "assistant", "content": [
                {
                    "type": "image",
                    "image": output
                }
            ]})
        if step.tool == "send_chat_suggestions":
            suggestions = output
            
    return {
        "messages": messages,
        "suggestions": suggestions
    }