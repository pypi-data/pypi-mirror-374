'''
A collection of prompts for the general reasoning operator.
'''

class GeneralAnswerGeneratorPrompt:
    '''
    The prompt for the answer generator.
    '''
    def __init__(self):
        pass

    def build_prompt(self, question: str) -> str:
        """
        for general reasoning answer generation
        """
        prompt = (
            r'''You are an intelligent chatbot designed for producing the answer to the given reasoning task.
        Remember: DO NOT output anything else, only output the answer you generate.
        Generate a solution to the given task strictly following this format:
        1. Identify key components and premises of the task
        2. Apply relevant principles, theorems, or methods with step-by-step derivation or argument
        3. Perform any necessary calculations or logical checks with intermediate verification
        4. Present the final answer or conclusion in a clear, unambiguous notation

        Format Requirements:
        - Prefix each step with "→" (use the actual arrow symbol, not its Unicode escape sequence)
        - Ensure all symbols and special characters are presented using appropriate markup (e.g., LaTeX commands for mathematical symbols, code formatting for code snippets)

        Example Template:
        Task: Analyze the time complexity of the following sorting algorithm and prove its correctness.

        Solution:
        1. Identify components:
        → Algorithm uses divide-and-conquer to split the list in half
        → Merging step compares elements pairwise

        2. Apply principles:
        → Recurrence: T(n) = 2T(n/2) + O(n)
        → By Master Theorem, T(n) = O(n log n)

        3. Verification:
        → Check base case T(1) = O(1)
        → Inductive step holds for n = 2^k

        4. Conclusion:
        → The algorithm runs in \\boxed{O(n\\log n)} time and correctly sorts any input list.

        Here is the given task you need to solve:
        '''
        )
        return prompt + question + r'''Your response must start directly with "Solution:" without any preamble. Finish your response immediately after the solution.'''


class GeneralQuestionSynthesisPrompt:
    '''
    The prompt for the question synthesis.
    '''
    def __init__(self):
        pass

    def build_prompt(self, items: str, question: str) -> str:
        prompt = f"""
        Create a new, high‑quality reasoning task from the original by applying some of the following transformations (focus on all transformations of "{items}"):

        1. Alter any quantitative or qualitative elements (numbers, dates, variables, data types, code snippets), ensuring the new task remains coherent and solvable.
        2. Change the task type or domain: e.g. switch from calculation to proof, from mathematical derivation to algorithm design, from text analysis to code debugging, or vice versa.
        3. Reframe the scenario in a different real‑world or abstract context (e.g. finance, engineering, language translation, data processing, robotics), incorporating relevant domain details.
        4. Introduce new premises or constraints that require separate consideration or conditional logic in the solution.
        5. Increase complexity by adding multiple interdependent steps, branching cases, or requiring integration of diverse skills (e.g. math + coding + reasoning).
        6. Vary the output format: require a formal proof, pseudocode, annotated explanation, or numeric answer as appropriate.

        Here is the original task:
        {question}

        Generate a fully self‑contained new task inspired by the above. Start directly with the task statement; do NOT include any framing phrases like “Here is a new task inspired by…”. End your response immediately after the task description.
        """
        return prompt
    
class GeneralQuestionFilterPrompt:
    def __init__(self):
        pass
    
    def build_prompt(self, question: str) -> str:
        prompt = f"""You are given a reasoning task. Follow these four steps in order and stop at the first failure:
        0. First, verify the input contains only a single clear reasoning task (no extra instructions like “rewrite”, “translate”, or a provided answer); if not, output judgement_test=false.
        1. Check spelling, grammar, and formatting (e.g. code indentation, LaTeX, Markdown), without interpreting semantics.
        2. For each minimal premise (cannot be further decomposed), verify it does not violate commonsense, domain facts, or task requirements (e.g. “half a person” is invalid; magical operations allowed only if explicitly assumed); if invalid, fail.
        3. Check for any contradictions among premises or in the reasoning process, or if the final result is clearly unreasonable or unsolvable; if so, fail.
        4. If all above pass, check whether there is enough information to complete the task; missing necessary conditions ⇒ fail, redundant details are acceptable.

        After these steps, output exactly:
        {{
            "judgement_test": true/false,
            "error_type": "<error description or null>"
        }}
        You may include your chain of thought, but the final output must be the JSON above.

        Here is the content to evaluate:
        -------------------------------
        {question}
        -------------------------------
        """
        return prompt

