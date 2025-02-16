import os
import subprocess
import time
import tempfile
import logging
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

LOG_FILE = "agent.log"

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

clear_log()

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('OPENAI_API_BASE')


memory = ConversationBufferMemory(memory_key="chat_history")

llm = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ.get("OPENAI_API_BASE"),
    temperature=0
)

prompt = PromptTemplate(
    input_variables=["chat_history", "query"],
    template="Chat History:\n{chat_history}\nUser: {query}\nAI:"
)

chat_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)

def run_adb_command(cmd):
    logger.info(f"Executing ADB command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    output = result.stdout.strip()
    error = result.stderr.strip()
    
    if output:
        logger.info(f"ADB Output: {output}")
    if error:
        logger.error(f"ADB Error: {error}")

    return output

# def prompt_chatgpt(query, xml_file=None):
#     if xml_file:
#         with open(xml_file, 'r') as f:
#             xml_content = f.read()
#         query += f"\nHere is the UI XML:\n{xml_content}"

#     logger.info(f"Prompting GPT-4o Mini: {query}")
#     response = chat_chain.run(query=query)
#     logger.info(f"GPT-4o Mini Response: {response}")
#     return response.strip()

def prompt_chatgpt(query, xml_file=None):
    xml_content = ""
    if xml_file:
        with open(xml_file, 'r') as f:
            xml_content = f.read()
        query_with_xml = f"{query}\nHere is the UI XML:\n{xml_content}"
    else:
        query_with_xml = query

    logger.info(f"Prompting GPT-4o: {query_with_xml}")
    response = chat_chain.llm.predict(prompt.format(chat_history=memory.load_memory_variables({})["chat_history"], query=query_with_xml))

    # Store memory WITHOUT XML
    memory.save_context({"input": query}, {"output": response})

    logger.info(f"GPT-4o Response: {response}")
    return response.strip()

def list_packages():
    output = run_adb_command("adb shell pm list packages")
    return output.split('\n')

def get_relevant_package(task, package_list):
    package_text = "\n".join(package_list)
    query = f'I would like to do "{task}". What is the most relevant package to this? Tell me ONLY the package name. Take packages ONLY FROM THIS LIST:\n{package_text}'
    return prompt_chatgpt(query)

def get_main_activity(package_name):
    # ON MAC
    # output = run_adb_command(f"adb shell dumpsys package {package_name} | grep -A 1 \"Main\"")
    # ON WINDOWS
    output = run_adb_command(f"adb shell dumpsys package {package_name} | findstr /C:\"Main\"")
    query = f"Please extract the {package_name}/<activity> for the app's main activity view intent, only from this output of dumpsys: \n{output}\n. Please tell me in form {package_name}/<activity> and say nothing else.\n{output}"
    return prompt_chatgpt(query)

def run_relevant_package(main_activity):
    run_adb_command(f"adb shell am start -n {main_activity}")
    time.sleep(2)

def dump_ui(temp_dir):
    run_adb_command("adb shell uiautomator dump /sdcard/ui.xml")
    local_path = f"{temp_dir}/ui.xml"
    run_adb_command(f"adb pull /sdcard/ui.xml {local_path}")
    return local_path

def analyze_ui(xml_path, task):
    query = (
        f'I would like to do "{task}". What is this screen showing? '
        "What is the right UI element to invoke? Do we need to go back? "
        "Do we need to scroll on a ScrollView or TextView? "
    )
    return prompt_chatgpt(query, xml_file=xml_path)

def check_stop(task):
    query = (
        f'Based off the previous response, state why or why not we have completed our objective of {task}. If we have, write STOP. Otherwise, DO NOT SAY THAT WORD.'
    )
    return prompt_chatgpt(query)

def get_adb_commands(xml_path):
    query = (
        "Please provide a list of ADB commands necessary to invoke the right UI elements "
        "or go back. Only give ADB commands in a list and nothing else."
    )
    response = prompt_chatgpt(query, xml_file=xml_path)
    commands = [cmd.strip() for cmd in response.splitlines() if cmd.strip()]
    return commands

def run_agent(task):
    logger.info(f"Starting agent for task: {task}")
    
    system_prompt = (
        "You are an AI assistant controlling an Android device via ADB. "
        "If asked to give ADB commands, ONLY give adb commands and nothing else. "
        "If asked otherwise, ONLY use material given to you and no outside knowledge. Use proper grammar."
    )
    memory.clear()
    memory.save_context({"input": "System"}, {"output": system_prompt})
    logger.info(f"System prompt set: {system_prompt}")

    package_list = list_packages()
    package_name = get_relevant_package(task, package_list)
    main_activity = get_main_activity(package_name)
    run_relevant_package(main_activity)

    temp_dir = tempfile.mkdtemp()

    while True:
        xml_path = dump_ui(temp_dir)
        analysis = analyze_ui(xml_path, task)
        check = check_stop(task)
        if "STOP" in check.upper():
            logger.info("Task completed. Exiting.")
            print("DONE")
            break

        adb_commands = get_adb_commands(xml_path)
        for cmd in adb_commands:
            run_adb_command(cmd)
            time.sleep(0.1)

if __name__ == "__main__":
    task_description = "Add a new contact with first name of Donald and surname of Duck with the number 1234567"
    run_agent(task_description)
