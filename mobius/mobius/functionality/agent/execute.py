from mobius.models import ActiveTask
import os
import subprocess
import logging
from typing import Dict, Annotated
from dotenv import load_dotenv
from langgraph.graph import Graph, MessageGraph
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import base64

logger = logging.getLogger()

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')

adb_commands = """# App Management
adb install [-l] [-r] [-s] [-d] [-g] <path_to_apk>
adb uninstall [-k] <package_name>
adb shell pm list packages [-f] [-d] [-e] [-s] [-3] [-i] [-u]
adb shell pm clear <package_name>
adb shell pm disable-user [-u <USER_ID>] <package_name>
adb shell pm enable <package_name>
adb shell monkey -p <package_name> -c android.intent.category.LAUNCHER 1

# UI Navigation and Input
adb shell input tap <x> <y>
adb shell input swipe <x1> <y1> <x2> <y2> [duration_ms]
adb shell input draganddrop <x1> <y1> <x2> <y2> [duration_ms]
adb shell input text "<text>"
adb shell input keyevent <keycode>
adb shell input touchscreen swipe <x1> <y1> <x2> <y2> [duration_ms]
adb shell input touchscreen tap <x> <y>
adb shell input touchscreen longpress <x> <y>
adb shell input roll <dx> <dy>

# Key Events (common ones)
adb shell input keyevent KEYCODE_HOME
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_MENU
adb shell input keyevent KEYCODE_APP_SWITCH
adb shell input keyevent KEYCODE_ENTER
adb shell input keyevent KEYCODE_VOLUME_UP
adb shell input keyevent KEYCODE_VOLUME_DOWN
adb shell input keyevent KEYCODE_POWER
adb shell input keyevent KEYCODE_CAMERA
adb shell input keyevent KEYCODE_BRIGHTNESS_UP
adb shell input keyevent KEYCODE_BRIGHTNESS_DOWN

# Gesture Navigation
adb shell wm overscan <left> <top> <right> <bottom>
adb shell cmd statusbar expand-notifications
adb shell cmd statusbar expand-settings
adb shell cmd statusbar collapse
adb shell service call statusbar 1"""

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.4
)

def read_file(filename):
    with open(filename) as f:
        return f.read()
    
def read_xml(filename):
    """Read XML data from file."""
    with open(filename, "r") as f:
        return f.read()
    
def encode_image(image_path):
    """Encode an image as a base64 string."""
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# def list_packages() -> str:
#     """Get list of installed packages."""
#     # return run_adb_command("adb shell pm list packages")
#     return read_file("agent/testPackages.txt")

def init_stage(state: Dict) -> Dict:
    """Initialize the system with necessary context."""
    # System prompt with ADB commands

    system_prompt = f"""You are an AI assistant controlling an Android device via ADB commands. 
The following is a list of potential ADB commands you can use:

{adb_commands}"""

    # Get list of packages
    # packages = list_packages()
    packages = state['task'].handler.call('adb shell pm list packages')['output']
    
    encoded_image = encode_image(state['task'].handler.get_screenshot())
    
    # Construct user message
    
    user_message = [
        {"type": "text", 
        "text": f"""Task: {state['user_task']}

Here are the installed packages on the device:
{packages}

A screenshot of the current screen state is attached to this message.

Based on this task, determine the most relevant package and generate the appropriate ADB command to open it. Output ONLY the ADB command and nothing else. DO NOT add backticks."""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    # Call LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message,)
    ]
    
    
    response = llm.invoke(messages)
    
    # Extract ADB command and execute it

    adb_command = response.content.strip()
    print(adb_command)
    # run_adb_command(adb_command)
    state['task'].handler.call(adb_command)
    
    state['init_response'] = response.content
    return state

def planning_stage(state: Dict) -> Dict:
    """Generate high-level steps for completing the task."""
    system_prompt = """You are an AI assistant controlling an Android device. 

Generate a set of high-level steps to achieve the user's task, similar to how a human would operate the phone.

Focus on user interface interactions and navigation.

DO NOT make assumptions about selecting or interacting with content that is unspecified. For instance, if the user has requested to message 'a friend' but not specified their name, note somewhere that the name is unspecified, or if a user has tasked 'order food' but not specified what food, DO NOT assume the food - write that is must be asked."""

    encoded_image = encode_image(state['task'].handler.get_screenshot())

    user_message = [
        {"type": "text",
        "text": f"""Your task: {state['user_task']}

A screenshot of the current screen state is attached to this message.

Please provide a sequence of steps to complete this task."""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    response = llm.invoke(messages)
    state['plan'] = response.content
    print(response.content.strip())
    return state

def pre_action_stage(state: Dict) -> Dict:
    """Generate initial action before questions."""
    system_prompt = """You are an AI assistant controlling an Android device. You will be provided with:

1. A task the user wants to execute.
2. A set of very high-level instructions generated within a previous context about how to perform the task. These instructions are merely guides and do not have to be applied strictly.
3. A screenshot of the current phone state - autonomously assess what stage the task is currently at.
4. A comprehensive XML representation of the current screen view - keep in mind that objects outside of screen view are not included within this.

You will output a single string, with NO formatting or quotation marks, of a sentence that describes specifically the singular action that must currently be performed. E.g: "Click on the search bar at the top to pull up the search menu." Keep in mind that this action will later be parsed into a an ADB command, and thus it must be a singular action."""
    
    xml_data = read_xml(state['task'].handler.get_xml())
    encoded_image = encode_image(state['task'].handler.get_screenshot())
    
    user_message = [
        {"type": "text", 
         "text": f"""Task: {state['user_task']}

High-level plan:
{state['plan']}

Current screen XML:
{xml_data}"""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    response = llm.invoke(messages)
    state['pre_action'] = response.content.strip()
    print("\nPre-Questions Action:", state["pre_action"])
    return state

def questions_stage(state: Dict) -> Dict:
    """Handle the questioning phase of the task."""
    system_prompt = """You are an AI assistant controlling an Android device. You will be provided with:

1. A task the user wants to execute.
2. A set of very high-level instructions generated within a previous context about how to perform the task. These instructions are merely guides and do not have to be applied strictly.
3. A screenshot of the current phone state - autonomously assess what stage the task is currently at.
4. A comprehensive XML representation of the current screen view - keep in mind that objects outside of screen view are not included within this.
5. The next action you intend to take based on current information.

You will repeatedly assess whether you are missing any information to concretely execute the command, and thus need to ask the user a question for further clarification. For example, if you are messaging someone but the identity is unspecified, or if you are ordering a pizza and the type/topping are unspecified, etc. then in those cases you SHOULD ask a question. If such a question is necessary, output the question as a string - DO NOT output anything except the question itself, including NO formatting. If there is NO question to be asked, output the word "NONE" (WITHOUT the quotation marks)."""

    xml_data = read_xml(state['task'].handler.get_xml())
    encoded_image = encode_image(state['task'].handler.get_screenshot())
    
    qa_pairs = []

    user_message = [
        {"type": "text", 
            "text": f"""Task: {state['user_task']}

High-level plan:
{state['plan']}

Current screen XML:
{xml_data}

Intended next action:
{state['pre_action']}"""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    print("Thinking of a question... ")
    
    while True: 
        response = llm.invoke(messages)

        question = response.content.strip()
        
        if question == "NONE":
            break
            
        print("\nAI Question:", question)
        answer = input("Your answer: ")
        messages.append(AIMessage(content=question))
        messages.append(HumanMessage(content=answer))
        qa_pairs.append({"question": question, "answer": answer})
    
    state['qa_pairs'] = qa_pairs
    print("\nQuestion-Answer Pairs:", state.get("qa_pairs", "No questions were asked"))
    return state

def post_action_stage(state: Dict) -> Dict:
    """Generate final action after questions."""
    system_prompt = """You are an AI assistant controlling an Android device. You will be provided with:
1. A task the user wants to execute.
2. A set of very high-level instructions generated within a previous context about how to perform the task. These instructions are merely guides and do not have to be applied strictly.
3. A screenshot of the current phone state - autonomously assess what stage the task is currently at.
4. A comprehensive XML representation of the current screen view - keep in mind that objects outside of screen view are not included within this.
5. A set of questions and answers between yourself and the user, if applicable - keep in mind that this might not be provided if no questions were asked.

You will output a single string, with NO formatting or quotation marks, of a sentence that describes specifically the singular action that must currently be performed. E.g: "Click on the search bar at the top to pull up the search menu." Keep in mind that this action will later be parsed into a an ADB command, and thus it must be a singular action."""

    xml_data = read_xml(state['task'].handler.get_xml())
    encoded_image = encode_image(state['task'].handler.get_screenshot())
    
    qa_history = ""
    if state.get('qa_pairs'):
        qa_history = "\nQuestion-Answer History:\n"
        for pair in state['qa_pairs']:
            qa_history += f"Q: {pair['question']}\nA: {pair['answer']}\n"
    
    user_message = [
        {"type": "text", 
         "text": f"""Task: {state['user_task']}

High-level plan:
{state['plan']}

Current screen XML:
{xml_data}{qa_history}"""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    response = llm.invoke(messages)
    state['post_action'] = response.content.strip()
    print("\nPost-Questions Action:", state["post_action"])
    return state

def command_generation_stage(state: Dict) -> Dict:
    """Generate ADB commands to execute the current action."""
    system_prompt = f"""You are an AI assistant controlling an Android device through ADB commands. The following is a list of potential ADB commands you can use:

{adb_commands}

You will be provided with:

1. A broad, ultimate task the user wants to execute.
2. A set of very high-level instructions generated within a previous context about how to perform the task. These instructions are merely guides and do not have to be applied strictly.
3. A screenshot of the current phone state.
4. A comprehensive XML representation of the current screen view - keep in mind that objects outside of screen view are not included within this.
5. A string describing the exact action you are currently supposed to execute.

You will output a set of ADB commands to achieve the action you are currently supposed to execute. This might be a single ADB command or it might be more. Output NOTHING but these commands, and place each command on a new line. DO NOT use backticks or any other form of formatting."""

    xml_data = read_xml(state['task'].handler.get_xml() if not state.get('current_xml') else state['current_xml'])
    encoded_image = encode_image(state['task'].handler.get_screenshot() if not state.get('current_image') else state['current_image'])
    
    user_message = [
        {"type": "text", 
         "text": f"""Task: {state['user_task']}

High-level plan:
{state['plan']}

Current screen XML:
{xml_data}

Action to execute:
{state['post_action']}"""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    print("generating commands")
    
    response = llm.invoke(messages)
    
    commands = response.content.strip().split('\n')
    print(commands)
    
    # Store both the commands and the action they're trying to achieve
    state['current_commands'] = commands
    state['current_action'] = state['post_action']
    
    # Execute commands
    for cmd in commands:
        # run_adb_command(cmd.strip())
        state['task'].handler.call(cmd.strip())
    
    # Update state with new screen info
    state['current_xml'] = state['task'].handler.get_xml()
    state['current_image'] = state['task'].handler.get_screenshot()
    
    return state

def verification_stage(state: Dict) -> Dict:
    """Verify if the executed commands achieved the desired outcome."""
    system_prompt = """You are an AI assistant controlling an Android device through ADB commands. You will be provided with:

1. A broad, ultimate task the user wants to execute.
2. A set of very high-level instructions generated within a previous context about how to perform the task. These instructions are merely guides and do not have to be applied strictly.
3. A string describing the exact action you have just executed and what the expected outcome should be.
4. A set of ADB commands you have just executed.
5. A screenshot of the current phone state.
6. A comprehensive XML representation of the current screen view - keep in mind that objects outside of screen view are not included within this.

You will assess whether the actions performed have indeed resulted in the expected outcome, and whether you are free to proceed to the next step. If the actions HAVE indeed been successful, output the single word "RIGHT". If the actions have NOT been successful, output the single word "WRONG" and then, on the next line, a single string, with NO formatting or quotation marks, of a sentence that describes specifically the singular action that must currently be performed to return the phone to the state it was before the most recent action that was performed.

If the FINAL task has been achieved as requested by the user, output the single word "FINISH" instead."""

    xml_data = read_xml(state['current_xml'])
    encoded_image = encode_image(state['current_image'])
    
    commands_text = "\n".join(state['current_commands'])
    
    user_message = [
        {"type": "text", 
         "text": f"""Task: {state['user_task']}

High-level plan:
{state['plan']}

Action just executed:
{state['current_action']}

Commands executed:
{commands_text}

Current screen XML:
{xml_data}"""},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    
    response = llm.invoke(messages)
    
    result = response.content.strip()
    
    if result.startswith("WRONG"):
        # Extract recovery action if present
        parts = result.split('\n')
        if len(parts) > 1:
            state['recovery_action'] = parts[1]
            state['post_action'] = parts[1]  # Set this for the next iteration
    
    state['verification_result'] = result.split('\n')[0]  # Get just the status
    
    # Handle the flow control based on verification result
    if result.startswith("RIGHT"):
        # Reset execution state for next iteration from pre_action
        state = pre_action_stage(state)
        state = questions_stage(state)
        state = post_action_stage(state)
    
    return state

def create_graph() -> MessageGraph:
    """Create the combined workflow with all stages."""
    workflow = Graph()
    
    # Add all nodes
    workflow.add_node("init", init_stage)
    workflow.add_node("planning", planning_stage)
    workflow.add_node("pre_action", pre_action_stage)
    workflow.add_node("questions", questions_stage)
    workflow.add_node("post_action", post_action_stage)
    workflow.add_node("command_generation", command_generation_stage)
    workflow.add_node("verification", verification_stage)
    
    # Define conditional routing
    def router(state: Dict) -> Dict:
        result = state.get('verification_result')
        state['next_node'] = "end" if result == "FINISH" else "command_generation"
        return state

    # Connect nodes in sequence
    workflow.add_edge("init", "planning")
    workflow.add_edge("planning", "pre_action")
    workflow.add_edge("pre_action", "questions")
    workflow.add_edge("questions", "post_action")
    workflow.add_edge("post_action", "command_generation")
    workflow.add_edge("command_generation", "verification")
    
    # Add conditional routing
    workflow.add_node("router", router)
    workflow.add_edge("verification", "router")
    workflow.add_edge("router", "command_generation")
    
    # Set entry point
    workflow.set_entry_point("init")
    
    return workflow.compile()

def run_agent(user_task : str, task: ActiveTask):
    """Main function to run the agent."""
    logger.info(f"Starting agent for task: {task}")
    
    initial_state = {
        "user_task": user_task,
        "task": task
    }
    
    graph = create_graph()
    final_state = graph.invoke(initial_state)
    
    return final_state

async def execute(task: ActiveTask):
    # SAMPLE INVOCATIONS
    # logging.info(task.handler.call("adb shell wm size"))
    # logging.info(task.handler.get_xml())
    # logging.info(task.handler.get_screenshot())
    result = run_agent(user_task = task.natural_language_task, task = task)
    # import pdb; pdb.set_trace()
    print("\nQuestion-Answer Pairs:", result.get("qa_pairs", "No questions were asked"))
    print("\nPost-Questions Action:", result["post_action"])
    print("\nFinal Status:", result["verification_result"])

    return True
