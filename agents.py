import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from models import Assessment, AphoristicorResponse, AssessorResponse, PhilosophicalStatement
from typing import Optional


class AphoristicorAgent:
    def __init__(self):
        self.agent = Agent(
            name="Aphoristicor",
            model=OpenAIChat(
                id="gpt-4o"
            ),
            response_model=AphoristicorResponse,
            introduction="""You are Aphoristicor, a philosophical statement creator and refiner. 
            Your role is to craft and iteratively improve philosophical statements based on critical assessments.
            
            When you receive an assessment, you must:
            1. Preserve the core meaning and philosophical insight
            2. Address each identified weakness systematically  
            3. Maintain and strengthen what was assessed as strong
            4. Enhance clarity, precision, and logical coherence
            5. Ensure epistemological soundness
            
            You excel at philosophical reasoning, logical precision, and semantic refinement."""
        )
    
    def create_initial_statement(self, prompt: str) -> AphoristicorResponse:
        system_prompt = f"""Create a philosophical statement based on: "{prompt}"
        
        Craft a thoughtful, precise philosophical statement that:
        - Captures deep philosophical insight
        - Is logically coherent
        - Has epistemological validity
        - Is clear and well-articulated
        
        Return your response as a structured AphoristicorResponse."""
        
        response = self.agent.run(system_prompt)
        return response.content
    
    def refine_statement(self, current_statement: str, assessment: Assessment, iteration: int) -> AphoristicorResponse:
        system_prompt = f"""Current philosophical statement: "{current_statement}"
        
        Assessment received:
        - Overview: {assessment.overview}
        - Strengths: {', '.join(assessment.strengths)}
        - Weaknesses: {', '.join(assessment.weaknesses)}
        - Ranking: {assessment.ranking}/10
        - Reasoning: {assessment.reasoning}
        
        Your task is to refine this statement for iteration {iteration}:
        1. Preserve the core philosophical meaning
        2. Address each weakness systematically:
           {chr(10).join([f'   - {w}' for w in assessment.weaknesses])}
        3. Maintain these strengths:
           {chr(10).join([f'   - {s}' for s in assessment.strengths])}
        4. Enhance clarity, precision, and logical coherence
        5. Improve epistemological validity
        
        Return your refined statement with explanation as AphoristicorResponse."""
        
        response = self.agent.run(system_prompt)
        return response.content


class AssessorAgent:
    def __init__(self):
        self.agent = Agent(
            name="Assessor", 
            model=Claude(
                id="claude-3-5-sonnet-20241022"
            ),
            response_model=AssessorResponse,
            introduction="""You are Assessor, a rigorous philosophical and scientific evaluator.
            Your role is to critically assess philosophical statements from epistemological and scientific reasoning perspectives.
            
            For each statement, provide:
            1. Overview: Comprehensive assessment summary
            2. Strengths: What works well philosophically and logically
            3. Weaknesses: Critical flaws in reasoning, clarity, or validity
            4. Ranking: 1-10 score (1=weakest, 10=strongest) based on:
               - Logical coherence and consistency
               - Epistemological validity
               - Clarity and precision of expression
               - Scientific compatibility where applicable
               - Philosophical depth and insight
            5. Reasoning: Detailed justification for the ranking
            
            Be thorough, rigorous, and constructive in your analysis."""
        )
    
    def assess_statement(self, statement: str, iteration: int) -> AssessorResponse:
        system_prompt = f"""Assess this philosophical statement (iteration {iteration}): "{statement}"
        
        Evaluate from both epistemological and scientific reasoning perspectives:
        
        1. OVERVIEW: Provide a comprehensive assessment summary
        
        2. STRENGTHS: Identify what works well:
           - Logical coherence and structure
           - Epistemological soundness 
           - Clarity of expression
           - Philosophical insight depth
           - Scientific compatibility (where relevant)
        
        3. WEAKNESSES: Identify critical flaws:
           - Logical inconsistencies or fallacies
           - Epistemological problems
           - Ambiguity or vagueness
           - Unsupported claims
           - Scientific inaccuracies (where relevant)
           - Missing philosophical rigor
        
        4. RANKING: Score 1-10 where:
           - 1-3: Fundamental flaws, poor reasoning
           - 4-6: Some merit but significant issues
           - 7-8: Good with minor weaknesses
           - 9-10: Excellent philosophical statement
        
        5. REASONING: Detailed justification for ranking
        
        Return as structured AssessorResponse."""
        
        response = self.agent.run(system_prompt)
        return response.content