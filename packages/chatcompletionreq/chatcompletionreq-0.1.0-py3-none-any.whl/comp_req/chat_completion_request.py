import requests
import subprocess
import re
import json


class ChatCompletionRequest:
    def __init__(self, model:str="qwen3-0.6b", api_key:str=None, messages:list=[], max_tokens:int=2096, top_p:float=1.0, top_k:int=50, stop:str|list[str]=None, presence_penalty:float=0.0, frequency_penalty:float=0.0, logit_bias:dict={}, repeat_penalty:float=1.0, seed:int=None):
        
        """
        | Parameter           | Type                       | Description                                                          |
        | ------------------- | -------------------------- | -------------------------------------------------------------------- |
        | `model`             | `string`                   | The model identifier                                                 |
        | `top_p`             | `float`                    | Nucleus sampling threshold (0-1)                                     |
        | `top_k`             | `int`                      | Limits sampling to top-k tokens                                      |
        | `messages`          | `list`                     | List of message dicts for chat (format below)                        |
        | `temperature`       | `float`                    | Controls randomness (0 = deterministic, >1 = more random)            |
        | `max_tokens`        | `int`                      | Maximum tokens to generate in response                               |
        | `stream`            | `bool`                     | Whether to stream responses (if supported)                           |
        | `stop`              | `string` or `list[string]` | Stop sequence(s) to end generation                                   |
        | `presence_penalty`  | `float`                    | Penalizes new tokens based on their presence in text so far          |
        | `frequency_penalty` | `float`                    | Penalizes repeated tokens based on frequency                         |
        | `logit_bias`        | `dict`                     | Map of token IDs to bias values (advanced use)                       |
        | `repeat_penalty`    | `float`                    | Penalizes token repetition in a different way than frequency penalty |
        | `seed`              | `int`                      | Random seed for reproducibility                                      |
        |-------------------------------------------------------------------------------------------------------------------------|     
        | "role"              | "string"                   | Initial model role                                                   |
        | "url"               | "string"                   | Local model url for where the requests are done                      | 
        """
        
        # FOR BEST PERFORMANCE:
        # - lower context length
        # - keep max_tokens low
        # - lower temperature
        # - do not include presemce_penalty, frequency_penalty, logit_bias, ...
        
        self.__model = model
        self.__messages = messages
        self.__max_tokens = max_tokens
        self.__top_p = top_p
        self.__top_k = top_k
        self.__stop = stop
        self.__presence_penalty = presence_penalty
        self.__frequency_penalty = frequency_penalty
        self.__logit_bias = logit_bias
        self.__repeat_penalty = repeat_penalty
        self.__seed = seed
        
        self.__role = "you are a general knowledge assistant, complete any task the user gives you"
        self.__url = "http://localhost:1234/v1/chat/completions"
        self.__api_key = api_key
        
        if not self.__api_key:
            self._run_os_commands(["lms", "server", "start"])
            self._load_only_given_model()
        
    def _run_os_commands(self, comand_list):
        try:
            subprocess.run(comand_list, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}")
        
    def _get_identifiers(self):
        out = subprocess.check_output(["lms", "ps"]).decode("utf-8")
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean_text = ansi_escape.sub('', out)
        identifiers = re.findall(r'(?<=Identifier:\s)[^\s]+', clean_text)
        
        return identifiers

    def _load_only_given_model(self):
        already_loaded = False
        loaded_models = self._get_identifiers()
                
        if loaded_models:
            for mod in loaded_models:
                if mod == self.__model:
                    already_loaded = True
                    print(f"{self.__model} already loaded")
                    continue
                self._run_os_commands(["lms", "unload", mod])
                print(f"unloaded - {mod}")

        if not already_loaded:
            out = subprocess.check_output(["lms", "ls"]).decode("utf-8")
            llm_lines = re.findall(r'LLMs \(Large Language Models\).*?\n(.*?)(?:\n\n|Embedding Models)', out, re.DOTALL)
            if llm_lines:
                llm_names = [line.split()[0] for line in llm_lines[0].splitlines() if line.strip()]

            if self.__model not in llm_names:
                raise ValueError("Model non existent on machine")
            else:
                self._run_os_commands(["lms", "load", self.__model])
                print(f"loaded {self.__model}")
        
    @property
    def model(self):
        return self.__model    
    
    @model.setter
    def load_model(self, new_model_identifier):
        old_model = self.__model
        self.__model = new_model_identifier
        
        try:
            self._load_only_given_model()
            
        except Exception as e:
            print(e)
            self.__model = old_model
            
    @property
    def role(self):
        return self.__role
    
    @role.setter
    def role(self, new_role:str):
        self.__role = new_role
        
    @property
    def messages(self):
        return self.__messages
    
    @property
    def max_tokens(self):
        return self.__max_tokens
    
    @max_tokens.setter
    def max_tokens(self, max_tokens:int):
        self.__max_tokens = max_tokens
        
    @property
    def top_p(self):
        return self.__top_p
    
    @top_p.setter
    def top_p(self, top_p:float):
        self.__top_p = top_p
        
    @property
    def top_k(self):
        return self.__top_k
    
    @top_k.setter
    def top_k(self, top_k:int):
        self.__top_k = top_k
        
    @property
    def stop(self):
        return self.__stop
    
    @stop.setter
    def stop(self, stop:str|list[str]):
        self.__stop = stop
        
    @property
    def presence_penalty(self):
        return self.__presence_penalty
    
    @presence_penalty.setter
    def presence_penalty(self, presence_penalty:float):
        self.__presence_penalty = presence_penalty
        
    @property
    def frequency_penalty(self):
        return self.__frequency_penalty
    
    @frequency_penalty.setter
    def frequency_penalty(self, frequency_penalty:float):
        self.__frequency_penalty = frequency_penalty
        
    @property
    def logit_bias(self):
        return self.__logit_bias
    
    @logit_bias.setter
    def logit_bias(self, logit_bias:dict):
        self.__logit_bias = logit_bias
    
    @property
    def repeat_penalty(self):
        return self.__repeat_penalty
    
    @repeat_penalty.setter
    def repeat_penalty(self, repeat_penalty:float):
        self.__repeat_penalty = repeat_penalty
        
    @property
    def seed(self):
        return self.__seed
    
    @seed.setter
    def seed(self, seed:int):
        self.__seed = seed
        
    @property
    def url(self):
        return self.__url
    
    @url.setter
    def url(self, url:str):
        self.__url = url
        
    
    def _return_stream_content(self, res:requests, return_reasoning:bool):
        with res as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8").strip()
                if not line_str.startswith("data: "):
                    continue

                json_str = line_str[len("data: "):]
                
                if json_str.strip() == "[DONE]":
                    break
                
                try:
                    chunk = json.loads(json_str)
                    delta = chunk["choices"][0]["delta"]
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError):
                    continue      
        
    def _return_content(self, res:requests, return_reasoning:bool):
        if res.ok:
            content = res.json()["choices"][0]["message"]["content"]
            
            if return_reasoning:
                return content
            
            else:
                cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
                return cleaned
        else:
            print("Error:", res.status_code, res.text)
             
        
    def query(self, query:str, with_history:bool=False, return_reasoning:bool=False, temperature:float=0.5, stream:bool=False):

        if with_history:            
            self.__messages.append({"role": "system", "content": self.__role})
            self.__messages.append({"role": "user", "content": f"answer the following: {query}"})
            
        else:
            self.__messages = [{"role": "system", "content": self.__role}, {"role": "user", "content": f"answer the following: {query}"}]
            
        header = {
        "Content-Type": "application/json",
        "Authorization": self.__api_key
        }

        payload = {
            "model": f"{self.__model}",
            "messages": self.__messages,
            "temperature": temperature,
            "max_tokens": self.__max_tokens,
            "stream": stream,
            "top_p": self.__top_p, 
            "top_k": self.__top_k, 
            "stop": self.__stop, 
            "presence_penalty": self.__presence_penalty,
            "frequency_penalty": self.__frequency_penalty,
            "logit_bias": self.__logit_bias,
            "repeat_penalty": self.__repeat_penalty,
            "seed": self.__seed
        }    
        
        res = requests.post(url=self.__url, headers=header, json=payload, stream=stream)
        if stream: 
            return self._return_stream_content(res, return_reasoning)
        
        else:
            return self._return_content(res, return_reasoning)
            
            
if __name__ == "__main__":
    
    # using remote api endpoint
    lm_studio_chat = ChatCompletionRequest(model="mistralai/mistral-7b-instruct:free", api_key="Bearer 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")
    lm_studio_chat.url = "https://openrouter.ai/api/v1/chat/completions"
    
    res = lm_studio_chat.query("what is the power house of a cell?", stream=True)
    for chunk in res:
        print(chunk, end="", flush=True)
    
    """# using local endpoint with lm studio
    lm_studio_chat = ChatCompletionRequest(model="qwen3-0.6b")
    
    res = lm_studio_chat.query("what is the power house of a cell?")
    print(res)"""