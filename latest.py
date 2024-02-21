import re
import openai
from time import time
import textwrap
import streamlit as st

### File operations

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

### API functions
openai.api_key = st.secrets["api_secret"]

def generate_response(conversation, temperature=0, model="gpt-3.5-turbo-0125"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=conversation,
            temperature=temperature,
            max_tokens=2000
        )
        text = response.choices[0].message['content']
        return text, response.usage.total_tokens
    except Exception as e:
        st.error(f"Error communicating with OpenAI: \"{e}\"")
        st.stop()

if __name__ == '__main__':
    # Set OpenAI API key
    openai.api_key = st.secrets["api_secret"]

    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    st.write('Describe your symptoms to the intake bot. Type DONE when done.')


    ### INTAKE PORTION

    while True:
        text = st.text_input('PATIENT:')
        if text == 'DONE':
            break
        user_messages.append(text)
        all_messages.append('PATIENT: %s' % text)
        conversation.append({'role': 'user', 'content': text})
        response, tokens = generate_response(conversation)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('INTAKE: %s' % response)
        st.write('\n\nINTAKE: %s' % response)

    
    ## CHARTING NOTES
    
    print('\n\nGenerating Intake Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN PATIENT INTAKE CHAT>>\n\n%s\n\n<<END PATIENT INTAKE CHAT>>' % text_block
    save_file('logs/log_%s_chat.txt' % time(), chat_log)
    conversation.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(conversation)
    print('\n\nNotes version of conversation:\n\n%s' % notes)
    save_file('logs/log_%s_notes.txt' % time(), notes)
    
    
    ## GENERATING REPORT

    print('\n\nGenerating Hypothesis Report')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_diagnosis.md')})
    conversation.append({'role': 'user', 'content': notes})
    report, tokens = chatbot(conversation)
    save_file('logs/log_%s_diagnosis.txt' % time(), report)
    print('\n\nHypothesis Report:\n\n%s' % report)


    ## CLINICAL EVALUATION

    print('\n\nPreparing for Clinical Evaluation')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_clinical.md')})
    conversation.append({'role': 'user', 'content': notes})
    clinical, tokens = chatbot(conversation)
    save_file('logs/log_%s_clinical.txt' % time(), clinical)
    print('\n\nClinical Evaluation:\n\n%s' % clinical)


    ## REFERRALS & TESTS

    print('\n\nGenerating Referrals and Tests')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_referrals.md')})
    conversation.append({'role': 'user', 'content': notes})
    referrals, tokens = chatbot(conversation)
    save_file('logs/log_%s_referrals.txt' % time(), referrals)
    print('\n\nReferrals and Tests:\n\n%s' % referrals)
