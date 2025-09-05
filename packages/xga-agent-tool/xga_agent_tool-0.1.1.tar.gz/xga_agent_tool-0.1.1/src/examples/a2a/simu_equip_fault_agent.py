import logging

from a2a.types import Part, TextPart, AgentCapabilities, AgentCard, AgentSkill
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_task, new_agent_text_message

from xga_agent_tool.tool_base import XGAAgentResult

def getHostFaultCause(input: str)-> XGAAgentResult:
    fault_cause:XGAAgentResult = None
    if 'F02' in input:
        fault_cause:XGAAgentResult = {
            'type': "answer",
            'content': "Host Fault, Fault Cause is 'Host Disk is Damaged' ，Solution is 'Change Host Disk'"
        }
    else:
        fault_cause:XGAAgentResult = {
            'type': "ask",
            'content': f"input your Equip Fault Code"
        }

    return  fault_cause


class EquipFaultAgent:
    async def invoke(self, input:str) -> XGAAgentResult:
        # real agent should select tool, just simulate
        logging.info(f"--- EquipFaultAgent invoke: input={input}")
        result =  getHostFaultCause(input)
        logging.info(f"--- EquipFaultAgent invoke: result={result}")
        return result


getHostFaultCause_skill = AgentSkill(
    id          ="getHostFaultCause",
    name        ="getHostFaultCause",
    description ="Get Host Fault Cause by Code",
    tags        =[],
    examples    =[],
)


def get_agent_card(base_url: str)->AgentCard :
     return AgentCard(
        name                    = "EquipFaultAgent",
        description             = "Locate Equipment Fault Cause",
        url                     = base_url,
        version                 = "1.0.0",
        default_input_modes     = ['text'],
        default_output_modes    = ['text'],
        capabilities            = AgentCapabilities(streaming=True),
        skills                  = [getHostFaultCause_skill],  # Only the basic skill for the public card
        supports_authenticated_extended_card = False,
    )


class EquipFaultAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = EquipFaultAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        agent_result = await self.agent.invoke(query)
        result_type = agent_result['type']
        result_content = agent_result['content']

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        if result_type == 'ask':
            await updater.update_status(
                state = "input-required",
                message = new_agent_text_message(result_content, task.context_id,task.id)
            )
            logging.info("--- EquipFaultAgentExecutor: update_status 'input-required' end")
        else:
            await updater.add_artifact(
                [Part(root=TextPart(text=result_content))],
                name='conversion_result',
            )
            await updater.complete()
            logging.info("--- EquipFaultAgentExecutor: add artifact end")

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('EquipFaultAgentExecutor: cancel not supported')

