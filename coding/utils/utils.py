import json

from crypto_agent.agents.abe_agent.coding.prompts import TASK_INSTRUECTION,SEARCH_LOC_TASK_INSTRUCTION,OUTPUT_FORMAT_LOC,PR_TEMPLATE

def get_task_instruction(instance: dict, task: str = 'auto_search', include_pr=False, include_hint=False):
    """Identical implementation to original"""
    output_format = None
    instruction = ""

    if task.strip() == 'auto_search':
        # 简化后的 TASK_INSTRUECTION 不再需要 package_name 占位符
        task_description = TASK_INSTRUECTION
    elif task.strip() == 'simple_localize':
        task_description = SEARCH_LOC_TASK_INSTRUCTION
        output_format = OUTPUT_FORMAT_LOC
    else:
        return None

    instruction += task_description

    if include_pr:
        problem_statement = instance['problem_statement']
        instruction += PR_TEMPLATE.format(
            title=problem_statement.strip().split('\n')[0],
            description='\n'.join(problem_statement.strip().split('\n')[1:]).strip()
        )

    if output_format:
        instruction += output_format

    if include_hint:
        instruction += (
            'IMPORTANT: You should ONLY interact with the environment provided to you AND NEVER ASK FOR HUMAN HELP.\n'
            'Don\'t include any lambda functions!\n'
            'You should NOT modify any files!\n'
        )

    return instruction


def convert_to_json(obj):
    if isinstance(obj, list):
        res_obj = []
        for o in obj:
            try:
                json_o = json.loads(o.model_dump_json())
            except:
                json_o = o
            res_obj.append(json_o)
        return res_obj
    else:
        try:
            return json.loads(obj.model_dump_json())
        except:
            print(f'{type(obj)} cannot be converted to json directly.')
            return None

