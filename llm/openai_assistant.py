import re
import os
import json
import deepl
from typing import Union, List, Literal, Tuple
from openai import OpenAI
from openai.types.beta import Thread


with open("config/api_key.json", "r", encoding="utf-8") as fp:
    KEYS = json.load(fp)

class Assistant:
    def __init__(self, 
                 instructions:str,
                 name:str="Assistant",
                 tools:List[dict]=[{"type": "code_interpreter"}],
                 model:str="gpt-3.5-turbo",
                 description:str=None,
                 file_ids:List[str]=[],
                 metadata:Union[dict, map]={},
                 saveInform:bool=True) -> None:
        '''
        Args:
            ref: https://platform.openai.com/docs/api-reference/assistants/createAssistant
            name (str): assistant의 이름
            instruction (str, required): assistant가 사용할 시스템 명령
                assistant는 서로 다른 message를 갖는 여러 thread가 만들어지더라도 해당 명령만은 반드시 준수
            tools (List[dict]): assistant에서 활성화될 도구 목록
                {"type": "tool_name"} 형태. tool_name: choices=["code_interpreter", "retrieval", "function"]
            model (str): https://platform.openai.com/docs/api-reference/models/list 중 택 1
            description (str): assistant에 대한 설명. 실제 assistant의 동작에는 영향 X
            file_ids (List[str]): openai.client.files.create로 업로드된 file의 id, 최대 20개까지 가능
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 assistant 객체에 메모 형식으로 저장. 실제 assistant의 동작에는 영향 X
            saveInform (bool): assistant 생성 후 관련 정보 저장 옵션(비정상 종료시 assistant 수동 삭제에 사용), default=True
        '''
        self.client = OpenAI(api_key=KEYS["openai"])

        self.asst = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
            description=description,
            file_ids=file_ids,
            metadata=metadata
        )
        self.thread_ids = []    # 스레드를 수동으로 삭제하지 않고 종료시 자동으로 삭제하기 위함

        if saveInform:
            os.makedirs("tmp", exist_ok=True)
            with open(f"tmp/asst_{name}.json", "w") as fp:
                json.dump(
                    {
                        "id": self.asst.id,
                        "name": self.asst.name,
                        "model": self.asst.model,
                        "instructions": self.asst.instructions,
                        "tools": str(self.asst.tools),
                        "file_ids": self.asst.file_ids,
                        "description": description,
                        "metadata": metadata
                    }, fp
                )

    def __del__(self) -> None:
        if self.thread_ids:
            for thread_id in self.thread_ids:
                status = self.delete_thread(thread=thread_id)
        try:
            self.client.beta.assistants.delete(self.asst.id)
        except Exception as e:
            print(f"[ERROR] assistant 제거에 실패했습니다.\n[Error Message] {e}\n[Assistnat Information] {self.asst} (tmp/asst_{self.asst.name}.json)")
            return "failed"
        if os.path.exists(f"tmp/asst_{self.asst.name}.json"):
            os.remove(f"tmp/asst_{self.asst.name}.json")
        return "completed"
    
    def modify(self,
               instructions:str=None,
               name:str=None,
               tools:List[dict]=[],
               model:str=None,
               description:str=None,
               file_ids:List[str]=[],
               metadata:Union[dict, map]={}) -> Tuple[str, str]:
        '''
        Args:
            ref: https://platform.openai.com/docs/api-reference/assistants/createAssistant
            name (str): assistant의 이름
            instruction (str, required): assistant가 사용할 시스템 명령
                assistant는 서로 다른 message를 갖는 여러 thread가 만들어지더라도 해당 명령만은 반드시 준수
            tools (List[dict]): assistant에서 활성화될 도구 목록
                {"type": "tool_name"} 형태. tool_name: choices=["code_interpreter", "retrieval", "function"]
            model (str): https://platform.openai.com/docs/api-reference/models/list 중 택 1
            description (str): assistant에 대한 설명. 실제 assistant의 동작에는 영향 X
            file_ids (List[str]): openai.client.files.create로 업로드된 file의 id, 최대 20개까지 가능
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 assistant 객체에 메모 형식으로 저장. 실제 assistant의 동작에는 영향 X
        Return:
            Status(and Error Message)
        '''
        try:
            if instructions:        
                self.client.beta.assistants.update(self.asst.id, instructions=instructions)
            if name:        
                self.client.beta.assistants.update(self.asst.id, name=name)
            if tools:        
                self.client.beta.assistants.update(self.asst.id, tools=tools)
            if model:        
                self.client.beta.assistants.update(self.asst.id, model=model)
            if description:        
                self.client.beta.assistants.update(self.asst.id, description=description)
            if file_ids:        
                self.client.beta.assistants.update(self.asst.id, file_ids=file_ids)
            if metadata:        
                self.client.beta.assistants.update(self.asst.id, metadata=metadata)
            return "complete"
        except Exception as e:
            return f"failed: {e}"

    def create_thread(self,
                      content:str=None,
                      file_ids:List[str]=[],
                      metadata:Union[dict, map]={},
                      saveInform:bool=True) -> Literal["thread"]:
        '''
        Args:
            ref: https://platform.openai.com/docs/api-reference/threads/createThread
            content (str): assistant(GPT)에 전달할 유저 명령
            file_ids (List[str]): openai.client.files.create로 업로드된 file의 id, 최대 20개까지 가능
                If passing a file at the thread level, the file can only be accessed by a specific thread.
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 thread 객체에 메모 형식으로 저장. 실제 thread의 동작에는 영향 X
            saveInform (bool): thread 생성 후 관련 정보 저장 옵션(비정상 종료시 thread 수동 삭제에 사용), default=True
        Returns:
            thread 객체
        '''
        if content:
            thread = self.client.beta.threads.create(
                role="user",
                content=content,
                file_ids=file_ids,
                metadata=metadata
            )
        else:
            thread = self.client.beta.threads.create()
        self.thread_ids.append(thread.id)
        
        if saveInform:
            os.makedirs("tmp", exist_ok=True)
            with open(f"tmp/thread_{thread.id}.json", "w") as fp:
                json.dump(
                    {
                        "id": thread.id,
                        "object": thread.object,
                        "created_at": thread.created_at,
                        "metadata": thread.metadata
                    }, fp
                )
        return thread

    def delete_thread(self, thread:Union[Thread, str]) -> None:
        '''
        Args:
            thread (openai.types.beta.Thread, str): 삭제할 OpenAI thread 객체
                객체를 그대로 전달하거나, thread.id를 전달
        '''
        try:
            if type(thread) == str:
                id = thread
            else:
                id = thread.id
            self.thread_ids.remove(id)
            self.client.beta.threads.delete(id)
        except:
            print(f"[ERROR] thread 제거에 실패했습니다.\n[Thread Information] {thread}")
            if type(thread) != str and type(thread) != Thread:
                print("올바른 thread 객체 혹은 thread.id를 입력해주세요.")
            return "failed"
        if os.path.exists(f"tmp/thread_{id}.json"):
            os.remove(f"tmp/thread_{id}.json")
        return "completed"

    def add_message(self,
                    thread_id:str,
                    content:str,
                    file_ids:List[str]=[],
                    metadata:Union[dict, map]={}) -> Literal["message"]:
        '''
        Args:
            thread_id (str): 메세지를 추가할 thread의 id
            content (str): 모델에 전달할 메세지
            file_ids (List[str]): openai.client.files.create로 업로드된 file의 id, 최대 10개까지 가능
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 message 객체에 메모 형식으로 저장. 실제 message의 동작에는 영향 X
        Returns:
            message 객체
                ref: https://platform.openai.com/docs/api-reference/messages
        '''
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            conent=content,
            file_ids=file_ids,
            metadata=metadata
        )
        return message

    def get_assistant_response(self,
                               thread_id:str) -> str:
        '''
        Args:
            thread_id (str): 실행한 thread의 id
        Returns:
            사용자의 마지막 입력(메시지)에 대한 assistant의 응답
        '''
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        asst_msg = [msg.content for msg in messages.data if msg.role == "assistant"]
        return asst_msg[0][0].text.value
    
    def create_run(self,
                   thread_id:str,
                   instructions:str=None,
                   additional_instructions:str=None,
                   model:str=None,
                   tools:List[dict]=[],
                   metadata:Union[dict, map]={}) -> Literal["run"]:
        '''
        Args:
            thread_id (str): 실행할 thread의 id
            instructions (str): assistant 생성 시 설정한 instruction을 무시하고 기본으로 실행할 instruction
                per-run으로 동작을 수정하는데에 유용함
            additional_instructions (str): run의 instructions 후 추가로 실행할 instructions
                다른 instruction을 건드리는 일 없이 per-run으로 동작을 수정하는 데에 유용함
            model (str): assistant 생성 시 설정한 모델과 다른 값을 줄 경우 assistant에 연결된 모델이 재정의됨
                그렇지 않으면 assistant와 연결된 모델 사용
            tools (List[dict]): assistant가 이 run에 사용할 수 있는 tool을 재정의
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 run 객체에 메모 형식으로 저장. 실제 run의 동작에는 영향 X
        Returns:
            run 객체
                ref: https://platform.openai.com/docs/api-reference/runs/object
        '''
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.asst.id
        )

        if instructions:
            run = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run.id,
                instructions=instructions
            )
        if additional_instructions:
            run = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run.id,
                additional_instructions=additional_instructions
            )
        if model:
            run = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run.id,
                model=model
            )
        if tools:
            run = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run.id,
                tools=tools
            )
        if metadata:
            run = self.client.beta.threads.runs.update(
                thread_id=thread_id,
                run_id=run.id,
                metadata=metadata
            )
        return run
    
    def run(self,
            thread_id:str,
            instructions:str=None,
            additional_instructions:str=None,
            model:str=None,
            tools:List[dict]=[],
            metadata:Union[dict, map]={}) -> None:
        '''
        Args:
            thread_id (str): 실행할 thread의 id
            instructions (str): assistant 생성 시 설정한 instruction을 무시하고 기본으로 실행할 instruction
                per-run으로 동작을 수정하는데에 유용함
            additional_instructions (str): run의 instructions 후 추가로 실행할 instructions
                다른 instruction을 건드리는 일 없이 per-run으로 동작을 수정하는 데에 유용함
            model (str): assistant 생성 시 설정한 모델과 다른 값을 줄 경우 assistant에 연결된 모델이 재정의됨
                그렇지 않으면 assistant와 연결된 모델 사용
            tools (List[dict]): assistant가 이 run에 사용할 수 있는 tool을 재정의
            metadata (dict, map): 16개의 key-value 쌍. 추가 정보를 run 객체에 메모 형식으로 저장. 실제 run의 동작에는 영향 X
        Returns:
            Status
            Assistant's Response (or error message)
        '''
        _run = self.create_run(thread_id=thread_id,
                               instructions=instructions,
                               additional_instructions=additional_instructions,
                               model=model,
                               tools=tools,
                               metadata=metadata)
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=_run.id
            )

            if run_status.status in ["completed", "failed", "expired"]:
                return run_status.status, self.get_assistant_response(thread_id=thread_id)
            