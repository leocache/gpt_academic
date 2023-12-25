from toolbox import get_conf
import threading
import logging

timeout_bot_msg = '[Local Message] Request timeout. Network error.'

class GeminiInstance():
    def __init__(self):

        self.time_to_yield_event = threading.Event()
        self.time_to_exit_event = threading.Event()

        self.result_buf = ""

    def generate(self, inputs, llm_kwargs, history, system_prompt):
        # import _thread as thread
        import google.generativeai as genai
        GOOGLE_GEMINI_KEY, GOOGLE_GEMINI_MODEL = get_conf("GOOGLE_GEMINI_KEY", "GOOGLE_GEMINI_MODEL")
        genai.configure(api_key=GOOGLE_GEMINI_KEY,
                        transport='rest',
                        )
        genai.GenerationConfig(
            temperature=llm_kwargs['temperature'],
            top_p=llm_kwargs['top_p'],
        )
        model = genai.GenerativeModel(GOOGLE_GEMINI_MODEL)
        self.result_buf = ""
        print("1")
        response = model.generate_content(
            contents=generate_message_payload(inputs, llm_kwargs, history, system_prompt),
            # "你好"
        )
        print("2")
        # for event in response.events():
        #     if event.event == "add":
        #         self.result_buf += event.data
        #         yield self.result_buf
        #     elif event.event == "error" or event.event == "interrupted":
        #         raise RuntimeError("Unknown error:" + event.data)
        #     elif event.event == "finish":
        #         yield self.result_buf
        #         break
        #     else:
        #         raise RuntimeError("Unknown error:" + str(event))
            
        # logging.info(f'[raw_input] {inputs}')
        # logging.info(f'[response] {self.result_buf}')
        return response.text

def generate_message_payload(inputs, llm_kwargs, history, system_prompt):
    conversation_cnt = len(history) // 2

    messages = [{"role": "user", "parts": system_prompt}, {"role": "model", "parts": "Certainly!"}]

    if conversation_cnt:
        for index in range(0, 2*conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["parts"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "model"
            what_gpt_answer["parts"] = history[index+1]
            if what_i_have_asked["parts"] != "":
                if what_gpt_answer["parts"] == "":
                    continue
                if what_gpt_answer["parts"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]['parts'] = what_gpt_answer['parts']
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["parts"] = inputs
    messages.append(what_i_ask_now)
    return messages
